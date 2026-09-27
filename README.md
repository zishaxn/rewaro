# Rewaro — Customer Loyalty & Engagement Platform

Rewaro is a **serverless microservices platform** for restaurants and retail businesses to run loyalty programs, digital coupons, customer feedback collection, digital menus, QR-based engagement, and referral campaigns. Built entirely on **AWS Lambda + API Gateway + PostgreSQL + DynamoDB**, the platform serves both merchants (via a dashboard) and end customers (via mobile-friendly portals).

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Services](#services)
  - [Authentication Portals (React SPAs)](#authentication-portals-react-spas)
  - [Backend Microservices (Python Lambdas)](#backend-microservices-python-lambdas)
- [Database](#database)
- [Shared Lambda Layers](#shared-lambda-layers)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [Deployment](#deployment)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       FRONTEND / AUTH SPAs (React)                        │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────┐     │
│  │ APiManagerAuth  │  │ ClientAuthProd   │  │ CustomerAuthProd    │     │
│  │ (Admin portal)  │  │ (Merchant login) │  │ (Customer login)    │     │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬────────────┘     │
│           └────────────────────┼─────────────────────┘                   │
│                                ▼                                         │
│                     ┌────────────────────┐                               │
│                     │   AWS Cognito      │                               │
│                     │  (3 User Pools)    │                               │
│                     └────────────────────┘                               │
├──────────────────────────────────────────────────────────────────────────┤
│                  AWS API GATEWAY  (services-api-np.rewaro.in)            │
│         Cognito Authorizers · API Key Auth · CORS Preflight              │
├──────────────────────────────────────────────────────────────────────────┤
│                BACKEND MICROSERVICES  (Python 3.12 · AWS Lambda)         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │ DashboardService│  │ CustomerView     │  │ MenuService /    │        │
│  │ (21 Lambdas)    │  │ (15 Lambdas)     │  │ Menu (1 Lambda)  │        │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘        │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │ CouponService   │  │ LoyaltyService   │  │ FeedbackService  │        │
│  │ (2 Lambdas)     │  │ (5 Lambdas)      │  │ (3 Lambdas)      │        │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘        │
│  ┌─────────────────┐                                                     │
│  │ OnboardService  │                                                     │
│  │ (2 Lambdas)     │                                                     │
│  └─────────────────┘                                                     │
├──────────────────────────────────────────────────────────────────────────┤
│                           DATA LAYER                                     │
│  ┌──────────────────┐  ┌───────────────┐  ┌────────────────────┐        │
│  │ PostgreSQL (RDS) │  │ DynamoDB      │  │ S3 Buckets         │        │
│  │ Port 5432        │  │ (feedback,    │  │ (docs, images,     │        │
│  │ 3 databases      │  │  icons, menu) │  │  QR codes, audio)  │        │
│  └──────────────────┘  └───────────────┘  └────────────────────┘        │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐        │
│  │    SNS/SQS (async messaging) · Transcribe · CloudWatch      │        │
│  └──────────────────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer              | Technology                                                                 |
| ------------------ | -------------------------------------------------------------------------- |
| **Backend**        | Python 3.9 / 3.12, AWS Lambda                                             |
| **API Layer**      | AWS API Gateway (REST, Regional) with Cognito Authorizers                  |
| **Auth Frontends** | React 18 (CRA), AWS Amplify v5/v6, AWS Cognito User Pools                 |
| **Database**       | PostgreSQL 13 (Amazon RDS `db.t3.micro`), Amazon DynamoDB                  |
| **ORM**            | SQLAlchemy 1.4 (Menu Service), raw `psycopg2` (all other services)        |
| **Storage**        | Amazon S3 (documents, images, QR codes, audio recordings)                  |
| **Messaging**      | Amazon SNS (FIFO), Amazon SQS (FIFO + standard)                           |
| **AI/ML**          | Amazon Transcribe (audio-to-text for voice feedback)                       |
| **IaC**            | AWS CloudFormation / SAM templates                                         |
| **Image/QR**       | Pillow, `qrcode` library, `sharp` (via layers)                            |
| **Data Processing**| Pandas, `geopy` (geodesic distance), `pytz`                               |

---

## Project Structure

```
Rewaro-Production-Code/
│
│  ── Auth Portals (React SPAs → Cognito) ──
├── RewaroAPiManagerAuth/       # Admin portal – email login (Amplify v5)
├── RewaroClientAuthProd/       # Merchant portal – phone + SMS MFA (Amplify v6)
├── RewaroCustomerAuthProd/     # Customer portal – phone + SMS MFA (Amplify v6)
│
│  ── Backend Microservices (Python Lambdas) ──
├── RewaroDashboardService/     # Merchant dashboard backend (21 Lambdas)
├── RewaroCustomerView/         # Customer-facing backend (15 Lambdas)
├── RewaroMenuService/          # Menu management API – deployable build (single Lambda router)
├── RewaroMenu/                 # Menu management API – source (single Lambda router)
├── RewaroCouponService/        # Coupon CRUD, validation, redemption (2 Lambdas)
├── RewaroLoyaltyService/       # Loyalty milestone journeys (5 Lambdas)
├── RewaroFeedbackService/      # Feedback + audio transcription pipeline (3 Lambdas)
├── RewaroOnboardService/       # Merchant onboarding + QR generation (2 Lambdas)
│
│  ── Infrastructure & Shared Code ──
├── RewaroDatabase/             # PostgreSQL schema SQL + CloudFormation for RDS
├── layers/                     # Shared AWS Lambda layers (Python packages)
├── RewaroServicesDocs/         # API documentation & architecture diagrams
│
└── README.md                   # ← You are here
```

---

## Services

### Authentication Portals (React SPAs)

All three auth services are **React single-page applications** that use **AWS Amplify** with **AWS Cognito User Pools** for identity management. They have no custom backend — authentication is handled directly by Cognito.

| Service                   | Audience               | Auth Method              | MFA    | Amplify | Cognito Region  |
| ------------------------- | ---------------------- | ------------------------ | ------ | ------- | --------------- |
| **RewaroAPiManagerAuth**  | Internal admins        | Email                    | Off    | v5      | `ap-south-1`    |
| **RewaroClientAuthProd**  | Merchants / businesses | Phone number             | SMS ✔  | v6      | `ap-south-1`    |
| **RewaroCustomerAuthProd**| End customers          | Phone number             | SMS ✔  | v6      | `ap-south-1`    |

All run on `localhost:3000` in development. Cognito configuration is statically compiled in source (no `.env` needed).

---

### Backend Microservices (Python Lambdas)

Every backend service follows the same pattern:
- **Runtime:** Python 3.9 or 3.12 on AWS Lambda
- **IaC:** CloudFormation templates in `build/template.yaml` or `template.yaml`
- **Deployment:** Custom Python scripts in `scripts/` (`deploy_cfn.py`, `deploy_lambda.py`, `generate_parameters.py`)
- **Database:** PostgreSQL (RDS) via `psycopg2` Lambda layer
- **Auth:** AWS Cognito User Pool authorizers on API Gateway

---

#### RewaroDashboardService — *Merchant Dashboard Backend*

The main backend for restaurant/business owners. 21 Lambda functions covering:

- Restaurant profile & "About Us" management
- Business operating hours & holiday schedules
- Gallery image uploads (S3 presigned URLs)
- Menu management (categories, items, images)
- Customer visit stamping & loyalty tracking
- Coupon issuance, listing, and redemption
- Review analytics & rating distribution
- Client status & onboarding checks

| Detail         | Value                                                     |
| -------------- | --------------------------------------------------------- |
| Lambda count   | 21                                                        |
| API base path  | `/dashboard`                                              |
| Auth           | Cognito Business User Pool                                |
| Databases      | `rewaro_rewards`, `rewaro_customer`, `rewaro_client` (PG) + DynamoDB |
| Storage        | S3 (gallery images, feedback audio, reward banners)       |

---

#### RewaroCustomerView — *Customer-Facing Backend*

Backend APIs powering the end-customer experience. 15 Lambda functions:

- Restaurant search, discovery, and nearby/featured listings (geodesic distance via `geopy`)
- Customer registration and profile management
- Menu browsing
- Coupon generation and redemption
- Loyalty milestone journey tracking
- Review submission and browsing
- Gallery image viewing

| Detail         | Value                                                     |
| -------------- | --------------------------------------------------------- |
| Lambda count   | 15                                                        |
| API base path  | `/customer-view`                                          |
| Auth           | Cognito Customer User Pool (some endpoints public)        |
| Databases      | `rewaro_rewards`, `rewaro_customer`, `rewaro_client` (PG) + DynamoDB |

---

#### RewaroMenu / RewaroMenuService — *Menu Management API*

Relational menu management microservice using **SQLAlchemy ORM**. A single Lambda with internal routing to handle full CRUD for categories, items, variations, and add-ons.

> `RewaroMenu` is the source repository; `RewaroMenuService` is the deployment-ready build with schema DDL and sample data.

| Detail          | Value                                                    |
| --------------- | -------------------------------------------------------- |
| Lambda count    | 1 (router pattern)                                       |
| API base path   | `/menu-service`                                          |
| Auth            | Cognito Business User Pool                               |
| ORM             | SQLAlchemy 1.4 + `pg8000` / `psycopg2`                  |
| Key endpoints   | `/categories`, `/items`, `/variations`, `/addons`, `/menu`, `/outlets/{id}/menu` |

---

#### RewaroCouponService — *Coupon Management*

Manages the full coupon lifecycle: create/update configurations (PROMO and MARKETING types), associate coupons with phone numbers, list with pagination.

| Detail         | Value                                                     |
| -------------- | --------------------------------------------------------- |
| Lambda count   | 2                                                         |
| API base path  | `/coupon-service`                                         |
| Auth           | Cognito Business User Pool                                |
| Key endpoints  | `POST /create-coupon-config`, `GET /list-coupon-config`   |
| Databases      | `rewaro_rewards`, `rewaro_client` (PostgreSQL)            |
| Extra layers   | Pandas (AWS SDK Pandas layer)                             |

---

#### RewaroLoyaltyService — *Loyalty & Milestone Journeys*

Manages visit-threshold loyalty programs. Merchants define milestone rewards (e.g., free item on 5th visit), track versions, and select reward icons synced from S3.

| Detail         | Value                                                         |
| -------------- | ------------------------------------------------------------- |
| Lambda count   | 5 (+ 1 S3-triggered sync)                                    |
| API base path  | `/loyalty-service`                                            |
| Auth           | Cognito Business User Pool                                    |
| Key endpoints  | `POST /create-reward`, `GET /get-rewards-info`, `GET /reward-icons` |
| Databases      | `rewaro_rewards`, `rewaro_client` (PG) + DynamoDB (`RewardIconsMapping`) |
| Event triggers | S3 `ObjectCreated` → auto-sync reward icons to DynamoDB       |

---

#### RewaroFeedbackService — *Feedback & Audio Transcription Pipeline*

Event-driven feedback collection with audio transcription:
1. Customer submits rating (1–5) with optional text/audio
2. Audio uploaded to S3, event published to **SNS FIFO → SQS FIFO**
3. Worker Lambda transcribes audio via **Amazon Transcribe** and saves to DynamoDB
4. Positive ratings (≥ 3) → return merchant's Google/Instagram links for public review
5. Negative ratings (≤ 2) → route to private contact form for merchant follow-up

| Detail         | Value                                                       |
| -------------- | ----------------------------------------------------------- |
| Lambda count   | 3                                                           |
| API base path  | `/feedback`                                                 |
| Auth           | Public (optional JWT extraction)                            |
| Key endpoints  | `POST /process-feedback`, `POST /feedback-response-form`    |
| Databases      | `rewaro_customer`, `rewaro_client` (PG) + DynamoDB (`CustomerFeedbackTable`) |
| Async pipeline | SNS FIFO → SQS FIFO → Transcribe → DynamoDB                |

---

#### RewaroOnboardService — *Merchant Onboarding & QR Generation*

Automated merchant onboarding:
1. Validates business data (GST, FSSAI, name, address) and uploads compliance documents to S3
2. Creates merchant record in PostgreSQL (`client_master_table`)
3. Publishes SQS message to trigger async QR code generation
4. Worker Lambda generates a branded QR code linking to the merchant's review page

| Detail         | Value                                                       |
| -------------- | ----------------------------------------------------------- |
| Lambda count   | 2                                                           |
| Auth           | Cognito Business User Pool                                  |
| Key endpoints  | `POST /onboard/setup-business` (via parent API Gateway)     |
| Async pipeline | SQS → QR generation → S3 upload                            |
| Libraries      | `qrcode`, `Pillow`                                          |

---

## Database

### PostgreSQL (Amazon RDS)

Provisioned via CloudFormation in [`RewaroDatabase/template.yaml`](RewaroDatabase/template.yaml) as a `db.t3.micro` PostgreSQL 13 instance.

**Instance:** `common-postgres` · **Port:** `5432` · **Region:** `ap-south-1`

Three logical databases:

| Database           | Purpose                              | Key Tables                                                        |
| ------------------ | ------------------------------------ | ----------------------------------------------------------------- |
| `rewaro_client`    | Merchant profiles & business data    | `client_master_table`, `client_info_table`, `client_business_timings` |
| `rewaro_customer`  | Customer identity & profiles         | `customer_master_table`                                           |
| `rewaro_rewards`   | Loyalty, coupons, & reward tracking  | `coupon_configurations`, `coupon_associations`, `customer_coupons`, `customer_progress`, `coupon_terms_and_conditions` |

Schema SQL files: [`client_db_tables.sql`](RewaroDatabase/client_db_tables.sql), [`customer_db_tables.sql`](RewaroDatabase/customer_db_tables.sql), [`rewards_db_tables.sql`](RewaroDatabase/rewards_db_tables.sql), [`menu_db_tables.sql`](RewaroDatabase/menu_db_tables.sql)

### Amazon DynamoDB

Used alongside PostgreSQL for specific workloads:

| Table                     | Service                    | Purpose                              |
| ------------------------- | -------------------------- | ------------------------------------ |
| `CustomerFeedbackTable`   | FeedbackService            | Ratings, text reviews, transcripts   |
| `RewardIconsMapping`      | LoyaltyService             | Reward icon metadata (synced from S3)|
| Menu category/item tables | DashboardService, CustomerView | Menu data caching                |

---

## Shared Lambda Layers

The [`layers/`](layers/) directory contains pre-packaged **Python Lambda layers** for common dependencies:

| Layer              | Contents                              | Used By                           |
| ------------------ | ------------------------------------- | --------------------------------- |
| `psycopg` / `postgres-layer` | `psycopg2-binary` 2.9.9 + `libpq.so` | All backend services       |
| `pandas`           | `pandas` 2.2, `numpy` 2.0            | CouponService                     |
| `geopy_layer`      | `geopy` 2.4.1                         | CustomerView (distance calc)      |
| `pytz`             | `pytz` 2024.2                          | CustomerView (timezone handling)  |
| `request`          | `requests` 2.32.3                      | FeedbackService (transcription)   |
| `lxml` + `bs4`     | `lxml` 5.2, `beautifulsoup4` 4.12     | OnboardService (QR SVG parsing)   |

---

## API Documentation

Detailed API docs are available in [`RewaroServicesDocs/`](RewaroServicesDocs/):

| File                                                              | Description                              |
| ----------------------------------------------------------------- | ---------------------------------------- |
| [`Onboarding.png`](RewaroServicesDocs/Onboarding.png)            | Onboarding architecture flow diagram     |
| [`feedback_service_overview.pdf`](RewaroServicesDocs/feedback_service_overview.pdf) | Feedback service API spec (5 pages) |

Individual service docs are also found in each service's `Docs/` or `ReadMe.md`.

---

## Environment Variables

Each service reads from a `.env` file (see `sample.env` in each directory). Core variables:

### Database & Network (all services)

```env
DB_HOST=<RDS endpoint>
DB_PORT=5432
DB_USER=<master username>
DB_PASSWORD=<master password>
SUBNET_IDS=subnet-xxx,subnet-yyy
SECURITY_GROUP_IDS=sg-xxx
REGION_ENV=ap-south-1
```

### Database Names

```env
REWARO_CLIENT_DB_NAME=rewaro_client
REWARO_CUSTOMER_DB_NAME=rewaro_customer
REWARO_REWARDS_DB_NAME=rewaro_rewards
REWARO_MENU_DB_NAME=rewaro_menu
```

### Auth

```env
BUSINESS_USER_POOL=arn:aws:cognito-idp:ap-south-1:...:userpool/...
CUSTOMER_USER_POOL=arn:aws:cognito-idp:ap-south-1:...:userpool/...
```

### Lambda & Deployment

```env
DOMAIN_NAME=services-api-np.rewaro.in
LAMBDA_PACKAGES_BUCKET=rewaro-lambda-packages
PSYCOPG2_LAYER=arn:aws:lambda:ap-south-1:...:layer:postgres:1
PANDAS_LAYER=arn:aws:lambda:ap-south-1:...:layer:AWSSDKPandas-Python312:15
CFN_S3_BUCKET=rewaro-cfn-packages
STACK_NAME=<service-stack-name>
```

### S3 Buckets

```env
CLIENT_MASTER_BUCKET=onboard-service-client-master-data-prod
CUSTOMER_FEEDBACK_AUDIOS_BUCKET=customer-feedback-audios
REWARD_JOURNEY_DATA_BUCKET_NAME=rewaro-reward-journey-data
```

---

## Getting Started

### Prerequisites

- **Python** 3.9+ (3.12 recommended)
- **AWS CLI** configured with appropriate IAM permissions
- **PostgreSQL** client (for schema setup)
- **Node.js** 16+ (for React auth portals only)
- **pip** for Python dependencies

### 1. Set Up the Database

```bash
# Create the RDS instance via CloudFormation
aws cloudformation deploy \
  --template-file RewaroDatabase/template.yaml \
  --stack-name common-postgres \
  --parameter-overrides file://RewaroDatabase/params.json

# Apply schema files
psql -h <RDS_HOST> -U mydbadmin -d rewaro_client -f RewaroDatabase/client_db_tables.sql
psql -h <RDS_HOST> -U mydbadmin -d rewaro_customer -f RewaroDatabase/customer_db_tables.sql
psql -h <RDS_HOST> -U mydbadmin -d rewaro_rewards -f RewaroDatabase/rewards_db_tables.sql
psql -h <RDS_HOST> -U mydbadmin -d rewaro_menu -f RewaroDatabase/menu_db_tables.sql
```

### 2. Configure Environment Variables

```bash
# For each service
cp sample.env .env
# Edit .env with your values
```

### 3. Deploy Backend Services

Each service follows a 3-step deployment:

```bash
cd <ServiceDirectory>

# Generate CloudFormation parameters from .env
python scripts/generate_parameters.py

# Deploy CloudFormation stack (creates Lambdas, API Gateway, IAM roles, etc.)
python scripts/deploy_cfn.py

# Deploy individual Lambda function code
python scripts/deploy_lambda.py <function-name>
```

### 4. Run Auth Portals (Development)

```bash
cd RewaroClientAuthProd   # or RewaroCustomerAuthProd / RewaroAPiManagerAuth
npm install
npm start                 # Opens on localhost:3000
```

### Recommended Deployment Order

1. **Database** — RDS + schema
2. **Lambda Layers** — Upload to S3 / create layers
3. **RewaroOnboardService** — Merchant onboarding pipeline
4. **RewaroFeedbackService** — Feedback collection
5. **RewaroCouponService** & **RewaroLoyaltyService** — Rewards engine
6. **RewaroDashboardService** — Merchant dashboard APIs
7. **RewaroMenuService** — Menu management
8. **RewaroCustomerView** — Customer-facing APIs
9. **Auth portals** — React SPAs (deploy to S3 + CloudFront)

---

## Deployment

All backend services are deployed as **AWS Lambda functions** behind **API Gateway**, provisioned via **CloudFormation** templates. The deployment pipeline:

1. `generate_parameters.py` reads `.env` and produces `build/parameters.json`
2. `deploy_cfn.py` uploads the CloudFormation template to S3 and creates/updates the stack
3. `deploy_lambda.py` packages individual Lambda function code into zip archives and updates the function

Frontend auth portals are standard React builds that can be deployed to S3 + CloudFront or any static hosting.

---

## License

Proprietary. All rights reserved.
