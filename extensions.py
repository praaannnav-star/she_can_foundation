import sqlite3
from urllib.parse import urlparse, urlunparse

from flask import current_app, g

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None


def is_postgres():
    return current_app.config["DATABASE_URL"].startswith(("postgres://", "postgresql://"))


def normalize_database_url(database_url):
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://") :]
    parsed = urlparse(database_url)
    query = parsed.query
    if "sslmode=" not in query:
        query = f"{query}&sslmode=require" if query else "sslmode=require"
    return urlunparse(parsed._replace(query=query))


def get_db():
    if "db" not in g:
        if is_postgres():
            if psycopg is None:
                raise RuntimeError("Install psycopg[binary] to use PostgreSQL.")
            g.db = psycopg.connect(
                normalize_database_url(current_app.config["DATABASE_URL"]),
                row_factory=dict_row,
            )
        else:
            g.db = sqlite3.connect(current_app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def placeholder():
    return "%s" if is_postgres() else "?"


def placeholders(count):
    return ", ".join([placeholder()] * count)


def execute(db, sql, params=()):
    return db.execute(sql.replace("?", placeholder()), params)
