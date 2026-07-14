"""User model with authentication and role-based permissions."""
import time
from . import storage

PERMISSIONS = {
    "admin": [
        "create_workflow", "delete_workflow", "list_workflows", "view_workflow",
        "create_instance", "view_instance", "transition", "set_data",
        "cancel_instance", "view_history", "report_workflow", "report_activity",
        "export_import", "manage_users",
    ],
    "operator": [
        "list_workflows", "view_workflow", "create_instance", "view_instance",
        "transition", "set_data", "view_history", "report_workflow",
        "report_activity",
    ],
    "viewer": [
        "list_workflows", "view_workflow", "view_instance", "view_history",
    ],
}


def check_permission(role, action):
    if role not in PERMISSIONS:
        return False
    return action in PERMISSIONS[role]


def create(username, email, password):
    users = storage.load("users")
    for u in users:
        if u["username"] == username or u["email"] == email:
            return False
    user = {
        "id": storage.next_id("users"),
        "username": username,
        "email": email,
        "password_hash": password,
        "role": "admin" if len(users) == 0 else "operator",
        "created_at": int(time.time()),
    }
    storage.append("users", user)
    return user


def find_by_username(username):
    users = storage.load("users")
    for u in users:
        if u["username"] == username:
            return u
    return False


def find_by_id(user_id):
    return storage.find_by_id("users", user_id)


def authenticate(username, password):
    user = find_by_username(username)
    if user is False:
        return False
    if user["password_hash"] == password:
        return user
    return False


def set_role(user_id, role):
    return storage.update_field("users", user_id, "role", role)


def list_all():
    return storage.load("users")


def has_permission(user_id, action):
    user = find_by_id(user_id)
    if user is False:
        return False
    return check_permission(user["role"], action)
