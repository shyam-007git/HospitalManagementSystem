-- =============================================================
--  HOSPITAL DATABASE MANAGEMENT SYSTEM
--  hospital_schema.sql
--  PostgreSQL Schema + Sample Data
-- =============================================================

-- Drop tables if they exist (clean slate for re-runs)
DROP TABLE IF EXISTS Billing        CASCADE;
DROP TABLE IF EXISTS Medical_Record CASCADE;
DROP TABLE IF EXISTS Appointment    CASCADE;
DROP TABLE IF EXISTS Patient        CASCADE;
DROP TABLE IF EXISTS Doctor         CASCADE;
DROP TABLE IF EXISTS Department     CASCADE;

-- =============================================================
-- 1. DEPARTMENT
-- =============================================================
CREATE TABLE Department (
    department_id   SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    location        VARCHAR(100) NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    head_of_dept    VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 2. DOCTOR
-- =============================================================
CREATE TABLE Doctor (
    doctor_id       SERIAL PRIMARY KEY,
    department_id   INT          NOT NULL REFERENCES Department(department_id) ON DELETE SET NULL,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    specialization  VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20)  NOT NULL,
    experience_yrs  INT          CHECK (experience_yrs >= 0),
    available_days  VARCHAR(100) DEFAULT 'Mon-Fri',  -- e.g. 'Mon,Wed,Fri'
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 3. PATIENT
-- =============================================================
CREATE TABLE Patient (
    patient_id      SERIAL PRIMARY KEY,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    date_of_birth   DATE         NOT NULL,
    gender          VARCHAR(10)  NOT NULL CHECK (gender IN ('Male','Female','Other')),
    blood_group     VARCHAR(5),
    phone           VARCHAR(20)  NOT NULL,
    email           VARCHAR(100) UNIQUE,
    address         TEXT,
    emergency_contact VARCHAR(20),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 4. APPOINTMENT
-- =============================================================
CREATE TABLE Appointment (
    appointment_id  SERIAL PRIMARY KEY,
    patient_id      INT  NOT NULL REFERENCES Patient(patient_id)  ON DELETE CASCADE,
    doctor_id       INT  NOT NULL REFERENCES Doctor(doctor_id)    ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason          TEXT,
    status          VARCHAR(20) DEFAULT 'Scheduled'
                    CHECK (status IN ('Scheduled','Completed','Cancelled','No-Show')),
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 5. MEDICAL RECORD
-- =============================================================
CREATE TABLE Medical_Record (
    record_id       SERIAL PRIMARY KEY,
    appointment_id  INT  NOT NULL UNIQUE REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    patient_id      INT  NOT NULL REFERENCES Patient(patient_id) ON DELETE CASCADE,
    doctor_id       INT  NOT NULL REFERENCES Doctor(doctor_id)   ON DELETE CASCADE,
    diagnosis       TEXT NOT NULL,
    treatment       TEXT,
    prescription    TEXT,
    follow_up_date  DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 6. BILLING
-- =============================================================
CREATE TABLE Billing (
    bill_id         SERIAL PRIMARY KEY,
    patient_id      INT            NOT NULL REFERENCES Patient(patient_id) ON DELETE CASCADE,
    appointment_id  INT            NOT NULL UNIQUE REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    consultation_fee NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    medicine_cost   NUMERIC(10,2) DEFAULT 0.00,
    test_cost       NUMERIC(10,2) DEFAULT 0.00,
    other_charges   NUMERIC(10,2) DEFAULT 0.00,
    total_amount    NUMERIC(10,2) GENERATED ALWAYS AS
                    (consultation_fee + medicine_cost + test_cost + other_charges) STORED,
    payment_status  VARCHAR(20) DEFAULT 'Pending'
                    CHECK (payment_status IN ('Pending','Paid','Partial','Waived')),
    payment_method  VARCHAR(20) CHECK (payment_method IN ('Cash','Card','Insurance','UPI', NULL)),
    bill_date       DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- SAMPLE DATA — Department (10 rows)
-- =============================================================
INSERT INTO Department (name, location, phone, head_of_dept) VALUES
('Cardiology',          'Block A, Floor 1', '044-2001-1001', 'Dr. Ramesh Iyer'),
('Neurology',           'Block A, Floor 2', '044-2001-1002', 'Dr. Priya Suresh'),
('Orthopedics',         'Block B, Floor 1', '044-2001-1003', 'Dr. Karan Mehta'),
('Pediatrics',          'Block B, Floor 2', '044-2001-1004', 'Dr. Anita Sharma'),
('Dermatology',         'Block C, Floor 1', '044-2001-1005', 'Dr. Vikram Nair'),
('Gynecology',          'Block C, Floor 2', '044-2001-1006', 'Dr. Sunita Rao'),
('Ophthalmology',       'Block D, Floor 1', '044-2001-1007', 'Dr. Arjun Pillai'),
('ENT',                 'Block D, Floor 2', '044-2001-1008', 'Dr. Meera Krishnan'),
('General Medicine',    'Block E, Floor 1', '044-2001-1009', 'Dr. Suresh Patel'),
('Emergency Medicine',  'Block E, Ground',  '044-2001-1010', 'Dr. Ravi Chandran');

-- =============================================================
-- SAMPLE DATA — Doctor (20 rows)
-- =============================================================
INSERT INTO Doctor (department_id, first_name, last_name, specialization, email, phone, experience_yrs, available_days) VALUES
(1,  'Ramesh',    'Iyer',       'Interventional Cardiology', 'ramesh.iyer@hospital.com',      '9840001001', 18, 'Mon,Tue,Wed,Thu,Fri'),
(1,  'Deepa',     'Nair',       'Echocardiography',          'deepa.nair@hospital.com',        '9840001002', 12, 'Mon,Wed,Fri'),
(2,  'Priya',     'Suresh',     'Clinical Neurology',        'priya.suresh@hospital.com',      '9840001003', 15, 'Mon,Tue,Thu,Fri'),
(2,  'Arun',      'Krishnan',   'Neuro Surgery',             'arun.krishnan@hospital.com',     '9840001004', 20, 'Tue,Thu'),
(3,  'Karan',     'Mehta',      'Joint Replacement',         'karan.mehta@hospital.com',       '9840001005', 14, 'Mon,Tue,Wed,Thu,Fri'),
(3,  'Sneha',     'Pillai',     'Spine Surgery',             'sneha.pillai@hospital.com',      '9840001006', 10, 'Mon,Wed,Fri'),
(4,  'Anita',     'Sharma',     'Neonatology',               'anita.sharma@hospital.com',      '9840001007', 11, 'Mon,Tue,Wed,Thu,Fri'),
(4,  'Rohan',     'Gupta',      'Pediatric Cardiology',      'rohan.gupta@hospital.com',       '9840001008',  8, 'Mon,Thu,Fri'),
(5,  'Vikram',    'Nair',       'Cosmetology',               'vikram.nair@hospital.com',       '9840001009', 13, 'Tue,Thu,Sat'),
(5,  'Lavanya',   'Menon',      'Clinical Dermatology',      'lavanya.menon@hospital.com',     '9840001010',  7, 'Mon,Wed,Fri'),
(6,  'Sunita',    'Rao',        'Obstetrics',                'sunita.rao@hospital.com',        '9840001011', 16, 'Mon,Tue,Wed,Thu,Fri'),
(6,  'Divya',     'Chakraborty','Reproductive Medicine',     'divya.chakra@hospital.com',      '9840001012',  9, 'Mon,Wed,Thu'),
(7,  'Arjun',     'Pillai',     'Retinal Surgery',           'arjun.pillai@hospital.com',      '9840001013', 17, 'Mon,Tue,Thu'),
(7,  'Meenakshi', 'Sundaram',   'Glaucoma Specialist',       'meenakshi.s@hospital.com',       '9840001014', 11, 'Tue,Wed,Fri'),
(8,  'Meera',     'Krishnan',   'Rhinology',                 'meera.krishnan@hospital.com',    '9840001015', 12, 'Mon,Tue,Wed,Thu,Fri'),
(8,  'Suresh',    'Balaji',     'Otology',                   'suresh.balaji@hospital.com',     '9840001016',  9, 'Mon,Wed,Fri'),
(9,  'Suresh',    'Patel',      'Internal Medicine',         'suresh.patel@hospital.com',      '9840001017', 22, 'Mon,Tue,Wed,Thu,Fri'),
(9,  'Kavitha',   'Rajan',      'Diabetology',               'kavitha.rajan@hospital.com',     '9840001018', 14, 'Tue,Thu,Fri'),
(10, 'Ravi',      'Chandran',   'Emergency & Trauma',        'ravi.chandran@hospital.com',     '9840001019', 19, 'Mon,Tue,Wed,Thu,Fri'),
(10, 'Nalini',    'Venkat',     'Critical Care Medicine',    'nalini.venkat@hospital.com',     '9840001020', 10, 'Mon,Tue,Wed,Thu,Fri,Sat,Sun');

-- =============================================================
-- SAMPLE DATA — Patient (20 rows)
-- =============================================================
INSERT INTO Patient (first_name, last_name, date_of_birth, gender, blood_group, phone, email, address, emergency_contact) VALUES
('Aditya',   'Kumar',      '1990-03-15', 'Male',   'O+',  '9500010001', 'aditya.kumar@gmail.com',    '12, Anna Nagar, Chennai',             '9500010011'),
('Bhavani',  'Devi',       '1985-07-22', 'Female', 'A+',  '9500010002', 'bhavani.d@gmail.com',        '34, T.Nagar, Chennai',                '9500010012'),
('Chandru',  'Sekhar',     '1978-11-05', 'Male',   'B+',  '9500010003', 'chandru.s@gmail.com',        '56, Velachery, Chennai',              '9500010013'),
('Dhivya',   'Lakshmi',    '1995-01-30', 'Female', 'AB+', '9500010004', 'dhivya.l@gmail.com',         '78, Adyar, Chennai',                  '9500010014'),
('Ezhilan',  'Murugan',    '1972-08-19', 'Male',   'O-',  '9500010005', 'ezhilan.m@gmail.com',        '90, Tambaram, Chennai',               '9500010015'),
('Fathima',  'Begum',      '1988-04-12', 'Female', 'B-',  '9500010006', 'fathima.b@gmail.com',        '102, Triplicane, Chennai',            '9500010016'),
('Ganesh',   'Raj',        '1993-09-25', 'Male',   'A-',  '9500010007', 'ganesh.raj@gmail.com',       '14, Porur, Chennai',                  '9500010017'),
('Hema',     'Priya',      '2000-12-08', 'Female', 'O+',  '9500010008', 'hema.priya@gmail.com',       '26, Guindy, Chennai',                 '9500010018'),
('Ilango',   'Selvam',     '1965-06-14', 'Male',   'AB-', '9500010009', 'ilango.s@gmail.com',         '38, Mylapore, Chennai',               '9500010019'),
('Jayanthi', 'Balamurugan','1982-02-28', 'Female', 'A+',  '9500010010', 'jayanthi.b@gmail.com',       '50, Kodambakkam, Chennai',            '9500010020'),
('Karthik',  'Sundaram',   '1997-05-17', 'Male',   'B+',  '9500010011', 'karthik.sun@gmail.com',      '62, Perambur, Chennai',               '9500010021'),
('Lalitha',  'Natarajan',  '1979-10-03', 'Female', 'O+',  '9500010012', 'lalitha.n@gmail.com',        '74, Chromepet, Chennai',              '9500010022'),
('Manoj',    'Rajan',      '1991-07-11', 'Male',   'A+',  '9500010013', 'manoj.r@gmail.com',          '86, Sholinganallur, Chennai',         '9500010023'),
('Nirmala',  'Sivakumar',  '1969-03-22', 'Female', 'B+',  '9500010014', 'nirmala.siv@gmail.com',      '98, Pallavaram, Chennai',             '9500010024'),
('Oviya',    'Anand',      '2002-11-29', 'Female', 'O+',  '9500010015', 'oviya.a@gmail.com',          '10, Madipakkam, Chennai',             '9500010025'),
('Prakash',  'Vel',        '1975-04-06', 'Male',   'AB+', '9500010016', 'prakash.vel@gmail.com',      '22, Nanganallur, Chennai',            '9500010026'),
('Queen',    'Mary',       '1988-08-13', 'Female', 'A-',  '9500010017', 'queen.mary@gmail.com',       '34, Nungambakkam, Chennai',           '9500010027'),
('Raghu',    'Nathan',     '1983-01-20', 'Male',   'O-',  '9500010018', 'raghu.n@gmail.com',          '46, Thiruvanmiyur, Chennai',          '9500010028'),
('Saranya',  'Kumari',     '1996-06-07', 'Female', 'B-',  '9500010019', 'saranya.k@gmail.com',        '58, Besant Nagar, Chennai',           '9500010029'),
('Thilak',   'Raj',        '1980-09-18', 'Male',   'A+',  '9500010020', 'thilak.raj@gmail.com',       '70, Kilpauk, Chennai',                '9500010030');

-- =============================================================
-- SAMPLE DATA — Appointment (20 rows)
-- =============================================================
INSERT INTO Appointment (patient_id, doctor_id, appointment_date, appointment_time, reason, status, notes) VALUES
(1,  1,  '2024-11-01', '09:00', 'Chest pain and shortness of breath',    'Completed',  'ECG done, referred for Echo'),
(2,  3,  '2024-11-02', '10:00', 'Persistent headaches and dizziness',    'Completed',  'MRI recommended'),
(3,  5,  '2024-11-03', '11:00', 'Right knee pain',                       'Completed',  'X-ray ordered'),
(4,  7,  '2024-11-04', '09:30', 'Routine prenatal checkup',              'Completed',  '28 weeks, normal'),
(5,  9,  '2024-11-05', '14:00', 'Skin rash on arms',                     'Completed',  'Allergy test suggested'),
(6,  11, '2024-11-06', '10:30', 'Irregular periods',                     'Completed',  'Ultrasound ordered'),
(7,  13, '2024-11-07', '11:30', 'Blurred vision in right eye',           'Completed',  'Fundus exam done'),
(8,  15, '2024-11-08', '12:00', 'Ear pain and hearing difficulty',       'Completed',  'Audiogram done'),
(9,  17, '2024-11-09', '09:00', 'High fever and body ache',              'Completed',  'Blood test ordered'),
(10, 19, '2024-11-10', '16:00', 'Road accident, head injury',            'Completed',  'CT scan done urgently'),
(11, 2,  '2024-11-11', '09:00', 'Heart palpitations',                    'Completed',  'Holter monitoring advised'),
(12, 4,  '2024-11-12', '10:00', 'Memory loss symptoms',                  'Completed',  'Neuropsych evaluation scheduled'),
(13, 6,  '2024-11-13', '11:00', 'Lower back pain',                       'Completed',  'MRI spine ordered'),
(14, 8,  '2024-11-14', '14:00', 'Child fever and cough',                 'Completed',  'Antibiotics prescribed'),
(15, 10, '2024-11-15', '15:00', 'Acne treatment follow-up',              'Completed',  'Retinol cream prescribed'),
(16, 12, '2024-11-18', '10:00', 'IVF consultation',                      'Completed',  'Hormonal profile tests ordered'),
(17, 14, '2024-11-19', '11:00', 'Eye pressure check',                    'Completed',  'Glaucoma medication adjusted'),
(18, 16, '2024-11-20', '12:00', 'Chronic sinus blockage',                'Completed',  'Nasal endoscopy scheduled'),
(19, 18, '2024-11-21', '09:30', 'Diabetes management consultation',      'Scheduled',  NULL),
(20, 20, '2024-11-22', '14:30', 'Post-ICU follow-up',                    'Scheduled',  NULL);

-- =============================================================
-- SAMPLE DATA — Medical_Record (18 rows, for completed appts)
-- =============================================================
INSERT INTO Medical_Record (appointment_id, patient_id, doctor_id, diagnosis, treatment, prescription, follow_up_date) VALUES
(1,  1,  1,  'Unstable Angina',                  'Rest, lifestyle changes, cardiac monitoring',   'Aspirin 75mg, Metoprolol 25mg',              '2024-12-01'),
(2,  2,  3,  'Migraine with Aura',               'Avoid triggers, stress management',             'Sumatriptan 50mg, Naproxen 500mg',           '2024-12-02'),
(3,  3,  5,  'Osteoarthritis - Right Knee',       'Physiotherapy, weight reduction',               'Diclofenac 50mg, Calcium supplements',       '2024-12-03'),
(4,  4,  7,  'Normal Pregnancy - 28 weeks',       'Iron and folic acid supplementation',           'Ferrous Sulfate, Folic Acid 5mg',            '2024-12-04'),
(5,  5,  9,  'Allergic Dermatitis',               'Avoid allergen, cool compress',                 'Hydrocortisone cream, Cetirizine 10mg',      '2024-12-05'),
(6,  6,  11, 'Polycystic Ovarian Syndrome (PCOS)','Diet modification, regular exercise',           'Metformin 500mg, OCP',                       '2024-12-06'),
(7,  7,  13, 'Diabetic Retinopathy - Mild',       'Laser photocoagulation if progressive',         'Anti-VEGF drops, Vitamin supplements',       '2024-12-07'),
(8,  8,  15, 'Otitis Media',                      'Ear drops, keep ear dry',                       'Ofloxacin ear drops, Amoxicillin 500mg',     '2024-12-08'),
(9,  9,  17, 'Viral Fever - Dengue suspected',    'IV fluids, rest, monitor platelet count',       'Paracetamol 650mg, ORS sachets',             '2024-11-16'),
(10, 10, 19, 'Traumatic Brain Injury - Mild',     'Observation, CT follow-up',                     'Analgesics, anti-emetics',                   '2024-11-17'),
(11, 11, 2,  'Supraventricular Tachycardia (SVT)','Valsalva maneuver, cardioversion if needed',    'Verapamil 40mg',                             '2024-12-11'),
(12, 12, 4,  'Mild Cognitive Impairment',         'Cognitive exercises, regular review',           'Donepezil 5mg, Vitamin B12',                 '2024-12-12'),
(13, 13, 6,  'Lumbar Disc Herniation - L4-L5',   'Traction, physiotherapy, possible surgery',     'Pregabalin 75mg, Methocarbamol',             '2024-12-13'),
(14, 14, 8,  'Pediatric Upper Respiratory Infection','Steam inhalation, rest, hydration',          'Amoxicillin syrup, Cough syrup',             '2024-11-21'),
(15, 15, 10, 'Moderate Inflammatory Acne',        'Chemical peel, topical retinoids',              'Tretinoin 0.025%, Doxycycline 100mg',        '2024-12-15'),
(16, 16, 12, 'Primary Infertility - PCOS related','Ovulation induction',                          'Clomiphene Citrate 50mg, Gonadotropins',     '2024-12-16'),
(17, 17, 14, 'Primary Open-Angle Glaucoma',       'Laser trabeculoplasty consideration',           'Timolol 0.5% eye drops, Latanoprost',        '2024-12-17'),
(18, 18, 16, 'Chronic Sinusitis',                 'Nasal irrigation, avoid allergens',             'Fluticasone nasal spray, Montelukast',       '2024-12-18');

-- =============================================================
-- SAMPLE DATA — Billing (18 rows)
-- =============================================================
INSERT INTO Billing (patient_id, appointment_id, consultation_fee, medicine_cost, test_cost, other_charges, payment_status, payment_method, bill_date) VALUES
(1,  1,  800.00,  350.00,  1200.00, 100.00, 'Paid',    'Card',      '2024-11-01'),
(2,  2,  700.00,  200.00,  1500.00, 100.00, 'Paid',    'UPI',       '2024-11-02'),
(3,  3,  750.00,  300.00,   800.00, 100.00, 'Paid',    'Cash',      '2024-11-03'),
(4,  4,  600.00,  250.00,   500.00,  50.00, 'Paid',    'Insurance', '2024-11-04'),
(5,  5,  500.00,  150.00,   600.00,  50.00, 'Paid',    'UPI',       '2024-11-05'),
(6,  6,  700.00,  400.00,   900.00, 100.00, 'Paid',    'Card',      '2024-11-06'),
(7,  7,  800.00,  200.00,   700.00,  50.00, 'Paid',    'Cash',      '2024-11-07'),
(8,  8,  500.00,  180.00,   400.00,  50.00, 'Paid',    'UPI',       '2024-11-08'),
(9,  9,  600.00,  250.00,  1000.00, 100.00, 'Paid',    'Card',      '2024-11-09'),
(10, 10, 900.00,  300.00,  2000.00, 200.00, 'Partial', 'Insurance', '2024-11-10'),
(11, 11, 800.00,  180.00,   600.00,  50.00, 'Paid',    'Card',      '2024-11-11'),
(12, 12, 700.00,  350.00,   800.00, 100.00, 'Paid',    'UPI',       '2024-11-12'),
(13, 13, 750.00,  400.00,  1200.00, 100.00, 'Paid',    'Insurance', '2024-11-13'),
(14, 14, 500.00,  200.00,   300.00,  50.00, 'Paid',    'Cash',      '2024-11-14'),
(15, 15, 500.00,  500.00,   400.00, 100.00, 'Paid',    'Card',      '2024-11-15'),
(16, 16, 800.00,  600.00,  1500.00, 200.00, 'Paid',    'Insurance', '2024-11-18'),
(17, 17, 700.00,  250.00,   500.00,  50.00, 'Paid',    'UPI',       '2024-11-19'),
(18, 18, 600.00,  300.00,   700.00, 100.00, 'Paid',    'Card',      '2024-11-20');

-- =============================================================
-- USEFUL VIEWS
-- =============================================================

-- Full appointment detail view
CREATE OR REPLACE VIEW v_appointment_details AS
SELECT
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    p.patient_id,
    p.first_name || ' ' || p.last_name  AS patient_name,
    p.phone                              AS patient_phone,
    d.doctor_id,
    'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
    d.specialization,
    dept.name                            AS department,
    a.reason,
    a.status,
    a.notes
FROM Appointment a
JOIN Patient    p    ON a.patient_id   = p.patient_id
JOIN Doctor     d    ON a.doctor_id    = d.doctor_id
JOIN Department dept ON d.department_id = dept.department_id;

-- Billing summary view
CREATE OR REPLACE VIEW v_billing_summary AS
SELECT
    b.bill_id,
    b.bill_date,
    p.first_name || ' ' || p.last_name AS patient_name,
    p.phone AS patient_phone,
    'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
    dept.name AS department,
    b.consultation_fee,
    b.medicine_cost,
    b.test_cost,
    b.other_charges,
    b.total_amount,
    b.payment_status,
    b.payment_method
FROM Billing b
JOIN Patient    p    ON b.patient_id    = p.patient_id
JOIN Appointment a  ON b.appointment_id = a.appointment_id
JOIN Doctor     d    ON a.doctor_id     = d.doctor_id
JOIN Department dept ON d.department_id = dept.department_id;

-- End of script
