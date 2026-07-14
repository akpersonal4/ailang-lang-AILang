"""User model with authentication and role-based permissions."""

import hashlib
import time
from typing import Optional

import storage
from storage import load, save, append, update_field, next_id

PERMISSIONS = {
    "admin": {
        "create_ticket", "update_own_ticket", "update_any_ticket",
        "assign_ticket", "resolve_ticket", "close_ticket", "reopen_ticket",
        "add_comment", "view_ticket", "search_tickets", "view_reports",
        "export_csv", "import_csv", "delete_ticket", "manage_users",
    },
    "manager": {
        "create_ticket", "update_own_ticket", "update_any_ticket",
        "assign_ticket", "resolve_ticket", "close_ticket", "reopen_ticket",
        "add_comment", "view_ticket", "search_tickets", "view_reports",
        "export_csv", "import_csv",
    },
    "agent": {
        "create_ticket", "update_own_ticket",
        "resolve_ticket", "close_ticket", "reopen_ticket",
        "add_comment", "view_ticket", "search_tickets",
    },
    "viewer": {
        "view_ticket", "search_tickets",
    },
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create(username: str, email: str, password: str) -> Optional[dict]:
    users = load("users")
    for u in users:
        if u["username"] == username or u["email"] == email:
            return None
    user = {
        "id": next_id("users"),
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "role": "admin" if not users else "agent",
        "created_at": int(time.time()),
    }
    append("users", user)
    return user


def find_by_username(username: str) -> Optional[dict]:
    users = load("users")
    for u in users:
        if u["username"] == username:
            return u
    return None


def find_by_id(user_id: int) -> Optional[dict]:
    return storage.find_by_id("users", user_id)


def authenticate(username: str, password: str) -> Optional[dict]:
    user = find_by_username(username)
    if not user:
        return None
    if user["password_hash"] != hash_password(password):
        return None
    return user


def set_role(user_id: int, role: str) -> bool:
    return update_field("users", user_id, "role", role)


def list_all() -> list[dict]:
    return load("users")


def has_permission(user_id: int, action: str) -> bool:
    user = find_by_id(user_id)
    if not user:
        return False
    role = user["role"]
    return action in PERMISSIONS.get(role, set())


def has_permission_on_ticket(user_id: int, action: str, ticket: dict) -> bool:
    user = find_by_id(user_id)
    if not user:
        return False
    if user["role"] == "admin":
        return True
    if action == "update_own_ticket":
        if ticket.get("creator_id") == user_id:
            return True
        if user["role"] == "manager":
            return True
        return False
    return has_permission(user_id, action)
