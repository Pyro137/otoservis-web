You are a senior software architect and backend engineer.

We are building a PROFESSIONAL, PRODUCTION-QUALITY Auto Service Management System.

This system must be architecturally clean, modular, scalable, and ready to evolve into a commercial SaaS in the future.

==================================================
TECH STACK
==================================================

Backend:
- FastAPI
- SQLAlchemy 2.0 (Declarative)
- SQLite (initially, but architecture must allow PostgreSQL migration)
- Alembic for migrations
- Pydantic v2
- Jinja2 Templates
- TailwindCSS (CDN)
- Uvicorn

PDF:
- ReportLab (custom invoice design)

Security:
- bcrypt password hashing
- Session-based authentication
- Role-based access (admin, technician)

Architecture:
- Clean Architecture principles
- Service Layer pattern
- Repository abstraction
- Dependency Injection
- Strict separation of concerns

==================================================
CORE ARCHITECTURAL RULES
==================================================

1. No business logic inside routers.
2. All business logic must be in service layer.
3. Database operations handled via repositories.
4. Use type hints everywhere.
5. Use Decimal for monetary values.
6. Use enums for status fields.
7. Add proper DB indexes.
8. Use soft delete (is_deleted flag).
9. Add created_at and updated_at in all tables.
10. Add audit logging system.

==================================================
PROJECT STRUCTURE
==================================================

app/
    main.py
    core/
        config.py
        security.py
        database.py
        enums.py
    models/
    schemas/
    repositories/
    services/
    routers/
    templates/
    static/
    utils/
        pdf_generator.py
        backup_service.py
        audit_logger.py

==================================================
DOMAIN MODEL (PROFESSIONAL LEVEL)
==================================================

1) User
- id
- username
- hashed_password
- role (admin, technician)
- is_active
- created_at
- updated_at

2) Customer
- id
- type (individual, corporate)
- full_name
- company_name
- tax_number
- tax_office
- phone
- email
- address
- city
- notes
- total_debt (derived but stored)
- is_deleted
- created_at
- updated_at

Indexes:
- phone
- tax_number

3) Vehicle
- id
- customer_id (FK)
- plate_number (unique)
- brand
- model
- year
- fuel_type
- transmission_type
- chassis_number
- engine_number
- current_km
- inspection_expiry_date
- insurance_expiry_date
- notes
- is_deleted
- created_at
- updated_at

Indexes:
- plate_number
- chassis_number

4) WorkOrder
- id
- work_order_number (unique)
- vehicle_id
- customer_id
- technician_id
- complaint_description
- internal_notes
- km_in
- km_out
- fuel_level
- status (pending, approved, in_progress, completed, delivered, cancelled)
- labor_total
- parts_total
- discount_total
- subtotal
- vat_rate
- vat_total
- grand_total
- created_at
- completed_at
- updated_at
- is_deleted

Indexes:
- status
- created_at

5) WorkOrderItem
- id
- work_order_id
- type (part, labor)
- part_id (nullable if labor)
- description
- quantity
- unit_price
- discount
- vat_rate
- total_price
- created_at
- updated_at

6) Part (Inventory)
- id
- stock_code
- name
- category
- purchase_price
- sale_price
- stock_quantity
- critical_level
- supplier_name
- is_active
- created_at
- updated_at

Constraints:
- Prevent negative stock
- Reduce stock when part added to completed work order

7) Payment
- id
- work_order_id
- amount
- payment_method (cash, card, transfer)
- payment_date
- reference_number
- created_at

8) Invoice
- id
- invoice_number
- work_order_id (unique)
- issue_date
- due_date
- payment_status (unpaid, partial, paid)
- subtotal
- vat_total
- grand_total
- created_at

9) AuditLog
- id
- user_id
- entity_name
- entity_id
- action (create, update, delete)
- timestamp
- changes_json

==================================================
FINANCIAL RULES
==================================================

- All money fields must use Decimal.
- Totals must be calculated in service layer.
- Never trust frontend totals.
- Recalculate totals before saving.
- VAT must be configurable globally.

==================================================
DASHBOARD REQUIREMENTS
==================================================

Dashboard must display:
- Active work orders
- Monthly revenue
- Today revenue
- Outstanding payments
- Low stock warnings
- Recently completed jobs

==================================================
REPORTING
==================================================

Generate reports:
- Revenue by date range
- Technician performance
- Most serviced vehicles
- Most used parts
- Debt summary by customer

==================================================
PDF INVOICE
==================================================

Generate professional PDF invoice including:
- Company logo
- Customer details
- Vehicle details
- Itemized table
- VAT breakdown
- Payment summary
- Signature area

Must be downloadable and printable.

==================================================
BACKUP & DATA SAFETY
==================================================

- Manual backup button
- Automatic daily backup
- Store backups with timestamps
- Restore functionality

==================================================
SECURITY
==================================================

- Protect all routes
- CSRF protection
- Input validation
- Role-based permissions
- Session expiration

==================================================
PERFORMANCE
==================================================

- Add DB indexes properly
- Avoid N+1 queries
- Use eager loading where needed
- Optimize list pages with pagination

==================================================
DEVELOPMENT STEPS
==================================================

1) Generate database models
2) Create Alembic migrations
3) Create repository layer
4) Implement service layer
5) Implement authentication
6) Implement core CRUD modules
7) Add inventory logic
8) Implement financial calculations
9) Add dashboard
10) Add reporting
11) Add PDF system
12) Add backup & audit log

Code must be modular, production-quality, and ready to migrate to PostgreSQL later without major refactoring.

Do not skip architectural principles.
