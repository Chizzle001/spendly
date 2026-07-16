import sqlite3
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import (
    create_user,
    get_db,
    get_expenses_by_user,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password or not confirm_password:
        flash("All fields are required.", "error")
        return render_template("register.html")

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("register.html")

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        flash("Email already registered.", "error")
        return render_template("register.html")

    flash("Account created! Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    user = get_user_by_email(email)

    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    session["user_id"] = user["id"]
    flash("Welcome back!", "success")
    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db_user = get_user_by_id(session["user_id"])
    if db_user is None:
        session.clear()
        return redirect(url_for("login"))

    name_parts = db_user["name"].split()
    initials = "".join(part[0].upper() for part in name_parts[:2]) or "?"
    member_since = datetime.strptime(
        db_user["created_at"], "%Y-%m-%d %H:%M:%S"
    ).strftime("%B %Y")

    user = {
        "name": db_user["name"],
        "initials": initials,
        "email": db_user["email"],
        "member_since": member_since,
    }

    expenses = get_expenses_by_user(session["user_id"])

    total_spent = sum(row["amount"] for row in expenses)

    category_totals = {}
    for row in expenses:
        category_totals[row["category"]] = category_totals.get(row["category"], 0) + row["amount"]

    top_category = max(category_totals, key=category_totals.get) if category_totals else "—"

    stats = {
        "total_spent": f"₹{total_spent:,.2f}",
        "transaction_count": len(expenses),
        "top_category": top_category,
    }

    transactions = [
        {
            "date": datetime.strptime(row["date"], "%Y-%m-%d").strftime("%d %b %Y"),
            "description": row["description"] or row["category"],
            "category": row["category"],
            "amount": f"₹{row['amount']:,.2f}",
        }
        for row in expenses[:10]
    ]

    max_category_total = max(category_totals.values()) if category_totals else 0
    categories = [
        {
            "name": category,
            "total": f"₹{amount:,.2f}",
            "percent": round((amount / max_category_total) * 100) if max_category_total else 0,
        }
        for category, amount in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
