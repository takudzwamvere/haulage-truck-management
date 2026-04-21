# Haulage Truck Management System

A full-stack web application for managing haulage trucks, drivers, and job assignments. Built with Django and PostgreSQL, with a REST API powered by Django Ninja.

**Live demo:** [haulagetrucks.lol](https://haulagetrucks.lol)
Just a little extra something, hosted on a Hetzner VPS using Dokploy which deploys docker containers like a charm
---

## Tech Stack

- **Backend:** Django 6, Django Ninja (REST API)
- **Database:** PostgreSQL 16
- **Frontend:** Django Templates
- **Auth:** JWT (Bearer tokens)
- **Containerisation:** Docker, Docker Compose

---

## Quick Start

```bash
git clone https://github.com/takudzwamvere/haulage-truck-management.git
cd haulage-truck-management
docker-compose up --build
```

Then visit:
- **Portal:** http://localhost:8000 or https://haulagetrucks.lol
- **API docs:** http://localhost:8000/api/docs or https://haulagetrucks.lol/api/docs

Create a superuser to log in:

```bash
docker-compose exec web python manage.py createsuperuser
```
for the live demo, the log in for adim are:
root
password

You can see all logs and can delete records, something regular users cant do
---
##Auth

Frontend auth is simple enough but for the Ninja docs portal, you will have log in through the Auth post method, enter your details and the response is a key you copy and then click authorize button and paste it in the pop up box to log in.

Pagination was implemented here but not in the frontend, might be implemented by the time you see this

## Testing the API

1. Visit http://localhost:8000/api/docs
2. Use `POST /api/auth/login/` with your credentials
3. Copy the `access_token` from the response
4. Click **Authorize** at the top right and enter `Bearer your_token_here`
5. All endpoints are now unlocked

---

## Running Tests

```bash
docker-compose exec web python manage.py test core --verbosity=2
```

There are 5 tests covering the core business rules — truck and driver assignment logic, job status transitions, and constraint validation.

---

## Project Structure

```
core/       — models, API endpoints, schemas, auth, business logic, tests
portal/     — frontend views, forms, templates, user management
haulage/    — project settings and URLs
```

---

## Environment Variables

Copy `.env.example` to `.env` and update the values before running in production.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` or `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated list of trusted origins with scheme |
| `DATABASE_URL` | PostgreSQL connection string |
