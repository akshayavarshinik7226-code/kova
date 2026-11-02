from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session

from . import ensure_csrf
from .db import audit, get_db, utcnow
from .security import DUMMY_HASH, verify_password
from .users import public_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    row = get_db().execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (uid,)).fetchone()
    return row


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if current_user() is None:
            return jsonify(error="Sign in to continue."), 401
        return fn(*a, **kw)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = current_user()
        if user is None:
            return jsonify(error="Sign in to continue."), 401
        if user["role"] != "admin":
            return jsonify(error="Only administrators can do this."), 403
        return fn(*a, **kw)
    return wrapper


@bp.get("/me")
def me():
    csrf = ensure_csrf()
    user = current_user()
    return jsonify(user=public_user(user) if user else None, csrf=csrf)


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    db = get_db()
    ip = request.remote_addr
    generic = jsonify(error="Email or password is incorrect."), 401

    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user is None:
        verify_password(password, DUMMY_HASH)  # equalise timing
        audit("login.failed", target=email, ip=ip, detail="unknown email")
        return generic

    now = datetime.now(timezone.utc)
    if user["locked_until"] and datetime.fromisoformat(user["locked_until"]) > now:
        audit("login.blocked", actor_id=user["id"], ip=ip, detail="account locked")
        minutes = current_app.config["LOGIN_LOCK_MINUTES"]
        return jsonify(error=f"Too many failed attempts. Try again in {minutes} minutes."), 429

    if not user["is_active"] or not verify_password(password, user["password_hash"]):
        failures = user["failed_logins"] + 1
        locked = None
        if failures >= current_app.config["LOGIN_MAX_FAILURES"]:
            locked = (now + timedelta(minutes=current_app.config["LOGIN_LOCK_MINUTES"])).isoformat(timespec="seconds")
            failures = 0
        db.execute("UPDATE users SET failed_logins=?, locked_until=? WHERE id=?", (failures, locked, user["id"]))
        db.commit()
        audit("login.failed", actor_id=user["id"], ip=ip, detail="locked" if locked else "bad password")
        return generic

    db.execute("UPDATE users SET failed_logins=0, locked_until=NULL, last_login_at=? WHERE id=?", (utcnow(), user["id"]))
    db.commit()
    session.clear()  # prevent session fixation
    session["uid"] = user["id"]
    csrf = ensure_csrf()
    audit("login.ok", actor_id=user["id"], ip=ip)
    return jsonify(user=public_user(user), csrf=csrf)


@bp.post("/logout")
def logout():
    user = current_user()
    if user:
        audit("logout", actor_id=user["id"], ip=request.remote_addr)
    session.clear()
    return jsonify(ok=True, csrf=ensure_csrf())
