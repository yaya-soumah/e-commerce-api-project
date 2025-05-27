# E-commerce API — DRF Backend for Modern Webshops

A robust and modular **Django REST Framework API** for managing e-commerce platforms. 
Built to showscase of clean DRF architecture, secure, role_based access control, production-quality test practices and real-world API features and analytics.

## Features includes:
- JWT Authentication with role & permission system
- Admin/staff APIs for users, roles, and hierarchical permissions
- Product & category management with nested trees
- Sales, payment, and product analytics with date filters
- Tested with `pytest`, `pytest-django`, and `factory_boy` — **91% coverage**.

## Technologies
- Django & DRF
- PostgreSQL (production) & SQLite (testing)
- Redis (caching)
- Swagger
- Pytest + Coverage
- Factory Boy

## Project Structure(Simplified)
```
e-commerce-api-project/
├── apps/ #Modular Django apps(users,orders,analytics,etc.)
├── e_commerce_api_project/
├── media
├── tests/
├── .env
├── manage.py
├── requirements.txt
```

## Setup Instructions
### 1. Clone the repo:
```bash
   git clone https://github.com/<your-username>/ecommerce-api.git
   cd ecommerce-api
```
### 2. Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4.Setup .env file
Example .env:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ecommerce_db
DATABASE_URL=postgresql://postgres:password@localhost:5432/ecommerce_db
DB_USER=your_username 
DB_PASSWORD=your_password 
DB_HOST=localhost 
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
```

### 5. Run migrations and start the server
```
python manage.py migrate
```

### 6. Run Server
```
python manage.py runserver 8888
```

## Usage

BASE URL: `http://127.0.0.1:8888/api/private/v1/`
Authentication: All endpoints require JWT authentication. Include header: `Authorization:Bearer <token>`. 
Swagger Docs: explore API at `http://127.0.0.1:8888/swagger/`
Example: Permission Tree view
```
curl -X 'GET' \
  curl -X GET \
  "http://127.0.0.1:8888/api/private/v1/permissions/?view=tree" \
  -H "Authorization: Bearer <token>" \
  -H "Accept: application/json"
```
Response:
```
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
```

## Key API Endpoints
| Endpoint                   | Method   | Description                        |
| -------------------------- | -------- | ---------------------------------- |
| `/auth/login/`             | POST     | Get JWT token                      |
| `/users/`                  | GET/POST | List / Create users                |
| `/roles/`                  | GET/POST | List / Create roles                |
| `/permissions/`            | GET/POST | List / Create permissions          |
| `/categories/`             | GET/POST | Category management (tree depth 4) |
| `/goods/`                  | GET/POST | Product CRUD                       |
| `/orders/`                 | GET/POST | Order management                   |
| `/reports/sales/`          | GET      | Sales summary (date filtered)      |
| `/reports/products/`       | GET      | Product popularity analytics       |
| `/reports/payment_status/` | GET      | Breakdown by payment status        |
| `/reports/categories/`     | GET      | Category-level sales summary       |

## Test & Coverage
Run Tests:
```
pytest -s -v
```
Run with coverage:
```
pytest apps/ --cov=apps/ --cov-report=html
```
**current test coverage: 91%**

## Contact
**GitHub**: yaya-soumah

**Email**: yaya-soumah@outlook.com

## License
MIT 
