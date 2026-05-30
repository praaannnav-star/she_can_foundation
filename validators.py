import re


VALID_STATUSES = ("Active", "Planning", "Paused", "Completed")
VALID_CATEGORIES = ("Health", "Education", "Advocacy", "Skill Training", "Relief")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(value, errors, field="email"):
    if not value:
        errors[field] = "Email is required."
    elif not EMAIL_RE.match(value):
        errors[field] = "Enter a valid email address."


def validate_signup_form(source):
    form = {
        "name": source.get("name", "").strip(),
        "email": source.get("email", "").strip().lower(),
        "password": source.get("password", ""),
    }
    errors = {}
    if len(form["name"]) < 2:
        errors["name"] = "Name must be at least 2 characters."
    validate_email(form["email"], errors)
    if len(form["password"]) < 6:
        errors["password"] = "Password must be at least 6 characters."
    return form, errors


def validate_login_form(source):
    form = {
        "email": source.get("email", "").strip().lower(),
        "password": source.get("password", ""),
    }
    errors = {}
    validate_email(form["email"], errors)
    if not form["password"]:
        errors["password"] = "Password is required."
    return form, errors


def validate_donation_form(source):
    form = {
        "name": source.get("name", "").strip(),
        "email": source.get("email", "").strip().lower(),
        "amount": source.get("amount", "").strip(),
        "message": source.get("message", "").strip(),
    }
    errors = {}
    if len(form["name"]) < 2:
        errors["name"] = "Name must be at least 2 characters."
    validate_email(form["email"], errors)
    amount_digits = re.sub(r"[^0-9]", "", form["amount"])
    if not amount_digits or int(amount_digits) < 100:
        errors["amount"] = "Enter an amount of at least INR 100."
    if len(form["message"]) > 300:
        errors["message"] = "Message must be 300 characters or fewer."
    return form, errors


def validate_program_form(source):
    form = {
        "title": source.get("title", "").strip(),
        "category": source.get("category", "").strip(),
        "location": source.get("location", "").strip(),
        "status": source.get("status", "Active").strip(),
        "goal": source.get("goal", "").strip(),
        "description": source.get("description", "").strip(),
    }
    errors = {}
    if len(form["title"]) < 4:
        errors["title"] = "Title must be at least 4 characters."
    if form["category"] not in VALID_CATEGORIES:
        errors["category"] = "Choose a valid category."
    if len(form["location"]) < 2:
        errors["location"] = "Location is required."
    if form["status"] not in VALID_STATUSES:
        errors["status"] = "Choose a valid status."
    if len(form["goal"]) < 8:
        errors["goal"] = "Goal must be at least 8 characters."
    if len(form["description"]) < 20:
        errors["description"] = "Description must be at least 20 characters."
    return form, errors
