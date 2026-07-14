## Introduction 

This minimal application is a Django boilerplate for web applications.
It contains everything you need to get started so that you can start building your functionality straight away.

---

<br>

## Getting Started


This project uses Python 3.13 and Django 5.2.

To setup the application, you will need to create a virtual environment and install the requirements:

``` 
python -m venv venv
```

Activate the virtual enviroment:

```
.\venv\Scripts\activate
```

Install the dependencies:

```
pip install -r .\requirements.txt
```

Copy the example environment variables:

```
cp example.env .env
```

Create your local database:

```
python app\manage.py migrate
```

Load the example fixtures:

```
python app\manage.py loaddata app\app_src\fixtures\01_users.json
python app\manage.py loaddata app\app_src\fixtures\02_notes.json
```

Create a local superuser account and answer the prompts

```
python app\manage.py createsuperuser
```

Run the application:

```
python app\manage.py runserver 8000
```


You should now be able to visit your running application at http://localhost:8000

<br>

## Migration history reset (July 2026)

The migration history was squashed into two migrations (`0001_initial` matching
the schema as it stood, and `0002_pack_group_system` adding pack groups). Fresh
databases just run `migrate` as normal.

If you have an **existing local database** created before the reset, align it
once with:

```
python -c "import sqlite3; c = sqlite3.connect('app/db.sqlite3'); c.execute(\"delete from django_migrations where app='app_src'\"); c.commit()"
python app\manage.py migrate app_src 0001 --fake
python app\manage.py migrate
```

<br>

## Where things live

- `app_src/models/` — one module per domain (applications & packs, interviews, question bank, notes, users).
- `app_src/views/` and `app_src/forms/` — same domain split; `app_src/services/` holds the query/save logic behind interviews, the results page, the dashboard and its PDF export.
- `app_src/static/js/main.js` — **all** of the site's JavaScript, one section per page, loaded from `base.html`. Templates pass data to it with `{{ value|json_script:"..." }}` blocks.

## How applications flow

1. Assessors create **categories**, **questions**, **indicators** and **packs** (a pack's interview questions come from its category).
2. Early-careers staff combine packs into a **pack group** (Create Pack Group), which applicants apply to in one submission — one `Application` row per pack, sharing an `application_id`.
3. Approving a submission schedules the interview and picks the **interview packs** (defaults to the group's packs).
4. The interview page walks every chosen pack's questions (notes, feedback, 1–6 score, autosaved) plus the indicator assessment.
5. **Interview Results** and **Candidate Statistics** show the scores, notes and feedback per candidate, organised by group and pack.

