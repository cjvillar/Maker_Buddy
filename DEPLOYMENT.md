# MakeBuddy — Docker Deployment Guide

## Project Structure (new files)

```
my_django_app/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── requirements.txt
└── config/
    └── settings.py      
```

---

## Quick Start (local)

```bash
# 1. Copy and fill in your environment variables
cp .env.example .env
# Edit .env with your SECRET_KEY, DB password, and OAuth credentials

# 2. Build and start
docker compose up --build

# 3. Create a superuser (first time only)
docker compose exec web python manage.py createsuperuser
```

App will be available at http://localhost:8000

---

## Environment Variables

| Variable | Required | Notes |
|---|---|---|
| `SECRET_KEY` | Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | Set to `0` in production |
| `ALLOWED_HOSTS` |  Comma-separated, e.g. `myapp.com,www.myapp.com` |
| `POSTGRES_DB` |  Database name |
| `POSTGRES_USER` |  Database user |
| `POSTGRES_PASSWORD` |Use a strong password |
| `GOOGLE_CLIENT_ID` |  Required for Google OAuth |
| `GOOGLE_CLIENT_SECRET` | Required for Google OAuth |
| `GITHUB_CLIENT_ID` |  Required for GitHub OAuth |
| `GITHUB_CLIENT_SECRET` | Required for GitHub OAuth |

---

## Deploying to Digital Ocean (App Platform)

1. **Push your code to GitHub** (make sure `.env` is in `.gitignore`)

2. **Create a new App** in the DO App Platform:
   - Source: your GitHub repo
   - Build: Docker (it will detect the `Dockerfile`)

3. **Add a PostgreSQL database** in the App's "Resources" tab:
   - DO will inject `DATABASE_URL` automatically

4. **Set environment variables** in App Platform Settings → Environment Variables

5. **Set `ALLOWED_HOSTS`** to your DO app domain (e.g. `myapp.ondigitalocean.app`)

6. **Add a persistent volume** for `/app/media` (for uploaded images)

### Alternative: Digital Ocean Droplet with Docker Compose

```bash
# On the droplet:
git clone https://github.com/you/makebuddy.git
cd makebuddy
cp .env.example .env  # fill in values
docker compose up -d --build
```

---

## Deploying to AWS (Elastic Beanstalk)

1. **Install EB CLI**: `pip install awsebcli`

2. **Initialize**:
```bash
eb init -p docker makebuddy --region us-east-1
eb create makebuddy-prod
```

3. **Set env vars**:
```bash
eb setenv SECRET_KEY=... ALLOWED_HOSTS=... DEBUG=0 ...
```

4. **For the database**: Use **AWS RDS (PostgreSQL)** and set `DATABASE_URL` accordingly.

5. **For media files**: Consider migrating `MEDIA_ROOT` to **S3** using `django-storages` (future enhancement).

### Alternative: AWS EC2 with Docker Compose

```bash
# On EC2 instance (Amazon Linux 2 / Ubuntu):
sudo yum install docker git -y   # or apt-get
sudo systemctl start docker
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

git clone https://github.com/you/makebuddy.git
cd makebuddy
cp .env.example .env   # fill in values
docker-compose up -d --build
```

---

## What Changed in settings.py

- **Database**: Now reads `DATABASE_URL` env var for PostgreSQL; falls back to SQLite for local dev without Docker
- **Static files**: Added `whitenoise` middleware for serving static files without a separate server
- **STATIC_ROOT**: Added for `collectstatic` (required in production)
- **STORAGES**: Uses `CompressedManifestStaticFilesStorage` for caching/compression
- **ALLOWED_HOSTS**: Now reads from env var (comma-separated)

---

## Useful Commands

```bash
# View logs
docker compose logs -f web

# Run migrations manually
docker compose exec web python manage.py migrate

# Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web python manage.py test

# Stop everything
docker compose down

# Stop and delete volumes (deletes DB data)
docker compose down -v
```
