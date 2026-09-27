import boto3
import os
import sys
import json
from dotenv import load_dotenv
import datetime

# Load environment variables from .env
load_dotenv()

STACK_NAME = os.getenv("STACK_NAME")
TEMPLATE_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "build", "template.yaml")
)
PARAMETERS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "build", "parameters.json")
)
S3_BUCKET = os.getenv("CFN_S3_BUCKET")  # Add S3 bucket name in .env
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
TEMPLATE_S3_KEY = f"{STACK_NAME}/{timestamp}_template.yaml"

if not STACK_NAME or not S3_BUCKET:
    print("❌ Error: STACK_NAME or S3_BUCKET is missing in the environment variables.")
    sys.exit(1)

s3_client = boto3.client("s3")
cf_client = boto3.client("cloudformation")

# Upload template to S3
print(f"📤 Uploading template to S3: s3://{S3_BUCKET}/{TEMPLATE_S3_KEY}")
try:
    s3_client.upload_file(TEMPLATE_FILE, S3_BUCKET, TEMPLATE_S3_KEY)
    template_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{TEMPLATE_S3_KEY}"
    print(f"✅ Template uploaded successfully! URL: {template_url}")
except Exception as e:
    print(f"❌ Failed to upload template to S3: {e}")
    sys.exit(1)

# Load parameters
if not os.path.exists(PARAMETERS_FILE):
    print(f"❌ Error: Parameters file not found: {PARAMETERS_FILE}")
    sys.exit(1)

with open(PARAMETERS_FILE, "r") as f:
    parameters = json.load(f)

parameter_overrides = [
    {"ParameterKey": p["ParameterKey"], "ParameterValue": str(p["ParameterValue"])}
    for p in parameters
]

# Deploy the stack using TemplateURL
print(f"🚀 Deploying CloudFormation stack: {STACK_NAME}...")
try:
    response = cf_client.create_stack(
        StackName=STACK_NAME,
        TemplateURL=template_url,
        Parameters=parameter_overrides,
        Capabilities=["CAPABILITY_NAMED_IAM"],
    )
    print(f"✅ Deployment initiated! Stack ID: {response['StackId']}")
except cf_client.exceptions.AlreadyExistsException:
    print("⚠️ Stack already exists, updating instead...")
    try:
        response = cf_client.update_stack(
            StackName=STACK_NAME,
            TemplateURL=template_url,
            Parameters=parameter_overrides,
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )
        print(f"🔄 Stack update initiated! Stack ID: {response['StackId']}")
    except cf_client.exceptions.ClientError as e:
        if "No updates are to be performed" in str(e):
            print("✅ No changes detected. Stack is already up to date.")
        elif "Parameters: [BusinessUserPool] do not exist in the template" in str(e):
            print(f"⚠️ Warning: {e}")
            # Continue with further code execution
        else:
            print(f"❌ Stack update failed: {e}")
            sys.exit(1)
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    sys.exit(1)
