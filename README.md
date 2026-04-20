# Haulage Truck Management System

## Getting Started

```bash
git clone https://github.com/takudzwamvere/haulage-truck-management.git
cd haulage-truck-management
docker-compose up --build
```

Then visit:
- **Portal:** http://localhost:8000
- **API docs:** http://localhost:8000/api/docs

To log in, create a superuser by running:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Testing the API in Swagger

1. Visit http://localhost:8000/api/docs
2. Use POST `/api/auth/login/` with your credentials.
3. Copy the `access_token` from the response.
4. Click **Authorize** at the top right of the page.
5. Enter `Bearer your_token_here`.
6. All endpoints are now unlocked and ready to test.

## Running Tests

```bash
python manage.py test core --verbosity=2
```
There are 5 tests that cover the core business rules and make sure assignments work properly.

## Project Structure

```
core/            — models, API endpoints, schemas, auth, business logic, tests
portal/          — frontend views, forms, templates, user management
haulage/         — project settings and URLs
Dockerfile       — container definition
docker-compose.yml — wires Django and PostgreSQL together
```
