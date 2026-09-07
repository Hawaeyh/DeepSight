#!/usr/bin/env python3
import argparse
import getpass
import re
import sys
from pathlib import Path

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import func, inspect


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or explicitly update a local DeepSight administrator."
    )
    parser.add_argument("--email", help="Administrator email; prompted when omitted.")
    parser.add_argument("--name", default="Administrator", help="Local display name.")
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Explicitly replace credentials and restore the admin role for an existing user.",
    )
    return parser.parse_args()


def validate_email(value: str) -> str:
    try:
        return str(TypeAdapter(EmailStr).validate_python(value.strip())).lower()
    except ValidationError as error:
        raise ValueError("Enter a valid email address.") from error


def validate_password(password: str) -> None:
    encoded_length = len(password.encode("utf-8"))
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")
    if encoded_length > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes.")
    requirements = [
        (r"[a-z]", "a lowercase letter"),
        (r"[A-Z]", "an uppercase letter"),
        (r"\d", "a number"),
        (r"[^A-Za-z0-9]", "a symbol"),
    ]
    missing = [description for pattern, description in requirements if not re.search(pattern, password)]
    if missing:
        raise ValueError("Password must include " + ", ".join(missing) + ".")


def prompt_password() -> str:
    password = getpass.getpass("Password: ")
    validate_password(password)
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("Password confirmation does not match.")
    return password


def main() -> int:
    args = parse_args()
    try:
        email = validate_email(args.email or input("Administrator email: "))
        password = prompt_password()
    except (EOFError, KeyboardInterrupt):
        print("Administrator creation cancelled.")
        return 130
    except ValueError as error:
        print(f"Administrator creation failed: {error}")
        return 2

    if not inspect(engine).has_table("users"):
        print("Administrator creation failed: users table is missing. Run init_database.py first.")
        return 2

    db = SessionLocal()
    try:
        user = db.query(User).filter(func.lower(User.email) == email).first()
        if user is not None and not args.update_existing:
            print("Administrator creation refused: user already exists. Use --update-existing explicitly.")
            return 3

        password_hash = hash_password(password)
        if user is None:
            user = User(
                email=email,
                full_name=args.name.strip() or "Administrator",
                password=password_hash,
                role="admin",
                is_active=True,
            )
            db.add(user)
            action = "created"
        else:
            user.full_name = args.name.strip() or user.full_name
            user.password = password_hash
            user.role = "admin"
            user.is_active = True
            action = "updated"
        db.commit()
        print(f"Local administrator {action}: {email}")
        print("This command does not create or update a Firebase Authentication user.")
        return 0
    except Exception as error:
        db.rollback()
        print(f"Administrator creation failed: {error}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
