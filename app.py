from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import calendar

app = Flask(__name__)
app.secret_key = "your-secret-key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DATABASE = "expenses.db"
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()

    user = conn.execute("""
        SELECT * FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if user is None:
        return None

    return User(user["id"], user["username"], user["password_hash"])

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            memo TEXT,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            UNIQUE(user_id, month),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)



    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/expenses")

@app.route("/expenses")
@login_required
def show_expenses():
    search = request.args.get("search")
    category = request.args.get("category")
    sort = request.args.get("sort")

    conn = get_db_connection()

    query = """
        SELECT * FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
    """

    params = [current_user.id]

    if search:
        query += """
            AND memo LIKE ?
        """
        params.append("%" + search + "%")

    if category:
        query += """
            AND category = ?
        """
        params.append(category)

    if sort == "date_old":
        query += """
            ORDER BY date ASC
        """
    elif sort == "amount_high":
        query += """
            ORDER BY amount DESC
        """
    elif sort == "amount_low":
        query += """
            ORDER BY amount ASC
        """
    else:
        query += """
            ORDER BY date DESC
        """

    expenses = conn.execute(query, params).fetchall()
    average_expense = conn.execute("""
        SELECT AVG(amount)
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
    """, (current_user.id,)).fetchone()[0]

    if average_expense is None:
        average_expense = 0
        
    conn.close()

    return render_template(
        "expenses.html",
        expenses=expenses,
        search=search,
        category=category,
        sort=sort,
        average_expense=average_expense
    )
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()

    total_spending = conn.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
    """, (current_user.id,)).fetchone()[0]

    number_of_expenses = conn.execute("""
        SELECT COUNT(*)
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
    """, (current_user.id,)).fetchone()[0]

    average_expense = conn.execute("""
        SELECT AVG(amount)
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
    """, (current_user.id,)).fetchone()[0]

    highest_expense = conn.execute("""
        SELECT *
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
        ORDER BY amount DESC
        LIMIT 1
    """, (current_user.id,)).fetchone()

    category_totals = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
        GROUP BY category
        ORDER BY total DESC
    """, (current_user.id,)).fetchall()

    categories = ["Food", "Transportation", "Shopping", "School", "Entertainment", "Other"]

    category_dict = {category: 0 for category in categories}
    for row in category_totals:
        category_dict[row["category"]] = row["total"]

    category_labels = list(category_dict.keys())
    category_values = list(category_dict.values())

    monthly_rows = conn.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month ASC
    """, (current_user.id,)).fetchall()

    recent_month_rows = conn.execute("""
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 3
    """, (current_user.id,)).fetchall()

    month_labels = [row["month"] for row in monthly_rows]
    month_totals = [row["total"] for row in monthly_rows]

    this_month_spending = conn.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """, (current_user.id,)).fetchone()[0]

    last_month_spending = conn.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE is_deleted = 0
        AND user_id = ?
        AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now', '-1 month')
    """, (current_user.id,)).fetchone()[0]

    current_month = conn.execute("""
        SELECT strftime('%Y-%m', 'now')
    """).fetchone()[0]

    budget_row = conn.execute("""
        SELECT amount
        FROM budgets
        WHERE month = ?
        AND user_id = ?
    """, (current_month, current_user.id)).fetchone()

    conn.close()

    if total_spending is None:
        total_spending = 0

    if average_expense is None:
        average_expense = 0

    if this_month_spending is None:
        this_month_spending = 0

    if last_month_spending is None:
        last_month_spending = 0

    if budget_row:
        monthly_budget = budget_row["amount"]
    else:
        monthly_budget = 0

    remaining_budget = monthly_budget - this_month_spending

    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_left = days_in_month - today.day + 1

    if days_left > 0 and remaining_budget > 0:
        recommended_daily_spending = remaining_budget / days_left
    else:
        recommended_daily_spending = 0

    if monthly_budget > 0:
        budget_used_percent = (this_month_spending / monthly_budget) * 100
    else:
        budget_used_percent = 0

    spending_difference = this_month_spending - last_month_spending

    if last_month_spending > 0:
        spending_change_percent = (spending_difference / last_month_spending) * 100
    else:
        spending_change_percent = 0

    if recent_month_rows:
        predicted_next_month = sum(row["total"] for row in recent_month_rows) / len(recent_month_rows)
    else:
        predicted_next_month = 0

    if monthly_budget > 0:
        predicted_difference_from_budget = monthly_budget - predicted_next_month
    else:
        predicted_difference_from_budget = 0

    return render_template(
        "dashboard.html",
        total_spending=total_spending,
        number_of_expenses=number_of_expenses,
        average_expense=average_expense,
        highest_expense=highest_expense,
        category_totals=category_totals,
        this_month_spending=this_month_spending,
        last_month_spending=last_month_spending,
        spending_difference=spending_difference,
        spending_change_percent=spending_change_percent,
        category_labels=category_labels,
        category_values=category_values,
        month_labels=month_labels,
        month_totals=month_totals,
        monthly_budget=monthly_budget,
        remaining_budget=remaining_budget,
        budget_used_percent=budget_used_percent,
        predicted_next_month=predicted_next_month,
        predicted_difference_from_budget=predicted_difference_from_budget,
        days_left=days_left,
        recommended_daily_spending=recommended_daily_spending
    )


@app.route("/trash")
@login_required
def show_trash():
    conn = get_db_connection()

    expenses = conn.execute("""
        SELECT * FROM expenses
        WHERE is_deleted = 1
        ORDER BY date DESC
    """).fetchall()

    conn.close()

    return render_template("trash.html", expenses=expenses)


@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        date = request.form.get("date")
        memo = request.form.get("memo")

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO expenses (user_id, amount, category, date, memo)
            VALUES (?, ?, ?, ?, ?)
        """, (current_user.id, amount, category, date, memo))

        conn.commit()
        conn.close()

        return redirect("/expenses")

    return render_template("add_expense.html")

@app.route("/expenses/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    conn = get_db_connection()

    expense = conn.execute("""
        SELECT * FROM expenses
        WHERE id = ?
        AND user_id = ?
    """, (expense_id, current_user.id)).fetchone()

    if expense is None:
        conn.close()
        return "Expense not found", 404

    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        date = request.form.get("date")
        memo = request.form.get("memo")

        conn.execute("""
            UPDATE expenses
            SET amount = ?, category = ?, date = ?, memo = ?
            WHERE id = ?
            AND user_id = ?
        """, (amount, category, date, memo, expense_id, current_user.id))

        conn.commit()
        conn.close()

        return redirect("/expenses")

    conn.close()
    return render_template("edit_expense.html", expense=expense)

@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE expenses
        SET is_deleted = 1
        WHERE id = ?
        AND user_id = ?
    """, (expense_id, current_user.id))

    conn.commit()
    conn.close()

    return redirect("/expenses")


@app.route("/expenses/<int:expense_id>/restore", methods=["POST"])
@login_required
def restore_expense(expense_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE expenses
        SET is_deleted = 0
        WHERE id = ?
        AND user_id = ?
    """, (expense_id, current_user.id))

    conn.commit()
    conn.close()

    return redirect("/trash")


@app.route("/expenses/<int:expense_id>/permanent-delete", methods=["POST"])
@login_required
def permanent_delete_expense(expense_id):
    conn = get_db_connection()

    conn.execute("""
        DELETE FROM expenses
        WHERE id = ?
        AND user_id = ?
    """, (expense_id, current_user.id))

    conn.commit()
    conn.close()

    return redirect("/trash")

@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    conn = get_db_connection()

    current_month = conn.execute("""
        SELECT strftime('%Y-%m', 'now')
    """).fetchone()[0]

    if request.method == "POST":
        amount = request.form.get("amount")

        conn.execute("""
            INSERT INTO budgets (user_id, month, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, month) DO UPDATE SET amount = excluded.amount
        """, (current_user.id, current_month, amount))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    budget_row = conn.execute("""
        SELECT * FROM budgets
        WHERE user_id = ? 
        AND month = ?
    """, (current_user.id, current_month)).fetchone()

    conn.close()

    return render_template(
        "budget.html",
        current_month=current_month,
        budget_row=budget_row
    )
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = generate_password_hash(password)

        conn = get_db_connection()

        existing_user = conn.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        if existing_user:
            conn.close()
            return "Username already exists"

        conn.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, (username, password_hash))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        conn.close()

        if user is None:
            return "Invalid username or password"

        if not check_password_hash(user["password_hash"], password):
            return "Invalid username or password"

        user_object = User(user["id"], user["username"], user["password_hash"])
        login_user(user_object)

        return redirect("/expenses")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=5001)
