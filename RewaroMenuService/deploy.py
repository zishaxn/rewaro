#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil
import zipfile
import tempfile
import json
from typing import Dict, Any

def parse_args():
    parser = argparse.ArgumentParser(description='Deploy Menu Service to AWS')
    parser.add_argument('--environment', '-e', required=True, choices=['dev', 'test', 'prod'],
                      help='Environment to deploy to')
    parser.add_argument('--s3-bucket', '-b', required=False,
                      help='S3 bucket to upload Lambda code to')
    parser.add_argument('--skip-deps', '-s', action='store_true',
                      help='Skip installing dependencies')
    parser.add_argument('--skip-db-init', '-d', action='store_true',
                      help='Skip database initialization')
    parser.add_argument('--env-file', default='env.json',
                      help='Path to environment config file')
    return parser.parse_args()

def load_environment_parameters(env_file: str) -> Dict[str, Any]:
    """Load parameters from environment JSON file"""
    try:
        with open(env_file) as f:
            data = json.load(f)
            return data['Parameters']
    except FileNotFoundError:
        print(f"Error: Environment file {env_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {env_file}")
        sys.exit(1)
    except KeyError:
        print("Error: Missing 'Parameters' key in environment file")
        sys.exit(1)

def run_command(command, cwd=None):
    """Run shell command with error handling"""
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)

def create_lambda_package(environment: str, skip_deps: bool = False):
    """Create Lambda deployment package"""
    print(f"Creating Lambda package for {environment} environment...")
    
    build_dir = tempfile.mkdtemp()
    try:
        # Copy Python files
        for root, _, files in os.walk('.'):
            if any(x in root for x in ['.git', '__pycache__', 'venv']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    rel_path = os.path.relpath(root, '.')
                    os.makedirs(os.path.join(build_dir, rel_path), exist_ok=True)
                    shutil.copy2(os.path.join(root, file), 
                                os.path.join(build_dir, rel_path, file))

        # Install dependencies if not skipped
        if not skip_deps:
            print("Installing dependencies...")
            run_command(['pip', 'install', '-r', 'requirements.txt', '-t', build_dir])

        # Create zip file
        zip_filename = f'menu-service-{environment}.zip'
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(build_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, build_dir)
                    zipf.write(file_path, arcname)

        print(f"Created {zip_filename}")
        return zip_filename

    finally:
        shutil.rmtree(build_dir)

def upload_to_s3(zip_filename: str, bucket_name: str, environment: str):
    """Upload Lambda package to S3"""
    print(f"Uploading {zip_filename} to S3 bucket {bucket_name}")
    s3_key = f"menu-service-{environment}.zip"
    run_command(['aws', 's3', 'cp', zip_filename, f's3://{bucket_name}/{s3_key}'])

def deploy_cloudformation(environment: str, env_params: Dict[str, Any]):
    """Deploy CloudFormation stack with all parameters"""
    print(f"Deploying CloudFormation stack for {environment} environment...")
    
    command = [
        'aws', 'cloudformation', 'deploy',
        '--template-file', 'cloudformation.yaml',
        '--stack-name', f'menu-service-{environment}',
        '--capabilities', 'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM',
        '--parameter-overrides'
    ]
    
    # Add all parameters
    for param, value in env_params.items():
        if isinstance(value, list):
            value = ",".join(value)
        command.append(f"{param}={value}")
    
    run_command(command)

def initialize_database(environment: str, env_params: Dict[str, Any]):
    """Initialize database schema"""
    if environment == 'dev':
        confirm = input("WARNING: Initializing PRODUCTION database. Continue? (y/n): ")
        if confirm.lower() != 'y':
            return

    print("Initializing database...")
    # Implement your database initialization logic here
    # Example: psql -h host -U user -d dbname -f schema.sql

def main():
    args = parse_args()
    env_params = load_environment_parameters(args.env_file)
    
    # Validate required parameters
    required_params = ['DomainName', 'BusinessUserPool', 'LambdaPackagesBucket',
                      'SubnetIds', 'SecurityGroupIds', 'DbHost', 'DbUser',
                      'DbPassword', 'RewaroMenuDbName', 'RegionEnv']
    
    for param in required_params:
        if param not in env_params:
            print(f"Error: Missing required parameter {param} in env.json")
            sys.exit(1)

    # Set environment from CLI args (overrides env.json)
    env_params['Environment'] = args.environment
    
    # Use provided bucket or get from env.json
    bucket_name = args.s3_bucket or env_params['LambdaPackagesBucket']
    
    # Deployment steps
    zip_filename = create_lambda_package(args.environment, args.skip_deps)
    upload_to_s3(zip_filename, bucket_name, args.environment)
    deploy_cloudformation(args.environment, env_params)
    
    if not args.skip_db_init:
        initialize_database(args.environment, env_params)
    
    print("Deployment completed successfully!")

if __name__ == '__main__':
    sys.exit(main())