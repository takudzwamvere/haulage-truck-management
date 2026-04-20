# Haulage Truck Management System

This is my technical assessment submission for Marytechenock Solutions. I made sure to meet every requirement from the assessment document, and I've ticked them off below so you can check them easily.

### Tech Stack
- Django 6
- Django Ninja (REST API + Swagger docs)
- PostgreSQL
- Docker + Docker Compose
- Bootstrap 5
- Gunicorn
- Whitenoise

## 1. Assessment Requirements Checklist

**Core requirements:**
- [x] Truck Management — register, update, view, delete trucks (Truck ID, Registration Number, Capacity, Status)
- [x] Driver Management — create, update, view, delete drivers (Driver ID, Name, License Number, Phone Number)
- [x] Job Management — create jobs, assign truck and driver, update status, view, delete (all required fields implemented)
- [x] Business rule: trucks blocked when in transit or under maintenance
- [x] Business rule: drivers cannot have multiple active jobs
- [x] Business rule: job status affects truck availability — truck freed automatically on completion or cancellation

**Technical requirements:**
- [x] REST API with Django Ninja
- [x] PostgreSQL database
- [x] Docker containerization with docker-compose

**Deliverables:**
- [x] GitHub repository
- [x] README with setup instructions
- [x] Docker setup — runs with `docker-compose up`
- [x] API documentation via Swagger UI at `/api/docs`

**Bonus:**
- [x] Authentication — JWT for API, session auth for portal
- [x] Pagination — all list endpoints paginated
- [x] Logging — server side logging to file, viewable in portal
- [x] Unit tests — 5 business rule tests, all passing

## 2. Project Overview

This system manages trucks, drivers, and delivery jobs for a haulage company. It provides a REST API for the backend and a simple web portal for the frontend. Both the API and the portal enforce the exact same business rules to keep data consistent.

## 3. Getting Started

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

## 4. Testing the API in Swagger

1. Visit http://localhost:8000/api/docs
2. Use POST `/api/auth/login/` with your credentials.
3. Copy the `access_token` from the response.
4. Click **Authorize** at the top right of the page.
5. Enter `Bearer your_token_here`.
6. All endpoints are now unlocked and ready to test.

## 5. Running Tests

```bash
python manage.py test core --verbosity=2
```
There are 5 tests that cover the core business rules and make sure assignments work properly.

## 6. Project Structure

```
core/            — models, API endpoints, schemas, auth, business logic, tests
portal/          — frontend views, forms, templates, user management
haulage/         — project settings and URLs
Dockerfile       — container definition
docker-compose.yml — wires Django and PostgreSQL together
```

## 7. Live Demo

Live at: https://yourdomain.lol

## 8. Tech Decisions

Django Ninja was chosen over DRF for its automatic Swagger docs and simpler schema definitions. I used session auth for the portal since it runs in the same browser context, and JWT for the API so it can work from any client. A single Django project serves both the API and the portal, which keeps the stack simple and puts the business logic in one place. I used Bootstrap 5 via CDN for the frontend because it has no build step and keeps the Docker image lean.
