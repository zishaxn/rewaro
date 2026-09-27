import os
import sys
import shutil
import zipfile
import subprocess
import time
import stat
from dotenv import load_dotenv
from InquirerPy import inquirer
import boto3

# Load environment variables from configs/.env
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, "configs", ".env"))

LAMBDA_PACKAGES_BUCKET = os.getenv("LAMBDA_PACKAGES_BUCKET")
PACKAGES_SUBFOLDER = os.getenv("PACKAGES_SUBFOLDER")
LAMBDA_NAME = os.getenv("LAMBDA_NAME")

REQUIREMENTS_PATH = os.path.join(BASE_DIR, "requirements.txt")
ROUTES_DIR = os.path.join(BASE_DIR, "routes")
APP_FILE = os.path.join(BASE_DIR, "app.py")

# Handle read-only files during deletion
def handle_remove_readonly(func, path, exc):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Error while force-deleting {path}: {e}")

# Robustly delete a directory with retries
def safe_rmtree(path, retries=3, delay=1):
    for i in range(retries):
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
            return
        except PermissionError as e:
            print(f"PermissionError on attempt {i+1}: {e}")
            time.sleep(delay)
    print(f"Failed to delete {path} after {retries} attempts.")

# Helper: Install dependencies to a local 'package' dir
def install_dependencies(target_dir):
    if os.path.exists(target_dir):
        safe_rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    print(f"Installing dependencies from {REQUIREMENTS_PATH} to {target_dir} ...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_PATH, "-t", target_dir], check=True)

# Helper: Zip routes/ and app.py (and dependencies)
def create_zip(zip_path, package_dir):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add dependencies
        for root, _, files in os.walk(package_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, package_dir)
                zipf.write(abs_path, rel_path)
        # Add routes/
        for root, _, files in os.walk(ROUTES_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, BASE_DIR)
                zipf.write(abs_path, rel_path)
        # Add app.py
        zipf.write(APP_FILE, os.path.relpath(APP_FILE, BASE_DIR))
    print(f"Created zip package: {zip_path}")

# Helper: Upload zip to S3
def upload_to_s3(zip_file):
    s3 = boto3.client("s3")
    s3_key = f"{PACKAGES_SUBFOLDER}/{os.path.basename(zip_file)}"
    print(f"Uploading {zip_file} to s3://{LAMBDA_PACKAGES_BUCKET}/{s3_key}")
    s3.upload_file(zip_file, LAMBDA_PACKAGES_BUCKET, s3_key)
    print("✅ Upload to S3 complete.")

# Helper: Upload zip directly to Lambda
def upload_to_lambda(zip_file):
    lambda_client = boto3.client("lambda")
    print(f"Uploading {zip_file} directly to Lambda: {LAMBDA_NAME}")
    with open(zip_file, "rb") as f:
        lambda_client.update_function_code(
            FunctionName=LAMBDA_NAME,
            ZipFile=f.read()
        )
    print("✅ Lambda function updated.")

def main():
    # Ask user for upload method
    upload_method = inquirer.select(
        message="Where do you want to upload?",
        choices=["s3", "lambda"],
        default="s3"
    ).execute()

    # Install dependencies locally
    package_dir = os.path.join(BASE_DIR, "package")
    install_dependencies(package_dir)

    # Create zip
    zip_filename = f"menu-service-package.zip"
    zip_path = os.path.join(BASE_DIR, zip_filename)
    create_zip(zip_path, package_dir)

    # Upload according to method
    if upload_method == "s3":
        upload_to_s3(zip_path)
    else:
        upload_to_lambda(zip_path)

    # Cleanup
    safe_rmtree(package_dir)
    try:
        os.remove(zip_path)
    except Exception as e:
        print(f"⚠️ Failed to delete zip file: {e}")

    print("🎉 Done!")

if __name__ == "__main__":
    main()
