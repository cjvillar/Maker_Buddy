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


### django shell
```bash
python manage.py shell # start shell

#example importing model and queries
from django.contrib.auth.models import User
from maker_projects.models import MakerProject

MakerProject.objects.all()
MakerProject.objects.count()
MakerProject.objects.first()  #last(), 
project = MakerProject.objects.get(id=1)
MakerProject.objects.get(title="<project_title>")
user = User.objects.get(username="chris")
user.maker_projects.all()
MakerProject.objects.values("title", "code_snippet")

#show model fields:
[field.name for field in MakerProject._meta.fields]
```
