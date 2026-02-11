import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.database import init_db
from app.core.security import hash_password
from app.core.enums import UserRole

# Import routers
from app.routers import auth, dashboard, customers, vehicles, work_orders, parts, payments, backup, reports

logger = logging.getLogger(__name__)

# Turkish-friendly error messages
ERROR_MESSAGES = {
    "int_parsing": "Geçerli bir tam sayı giriniz",
    "float_parsing": "Geçerli bir sayı giriniz",
    "missing": "Bu alan zorunludur",
    "string_too_short": "Bu alan çok kısa",
    "string_too_long": "Bu alan çok uzun",
    "value_error": "Geçersiz değer",
    "enum": "Geçersiz seçenek",
}

FIELD_NAMES = {
    "part_id": "Parça",
    "customer_id": "Müşteri",
    "vehicle_id": "Araç",
    "technician_id": "Teknisyen",
    "quantity": "Miktar",
    "unit_price": "Birim Fiyat",
    "discount": "İskonto",
    "amount": "Tutar",
    "km_in": "Giriş KM",
    "km_out": "Çıkış KM",
    "year": "Yıl",
    "current_km": "Güncel KM",
    "stock_quantity": "Stok Miktarı",
    "critical_level": "Kritik Seviye",
    "purchase_price": "Alış Fiyatı",
    "sale_price": "Satış Fiyatı",
    "full_name": "Ad Soyad",
    "phone": "Telefon",
    "stock_code": "Stok Kodu",
    "name": "Parça Adı",
    "plate_number": "Plaka",
    "brand": "Marka",
    "model": "Model",
    "description": "Açıklama",
    "type": "Tür",
    "payment_method": "Ödeme Yöntemi",
}


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

    # Session middleware
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=settings.SESSION_MAX_AGE)

    # Static files
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

    # Templates
    templates = Environment(
        loader=FileSystemLoader(str(settings.TEMPLATE_DIR)),
        autoescape=True,
    )
    app.state.templates = TemplateEngine(templates)

    # Register routers
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(customers.router)
    app.include_router(vehicles.router)
    app.include_router(work_orders.router)
    app.include_router(parts.router)
    app.include_router(payments.router)
    app.include_router(backup.router)
    app.include_router(reports.router)

    @app.on_event("startup")
    async def startup():
        init_db()
        _seed_admin()

    # ── Global Validation Error Handler ──
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Convert FastAPI validation errors to user-friendly Turkish toasts."""
        errors = []
        for err in exc.errors():
            field_name = err.get("loc", ["", ""])[-1]
            field_label = FIELD_NAMES.get(str(field_name), str(field_name))
            msg = ERROR_MESSAGES.get(err.get("type", ""), err.get("msg", "Geçersiz değer"))
            errors.append(f"<b>{field_label}</b>: {msg}")

        error_html = "<br>".join(errors)
        referer = request.headers.get("referer", "/")

        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Hata</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-[Inter]">
<div id="toast-overlay" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.3);z-index:9998;display:flex;align-items:center;justify-content:center;">
    <div class="bg-white rounded-2xl shadow-2xl border border-red-100 p-8 max-w-md w-full mx-4 animate-bounce-in" style="animation:popIn .3s ease-out">
        <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                </svg>
            </div>
            <div class="flex-1">
                <h3 class="text-lg font-bold text-gray-900 mb-2">Form Hatası</h3>
                <div class="text-sm text-gray-600 leading-relaxed">{error_html}</div>
            </div>
        </div>
        <div class="mt-6 flex justify-end">
            <a href="{referer}" class="bg-red-600 hover:bg-red-700 text-white font-semibold py-2.5 px-6 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md text-sm">
                ← Geri Dön
            </a>
        </div>
    </div>
</div>
<style>
@keyframes popIn {{ from {{ transform: scale(0.8); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
</style>
</body></html>"""
        return HTMLResponse(content=html, status_code=422)

    # ── Global Exception Handler ──
    @app.exception_handler(Exception)
    async def global_error_handler(request: Request, exc: Exception):
        """Catch-all for unhandled exceptions — show a toast instead of raw traceback."""
        logger.exception(f"Unhandled error: {exc}")
        referer = request.headers.get("referer", "/")
        error_msg = str(exc)
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."

        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Hata</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-[Inter]">
<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.3);z-index:9998;display:flex;align-items:center;justify-content:center;">
    <div class="bg-white rounded-2xl shadow-2xl border border-amber-100 p-8 max-w-md w-full mx-4" style="animation:popIn .3s ease-out">
        <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                </svg>
            </div>
            <div class="flex-1">
                <h3 class="text-lg font-bold text-gray-900 mb-2">İşlem Hatası</h3>
                <p class="text-sm text-gray-600">{error_msg}</p>
            </div>
        </div>
        <div class="mt-6 flex justify-end">
            <a href="{referer}" class="bg-amber-600 hover:bg-amber-700 text-white font-semibold py-2.5 px-6 rounded-xl transition-all duration-200 shadow-sm text-sm">
                ← Geri Dön
            </a>
        </div>
    </div>
</div>
<style>
@keyframes popIn {{ from {{ transform: scale(0.8); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
</style>
</body></html>"""
        return HTMLResponse(content=html, status_code=500)

    return app


class TemplateEngine:
    """Wraps Jinja2 Environment to provide TemplateResponse compatible with FastAPI."""

    def __init__(self, env: Environment):
        self.env = env

    def TemplateResponse(self, template_name: str, context: dict, status_code: int = 200):
        from fastapi.responses import HTMLResponse
        template = self.env.get_template(template_name)
        html = template.render(**context)
        return HTMLResponse(content=html, status_code=status_code)


def _seed_admin():
    """Create default admin user if not exists."""
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                full_name="Sistem Yöneticisi",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ Varsayılan admin kullanıcısı oluşturuldu (admin / admin123)")
    finally:
        db.close()


app = create_app()
