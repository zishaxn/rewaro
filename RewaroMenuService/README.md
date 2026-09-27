# Menu Management Microservice

This microservice provides APIs for merchants to create, update, and manage their menus, and for customers to browse menus.

## Features

- Menu categories management
- Menu items management
- Item variations (e.g., size, spice level)
- Item add-ons (e.g., extra cheese)
- Relationship with merchant data via outlet_id

## API Endpoints

### Categories
- GET /categories - List all categories
- GET /categories/{id} - Get category by ID
- POST /categories - Create a new category
- PUT /categories/{id} - Update a category
- DELETE /categories/{id} - Delete a category

### Menu Items
- GET /items - List all menu items
- GET /items/{id} - Get menu item by ID
- POST /items - Create a menu item
- PUT /items/{id} - Update a menu item
- DELETE /items/{id} - Delete a menu item

### Variations
- GET /variations - List all variations
- GET /variations/{id} - Get variation by ID
- POST /variations - Create a variation
- PUT /variations/{id} - Update a variation
- DELETE /variations/{id} - Delete a variation

### Add-ons
- GET /addons - List all add-ons
- GET /addons/{id} - Get add-on by ID
- POST /addons - Create an add-on
- PUT /addons/{id} - Update an add-on
- DELETE /addons/{id} - Delete an add-on

### Menu Management
- POST /items/{id}/variations/{variation_id} - Attach variation to menu item
- DELETE /items/{id}/variations/{variation_id} - Detach variation from menu item
- POST /items/{id}/addons/{addon_id} - Attach add-on to menu item
- DELETE /items/{id}/addons/{addon_id} - Detach add-on from menu item

### Menu Browsing
- GET /outlets/{outlet_id}/menu - Get complete menu for an outlet

## Deployment

This service is designed to be deployed on AWS Lambda with an RDS PostgreSQL database.

```bash
# Deploy to development environment
aws cloudformation deploy --template-file cloudformation.yaml --stack-name menu-service-dev --parameter-overrides Environment=dev

# Deploy to production environment
aws cloudformation deploy --template-file cloudformation.yaml --stack-name menu-service-prod --parameter-overrides Environment=prod
```
