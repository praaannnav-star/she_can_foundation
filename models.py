import os
import sqlite3

from flask import current_app
from werkzeug.security import generate_password_hash

from extensions import execute, is_postgres, normalize_database_url, placeholders

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None


SEED_PROGRAMS = [
    (
        "Menstrual Hygiene Dignity Kits",
        "Health",
        "India",
        "Distribute sanitary pads, dignity kits, and awareness material to girls who are at risk of missing school.",
        "Support 1,000 girls with monthly hygiene kits.",
        "Active",
    ),
    (
        "Women Skill Training Circles",
        "Education",
        "Community centers",
        "Local training sessions that help women build practical career, digital, and life skills.",
        "Run 24 workshops with local volunteers.",
        "Planning",
    ),
    (
        "Advocacy and Awareness Drives",
        "Advocacy",
        "Schools and colleges",
        "Campaigns focused on breaking barriers, raising awareness, and encouraging community support.",
        "Reach 10,000 students and families.",
        "Active",
    ),
]


def open_schema_connection():
    if is_postgres():
        if psycopg is None:
            raise RuntimeError("Install psycopg[binary] to use PostgreSQL.")
        return psycopg.connect(
            normalize_database_url(current_app.config["DATABASE_URL"]),
            row_factory=dict_row,
        )

    db = sqlite3.connect(current_app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = open_schema_connection()
    id_type = "SERIAL PRIMARY KEY" if is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    timestamp_type = "TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP" if is_postgres() else "TEXT DEFAULT CURRENT_TIMESTAMP"

    statements = [
        f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'volunteer',
            created_at {timestamp_type}
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS programs (
            id {id_type},
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            goal TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at {timestamp_type}
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS donor_messages (
            id {id_type},
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            amount TEXT NOT NULL,
            message TEXT,
            created_at {timestamp_type}
        )
        """,
    ]
    for statement in statements:
        db.execute(statement)

    ensure_user_role_column(db)
    seed_programs(db)
    db.commit()
    create_admin_from_env(db)
    db.commit()
    db.close()


def ensure_user_role_column(db):
    if is_postgres():
        has_role = db.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            )
            """,
        ).fetchone()["exists"]
        if not has_role:
            db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'volunteer'")
        return

    columns = [row["name"] for row in db.execute("PRAGMA table_info(users)").fetchall()]
    if "role" not in columns:
        db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'volunteer'")


def seed_programs(db):
    if fetch_count(db, "programs") > 0:
        return
    insert_sql = f"""
    INSERT INTO programs (title, category, location, description, goal, status)
    VALUES ({placeholders(6)})
    """
    for row in SEED_PROGRAMS:
        execute(db, insert_sql, row)


def create_admin_from_env(db):
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")
    name = os.environ.get("ADMIN_NAME", "She Can Admin").strip() or "She Can Admin"
    if not email or not password:
        return

    existing = execute(db, "SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing is None:
        execute(
            db,
            f"""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ({placeholders(4)})
            """,
            (name, email, generate_password_hash(password), "admin"),
        )
    else:
        execute(db, "UPDATE users SET role = 'admin' WHERE email = ?", (email,))


def create_or_promote_admin(db, name, email, password):
    existing = execute(db, "SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing is None:
        execute(
            db,
            f"""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ({placeholders(4)})
            """,
            (name, email, generate_password_hash(password), "admin"),
        )
        return "created"

    execute(db, "UPDATE users SET name = ?, password_hash = ?, role = 'admin' WHERE email = ?", (
        name,
        generate_password_hash(password),
        email,
    ))
    return "promoted"


def fetch_count(db, table):
    return db.execute(f"SELECT COUNT(*) AS total FROM {table}").fetchone()["total"]


def is_unique_error(error):
    if isinstance(error, sqlite3.IntegrityError):
        return True
    return error.__class__.__name__ == "UniqueViolation"


def get_user_by_id(db, user_id):
    return execute(
        db,
        "SELECT id, name, email, role FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


def get_user_by_email(db, email):
    return execute(db, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def create_user(db, form):
    role = "admin" if fetch_count(db, "users") == 0 else "volunteer"
    password_hash = generate_password_hash(form["password"])
    if is_postgres():
        cursor = execute(
            db,
            f"""
            INSERT INTO users (name, email, password_hash, role)
            VALUES ({placeholders(4)})
            RETURNING id
            """,
            (form["name"], form["email"], password_hash, role),
        )
        return cursor.fetchone()["id"]

    cursor = execute(
        db,
        f"""
        INSERT INTO users (name, email, password_hash, role)
        VALUES ({placeholders(4)})
        """,
        (form["name"], form["email"], password_hash, role),
    )
    return cursor.lastrowid


def list_recent_programs(db, limit=3):
    return execute(
        db,
        "SELECT * FROM programs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()


def list_programs(db):
    return execute(db, "SELECT * FROM programs ORDER BY created_at DESC").fetchall()


def list_recent_donors(db, limit=6):
    return execute(
        db,
        "SELECT * FROM donor_messages ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()


def list_users(db):
    return execute(
        db,
        "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC",
    ).fetchall()


def get_program(db, program_id):
    return execute(db, "SELECT * FROM programs WHERE id = ?", (program_id,)).fetchone()


def create_program_record(db, form):
    execute(
        db,
        f"""
        INSERT INTO programs (title, category, location, description, goal, status)
        VALUES ({placeholders(6)})
        """,
        (
            form["title"],
            form["category"],
            form["location"],
            form["description"],
            form["goal"],
            form["status"],
        ),
    )


def update_program_record(db, program_id, form):
    execute(
        db,
        """
        UPDATE programs
        SET title = ?, category = ?, location = ?, description = ?, goal = ?, status = ?
        WHERE id = ?
        """,
        (
            form["title"],
            form["category"],
            form["location"],
            form["description"],
            form["goal"],
            form["status"],
            program_id,
        ),
    )


def delete_program_record(db, program_id):
    execute(db, "DELETE FROM programs WHERE id = ?", (program_id,))


def create_donor_message(db, form):
    execute(
        db,
        """
        INSERT INTO donor_messages (name, email, amount, message)
        VALUES (?, ?, ?, ?)
        """,
        (form["name"], form["email"], form["amount"], form["message"]),
    )
