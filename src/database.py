import sqlite3
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Sequence, Tuple

DB_NAME = "water_tracker.db"


def _connect():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            intake_ml INTEGER,
            date TEXT
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_goals (
            user_id TEXT PRIMARY KEY,
            daily_goal_ml INTEGER,
            updated_at TEXT
        )
    """
    )
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            reminder_time TEXT,
            label TEXT,
            created_at TEXT
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mood_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            mood_level INTEGER,
            note TEXT,
            date TEXT
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS habit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            habit TEXT,
            completed BOOLEAN,
            date TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def log_intake(user_id: str, intake_ml: int, date: Optional[str] = None) -> None:
    conn = _connect()
    cursor = conn.cursor()
    date_value = date or datetime.today().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO water_intake (user_id, intake_ml, date) VALUES (?, ?, ?)",
        (user_id, intake_ml, date_value),
    )
    conn.commit()
    conn.close()


def get_intake_history(user_id: str) -> List[Tuple[int, str]]:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT intake_ml, date FROM water_intake WHERE user_id = ? ORDER BY date ASC",
        (user_id,),
    )
    records = cursor.fetchall()
    conn.close()
    return records


def get_daily_totals(user_id: str, days: Optional[int] = None) -> Sequence[Tuple[str, int]]:
    conn = _connect()
    cursor = conn.cursor()
    params: List = [user_id]
    query = """
        SELECT date, SUM(intake_ml) FROM water_intake
        WHERE user_id = ?
    """
    if days:
        threshold = (datetime.today() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        query += " AND date >= ?"
        params.append(threshold)
    query += " GROUP BY date ORDER BY date ASC"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


def get_leaderboard(top_n: int = 5, days: int = 7) -> Sequence[Tuple[str, int]]:
    conn = _connect()
    cursor = conn.cursor()
    threshold = (datetime.today() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT user_id, SUM(intake_ml) as total FROM water_intake
        WHERE date >= ? GROUP BY user_id ORDER BY total DESC LIMIT ?
    """,
        (threshold, top_n),
    )
    leaders = cursor.fetchall()
    conn.close()
    return leaders


def get_user_goal(user_id: str) -> int:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT daily_goal_ml FROM user_goals WHERE user_id = ?", (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else 2000


def upsert_user_goal(user_id: str, goal_ml: int) -> None:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_goals (user_id, daily_goal_ml, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            daily_goal_ml = excluded.daily_goal_ml,
            updated_at = excluded.updated_at
    """,
        (user_id, goal_ml, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def add_reminder(user_id: str, reminder_time: str, label: Optional[str]) -> None:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reminders (user_id, reminder_time, label, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, reminder_time, label or "", datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_reminders(user_id: str) -> Sequence[Tuple[int, str, str, str]]:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, reminder_time, label, created_at FROM reminders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    records = cursor.fetchall()
    conn.close()
    return records


def delete_reminder(reminder_id: int) -> None:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def log_mood(user_id: str, mood_level: int, note: Optional[str] = None, date: Optional[str] = None) -> None:
    conn = _connect()
    cursor = conn.cursor()
    date_value = date or datetime.today().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO mood_journal (user_id, mood_level, note, date) VALUES (?, ?, ?, ?)",
        (user_id, mood_level, note or "", date_value),
    )
    conn.commit()
    conn.close()


def get_mood_history(user_id: str, days: Optional[int] = 14) -> List[Tuple[str, int, str]]:
    conn = _connect()
    cursor = conn.cursor()
    query = "SELECT date, mood_level, note FROM mood_journal WHERE user_id = ?"
    params: List = [user_id]
    if days:
        threshold = (datetime.today() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        query += " AND date >= ?"
        params.append(threshold)
    query += " ORDER BY date DESC"
    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()
    return records


def log_habit(user_id: str, habit: str, completed: bool, date: Optional[str] = None) -> None:
    conn = _connect()
    cursor = conn.cursor()
    date_value = date or datetime.today().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO habit_log (user_id, habit, completed, date) VALUES (?, ?, ?, ?)",
        (user_id, habit, int(completed), date_value),
    )
    conn.commit()
    conn.close()


def get_habit_summary(user_id: str, days: Optional[int] = 7) -> Sequence[Tuple[str, int, int]]:
    conn = _connect()
    cursor = conn.cursor()
    query = """
        SELECT habit,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed,
            COUNT(*) as total
        FROM habit_log
        WHERE user_id = ?
    """
    params: List = [user_id]
    if days:
        threshold = (datetime.today() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        query += " AND date >= ?"
        params.append(threshold)
    query += " GROUP BY habit"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


def import_records(records: Iterable[Tuple[str, int, str]]) -> None:
    for user_id, intake_ml, intake_date in records:
        log_intake(user_id, intake_ml, date=intake_date)


# Initialize the table
create_tables()
