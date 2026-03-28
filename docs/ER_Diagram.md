# Entity–Relationship Diagram — Hospital DBMS

## Entities & Relationships

```
┌─────────────────┐       ┌──────────────────────┐
│   Department    │ 1   N │       Doctor          │
│─────────────────│───────│──────────────────────│
│ department_id PK│       │ doctor_id          PK │
│ name            │       │ department_id      FK │
│ location        │       │ first_name, last_name │
│ phone           │       │ specialization        │
│ head_of_dept    │       │ email (UNIQUE)         │
└─────────────────┘       │ phone                 │
                          │ experience_yrs        │
                          │ available_days        │
                          └──────────┬────────────┘
                                     │ 1
                                     │
                                     │ N
              ┌──────────────────────▼────────────────────────┐
              │                 Appointment                    │
              │────────────────────────────────────────────── │
              │ appointment_id  PK                             │
              │ patient_id      FK ──────────────────────────►│
              │ doctor_id       FK                             │
              │ appointment_date                               │
              │ appointment_time                               │
              │ reason                                         │
              │ status  CHECK(Scheduled/Completed/Cancelled)   │
              └────────────┬───────────────┬──────────────────┘
                           │ 1             │ 1
                           │               │
                           │ 0..1          │ 0..1
             ┌─────────────▼──────┐ ┌─────▼────────────────┐
             │  Medical_Record    │ │      Billing          │
             │────────────────────│ │───────────────────────│
             │ record_id       PK │ │ bill_id            PK │
             │ appointment_id  FK │ │ appointment_id     FK │
             │ patient_id      FK │ │ patient_id         FK │
             │ doctor_id       FK │ │ consultation_fee      │
             │ diagnosis          │ │ medicine_cost         │
             │ treatment          │ │ test_cost             │
             │ prescription       │ │ other_charges         │
             │ follow_up_date     │ │ total_amount (STORED) │
             └────────────────────┘ │ payment_status        │
                                    │ payment_method        │
                                    └───────────────────────┘

┌──────────────────────────────────────┐
│              Patient                  │
│──────────────────────────────────────│
│ patient_id       PK                  │
│ first_name, last_name                │
│ date_of_birth                        │
│ gender  CHECK(Male/Female/Other)     │
│ blood_group                          │
│ phone                                │
│ email  (UNIQUE)                      │
│ address                              │
│ emergency_contact                    │
└──────────────────────────────────────┘
```

## Key Constraints

| Table | Constraint | Type |
|---|---|---|
| Doctor.email | Must be unique | UNIQUE |
| Patient.email | Must be unique | UNIQUE |
| Patient.gender | Only Male/Female/Other | CHECK |
| Appointment.status | Scheduled/Completed/Cancelled/No-Show | CHECK |
| Billing.payment_status | Pending/Paid/Partial/Waived | CHECK |
| Billing.total_amount | Auto-calculated | GENERATED ALWAYS AS |
| Medical_Record.appointment_id | One record per appointment | UNIQUE |
| Billing.appointment_id | One bill per appointment | UNIQUE |

## Cascade Rules

- Deleting a **Patient** → cascades to Appointment, Medical_Record, Billing
- Deleting an **Appointment** → cascades to Medical_Record, Billing
- Deleting a **Doctor** → cascades to Appointment, Medical_Record
- Deleting a **Department** → sets Doctor.department_id to NULL
