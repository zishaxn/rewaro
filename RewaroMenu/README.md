# Menu Management Microservice

This project is a **Menu Management Microservice** designed to handle menu operations for merchants and customers. It provides a set of RESTful APIs to manage menu categories, items, variations, and add-ons. The service is built to be deployed on AWS Lambda and uses a PostgreSQL database for data storage.

## Key Features
- **Menu Categories Management**: Create, update, delete, and list menu categories.
- **Menu Items Management**: Handle operations for menu items, including CRUD operations.
- **Item Variations**: Manage variations of items, such as size or spice level.
- **Item Add-ons**: Manage add-ons for items, like extra cheese or toppings.
- **Menu Browsing**: Customers can browse the complete menu for a specific outlet.

## API Endpoints
- **Categories**: CRUD operations for menu categories.
- **Items**: CRUD operations for menu items, including attaching/detaching variations and add-ons.
- **Variations**: CRUD operations for item variations.
- **Add-ons**: CRUD operations for item add-ons.
- **Menu**: Retrieve the complete menu for a specific outlet.

## Deployment
The service is designed to be deployed on AWS Lambda with an RDS PostgreSQL database. Deployment scripts are provided for both development and production environments using AWS CloudFormation.

## Database
The database schema includes tables for categories, items, variations, and add-ons, with relationships managed through association tables. Triggers are used to update timestamps on modification.

## Error Handling
The service includes comprehensive error handling and logging to ensure robust operation and easy debugging.

```bash
# Deploy to development environment
aws cloudformation deploy --template-file cloudformation.yaml --stack-name menu-service-dev --parameter-overrides Environment=dev

# Deploy to production environment
aws cloudformation deploy --template-file cloudformation.yaml --stack-name menu-service-prod --parameter-overrides Environment=prod
```
