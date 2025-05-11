# E-commerce API

A Django REST Framework API for an e-commerce platform with user management, permissions, roles, categories, attributes, products, orders, and analytics.

## Features
- **Users**: CRUD, JWT auth, email uniqueness, role assignment, admin-only non-safe requests.
- **Permissions**: CRUD, tree view (depth 3).
- **Roles**: CRUD, tree view.
- **Categories**: CRUD, tree view (depth 4).
- **Attributes**: CRUD, pricing support.
- **Products**: CRUD, image uploads, state management.
- **Orders**: CRUD, state/address updates, shipping tracking.
- **Analytics**: Sales, product, payment status reports with date filtering and caching.

## Setup
1. Clone:
   ```bash
   git clone https://github.com/<your-username>/ecommerce-api.git
   cd ecommerce-api


Virtual environment:python -m venv .venv
.venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Set up Postgres (ecommerce_db), Redis.
Configure .env

Example .env:
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ecommerce_db
DATABASE_URL=postgresql://postgres:password@localhost:5432/ecommerce_db
DB_USER=your_username 
DB_PASSWORD=your_password 
DB_HOST=localhost 
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1


Migrate:python manage.py migrate


Run:set DJANGO_SETTINGS_MODULE=ecommerce_api.settings.dev
python manage.py runserver 8888


API Endpoints
BASE: http://127.0.0.1:8888/api/private/v1/
All endpoints require JWT authentication. All requests must have in the header the "Authorization" attribute set to "Bearer <token>".  Explore the API at http://127.0.0.1:8888/swagger/.


Endpoint
Method
Description
Query Parameters



/api/private/v1/auth/login/
POST
Get JWT token
None


/api/private/v1/users/
POST
create users
None


/api/private/v1/users/
GET
List of users with filter
query, pagenum, pagesize


/api/private/v1/users/<id>/
GET, PUT, DELETE
User details/update/delete
None


/api/private/v1/users/<id>/assign-role/
PATCH
Assign a role to a user
None


/api/private/v1/permissions/
POST
create permissions
None


/api/private/v1/permissions/
GET
List of Permissions in list view or tree view (depth 3)
view

/api/private/v1/permissions/<id>/
GET, PUT, DELETE
Permission details/update/delete
None


/api/private/v1/roles/
GET, POST
List/Create role
None

/api/private/v1/roles/<id>/
GET, PUT, DELETE
Role details/update/delete
None

/api/private/v1/categories/
POST
create categories
None


/api/private/v1/categories/
GET
List of categories (depth 4)
level, pagenum, pagesize


/api/private/v1/categories/<id>/
GET, PUT, DELETE
Categorie details/update/delete
None


/api/private/v1/categories/<id>/attributes/
GET, POST
List/create attributes of a category
None

/api/private/v1/categories/<id>/attributes/<attr_id>
GET, PUT, DELETE
Attributes details/update/delete
None


/api/private/v1/goods/
GET, POST
List/create products
None

/api/private/v1/goods/<id>
GET, PUT, DELETE
Products details/update/delete
None

/api/private/v1/upload/
POST
Upload a product png image
None


/api/private/v1/orders/
GET, POST
List/create orders
None


/api/private/v1/orders/<id>/change_address/
PATCH
Update order address
None


/api/private/v1/orders/<id>/update_tracking/
POST
Update carrier, tracking number or status
None


/api/private/v1/reports/sales/
GET
Sales report
start_date, end_date


/api/private/v1/reports/products/
GET
Product popularity report
start_date, end_date


/api/private/v1/reports/payment_status/
GET
Payment status report
start_date, end_date


Example Request
Get Permissions tree view:
curl -X 'GET' \
  'http://127.0.0.1:8888/api/private/v1/permissions/' \
  -H 'accept: application/json' \
  -H 'X-CSRFTOKEN: 4IzFN7qk9holElKCXfzkAKKsOZsygJSH'

Response:
{
    "status": "success",
    "data": [
        {
            "id": 2,
            "name": "Browse products",
            "level": 1,
            "parent": null,
            "children": [],
            "created_at": "2025-05-05T13:47:05.053580Z",
            "updated_at": "2025-05-12T01:28:54.576289Z"
        },
        {
            "id": 3,
            "name": "Manage all users",
            "level": 1,
            "parent": null,
            "children": [
                {
                    "id": 4,
                    "name": "Create roles",
                    "level": 2,
                    "parent": 3,
                    "children": [],
                    "created_at": "2025-05-05T13:47:05.056783Z",
                    "updated_at": "2025-05-12T01:33:54.727378Z"
                },
                {
                    "id": 5,
                    "name": "Delete roles",
                    "level": 2,
                    "parent": 3,
                    "children": [],
                    "created_at": "2025-05-12T01:34:32.304825Z",
                    "updated_at": "2025-05-12T01:34:32.304838Z"
                }
            ],
            "created_at": "2025-05-05T13:47:05.055528Z",
            "updated_at": "2025-05-12T01:33:27.152729Z"
        }
    ],
    "message": "Operation successful",
    "errors": null,
    "meta": {}
}

Project Structure
e-commerce-api-project/
├── apps/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   ├── attributes/
│   ├── auth/
│   ├── categories/
│   ├── core/
│   ├── orders/
│   ├── permissions/
│   ├── products/
│   ├── roles/
│   ├── users/
│   ├── __init__.py
├── ecommerce_api/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── swagger.py
├── media
├── tests/
├── .env
├── .gitignore
├── manage.py
├── README.md
├── requirements.txt


License
MIT```
