# Deployment Guide: Vercel + Neon Postgres & Object Storage

This guide explains how to deploy the **Haulage Truck Management System** to [Vercel](https://vercel.com/) with a serverless [Neon PostgreSQL](https://neon.tech/) database and [Neon Object Storage](https://neon.tech/) (S3-compatible) for photo uploads.

---

## 1. Before Publishing (Local Setup)

> [!IMPORTANT]
> **Shared Production Database & Object Storage:**
> Local runs configured with `.env.local` connect directly to the same **Neon production branch** and **assets S3 bucket** as the live site. Any records created, profiles modified, or photos uploaded during local testing will be immediately visible on the live deployed application.

Run these exact commands locally in order before publishing to Vercel:

```bash
# 1. Run migrations against Neon direct/unpooled connection
python manage.py migrate

# 2. Seed the fleet with 10 Zimbabwean drivers and 10 trucks (idempotent)
python manage.py seed_fleet

# 3. Create your administrative superuser account
python manage.py createsuperuser

# 4. Start the local server to log in, test driver profiles, and upload photos
python manage.py runserver
```

Once running locally at `http://127.0.0.1:8000/`:
1. Log into the portal at `/login/` with your superuser credentials.
2. Edit truck records and upload truck photos.
3. Edit driver records, link a User account to a Driver, and test `/drivers/me/` self-service profile and photo upload.
4. Verify photos render properly via signed S3 URLs.

---

## 2. Set Vercel Environment Variables

In your [Vercel Project Settings](https://vercel.com/) under **Settings** → **Environment Variables**, configure the following variables:

| Variable | Value / Description |
| :--- | :--- |
| `DATABASE_URL` | Neon pooled PostgreSQL connection string (`-pooler` host with `?sslmode=require`) |
| `AWS_ACCESS_KEY_ID` | Neon Object Storage S3 access key ID (from `.env.local`) |
| `AWS_SECRET_ACCESS_KEY` | Neon Object Storage S3 secret access key (from `.env.local`) |
| `AWS_ENDPOINT_URL_S3` | Neon Object Storage S3 endpoint URL (e.g. `https://storage.neon.tech`) |
| `AWS_REGION` | S3 AWS region identifier (e.g. `us-east-1`) |
| `SECRET_KEY` | Cryptographically random secret string (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DEBUG` | `False` (mandatory in production) |
| `ALLOWED_HOSTS` | `.vercel.app` (plus any custom domain, comma-separated) |
| `CSRF_TRUSTED_ORIGINS` | `https://*.vercel.app` (plus any custom domain HTTPS URL) |

> [!NOTE]
> Database migrations should be executed locally using `DATABASE_URL_UNPOOLED` / `DIRECT_URL`. Vercel build runs `python manage.py collectstatic --noinput` to bundle static assets into WhiteNoise.

---

## 3. Deploy to Vercel

### Option A: Via Vercel CLI
```bash
# Install Vercel CLI if needed
npm install -g vercel

# Deploy to production
vercel --prod
```

### Option B: Via Git Integration
1. Push your repository to GitHub / GitLab / Bitbucket.
2. Import the project in Vercel.
3. Configure the environment variables listed in Section 2.
4. Click **Deploy**.

---

## 4. Post-Deployment Verification

After the deployment succeeds:

1. **Verify API Documentation**:
   Navigate to `https://<your-app>.vercel.app/api/docs`.
   Confirm the OpenAPI interactive docs load and show all Truck, Driver, Job, and Auth endpoints.

2. **Verify Static CSS**:
   Visit `https://<your-app>.vercel.app/login/`.
   Verify that Tailwind CSS styles, styling cards, and buttons load properly without 404 errors (served via WhiteNoise `CompressedManifestStaticFilesStorage`).

3. **Verify Image Upload & Signed URLs**:
   - Log in as admin and visit `/trucks/` or `/drivers/`.
   - Edit a truck or driver and upload a photo (JPEG/PNG/WebP, < 2 MB).
   - Verify the photo appears on list and detail pages.
   - Inspect the image element: verify that `src` is a secure signed S3 URL with AWS credentials parameters (`X-Amz-Signature`, `X-Amz-Expires`) and that the browser loads it with HTTP 200.
