# She Can Foundation Flask CRUD

A small Flask application inspired by the public She Can Foundation website.

## What it includes

- Public pages for Home, About, Certificate, and Donate.
- Signup, login, and logout with hashed passwords.
- Admin panel for managing foundation programs.
- Create, read, update, and delete operations for programs.
- SQLite storage locally, or Render Postgres with `DATABASE_URL`.

## Project structure

- `app.py` creates the Flask app and registers routes.
- `config.py` stores environment-based configuration.
- `extensions.py` contains database connection helpers.
- `models.py` contains schema setup and database queries.
- `routes.py` contains public, auth, dashboard, and admin routes.
- `validators.py` contains form validation rules.

## Run it

```powershell
python -m pip install -r requirements.txt
python app.py
```

The first account created becomes the admin. You can also create or promote an admin on startup with:

Or create/promote an admin from the terminal:

```powershell
$env:DATABASE_URL=""
flask --app app create-admin
```

