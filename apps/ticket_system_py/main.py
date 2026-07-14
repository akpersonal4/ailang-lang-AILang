"""Ticket Management System CLI."""

import json
import sys
from pathlib import Path

import storage
import user
import ticket
import comment
import audit_log
import csv_ops

SESSION_FILE = Path("data/session.json")


def session_load() -> dict:
    if not SESSION_FILE.exists():
        return {}
    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def session_save(user_id: int, username: str) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"user_id": user_id, "username": username}, f)


def session_clear() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def session_get_user_id() -> int:
    s = session_load()
    return s.get("user_id", 0)


def require_login() -> int:
    uid = session_get_user_id()
    if uid == 0:
        print("Error: Not logged in. Use 'login <username> <password>' first.")
    return uid


def require_role(action: str) -> int:
    uid = require_login()
    if uid == 0:
        return 0
    if not user.has_permission(uid, action):
        print(f"Error: Insufficient permissions for {action}")
        return 0
    return uid


def cmd_register(args):
    if len(args) < 4:
        print("Usage: register <username> <email> <password>")
        return
    u = user.create(args[1], args[2], args[3])
    if not u:
        print("Error: Username or email already exists.")
        return
    print(f"User registered: {args[1]} (ID: {u['id']})")


def cmd_login(args):
    if len(args) < 3:
        print("Usage: login <username> <password>")
        return
    u = user.authenticate(args[1], args[2])
    if not u:
        print("Error: Invalid username or password.")
        return
    session_save(u["id"], args[1])
    print(f"Logged in as {args[1]} (role: {u['role']})")


def cmd_logout(args):
    uid = require_login()
    if uid == 0:
        return
    s = session_load()
    session_clear()
    print(f"Logged out {s.get('username', '')}")


def cmd_create_ticket(args):
    uid = require_role("create_ticket")
    if uid == 0:
        return
    if len(args) < 5:
        print("Usage: create-ticket <title> <priority> <category> <description>")
        return
    t = ticket.create(args[1], args[2], args[3], args[4], uid)
    audit_log.add(t["id"], uid, "created", "", args[1])
    print(f"Ticket created: ID {t['id']}")


def cmd_update_ticket(args):
    if len(args) < 4:
        print("Usage: update-ticket <id> <field> <value>")
        return
    ticket_id = int(args[1])
    field, value = args[2], args[3]
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    uid = require_login()
    if uid == 0:
        return
    if not user.has_permission(uid, "update_any_ticket"):
        if not user.has_permission_on_ticket(uid, "update_own_ticket", t):
            print("Error: Cannot update this ticket.")
            return
    old_value = str(t.get(field, ""))
    ticket.update(ticket_id, field, value)
    audit_log.add(ticket_id, uid, "updated", old_value, value)
    print(f"Ticket {ticket_id} updated: {field} = {value}")


def cmd_assign_ticket(args):
    uid = require_role("assign_ticket")
    if uid == 0:
        return
    if len(args) < 3:
        print("Usage: assign-ticket <id> <username>")
        return
    ticket_id = int(args[1])
    assignee = user.find_by_username(args[2])
    if not assignee:
        print("Error: User not found.")
        return
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    old_assignee = str(t.get("assignee_id", 0))
    ticket.assign(ticket_id, assignee["id"])
    audit_log.add(ticket_id, uid, "assigned", old_assignee, args[2])
    print(f"Ticket {ticket_id} assigned to {args[2]}")


def cmd_resolve_ticket(args):
    uid = require_role("resolve_ticket")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: resolve-ticket <id>")
        return
    ticket_id = int(args[1])
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    old_status = t["status"]
    ticket.set_status(ticket_id, "resolved")
    audit_log.add(ticket_id, uid, "status_changed", old_status, "resolved")
    print(f"Ticket {ticket_id} resolved.")


def cmd_close_ticket(args):
    uid = require_role("close_ticket")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: close-ticket <id>")
        return
    ticket_id = int(args[1])
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    old_status = t["status"]
    ticket.set_status(ticket_id, "closed")
    audit_log.add(ticket_id, uid, "status_changed", old_status, "closed")
    print(f"Ticket {ticket_id} closed.")


def cmd_reopen_ticket(args):
    uid = require_role("reopen_ticket")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: reopen-ticket <id>")
        return
    ticket_id = int(args[1])
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    old_status = t["status"]
    ticket.set_status(ticket_id, "open")
    audit_log.add(ticket_id, uid, "status_changed", old_status, "open")
    print(f"Ticket {ticket_id} reopened.")


def cmd_add_comment(args):
    uid = require_role("add_comment")
    if uid == 0:
        return
    if len(args) < 3:
        print("Usage: add-comment <ticket_id> <content>")
        return
    ticket_id = int(args[1])
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    comment.create(ticket_id, uid, args[2])
    audit_log.add(ticket_id, uid, "commented", "", args[2])
    print(f"Comment added to ticket {ticket_id}")


def cmd_view_ticket(args):
    uid = require_role("view_ticket")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: view-ticket <id>")
        return
    ticket_id = int(args[1])
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    print(f"--- Ticket {ticket_id} ---")
    print(f"Title: {t['title']}")
    print(f"Status: {t['status']}")
    print(f"Priority: {t['priority']}")
    print(f"Category: {t['category']}")
    print(f"Creator ID: {t['creator_id']}")
    print(f"Assignee ID: {t['assignee_id']}")
    print(f"Description: {t['description']}")
    print(f"Created: {t['created_at']}")
    comments = comment.list_by_ticket(ticket_id)
    if comments:
        print(f"--- Comments ({len(comments)}) ---")
        for c in comments:
            print(f"[{c['author_id']}] {c['content']}")


def cmd_search_tickets(args):
    uid = require_role("search_tickets")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: search-tickets <query>")
        return
    results = ticket.search(args[1])
    print(f"Found {len(results)} tickets matching '{args[1]}'")
    for t in results:
        print(f"  [{t['id']}] {t['title']} ({t['status']}, {t['priority']})")


def cmd_filter_tickets(args):
    uid = require_role("search_tickets")
    if uid == 0:
        return
    if len(args) < 3:
        print("Usage: filter-tickets <field> <value>")
        return
    results = ticket.filter_by(args[1], args[2])
    print(f"Found {len(results)} tickets with {args[1]} = {args[2]}")
    for t in results:
        print(f"  [{t['id']}] {t['title']} ({t['status']})")


def cmd_my_tickets(args):
    uid = require_role("view_ticket")
    if uid == 0:
        return
    results = ticket.list_by_user(uid)
    print(f"Tickets assigned to you: {len(results)}")
    for t in results:
        print(f"  [{t['id']}] {t['title']} ({t['status']}, {t['priority']})")


def cmd_report_status(args):
    uid = require_role("view_reports")
    if uid == 0:
        return
    counts = ticket.count_by_status()
    print("--- Status Report ---")
    print(f"Open: {counts['open']}")
    print(f"In Progress: {counts['in_progress']}")
    print(f"Resolved: {counts['resolved']}")
    print(f"Closed: {counts['closed']}")


def cmd_report_priority(args):
    uid = require_role("view_reports")
    if uid == 0:
        return
    counts = ticket.count_by_priority()
    print("--- Priority Report ---")
    print(f"Low: {counts['low']}")
    print(f"Medium: {counts['medium']}")
    print(f"High: {counts['high']}")
    print(f"Critical: {counts['critical']}")


def cmd_report_agent(args):
    uid = require_role("view_reports")
    if uid == 0:
        return
    counts = ticket.count_by_agent()
    tickets = ticket.list_all()
    print("--- Agent Report ---")
    print(f"Total tickets: {len(tickets)}")
    print("Tickets by assignee ID:")
    for aid, cnt in counts.items():
        print(f"  Agent {aid}: {cnt}")


def cmd_report_daily(args):
    uid = require_role("view_reports")
    if uid == 0:
        return
    import time
    now = int(time.time())
    seven_days = 604800
    tickets = ticket.list_all()
    created = sum(1 for t in tickets if now - t["created_at"] < seven_days)
    print("--- Daily Report (last 7 days) ---")
    print(f"Created: {created}")


def cmd_export_csv(args):
    uid = require_role("export_csv")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: export-csv <filename>")
        return
    if csv_ops.export_tickets(args[1]):
        print(f"Exported to {args[1]}")
    else:
        print("Error: Export failed.")


def cmd_import_csv(args):
    uid = require_role("import_csv")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: import-csv <filename>")
        return
    imported = csv_ops.import_tickets(args[1])
    print(f"Imported {imported} tickets from {args[1]}")


def cmd_list_users(args):
    uid = require_role("manage_users")
    if uid == 0:
        return
    users = user.list_all()
    print(f"--- Users ({len(users)}) ---")
    for u in users:
        print(f"  [{u['id']}] {u['username']} ({u['role']})")


def cmd_set_role(args):
    uid = require_role("manage_users")
    if uid == 0:
        return
    if len(args) < 3:
        print("Usage: set-role <username> <role>")
        print("Roles: admin, manager, agent, viewer")
        return
    target = user.find_by_username(args[1])
    if not target:
        print("Error: User not found.")
        return
    user.set_role(target["id"], args[2])
    print(f"Set {args[1]} role to {args[2]}")


def cmd_delete_ticket(args):
    uid = require_role("delete_ticket")
    if uid == 0:
        return
    if len(args) < 2:
        print("Usage: delete-ticket <id>")
        return
    ticket_id = int(args[1])
    t = ticket.find_by_id(ticket_id)
    if not t:
        print("Error: Ticket not found.")
        return
    ticket.delete(ticket_id)
    audit_log.add(ticket_id, uid, "deleted", t["title"], "")
    print(f"Ticket {ticket_id} deleted.")


def cmd_escalate(args):
    uid = require_role("view_reports")
    if uid == 0:
        return
    sla_count = ticket.escalate_sla()
    unassigned_count = ticket.escalate_unassigned()
    print("Escalation complete:")
    print(f"  SLA breaches escalated: {sla_count}")
    print(f"  Unassigned critical: {unassigned_count}")


def cmd_help(args):
    print("Available commands:")
    print("  register <username> <email> <password>")
    print("  login <username> <password>")
    print("  logout")
    print("  create-ticket <title> <priority> <category> <description>")
    print("  update-ticket <id> <field> <value>")
    print("  assign-ticket <id> <username>")
    print("  resolve-ticket <id>")
    print("  close-ticket <id>")
    print("  reopen-ticket <id>")
    print("  add-comment <ticket_id> <content>")
    print("  view-ticket <id>")
    print("  search-tickets <query>")
    print("  filter-tickets <field> <value>")
    print("  my-tickets")
    print("  report-status")
    print("  report-priority")
    print("  report-agent")
    print("  report-daily")
    print("  export-csv <filename>")
    print("  import-csv <filename>")
    print("  list-users")
    print("  set-role <username> <role>")
    print("  delete-ticket <id>")
    print("  escalate")
    print("  help")


COMMANDS = {
    "register": cmd_register,
    "login": cmd_login,
    "logout": cmd_logout,
    "create-ticket": cmd_create_ticket,
    "update-ticket": cmd_update_ticket,
    "assign-ticket": cmd_assign_ticket,
    "resolve-ticket": cmd_resolve_ticket,
    "close-ticket": cmd_close_ticket,
    "reopen-ticket": cmd_reopen_ticket,
    "add-comment": cmd_add_comment,
    "view-ticket": cmd_view_ticket,
    "search-tickets": cmd_search_tickets,
    "filter-tickets": cmd_filter_tickets,
    "my-tickets": cmd_my_tickets,
    "report-status": cmd_report_status,
    "report-priority": cmd_report_priority,
    "report-agent": cmd_report_agent,
    "report-daily": cmd_report_daily,
    "export-csv": cmd_export_csv,
    "import-csv": cmd_import_csv,
    "list-users": cmd_list_users,
    "set-role": cmd_set_role,
    "delete-ticket": cmd_delete_ticket,
    "escalate": cmd_escalate,
    "help": cmd_help,
}


def main():
    storage.DATA_DIR = Path("data")
    args = sys.argv[1:]
    if not args:
        print("Ticket Management System v1.0 (Python)")
        print("Usage: python main.py <command> [args...]")
        print("Type 'help' for available commands.")
        return
    command = args[0]
    if command in COMMANDS:
        COMMANDS[command](args)
    else:
        print(f"Unknown command: {command}. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
