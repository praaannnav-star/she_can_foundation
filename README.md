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

Open `http://127.0.0.1:5000` in your browser.

The first account created becomes the admin. You can also create or promote an admin on startup with:

```powershell
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="change-this-password"
$env:ADMIN_NAME="She Can Admin"
python app.py
```

Or create/promote an admin from the terminal:

```powershell
$env:DATABASE_URL=""
flask --app app create-admin
```

After that, open `http://127.0.0.1:5000/admin` and log in with the admin account.

## Render Postgres

1. Create a Render Postgres database.
2. In your Render web service, add `DATABASE_URL` using the database Internal URL when the service is in the same region.
3. Add a strong `SECRET_KEY`.
4. Add `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and optionally `ADMIN_NAME` for the first admin.
5. Use this start command:

```bash
gunicorn app:app
```
