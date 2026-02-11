You are a senior DevOps engineer and software architect.

The Auto Service Management System project is fully completed.

Your task is to:

1) Audit the entire codebase
2) Refactor if necessary
3) Optimize for production
4) Prepare a Windows desktop build (.exe)
5) Create a clean distribution package

==================================================
GENERAL GOAL
==================================================

Convert this FastAPI + SQLite application into a production-ready Windows desktop application with the following characteristics:

- Single user
- Local execution
- No external server required
- Clean UI window (no browser address bar)
- Professional behavior
- Auto database handling
- Backup system included
- Ready for real-world workshop use

==================================================
STEP 1 — CODEBASE AUDIT
==================================================

- Ensure no business logic inside routers
- Validate all monetary fields use Decimal
- Ensure all totals are calculated in service layer
- Remove unused imports
- Add missing type hints
- Ensure proper exception handling
- Validate DB relationships
- Ensure no N+1 queries
- Ensure indexes exist where necessary
- Confirm soft delete implementation works

==================================================
STEP 2 — PRODUCTION CONFIG
==================================================

- Disable debug mode
- Add centralized logging system
- Add global error handler
- Add config class for:
    - Company name
    - VAT rate
    - Currency
    - Backup path

==================================================
STEP 3 — EMBEDDED DESKTOP VERSION
==================================================

Replace browser-based startup with:

- PyWebView window
- Embedded Chromium
- Custom window title: "Oto Servis Yönetim Sistemi"
- Fixed window size (1280x800)
- Disable resize if needed
- Clean application icon

==================================================
STEP 4 — DATABASE HANDLING
==================================================

- Ensure database.db is created automatically if missing
- Ensure migrations run automatically on first launch
- Store DB in:
    %APPDATA%/OtoServisApp/

NOT inside program folder.

==================================================
STEP 5 — BACKUP SYSTEM
==================================================

- Create automatic daily backup
- Store backups in:
    %APPDATA%/OtoServisApp/backups/
- Add manual backup trigger
- Use timestamp format:
    backup_YYYYMMDD_HHMMSS.db

==================================================
STEP 6 — BUILD PROCESS
==================================================

Use:

- PyInstaller
- --onefile
- --noconsole
- Custom icon
- Include hidden imports if required

Generate a working .spec file.

Ensure:
- Templates included
- Static files included
- No missing dependency at runtime

==================================================
STEP 7 — INSTALLER PACKAGE
==================================================

Prepare project for optional installer creation.

Structure final distribution folder:

/dist
    OtoServis.exe
    config.ini
    README.txt

README should include:
- First run instructions
- Backup info
- Database location
- How to restore backup

==================================================
STEP 8 — SECURITY HARDENING
==================================================

- Ensure passwords are hashed
- Ensure session timeout implemented
- Protect all routes
- Prevent direct DB tampering

==================================================
STEP 9 — FINAL VALIDATION CHECKLIST
==================================================

Verify:

[ ] Login works
[ ] Customer CRUD works
[ ] Vehicle CRUD works
[ ] Work order flow works
[ ] Stock decreases properly
[ ] Totals calculated correctly
[ ] Invoice PDF generated correctly
[ ] Payment system works
[ ] Dashboard loads fast
[ ] Backup works
[ ] App closes gracefully

==================================================
FINAL OUTPUT REQUIREMENT
==================================================

Provide:

1) Optimized entry-point file
2) PyWebView launcher file
3) PyInstaller command
4) Full .spec file
5) Folder structure
6) Build instructions
7) Common troubleshooting tips

Do not skip production best practices.
Make it stable and professional.
