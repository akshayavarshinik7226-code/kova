import hmac
import os
import secrets

from flask import Flask, jsonify, request, session

from . import db as dbmod
from .config import build_config, load_dotenv
from .users import ValidationError, create_user

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.update(build_config())
    if test_config:
        app.config.update(test_config)

    dbmod.migrate(app.config["DATABASE"])
    app.teardown_appcontext(dbmod.close_db)
    _bootstrap_admin(app)

    from .auth import bp as auth_bp
    from .pages import bp as pages_bp
    from .status import bp as status_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(pages_bp)

    @app.before_request
    def csrf_protect():
        if request.path.startswith("/api/") and request.method not in SAFE_METHODS:
            sent = request.headers.get("X-CSRF-Token", "")
            expected = session.get("csrf", "")
            if not expected or not hmac.compare_digest(sent, expected):
                return jsonify(error="Your session expired. Reload the page and try again."), 403

    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found."), 404
        return "Not found", 404

    @app.errorhandler(405)
    def not_allowed(_e):
        return jsonify(error="Method not allowed."), 405

    return app


def ensure_csrf() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def _bootstrap_admin(app: Flask):
    """Create the first admin from env vars only when no users exist."""
    email = os.environ.get("KOVA_ADMIN_EMAIL", "").strip()
    password = os.environ.get("KOVA_ADMIN_PASSWORD", "")
    if not email or not password:
        return
    conn = dbmod.connect(app.config["DATABASE"])
    try:
        if conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            return
        try:
            create_user(conn, email, os.environ.get("KOVA_ADMIN_NAME", "Administrator"), password, "admin")
            app.logger.info("Bootstrap admin created for %s", email)
        except ValidationError as exc:
            app.logger.error("Bootstrap admin NOT created: %s", exc)
    finally:
        conn.close()
