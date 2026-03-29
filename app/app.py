# =========================================================
#  app.py  —  Hospital Database Management System
#  Run with:  streamlit run app.py
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date, time
import sys, os

# Make sure db_connection is importable from the same folder
sys.path.insert(0, os.path.dirname(__file__))
from db_connection import (
    run_query, run_insert,
    get_departments, get_doctors, get_patients,
    get_appointments, get_billing_summary,
)

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
ER_DIAGRAM_PATH = os.path.join(DOCS_DIR, "ER_Diagram.md")

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Hospital DBMS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] { background: #0f2b46; }
    [data-testid="stSidebar"] .css-1d391kg { color: white; }

    /* Cards */
    .stat-card {
        background: #1e3a5f;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        margin: 4px;
    }
    .stat-card h2 { font-size: 2.4rem; margin: 0; color: #4fc3f7; }
    .stat-card p  { margin: 0; opacity: .8; font-size: .9rem; }

    /* Section headers */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a5f;
        border-left: 4px solid #4fc3f7;
        padding-left: 12px;
        margin-bottom: 16px;
    }

    /* Success / error feedback */
    .stSuccess, .stError { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar navigation ────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Hospital DBMS")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "👤 Add Patient",
            "🩺 View Patients",
            "👨‍⚕️ Add Doctor",
            "📅 Book Appointment",
            "📋 View Appointments",
            "💳 Billing Overview",
            "🗂️ ER Diagram",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Hospital DBMS v1.0 • PostgreSQL + Streamlit")


# =============================================================
# PAGE 1 — DASHBOARD
# =============================================================
if page == "📊 Dashboard":
    st.title("🏥 Hospital Dashboard")
    st.markdown("Real-time summary from the PostgreSQL database.")
    st.markdown("---")

    # KPI metrics
    total_patients  = run_query("SELECT COUNT(*) AS n FROM Patient")
    total_doctors   = run_query("SELECT COUNT(*) AS n FROM Doctor")
    total_appts     = run_query("SELECT COUNT(*) AS n FROM Appointment")
    total_revenue   = run_query("SELECT COALESCE(SUM(total_amount),0) AS n FROM Billing WHERE payment_status='Paid'")

    c1, c2, c3, c4 = st.columns(4)
    def kpi(col, icon, label, rows):
        val = rows[0]["n"] if rows else 0
        col.markdown(f"""
        <div class="stat-card">
            <h2>{icon} {val:,.0f}</h2>
            <p>{label}</p>
        </div>""", unsafe_allow_html=True)

    kpi(c1, "👤", "Total Patients",    total_patients)
    kpi(c2, "👨‍⚕️", "Total Doctors",   total_doctors)
    kpi(c3, "📅", "Appointments",      total_appts)
    kpi(c4, "₹", "Revenue Collected",  total_revenue)

    st.markdown("---")

    # Recent appointments table
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-title">Recent Appointments</div>', unsafe_allow_html=True)
        appts = run_query("""
            SELECT appointment_date AS "Date",
                   appointment_time AS "Time",
                   patient_name     AS "Patient",
                   doctor_name      AS "Doctor",
                   status           AS "Status"
            FROM v_appointment_details
            ORDER BY appointment_date DESC
            LIMIT 8
        """)
        if appts:
            df = pd.DataFrame(appts)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No appointment data yet.")

    with col2:
        st.markdown('<div class="section-title">Appointments by Status</div>', unsafe_allow_html=True)
        status_data = run_query("""
            SELECT status AS "Status", COUNT(*) AS "Count"
            FROM Appointment GROUP BY status ORDER BY "Count" DESC
        """)
        if status_data:
            df_s = pd.DataFrame(status_data).set_index("Status")
            st.bar_chart(df_s)

    st.markdown("---")

    # Department doctor distribution
    st.markdown('<div class="section-title">Doctors per Department</div>', unsafe_allow_html=True)
    dept_data = run_query("""
        SELECT dept.name AS "Department", COUNT(d.doctor_id) AS "Doctors"
        FROM Department dept
        LEFT JOIN Doctor d ON dept.department_id = d.department_id
        GROUP BY dept.name ORDER BY "Doctors" DESC
    """)
    if dept_data:
        df_dept = pd.DataFrame(dept_data).set_index("Department")
        st.bar_chart(df_dept)


# =============================================================
# PAGE 2 — ADD PATIENT
# =============================================================
elif page == "👤 Add Patient":
    st.title("👤 Register New Patient")
    st.markdown("---")

    with st.form("add_patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name *")
            last_name  = st.text_input("Last Name *")
            dob        = st.date_input("Date of Birth *", min_value=date(1920, 1, 1), max_value=date.today())
            gender     = st.selectbox("Gender *", ["Male", "Female", "Other"])

        with col2:
            blood_group = st.selectbox("Blood Group", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            phone       = st.text_input("Phone Number *")
            email       = st.text_input("Email")
            emergency   = st.text_input("Emergency Contact Number")

        address = st.text_area("Address")

        submitted = st.form_submit_button("✅ Register Patient", use_container_width=True)

        if submitted:
            # Validation
            errors = []
            if not first_name.strip(): errors.append("First name is required.")
            if not last_name.strip():  errors.append("Last name is required.")
            if not phone.strip():      errors.append("Phone number is required.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                sql = """
                    INSERT INTO Patient
                        (first_name, last_name, date_of_birth, gender, blood_group,
                         phone, email, address, emergency_contact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                ok = run_insert(sql, (
                    first_name.strip(), last_name.strip(), dob, gender,
                    blood_group or None, phone.strip(),
                    email.strip() or None, address.strip() or None,
                    emergency.strip() or None,
                ))
                if ok:
                    st.success(f"✅ Patient {first_name} {last_name} registered successfully!")


# =============================================================
# PAGE 3 — VIEW PATIENTS
# =============================================================
elif page == "🩺 View Patients":
    st.title("🩺 Patient Records")
    st.markdown("---")

    search = st.text_input("🔍 Search by name or phone", placeholder="e.g. Kumar or 9500010001")

    if search:
        sql = """
            SELECT patient_id AS "ID",
                   first_name || ' ' || last_name AS "Name",
                   date_of_birth AS "DOB",
                   gender AS "Gender",
                   blood_group AS "Blood",
                   phone AS "Phone",
                   email AS "Email",
                   address AS "Address"
            FROM Patient
            WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER(%s)
               OR phone LIKE %s
            ORDER BY last_name
        """
        rows = run_query(sql, (f"%{search}%", f"%{search}%"))
    else:
        sql = """
            SELECT patient_id AS "ID",
                   first_name || ' ' || last_name AS "Name",
                   date_of_birth AS "DOB",
                   gender AS "Gender",
                   blood_group AS "Blood",
                   phone AS "Phone",
                   email AS "Email",
                   address AS "Address"
            FROM Patient ORDER BY last_name
        """
        rows = run_query(sql)

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df)} patient(s)")
    else:
        st.info("No patients found.")


# =============================================================
# PAGE 4 — ADD DOCTOR
# =============================================================
elif page == "👨‍⚕️ Add Doctor":
    st.title("👨‍⚕️ Register New Doctor")
    st.markdown("---")

    depts = get_departments()
    dept_map = {d["name"]: d["department_id"] for d in depts}

    with st.form("add_doctor_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            first_name     = st.text_input("First Name *")
            last_name      = st.text_input("Last Name *")
            specialization = st.text_input("Specialization *")
            department     = st.selectbox("Department *", list(dept_map.keys()))

        with col2:
            email          = st.text_input("Email *")
            phone          = st.text_input("Phone *")
            experience     = st.number_input("Experience (years)", min_value=0, max_value=50, value=5)
            available_days = st.text_input("Available Days", value="Mon,Tue,Wed,Thu,Fri",
                                           help="e.g. Mon,Wed,Fri")

        submitted = st.form_submit_button("✅ Add Doctor", use_container_width=True)

        if submitted:
            errors = []
            if not first_name.strip():     errors.append("First name required.")
            if not last_name.strip():      errors.append("Last name required.")
            if not specialization.strip(): errors.append("Specialization required.")
            if not email.strip():          errors.append("Email required.")
            if not phone.strip():          errors.append("Phone required.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                sql = """
                    INSERT INTO Doctor
                        (department_id, first_name, last_name, specialization,
                         email, phone, experience_yrs, available_days)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                ok = run_insert(sql, (
                    dept_map[department],
                    first_name.strip(), last_name.strip(),
                    specialization.strip(), email.strip(),
                    phone.strip(), experience,
                    available_days.strip(),
                ))
                if ok:
                    st.success(f"✅ Dr. {first_name} {last_name} added successfully!")


# =============================================================
# PAGE 5 — BOOK APPOINTMENT
# =============================================================
elif page == "📅 Book Appointment":
    st.title("📅 Book Appointment")
    st.markdown("---")

    patients = get_patients()
    patient_map = {
        f"{p['patient_name']} — {p['phone']}": p["patient_id"]
        for p in patients
    }

    depts = get_departments()
    dept_map = {d["name"]: d["department_id"] for d in depts}

    with st.form("book_appt_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            patient_label = st.selectbox("Select Patient *", list(patient_map.keys()))
            dept_label    = st.selectbox("Department *", list(dept_map.keys()))

            # Load doctors for the chosen department
            dept_id  = dept_map[dept_label]
            doctors  = get_doctors(department_id=dept_id)
            doc_map  = {d["doctor_name"]: d["doctor_id"] for d in doctors}
            doc_label = st.selectbox("Select Doctor *", list(doc_map.keys()) if doc_map else ["No doctors in dept"])

        with col2:
            appt_date = st.date_input("Appointment Date *", min_value=date.today())
            appt_time = st.time_input("Appointment Time *", value=time(9, 0))
            reason    = st.text_area("Reason for Visit")
            notes     = st.text_input("Notes (optional)")

        submitted = st.form_submit_button("📅 Book Appointment", use_container_width=True)

        if submitted:
            if not doc_map:
                st.error("No doctors available in selected department.")
            else:
                sql = """
                    INSERT INTO Appointment
                        (patient_id, doctor_id, appointment_date,
                         appointment_time, reason, status, notes)
                    VALUES (%s, %s, %s, %s, %s, 'Scheduled', %s)
                """
                ok = run_insert(sql, (
                    patient_map[patient_label],
                    doc_map[doc_label],
                    appt_date, appt_time,
                    reason.strip() or None,
                    notes.strip() or None,
                ))
                if ok:
                    st.success("✅ Appointment booked successfully!")


# =============================================================
# PAGE 6 — VIEW APPOINTMENTS
# =============================================================
elif page == "📋 View Appointments":
    st.title("📋 Appointments")
    st.markdown("---")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Scheduled", "Completed", "Cancelled", "No-Show"])
    with col2:
        filter_date_from = st.date_input("From Date", value=date(2024, 1, 1))
    with col3:
        filter_date_to = st.date_input("To Date", value=date.today())

    sql = """
        SELECT appointment_id  AS "ID",
               appointment_date AS "Date",
               appointment_time AS "Time",
               patient_name     AS "Patient",
               doctor_name      AS "Doctor",
               department       AS "Department",
               reason           AS "Reason",
               status           AS "Status"
        FROM v_appointment_details
        WHERE appointment_date BETWEEN %s AND %s
    """
    params = [filter_date_from, filter_date_to]

    if filter_status != "All":
        sql += " AND status = %s"
        params.append(filter_status)

    sql += " ORDER BY appointment_date DESC, appointment_time"

    rows = run_query(sql, params)

    if rows:
        df = pd.DataFrame(rows)
        # Colour-code status
        def color_status(val):
            colors = {
                "Scheduled":  "background-color:#e3f2fd; color:#1565c0",
                "Completed":  "background-color:#e8f5e9; color:#2e7d32",
                "Cancelled":  "background-color:#ffebee; color:#c62828",
                "No-Show":    "background-color:#fff3e0; color:#e65100",
            }
            return colors.get(val, "")

        styled = df.style.applymap(color_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df)} appointment(s)")
    else:
        st.info("No appointments found for selected filters.")


# =============================================================
# PAGE 7 — BILLING OVERVIEW
# =============================================================
elif page == "💳 Billing Overview":
    st.title("💳 Billing Overview")
    st.markdown("---")

    # Summary KPIs
    kpi_data = run_query("""
        SELECT
            COUNT(*)                                          AS total_bills,
            COALESCE(SUM(total_amount), 0)                   AS gross_revenue,
            COALESCE(SUM(CASE WHEN payment_status='Paid'
                             THEN total_amount END), 0)       AS collected,
            COALESCE(SUM(CASE WHEN payment_status='Pending'
                             THEN total_amount END), 0)       AS pending
        FROM Billing
    """)

    if kpi_data:
        kpi = kpi_data[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Bills",       f"{kpi['total_bills']}")
        c2.metric("Gross Revenue",     f"₹ {kpi['gross_revenue']:,.2f}")
        c3.metric("Collected",         f"₹ {kpi['collected']:,.2f}")
        c4.metric("Pending",           f"₹ {kpi['pending']:,.2f}")

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Revenue by Payment Method</div>', unsafe_allow_html=True)
        pm_data = run_query("""
            SELECT COALESCE(payment_method,'Unknown') AS "Method",
                   SUM(total_amount) AS "Amount"
            FROM Billing GROUP BY payment_method ORDER BY "Amount" DESC
        """)
        if pm_data:
            st.bar_chart(pd.DataFrame(pm_data).set_index("Method"))

    with col2:
        st.markdown('<div class="section-title">Payment Status Distribution</div>', unsafe_allow_html=True)
        ps_data = run_query("""
            SELECT payment_status AS "Status", COUNT(*) AS "Count"
            FROM Billing GROUP BY payment_status
        """)
        if ps_data:
            st.bar_chart(pd.DataFrame(ps_data).set_index("Status"))

    st.markdown("---")

    # Detailed billing table
    st.markdown('<div class="section-title">Billing Details</div>', unsafe_allow_html=True)
    rows = get_billing_summary()
    if rows:
        df = pd.DataFrame(rows)
        # Rename columns for display
        df.columns = [c.replace("_", " ").title() for c in df.columns]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No billing records found.")



# =============================================================
# PAGE 8 — ER DIAGRAM
# =============================================================
elif page == "🗂️ ER Diagram":
    st.title("🐾 Hospital ER Diagram")
    st.markdown("---")
    
    import streamlit.components.v1 as components
    
    er_html = """
    <style>
        #erd-container {
            background: #ffffff; /* Clean White Background */
            border-radius: 16px;
            padding: 25px;
            border: 2px solid #e0e0e0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: auto;
        }
        
        /* THE VIBRANIUM BLACK EFFECT: Glowing Black Text */
        svg text {
            fill: #1a1a1a !important; /* Deep Black */
            font-family: 'Inter', system-ui, sans-serif !important;
            font-weight: 800 !important;
            font-size: 16px !important;
            filter: drop-shadow(0 0 1px #6B00FF); /* Subtle Purple Glow */
        }

        /* Entity Headers - Black with Purple Aura */
        svg .node .entityBox text {
            fill: #000000 !important;
            font-size: 18px !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            filter: drop-shadow(0 0 3px #6B00FF);
        }
        
        /* Relationship Lines - Glowing Black/Cyan */
        svg .edgePath path {
            stroke: #000000 !important;
            stroke-width: 2.5px !important;
            filter: drop-shadow(0 0 2px #00f5ff);
        }

        /* Relationship Labels */
        svg .edgeLabel text {
            fill: #6B00FF !important; /* Purple for action labels */
            background: white !important;
            font-weight: bold !important;
        }
        
        /* Entity Boxes - White with Black/Purple borders */
        svg .node rect {
            fill: #ffffff !important;
            stroke: #000000 !important;
            stroke-width: 3px !important;
            rx: 10 !important;
            filter: drop-shadow(4px 4px 0px #6B00FF); /* Vibranium offset shadow */
        }

        /* PK/FK Indicators - High Visibility Red/Cyan */
        svg text[tspan*="PK"] { fill: #ff0055 !important; }
        svg text[tspan*="FK"] { fill: #008cff !important; }
        
        /* Interaction Hover */
        svg .node:hover rect {
            fill: #f8f0ff !important;
            stroke: #6B00FF !important;
            transform: translateY(-3px);
            transition: 0.3s ease;
        }
    </style>
    
    <div id="erd-container">
        <div id="erd" style="width:100%; min-height: 900px;"></div>
    </div>
    
    <script type="module">
      import mermaid from 'https://esm.sh/mermaid@11/dist/mermaid.esm.min.mjs';
      
      mermaid.initialize({
        startOnLoad: false,
        theme: 'default', // Using default base for white background
        er: {
            useMaxWidth: true,
            diagramPadding: 20,
            layoutDirection: 'TB',
            minEntityWidth: 180,
            minEntityHeight: 90
        },
        themeVariables: {
          darkMode: false,
          background: '#ffffff',
          lineColor: '#000000',
          primaryColor: '#ffffff',
          primaryBorderColor: '#000000',
          primaryTextColor: '#000000',
          secondaryColor: '#6B00FF',
          tertiaryColor: '#f8f9fa'
        }
      });
      
      const diagram = `erDiagram
        DEPARTMENT {
          serial department_id PK
          varchar name
          varchar location
          varchar head_of_dept
        }
        DOCTOR {
          serial doctor_id PK
          int department_id FK
          varchar first_name
          varchar last_name
          varchar specialization
          int experience_yrs
        }
        PATIENT {
          serial patient_id PK
          varchar first_name
          varchar last_name
          varchar blood_group
          varchar phone
        }
        APPOINTMENT {
          serial appointment_id PK
          int patient_id FK
          int doctor_id FK
          date appointment_date
          varchar status
        }
        MEDICAL_RECORD {
          serial record_id PK
          int appointment_id FK
          text diagnosis
          text treatment
          date follow_up_date
        }
        BILLING {
          serial bill_id PK
          int appointment_id FK
          numeric total_amount
          varchar payment_status
        }
        DEPARTMENT ||--o{ DOCTOR : "employs"
        DOCTOR ||--o{ APPOINTMENT : "attends"
        PATIENT ||--o{ APPOINTMENT : "books"
        APPOINTMENT ||--o| MEDICAL_RECORD : "generates"
        APPOINTMENT ||--o| BILLING : "billed via"
        PATIENT ||--o{ BILLING : "pays"
        PATIENT ||--o{ MEDICAL_RECORD : "has"
        DOCTOR ||--o{ MEDICAL_RECORD : "creates"
      `;
      
      const { svg } = await mermaid.render('erd-svg', diagram);
      const container = document.getElementById('erd');
      container.innerHTML = svg;
      
      const svgElement = container.querySelector('svg');
      if (svgElement) {
        svgElement.style.width = '100%';
        svgElement.style.height = 'auto';
      }
    </script>
    """
    
    components.html(er_html, height=950, scrolling=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🧬 Database Core Logic")
        st.write("""
        This schema follows a **Relational Model** designed for a Multi-specialty Hospital. 
        The **Department** acts as the root entity, organizing **Doctors** who are 
        linked to **Patients** through the central **Appointment** table. 
        """)
    with col2:
        st.markdown("### 🔗 Relationship Integrity")
        st.write("""
        - **1:M (One-to-Many):** A Patient can have multiple Appointments and Medical Records.
        - **1:1 (One-to-One):** Each unique Appointment triggers exactly one Billing entry 
          and one specific Diagnosis record to maintain data normalization.
        """)