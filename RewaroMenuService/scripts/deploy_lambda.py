import os
import zipfile
import boto3
import argparse
import subprocess
import shutil
import sys
import tempfile
import json

# Base path where Lambda functions are stored (root directory)
BASE_PATH = os.path.dirname(os.path.dirname(__file__))  # One level up from 'scripts'
REQUIREMENTS_FILE = os.path.join(BASE_PATH, "requirements.txt")
CLOUDFORMATION_FILE = os.path.join(BASE_PATH, "cloudformation.yaml")
ENV_FILE = os.path.join(BASE_PATH, "env.json")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Update Lambda Function Code")
    parser.add_argument("-e", "--environment", required=True, choices=['dev', 'test', 'prod'],
                      help='Environment to deploy to')
    parser.add_argument("--region", default="ap-south-1", help="AWS region (default: ap-south-1)")
    parser.add_argument("--skip-deps", action="store_true", help="Skip installing dependencies")
    return parser.parse_args()

def get_function_name(environment):
    """Get Lambda function name from environment"""
    return f"menu-service-{environment}"

def run_command(command, cwd=None):
    """Run shell command with error handling"""
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        sys.exit(1)

def create_lambda_package(skip_deps=False):
    """Create Lambda deployment package"""
    print("Creating Lambda package...")
    
    build_dir = tempfile.mkdtemp()
    try:
        # Copy Python files
        for root, _, files in os.walk(BASE_PATH):
            if any(x in root for x in ['.git', '__pycache__', 'venv', 'scripts']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    rel_path = os.path.relpath(root, BASE_PATH)
                    os.makedirs(os.path.join(build_dir, rel_path), exist_ok=True)
                    shutil.copy2(os.path.join(root, file), 
                                os.path.join(build_dir, rel_path, file))

        # Install dependencies if not skipped
        if not skip_deps:
            print("Installing dependencies...")
            run_command(['pip', 'install', '-r', REQUIREMENTS_FILE, '-t', build_dir])

        # Create zip file
        zip_filename = "lambda_package.zip"
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

def update_lambda_function(function_name, zip_filename, region):
    """Update Lambda function code directly"""
    print(f"Updating Lambda function {function_name}...")
    client = boto3.client("lambda", region_name=region)

    with open(zip_filename, "rb") as zip_file:
        response = client.update_function_code(
            FunctionName=function_name, 
            ZipFile=zip_file.read()
        )

    print(f" Lambda {function_name} updated at {response['LastModified']}")

def cleanup(zip_filename):
    """Clean up temporary files"""
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print(f" Removed deployment zip file: {zip_filename}")

def main():
    args = parse_args()
    
    # Get function name based on environment
    function_name = get_function_name(args.environment)
    
    try:
        # Create Lambda package
        zip_filename = create_lambda_package(args.skip_deps)
        
        # Update Lambda function
        update_lambda_function(function_name, zip_filename, args.region)
        
        print("Deployment completed successfully!")
    finally:
        # Clean up temporary files
        cleanup(zip_filename)

if __name__ == "__main__":
    sys.exit(main())
