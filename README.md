# 🏥 Hospital Database Management System

A full-stack portfolio project built with **PostgreSQL** and **Python Streamlit**, demonstrating real-world relational database design, backend connectivity, and an interactive frontend.

---

## 📌 Features

| Module | Description |
|---|---|
| 📊 Dashboard | Live KPIs — patients, doctors, appointments, revenue |
| 👤 Add Patient | Register new patients with full demographic info |
| 🩺 View Patients | Search & browse all patient records |
| 👨‍⚕️ Add Doctor | Onboard doctors with department & specialization |
| 📅 Book Appointment | Schedule patient–doctor appointments |
| 📋 View Appointments | Filter by date range and status |
| 💳 Billing Overview | Revenue breakdown by method and status |

---

## 🛠️ Technologies Used

- **Database:** PostgreSQL 15+
- **Backend:** Python 3.10+ · psycopg2-binary
- **Frontend:** Streamlit 1.32+
- **Data:** pandas

---

## 📁 Project Structure

```
hospital_dbms/
├── sql/
│   └── hospital_schema.sql     # Full schema + 100+ sample rows
├── app/
│   ├── db_connection.py        # PostgreSQL connection & query helpers
│   └── app.py                  # Streamlit frontend
├── docs/
│   └── ER_Diagram.md           # Entity–Relationship description
├── screenshots/                # UI screenshots (add your own)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites

- PostgreSQL 15+ installed and running
- Python 3.10+ installed
- `pip` package manager

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/hospital-dbms.git
cd hospital-dbms
```

### Step 2 — Create a Python virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Create the PostgreSQL database

```bash
# Log in to PostgreSQL
psql -U postgres

# Inside psql shell:
CREATE DATABASE hospital_db;
\q
```

### Step 5 — Run the SQL schema

```bash
psql -U postgres -d hospital_db -f sql/hospital_schema.sql
```

You should see a series of `INSERT` confirmations. The database is now populated with sample data.

### Step 6 — Configure your database credentials

Open `app/db_connection.py` and update the `DB_CONFIG` dictionary:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "hospital_db",
    "user":     "postgres",      # ← your PostgreSQL username
    "password": "your_password", # ← your PostgreSQL password
}
```

### Step 7 — Run the Streamlit app

```bash
cd app
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 🗂️ Database Schema Overview

```
Department ──< Doctor ──< Appointment >── Patient
                               │
                         Medical_Record
                               │
                            Billing
```

### Tables

| Table | Key Columns |
|---|---|
| `Department` | department_id, name, location, head_of_dept |
| `Doctor` | doctor_id, department_id (FK), specialization, experience_yrs |
| `Patient` | patient_id, gender, blood_group, emergency_contact |
| `Appointment` | appointment_id, patient_id (FK), doctor_id (FK), status |
| `Medical_Record` | record_id, appointment_id (FK), diagnosis, prescription |
| `Billing` | bill_id, appointment_id (FK), total_amount (computed), payment_status |

---

## 🔍 Sample SQL Queries

**Appointments this month:**
```sql
SELECT * FROM v_appointment_details
WHERE EXTRACT(MONTH FROM appointment_date) = EXTRACT(MONTH FROM CURRENT_DATE);
```

**Revenue by department:**
```sql
SELECT department, SUM(total_amount) AS revenue
FROM v_billing_summary
GROUP BY department
ORDER BY revenue DESC;
```

**Patients with pending bills:**
```sql
SELECT p.first_name || ' ' || p.last_name AS patient,
       b.total_amount, b.bill_date
FROM Billing b JOIN Patient p ON b.patient_id = p.patient_id
WHERE b.payment_status = 'Pending';
```

---

## 📸 Screenshots

> Add screenshots of your running app to the `screenshots/` folder and reference them here.

---

## 🚀 Future Enhancements

- [ ] Role-based login (Admin / Doctor / Receptionist)
- [ ] PDF invoice generation for billing
- [ ] Email appointment reminders
- [ ] REST API layer with FastAPI
- [ ] Docker Compose for one-command setup

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**Your Name**  
[GitHub](https://github.com/your-username) · [LinkedIn](https://linkedin.com/in/your-profile)
