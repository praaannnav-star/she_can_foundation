from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from extensions import get_db
from models import (
    create_donor_message,
    create_program_record,
    create_user,
    delete_program_record,
    fetch_count,
    get_program,
    get_user_by_email,
    get_user_by_id,
    is_unique_error,
    list_programs,
    list_recent_donors,
    list_recent_programs,
    list_users,
    update_program_record,
)
from validators import (
    VALID_CATEGORIES,
    VALID_STATUSES,
    validate_donation_form,
    validate_login_form,
    validate_program_form,
    validate_signup_form,
)


main_bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to access the dashboard.", "warning")
            return redirect(url_for("main.login"))
        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped_view(**kwargs):
        if g.user["role"] != "admin":
            flash("Only admins can access that page.", "danger")
            return redirect(url_for("main.home"))
        return view(**kwargs)

    return wrapped_view


@main_bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_user_by_id(get_db(), user_id)


@main_bp.route("/")
def home():
    programs = list_recent_programs(get_db())
    return render_template("home.html", programs=programs)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/certificate")
def certificate():
    return render_template("certificate.html")


@main_bp.route("/donate", methods=("GET", "POST"))
def donate():
    errors = {}
    form = {}
    if request.method == "POST":
        form, errors = validate_donation_form(request.form)
        if errors:
            flash("Please correct the highlighted fields.", "danger")
        else:
            db = get_db()
            create_donor_message(db, form)
            db.commit()
            flash("Thank you. Your support note has been saved.", "success")
            return redirect(url_for("main.donate"))

    return render_template("donate.html", errors=errors, form=form)


@main_bp.route("/signup", methods=("GET", "POST"))
def signup():
    errors = {}
    form = {}
    if request.method == "POST":
        form, errors = validate_signup_form(request.form)
        if errors:
            flash("Please correct the highlighted fields.", "danger")
        else:
            try:
                db = get_db()
                user_id = create_user(db, form)
                db.commit()
                session.clear()
                session["user_id"] = user_id
                flash("Account created. Welcome to the dashboard.", "success")
                return redirect(url_for("main.dashboard"))
            except Exception as error:
                if is_unique_error(error):
                    errors["email"] = "An account already exists for that email."
                    flash("Please correct the highlighted fields.", "danger")
                else:
                    raise

    return render_template("auth/signup.html", errors=errors, form=form)


@main_bp.route("/login", methods=("GET", "POST"))
def login():
    errors = {}
    form = {}
    if request.method == "POST":
        form, errors = validate_login_form(request.form)
        user = None
        if not errors:
            user = get_user_by_email(get_db(), form["email"])

        if errors:
            flash("Please correct the highlighted fields.", "danger")
        elif user is not None and check_password_hash(user["password_hash"], form["password"]):
            session.clear()
            session["user_id"] = user["id"]
            flash("You are logged in.", "success")
            return redirect(url_for("main.dashboard"))
        else:
            errors["email"] = "Invalid email or password."
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", errors=errors, form=form)


@main_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if g.user["role"] == "admin":
        return redirect(url_for("main.admin_panel"))
    programs = list_programs(get_db())
    return render_template("dashboard.html", programs=programs, donors=[], stats=None)


@main_bp.route("/admin")
@admin_required
def admin_panel():
    db = get_db()
    stats = {
        "programs": fetch_count(db, "programs"),
        "donors": fetch_count(db, "donor_messages"),
        "users": fetch_count(db, "users"),
    }
    return render_template(
        "dashboard.html",
        programs=list_programs(db),
        donors=list_recent_donors(db),
        users=list_users(db),
        stats=stats,
    )


@main_bp.route("/programs/new", methods=("GET", "POST"))
@admin_required
def create_program():
    errors = {}
    form = {}
    if request.method == "POST":
        form, errors = save_program()
        if not errors:
            flash("Program created successfully.", "success")
            return redirect(url_for("main.admin_panel"))
        flash("Please correct the highlighted fields.", "danger")
    return render_program_form(None, "Create", errors, form)


@main_bp.route("/programs/<int:program_id>/edit", methods=("GET", "POST"))
@admin_required
def edit_program(program_id):
    program = get_program_or_404(program_id)
    errors = {}
    form = dict(program)
    if request.method == "POST":
        form, errors = save_program(program_id)
        if not errors:
            flash("Program updated successfully.", "success")
            return redirect(url_for("main.admin_panel"))
        flash("Please correct the highlighted fields.", "danger")
    return render_program_form(program, "Update", errors, form)


@main_bp.route("/programs/<int:program_id>/delete", methods=("POST",))
@admin_required
def delete_program(program_id):
    get_program_or_404(program_id)
    db = get_db()
    delete_program_record(db, program_id)
    db.commit()
    flash("Program deleted.", "info")
    return redirect(url_for("main.admin_panel"))


def get_program_or_404(program_id):
    program = get_program(get_db(), program_id)
    if program is None:
        abort(404)
    return program


def save_program(program_id=None):
    form, errors = validate_program_form(request.form)
    if errors:
        return form, errors

    db = get_db()
    if program_id is None:
        create_program_record(db, form)
    else:
        update_program_record(db, program_id, form)
    db.commit()
    return form, {}


def render_program_form(program, action, errors, form):
    return render_template(
        "program_form.html",
        program=program,
        action=action,
        errors=errors,
        form=form,
        categories=VALID_CATEGORIES,
        statuses=VALID_STATUSES,
    )
