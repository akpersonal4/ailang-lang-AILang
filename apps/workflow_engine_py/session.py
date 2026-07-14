"""Session management via JSON file."""
import json
import os


SESSION_FILE = os.path.join(os.path.dirname(__file__), "data", "session.json")


def load():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "r") as f:
        content = f.read()
    if not content:
        return {}
    return json.loads(content)


def save(user_id, username):
    session = {"user_id": user_id, "username": username}
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)
    return True


def clear():
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        f.write("")
    return True


def get_user_id():
    session = load()
    return session.get("user_id", 0)
