
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY id DESC"
    ).fetchall()

    income = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE category='Income'"
    ).fetchone()[0] or 0

    expenses = conn.execute(
        "SELECT SUM(amount) FROM transactions WHERE category='Expense'"
    ).fetchone()[0] or 0

    conn.close()

    balance = income - expenses

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=balance
    )

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    amount = float(request.form["amount"])
    category = request.form["category"]

    if amount <= 0 or category not in ["Income", "Expense"]:
        return "Invalid transaction", 400

    conn = sqlite3.connect("database.db")
    conn.execute(
        "INSERT INTO transactions (title, amount, category) VALUES (?, ?, ?)",
        (title, amount, category)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("database.db")
    conn.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
