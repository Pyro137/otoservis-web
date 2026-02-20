# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for OtoServis Pro.

Usage (on Windows):
    pyinstaller otoservis.spec

Produces: dist/OtoServis.exe
"""

import os
import sys

block_cipher = None

# Absolute path to project root
PROJECT_DIR = os.path.abspath(os.path.dirname(SPEC))

a = Analysis(
    [os.path.join(PROJECT_DIR, 'launcher.py')],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        # Templates
        (os.path.join(PROJECT_DIR, 'app', 'templates'), os.path.join('app', 'templates')),
        # Static files (CSS, JS)
        (os.path.join(PROJECT_DIR, 'app', 'static'), os.path.join('app', 'static')),
    ],
    hiddenimports=[
        # FastAPI / Starlette / Uvicorn
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'starlette.responses',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.sessions',
        'starlette.staticfiles',
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.responses',

        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.sql.default_comparator',

        # Jinja2
        'jinja2',
        'jinja2.ext',

        # Pydantic
        'pydantic',
        'pydantic_settings',

        # Security
        'bcrypt',
        'itsdangerous',

        # PDF generation
        'reportlab',
        'reportlab.lib',
        'reportlab.pdfgen',
        'reportlab.platypus',
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'reportlab.pdfbase.pdfmetrics',

        # Other
        'multipart',
        'aiofiles',

        # PyWebView
        'webview',
        'webview.platforms.edgechromium',
        'webview.platforms.winforms',
        'webview.platforms.gtk',

        # Windows COM/CLR (needed by pywebview on Windows)
        'pythoncom',
        'pywintypes',
        'clr',
        'clr_loader',

        # App modules
        'app',
        'app.main',
        'app.core',
        'app.core.config',
        'app.core.database',
        'app.core.dependencies',
        'app.core.enums',
        'app.core.security',
        'app.models',
        'app.models.base',
        'app.models.user',
        'app.models.customer',
        'app.models.vehicle',
        'app.models.work_order',
        'app.models.work_order_item',
        'app.models.part',
        'app.models.payment',
        'app.models.invoice',
        'app.models.audit_log',
        'app.repositories',
        'app.services',
        'app.routers',
        'app.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OtoServis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # --noconsole
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',      # Uncomment when you have an icon file
)
