# MAKER BUDDY  
[![Django CI](https://github.com/cjvillar/Maker_Buddy/actions/workflows/django.yml/badge.svg?branch=main)](https://github.com/cjvillar/Maker_Buddy/actions/workflows/django.yml)

MakerBuddy is a platform to showcase hardware projects—from early prototypes to finished builds.  

Document your builds with project pages, track components, and share your work with other makers.  
Discover new ideas, stay accountable, and actually finish what you start.

---

##  Quick Start (Docker – Recommended)

This project uses Docker with **PostgreSQL + Gunicorn** for a production-like environment.

### 1. Set environment variables

Create a `.env` file in the project root:

```env
POSTGRES_DB=makebuddy
POSTGRES_USER=makebuddy_user
POSTGRES_PASSWORD=yourpassword
SECRET_KEY=your-secret-key
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
````

### 2. Build and run

```bash
docker compose up --build
```

### 3. Open the app

Visit:

```
http://localhost:8000
```

* PostgreSQL starts in a container
* Django runs migrations automatically
* App is served via Gunicorn

---

## Local Development (Without Docker)

### Setup virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Run development server

```bash
python manage.py migrate
python manage.py runserver
```

---

## Project Setup

### Create media directory

```bash
mkdir -p media/profile_pics
```

---

## Common Commands

### Check project

```bash
python manage.py check
```

### Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run tests

```bash
python manage.py test accounts --settings=config.settings_test
```

---

## Code Formatting

Using Black:

```bash
python -m black .
```

---

## Django Shell Tips (Because I always forget)

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from maker_projects.models import MakerProject

MakerProject.objects.all()
MakerProject.objects.count()
MakerProject.objects.first()

project = MakerProject.objects.get(id=1)
MakerProject.objects.get(title="<project_title>")

user = User.objects.get(username="chris")
user.maker_projects.all()

MakerProject.objects.values("title")

ProjectLink.objects.filter(link_type="github")

# Show model fields
[field.name for field in MakerProject._meta.fields]
```
---
## Notes

* Docker is the recommended way to run this project
* The app uses Gunicorn in containers 
* To reset database:

```bash
docker-compose down
docker-compose up --build
```


### Maker_Parts Tasks

1. Add parts to maker_parts/data/seed_parts.json


Test getting parts to list:
```bash
python manage.py seed_parts --file maker_parts/data/seed_parts.json --dry-run
```
Run:
```bash
python manage.py seed_parts --file maker_parts/data/seed_parts.json
```


Test enqueue_weekly_sync:

```bash
docker exec -it maker_buddy-web-1 python manage.py enqueue_weekly_sync
```
Check for Ready:

```bash
docker exec -it maker_buddy-web-1 python manage.py shell -c "
from django_tasks_db.models import DBTaskResult
print(DBTaskResult.objects.all().values('id', 'status', 'task_path').last())
"
```
Run
```bash
docker exec -it maker_buddy-web-1 python manage.py db_worker
```

```bash
docker logs maker_buddy-web-1 --tail 50
```



Running docker:
```bash
docker exec -it maker_buddy-web-1 python manage.py seed_parts --file maker_parts/data/seed_parts.json
```


---

## Future Improvements

* Add deployment guide (After testing a few services TBD)

