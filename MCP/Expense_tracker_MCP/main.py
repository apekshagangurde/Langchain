import sqlite3
from datetime import date
from pathlib import Path

from fastmcp import FastMCP

DB_PATH = Path(__file__).parent / "expenses.db"

mcp = FastMCP(name="Expense Tracker")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                expense_date TEXT NOT NULL
            )
            """
        )


init_db()


@mcp.tool
def add_expense(
    amount: float,
    category: str,
    description: str = "",
    expense_date: str = "",
) -> dict:
    """Add a new expense record. expense_date defaults to today if not given (format: YYYY-MM-DD)."""
    if not expense_date:
        expense_date = date.today().isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (amount, category, description, expense_date) VALUES (?, ?, ?, ?)",
            (amount, category, description, expense_date),
        )
        return {
            "id": cursor.lastrowid,
            "amount": amount,
            "category": category,
            "description": description,
            "expense_date": expense_date,
        }


@mcp.tool
def list_expenses(category: str = "", start_date: str = "", end_date: str = "") -> list[dict]:
    """List expenses, optionally filtered by category and/or a date range (YYYY-MM-DD)."""
    query = "SELECT * FROM expenses WHERE 1=1"
    params: list[str] = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND expense_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND expense_date <= ?"
        params.append(end_date)

    query += " ORDER BY expense_date DESC, id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


@mcp.tool
def update_expense(
    expense_id: int,
    amount: float | None = None,
    category: str | None = None,
    description: str | None = None,
    expense_date: str | None = None,
) -> dict:
    """Update fields of an existing expense by id. Only provided fields are changed."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if row is None:
            return {"error": f"No expense found with id {expense_id}"}

        updated = {
            "amount": amount if amount is not None else row["amount"],
            "category": category if category is not None else row["category"],
            "description": description if description is not None else row["description"],
            "expense_date": expense_date if expense_date is not None else row["expense_date"],
        }

        conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, description = ?, expense_date = ? WHERE id = ?",
            (updated["amount"], updated["category"], updated["description"], updated["expense_date"], expense_id),
        )
        return {"id": expense_id, **updated}


@mcp.tool
def delete_expense(expense_id: int) -> dict:
    """Delete an expense by id."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cursor.rowcount == 0:
            return {"error": f"No expense found with id {expense_id}"}
        return {"deleted_id": expense_id}


@mcp.tool
def get_summary(start_date: str = "", end_date: str = "") -> dict:
    """Get total spend and per-category breakdown, optionally within a date range (YYYY-MM-DD)."""
    query = "SELECT category, SUM(amount) as total FROM expenses WHERE 1=1"
    params: list[str] = []

    if start_date:
        query += " AND expense_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND expense_date <= ?"
        params.append(end_date)

    query += " GROUP BY category"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        by_category = {row["category"]: row["total"] for row in rows}
        return {
            "total": sum(by_category.values()),
            "by_category": by_category,
        }


if __name__ == "__main__":
    mcp.run()
