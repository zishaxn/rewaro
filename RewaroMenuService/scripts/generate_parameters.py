import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the base path of the project (one level up from `scripts/`)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILD_DIR = os.path.join(BASE_DIR, "build")
PARAMETERS_FILE = os.path.join(BUILD_DIR, "parameters.json")

# Ensure build directory exists
os.makedirs(BUILD_DIR, exist_ok=True)


def get_env_var(key, default=None):
    """Retrieve an environment variable, return None if not found (unless default is set)."""
    value = os.getenv(key, default)
    return (
        value if value not in (None, "", "null") else None
    )  # Exclude empty or "null" values


# Define parameter structure (only include vars that exist in the environment)
parameters_list = [
    {"ParameterKey": "SubnetIds", "ParameterValue": get_env_var("SUBNET_IDS")},
    {
        "ParameterKey": "SecurityGroupIds",
        "ParameterValue": get_env_var("SECURITY_GROUP_IDS"),
    },
    {"ParameterKey": "RegionEnv", "ParameterValue": get_env_var("REGION_ENV")},
    {
        "ParameterKey": "BusinessUserPool",
        "ParameterValue": get_env_var("BUSINESS_USER_POOL"),
    },
    {"ParameterKey": "DomainName", "ParameterValue": get_env_var("DOMAIN_NAME")},
    {"ParameterKey": "DbHost", "ParameterValue": get_env_var("DB_HOST")},
    {
        "ParameterKey": "DbPort",
        "ParameterValue": get_env_var("DB_PORT", "5432"),
    },  # Always retain DB_PORT with default
    {"ParameterKey": "DbUser", "ParameterValue": get_env_var("DB_USER")},
    {"ParameterKey": "DbPassword", "ParameterValue": get_env_var("DB_PASSWORD")},
    {
        "ParameterKey": "RewaroRewardsDbName",
        "ParameterValue": get_env_var("REWARO_REWARDS_DB_NAME"),
    },
    {
        "ParameterKey": "RewaroCustomerDbName",
        "ParameterValue": get_env_var("REWARO_CUSTOMER_DB_NAME"),
    },
    {
        "ParameterKey": "RewaroClientDbName",
        "ParameterValue": get_env_var("REWARO_CLIENT_DB_NAME"),
    },
    {
        "ParameterKey": "MerchantOnboardLambda",
        "ParameterValue": get_env_var("MERCHANT_ONBOARD_LAMBDA"),
    },
    {
        "ParameterKey": "ClientMasterTable",
        "ParameterValue": get_env_var("CLIENT_MASTER_TABLE"),
    },
    {
        "ParameterKey": "ClientInfoTable",
        "ParameterValue": get_env_var("CLIENT_INFO_TABLE"),
    },
    {
        "ParameterKey": "CouponsConfigTable",
        "ParameterValue": get_env_var("COUPONS_CONFIG_TABLE"),
    },
    {
        "ParameterKey": "CouponPhoneAssociationTable",
        "ParameterValue": get_env_var("COUPON_PHONE_ASSOCIATION_TABLE"),
    },
    {
        "ParameterKey": "CustomerCouponsTable",
        "ParameterValue": get_env_var("CUSTOMER_COUPONS_TABLE"),
    },
    {
        "ParameterKey": "TermsAndConditionsTable",
        "ParameterValue": get_env_var("TERMS_AND_CONDITIONS_TABLE"),
    },
    {
        "ParameterKey": "CustomerProgressTable",
        "ParameterValue": get_env_var("CUSTOMER_PROGRESS_TABLE"),
    },
    {
        "ParameterKey": "CustomerMasterTable",
        "ParameterValue": get_env_var("CUSTOMER_MASTER_TABLE"),
    },
    {
        "ParameterKey": "ClientBusinessTimingsTable",
        "ParameterValue": get_env_var("CLIENT_BUSINESS_TIMINGS_TABLE"),
    },
    {
        "ParameterKey": "CustomerFeedbackTable",
        "ParameterValue": get_env_var("CUSTOMER_FEEDBACK_TABLE"),
    },
    {
        "ParameterKey": "LambdaPackagesBucket",
        "ParameterValue": get_env_var("LAMBDA_PACKAGES_BUCKET"),
    },
    {"ParameterKey": "Psycopg2Layer", "ParameterValue": get_env_var("PSYCOPG2_LAYER")},
]

# Remove parameters where the value is None
filtered_parameters = [
    param for param in parameters_list if param["ParameterValue"] is not None
]

# Save to parameters.json
with open(PARAMETERS_FILE, "w") as f:
    json.dump(filtered_parameters, f, indent=2)

print(f"✅ parameters.json generated successfully at {PARAMETERS_FILE}!")
print(
    f"📌 Included Parameters: {[param['ParameterKey'] for param in filtered_parameters]}"
)
