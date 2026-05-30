import click
from flask import current_app

from models import create_or_promote_admin, open_schema_connection
from validators import validate_signup_form


def register_cli(app):
    @app.cli.command("create-admin")
    @click.option("--name", prompt=True, default="She Can Admin", show_default=True)
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(name, email, password):
        """Create or promote an admin user."""
        form, errors = validate_signup_form(
            {"name": name, "email": email, "password": password}
        )
        if errors:
            for field, message in errors.items():
                click.echo(f"{field}: {message}", err=True)
            raise click.ClickException("Admin account was not created.")

        db = open_schema_connection()
        result = create_or_promote_admin(
            db,
            form["name"],
            form["email"],
            form["password"],
        )
        db.commit()
        db.close()
        click.echo(f"Admin {result}: {form['email']}")
