"""Operator CLI.  Usage:
    python manage.py init-db
    python manage.py create-admin --email you@example.com --name "Your Name"
"""
import argparse
import getpass
import sys

from slipway import create_app
from slipway.db import connect, migrate
from slipway.users import ValidationError, create_user


def main():
    parser = argparse.ArgumentParser(prog="manage.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db")
    p = sub.add_parser("create-admin")
    p.add_argument("--email", required=True)
    p.add_argument("--name", default="Administrator")
    args = parser.parse_args()

    app = create_app()
    path = app.config["DATABASE"]
    if args.cmd == "init-db":
        print(f"Database ready at {path} (schema version {migrate(path)})")
        return 0
    password = getpass.getpass("Password (min 12 chars): ")
    if password != getpass.getpass("Repeat password: "):
        print("Passwords do not match.")
        return 1
    conn = connect(path)
    try:
        create_user(conn, args.email, args.name, password, "admin")
    except ValidationError as exc:
        print(f"Not created: {exc}")
        return 1
    finally:
        conn.close()
    print(f"Admin {args.email} created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
