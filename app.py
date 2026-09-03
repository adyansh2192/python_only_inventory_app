import os
from contextlib import closing
from flask import Flask, flash, redirect, render_template_string, request, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "replace-this-development-key")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "inventory_app"),
    "password": os.environ.get("DB_PASSWORD", "ChangeMe_Strong_2026"),
    "database": os.environ.get("DB_NAME", "inventory_db"),
}

PAGE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Python Inventory App</title>
  <style>
    :root { font-family: Arial, sans-serif; color: #172033; background: #f2f5fa; }
    body { margin: 0; }
    main { max-width: 820px; margin: 45px auto; padding: 28px; background: white;
           border-radius: 14px; box-shadow: 0 8px 28px rgba(0,0,0,.08); }
    h1 { margin-bottom: 4px; }
    .sub { color: #5b6575; margin-top: 0; }
    form { display: flex; gap: 10px; flex-wrap: wrap; margin: 24px 0; }
    input, button { padding: 11px; border-radius: 7px; border: 1px solid #cbd3df; }
    input[name=name] { flex: 1; min-width: 220px; }
    button { border: 0; background: #1769e0; color: white; cursor: pointer; }
    .delete { background: #b42318; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 11px; border-bottom: 1px solid #e5e9f0; }
    .message { padding: 10px; background: #ecfdf3; color: #027a48; border-radius: 7px; }
    .error { padding: 10px; background: #fef3f2; color: #b42318; border-radius: 7px; }
    .inline { margin: 0; display: inline; }
  </style>
</head>
<body>
<main>
  <h1>Inventory Application</h1>
  <p class="sub">Python Flask + Apache2 + MySQL on the same AWS EC2 instance</p>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
      <p class="{{ 'error' if category == 'error' else 'message' }}">{{ message }}</p>
    {% endfor %}
  {% endwith %}

  <form method="post" action="{{ url_for('add_item') }}">
    <input name="name" maxlength="120" placeholder="Item name" required>
    <input name="quantity" type="number" min="0" value="1" required>
    <button type="submit">Add item</button>
  </form>

  <table>
    <thead><tr><th>ID</th><th>Name</th><th>Quantity</th><th>Created</th><th>Action</th></tr></thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td>{{ item.id }}</td>
        <td>{{ item.name }}</td>
        <td>{{ item.quantity }}</td>
        <td>{{ item.created_at }}</td>
        <td>
          <form class="inline" method="post" action="{{ url_for('delete_item', item_id=item.id) }}">
            <button class="delete" type="submit">Delete</button>
          </form>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="5">No items found.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</main>
</body>
</html>'''


def db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.get("/")
def index():
    try:
        with closing(db_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute(
                    "SELECT id, name, quantity, created_at FROM items ORDER BY id DESC"
                )
                items = cursor.fetchall()
        return render_template_string(PAGE, items=items)
    except Error as exc:
        return render_template_string(
            PAGE, items=[],
        ) + f"<!-- Database error: {type(exc).__name__} -->", 500


@app.post("/items")
def add_item():
    name = request.form.get("name", "").strip()
    try:
        quantity = int(request.form.get("quantity", "0"))
    except ValueError:
        flash("Quantity must be a whole number.", "error")
        return redirect(url_for("index"))

    if not name or quantity < 0:
        flash("Enter a name and a quantity of zero or greater.", "error")
        return redirect(url_for("index"))

    try:
        with closing(db_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO items (name, quantity) VALUES (%s, %s)",
                    (name, quantity),
                )
                connection.commit()
        flash(f"Added {name} successfully.", "success")
    except Error:
        flash("The item could not be saved. Check MySQL and the Apache error log.", "error")
    return redirect(url_for("index"))


@app.post("/items/<int:item_id>/delete")
def delete_item(item_id):
    try:
        with closing(db_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
                connection.commit()
                deleted = cursor.rowcount
        flash("Item deleted." if deleted else "Item was not found.", "success")
    except Error:
        flash("The item could not be deleted.", "error")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    try:
        with closing(db_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return {"application": "UP", "database": "UP"}, 200
    except Error:
        return {"application": "UP", "database": "DOWN"}, 503


if __name__ == "__main__":
    # Development only. Apache/mod_wsgi serves the production application.
    app.run(host="127.0.0.1", port=5000, debug=False)
