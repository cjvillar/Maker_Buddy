# MAKE BUDDY

A Maker project accountability and helper resource.


## Get Started

```bash 
python -m venv .vpip env
.venv\Scripts\activate
pip install -r requirments.txt

```

### Check build
```bash
python manage.py check
python manage.py runserver
```
### Create Media dir
```bash
mkdir media/profile_pics
```

### Make Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run Test
Run Accounts test:

```bash
python manage.py test accounts/tests

```

### Formatting
I use python Black formatter:
```bash
 python -m black .
```