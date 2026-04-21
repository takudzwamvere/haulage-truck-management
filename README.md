# Haulage Truck Management System

<img width="1363" height="627" alt="20260421_131418" src="https://github.com/user-attachments/assets/9cc4ad23-bcef-4f9f-b83c-2696790a7b54" />


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

<img width="1351" height="626" alt="20260421_131633" src="https://github.com/user-attachments/assets/07bf69ba-9985-4763-87ae-bff82bbcb057" />


Create a superuser to log in:

```bash
docker-compose exec web python manage.py createsuperuser
```
for the live demo, the log in for adim are:
root
password

You can see all logs and can delete records, something regular users cant do

<img width="1351" height="626" alt="20260421_131633" src="https://github.com/user-attachments/assets/6deac200-bd6c-4188-b0c7-6e91af3dd3c1" />


---

## Auth

Frontend auth is simple enough but for the Ninja docs portal, you will have log in through the Auth post method, enter your details and the response is a key you copy and then click authorize button and paste it in the pop up box to log in.

<img width="1330" height="119" alt="20260421_131833" src="https://github.com/user-attachments/assets/e3e8d58c-40ef-4fdd-8efb-d051dbc89ac2" />

Try it out

<img width="1324" height="393" alt="20260421_131849" src="https://github.com/user-attachments/assets/efa46e06-d8bb-4295-8f42-c559cf7689fc" />

Replace the sefaults with user log in info

<img width="355" height="172" alt="20260421_131915" src="https://github.com/user-attachments/assets/ddee5403-ba17-46c1-9f06-ba30f6ef25d6" />

Execute

<img width="1269" height="90" alt="20260421_131922" src="https://github.com/user-attachments/assets/e9033e1c-e64b-4d31-a790-0c0599d9dbfe" />

You get a code, copy it, text only no qoutation marks

<img width="1289" height="215" alt="20260421_131936" src="https://github.com/user-attachments/assets/232d96c7-089f-450a-98eb-ddacba70d63c" />

CLick AUthorize button

<img width="668" height="298" alt="20260421_131955" src="https://github.com/user-attachments/assets/873b2a9c-0fdc-41e6-bcee-8231bc05c98c" />

Paste it and press enter

<img width="667" height="299" alt="20260421_132028" src="https://github.com/user-attachments/assets/614f7874-39db-46cf-a9bb-005fa8c7ec2d" />

You`re in. If you fail, try again

Pagination was implemented here but not in the frontend, might be implemented by the time you see this

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
