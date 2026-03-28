# =========================================================
#  db_connection.py
#  Handles all PostgreSQL connections via psycopg2
#  Update the DB_CONFIG dict with your local credentials
# =========================================================

import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

# ── Database credentials ──────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "hospital_db",
    "user":     "postgres",       # change if needed
    "password": "postgres",       # change to your password
}


# ── Connection helper ─────────────────────────────────────
def get_connection():
    """
    Returns a psycopg2 connection object.
    Uses Streamlit's session_state to cache within a session.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info("Please check your PostgreSQL credentials in `db_connection.py`.")
        return None


# ── Generic query runners ─────────────────────────────────
def run_query(sql: str, params=None, fetch: bool = True):
    """
    Execute a SELECT query and return rows as list-of-dicts.
    Returns empty list on error.
    """
    conn = get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
            return []
    except Exception as e:
        st.error(f"Query error: {e}")
        return []
    finally:
        conn.close()


def run_insert(sql: str, params=None) -> bool:
    """
    Execute an INSERT/UPDATE/DELETE query.
    Returns True on success, False on failure.
    """
    conn = get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Insert/Update error: {e}")
        return False
    finally:
        conn.close()


# ── Domain-specific helpers (used by app.py) ──────────────

def get_departments():
    return run_query("SELECT department_id, name FROM Department ORDER BY name")


def get_doctors(department_id=None):
    if department_id:
        sql = """
            SELECT d.doctor_id,
                   'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
                   d.specialization
            FROM Doctor d
            WHERE d.department_id = %s
            ORDER BY d.last_name
        """
        return run_query(sql, (department_id,))
    sql = """
        SELECT d.doctor_id,
               'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
               d.specialization, dept.name AS department
        FROM Doctor d
        JOIN Department dept ON d.department_id = dept.department_id
        ORDER BY dept.name, d.last_name
    """
    return run_query(sql)


def get_patients():
    sql = """
        SELECT patient_id,
               first_name || ' ' || last_name AS patient_name,
               phone, date_of_birth, gender, blood_group
        FROM Patient
        ORDER BY last_name
    """
    return run_query(sql)


def get_appointments():
    sql = """
        SELECT * FROM v_appointment_details
        ORDER BY appointment_date DESC, appointment_time
    """
    return run_query(sql)


def get_billing_summary():
    return run_query("SELECT * FROM v_billing_summary ORDER BY bill_date DESC")
