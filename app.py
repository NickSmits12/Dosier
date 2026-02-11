from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "dietist.db"
MAX_MEALS = 10

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key-in-production"
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024


# ---------- Database ----------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight REAL,
            meal_count INTEGER NOT NULL,
            meals_json TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


@app.teardown_appcontext
def close_db(_exception: BaseException | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------- Security headers ----------
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return response


# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/formulier", methods=["GET", "POST"])
def form_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_raw = request.form.get("age", "").strip()
        weight_raw = request.form.get("weight", "").strip()
        meal_count_raw = request.form.get("meal_count", "").strip()

        if not name:
            flash("Naam is verplicht.", "error")
            return render_template("form.html", max_meals=MAX_MEALS)

        try:
            age = int(age_raw)
            if age <= 0 or age > 120:
                raise ValueError
        except ValueError:
            flash("Leeftijd moet een getal tussen 1 en 120 zijn.", "error")
            return render_template("form.html", max_meals=MAX_MEALS)

        weight = None
        if weight_raw:
            try:
                weight = float(weight_raw)
                if weight <= 0 or weight > 500:
                    raise ValueError
            except ValueError:
                flash("Gewicht moet een realistisch getal zijn (optioneel veld).", "error")
                return render_template("form.html", max_meals=MAX_MEALS)

        try:
            meal_count = int(meal_count_raw)
            if meal_count < 1 or meal_count > MAX_MEALS:
                raise ValueError
        except ValueError:
            flash("Kies een geldig aantal maaltijden (1 t/m 10).", "error")
            return render_template("form.html", max_meals=MAX_MEALS)

        meals = []
        for index in range(1, meal_count + 1):
            item = request.form.get(f"meal_{index}", "").strip()
            if not item:
                flash(f"Maaltijd {index} is verplicht.", "error")
                return render_template("form.html", max_meals=MAX_MEALS)
            meals.append(item)

        db = get_db()
        db.execute(
            """
            INSERT INTO submissions (created_at, name, age, weight, meal_count, meals_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                name,
                age,
                weight,
                meal_count,
                json.dumps(meals, ensure_ascii=False),
            ),
        )
        db.commit()

        flash("Bedankt! Je formulier is lokaal opgeslagen.", "success")
        return redirect(url_for("my_data"))

    return render_template("form.html", max_meals=MAX_MEALS)


@app.route("/mijn-gegevens")
def my_data():
    db = get_db()
    rows = db.execute(
        "SELECT id, created_at, name, age, weight, meal_count, meals_json FROM submissions ORDER BY id DESC"
    ).fetchall()

    submissions = []
    for row in rows:
        submissions.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "name": row["name"],
                "age": row["age"],
                "weight": row["weight"],
                "meal_count": row["meal_count"],
                "meals": json.loads(row["meals_json"]),
            }
        )

    return render_template("my_data.html", submissions=submissions)


@app.route("/admin/database")
def admin_database():
    token = request.args.get("token", "")
    expected = "admin-demo-token"
    if token != expected:
        abort(403)

    db = get_db()
    rows = db.execute(
        "SELECT id, created_at, name, age, weight, meal_count, meals_json FROM submissions ORDER BY id DESC"
    ).fetchall()

    parsed_rows = []
    for row in rows:
        parsed_rows.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "name": row["name"],
                "age": row["age"],
                "weight": row["weight"],
                "meal_count": row["meal_count"],
                "meals": json.loads(row["meals_json"]),
            }
        )

    return render_template("admin.html", submissions=parsed_rows)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
