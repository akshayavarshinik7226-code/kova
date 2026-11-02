import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path=None):
    """Tiny .env loader (no extra dependency). Real environment wins."""
    path = Path(path or ROOT / ".env")
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _secret_key(instance_dir: Path, env: str) -> str:
    configured = os.environ.get("KOVA_SECRET_KEY", "").strip()
    if configured:
        return configured
    if env == "production":
        raise RuntimeError("KOVA_SECRET_KEY must be set when KOVA_ENV=production")
    key_file = instance_dir / "secret_key"
    if key_file.is_file():
        return key_file.read_text(encoding="utf-8").strip()
    instance_dir.mkdir(parents=True, exist_ok=True)
    key = secrets.token_hex(32)
    key_file.write_text(key, encoding="utf-8")
    return key


def build_config() -> dict:
    env = os.environ.get("KOVA_ENV", "development").lower()
    instance = Path(os.environ.get("KOVA_INSTANCE_DIR") or ROOT / "instance")
    instance.mkdir(parents=True, exist_ok=True)
    return {
        "ENV_NAME": env,
        "PLATFORM_NAME": os.environ.get("KOVA_PLATFORM_NAME", "KOVA"),
        "SECRET_KEY": _secret_key(instance, env),
        "DATABASE": str(instance / "kova.db"),
        "INSTANCE_DIR": str(instance),
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": os.environ.get("KOVA_COOKIE_SECURE", "0") == "1",
        "COOLIFY_URL": os.environ.get("COOLIFY_URL", "").strip().rstrip("/"),
        "COOLIFY_TOKEN": os.environ.get("COOLIFY_TOKEN", "").strip(),
        "LOGIN_MAX_FAILURES": 5,
        "LOGIN_LOCK_MINUTES": 15,
        "VERSION": "0.1.0",
    }
