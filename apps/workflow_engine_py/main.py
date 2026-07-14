"""CLI dispatch for workflow engine — 20 commands."""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apps.workflow_engine_py import storage
from apps.workflow_engine_py import user
from apps.workflow_engine_py import workflow_def
from apps.workflow_engine_py import instance
from apps.workflow_engine_py import history
from apps.workflow_engine_py import session


def require_role(action):
    user_id = session.get_user_id()
    if user_id == 0:
        print("Error: Not logged in. Use 'login <username> <password>' first.")
        return 0
    if not user.has_permission(user_id, action):
        print("Error: Insufficient permissions for " + action)
        return 0
    return user_id


def cmd_register(args):
    if len(args) < 4:
        print("Usage: register <username> <email> <password>")
        return
    username = args[1]
    email = args[2]
    password = args[3]
    result = user.create(username, email, password)
    if result is False:
        print("Error: Username or email already exists.")
        return
    print(f"User registered: {username} (ID: {result['id']})")


def cmd_login(args):
    if len(args) < 3:
        print("Usage: login <username> <password>")
        return
    username = args[1]
    password = args[2]
    u = user.authenticate(username, password)
    if u is False:
        print("Error: Invalid username or password.")
        return
    session.save(u["id"], username)
    print(f"Logged in as {username} (role: {u['role']})")


def cmd_logout(args):
    user_id = session.get_user_id()
    if user_id == 0:
        print("Error: Not logged in.")
        return
    s = session.load()
    username = s.get("username", "unknown")
    session.clear()
    print(f"Logged out {username}")


def cmd_create_workflow(args):
    user_id = require_role("create_workflow")
    if user_id == 0:
        return
    if len(args) < 4:
        print("Usage: create-workflow <name> <description> <states_csv>")
        print("  states_csv: state1,state2,state3")
        print("  Example: create-workflow Approval \"Simple approval\" pending,approved,rejected")
        return
    name = args[1]
    desc = args[2]
    states_csv = args[3]
    states = states_csv.split(",")
    initial_state = states[0]
    transitions = []
    defn = workflow_def.create_with_data(name, desc, states, initial_state, transitions)
    if defn is False:
        print("Error: Workflow name already exists.")
        return
    print(f"Workflow created: {name} (ID: {defn['id']})")
    print(f"States: {states_csv}")
    print("Use 'add-transition <workflow_id> <from> <to> <action> [role]' to add transitions.")


def cmd_add_transition(args):
    user_id = require_role("create_workflow")
    if user_id == 0:
        return
    if len(args) < 5:
        print("Usage: add-transition <workflow_id> <from_state> <to_state> <action> [required_role]")
        print("  Example: add-transition 1 pending approved approve operator")
        return
    wf_id = int(args[1])
    from_state = args[2]
    to_state = args[3]
    action = args[4]
    role = args[5] if len(args) > 5 else "operator"
    defn = workflow_def.find_by_id(wf_id)
    if defn is False:
        print("Error: Workflow not found.")
        return
    trans = {
        "from_state": from_state,
        "to_state": to_state,
        "action": action,
        "conditions": [],
        "required_role": role,
    }
    transitions = defn["transitions"]
    transitions.append(trans)
    storage.update_field("workflow_defs", wf_id, "transitions", transitions)
    print(f"Transition added: {from_state} -> {to_state} (action: {action})")


def cmd_list_workflows(args):
    user_id = require_role("list_workflows")
    if user_id == 0:
        return
    defs = workflow_def.list_all()
    print(f"--- Workflows ({len(defs)}) ---")
    for d in defs:
        print(f"  [{d['id']}] {d['name']}")


def cmd_view_workflow(args):
    user_id = require_role("view_workflow")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: view-workflow <id>")
        return
    wf_id = int(args[1])
    defn = workflow_def.find_by_id(wf_id)
    if defn is False:
        print("Error: Workflow not found.")
        return
    print(f"--- Workflow {defn['id']} ---")
    print(f"Name: {defn['name']}")
    print(f"Description: {defn['description']}")
    print(f"Initial state: {defn['initial_state']}")
    print(f"States: {json.dumps(defn['states'])}")
    print(f"Transitions ({len(defn['transitions'])}):")
    for t in defn["transitions"]:
        print(f"  {t['from_state']} --({t['action']})--> {t['to_state']} [{t['required_role']}]")


def cmd_delete_workflow(args):
    user_id = require_role("delete_workflow")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: delete-workflow <id>")
        return
    wf_id = int(args[1])
    result = workflow_def.delete(wf_id)
    if result is False:
        print("Error: Workflow not found or has active instances.")
        return
    print(f"Workflow {wf_id} deleted.")


def cmd_create_instance(args):
    user_id = require_role("create_instance")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: create-instance <workflow_id>")
        print("  Instance starts in the workflow's initial state.")
        return
    wf_id = int(args[1])
    data = {}
    data_json = json.dumps(data)
    result = instance.create(wf_id, user_id, data_json)
    if result is False:
        print("Error: Workflow not found.")
        return
    print(f"Instance created: ID {result['id']} in state '{result['current_state']}'")


def cmd_view_instance(args):
    user_id = require_role("view_instance")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: view-instance <id>")
        return
    inst_id = int(args[1])
    inst = instance.find_by_id(inst_id)
    if inst is False:
        print("Error: Instance not found.")
        return
    print(f"--- Instance {inst['id']} ---")
    print(f"Workflow ID: {inst['workflow_id']}")
    print(f"Current state: {inst['current_state']}")
    print(f"Data: {json.dumps(inst['data'])}")
    print(f"Created by: {inst['created_by']}")
    print(f"Created: {inst['created_at']}")


def cmd_list_instances(args):
    user_id = require_role("view_instance")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: list-instances <workflow_id>")
        return
    wf_id = int(args[1])
    instances = instance.list_by_workflow(wf_id)
    print(f"--- Instances for workflow {wf_id} ({len(instances)}) ---")
    for inst in instances:
        print(f"  [{inst['id']}] {inst['current_state']}")


def cmd_list_my_instances(args):
    user_id = session.get_user_id()
    if user_id == 0:
        print("Error: Not logged in.")
        return
    instances = instance.list_by_user(user_id)
    print(f"--- My instances ({len(instances)}) ---")
    for inst in instances:
        print(f"  [{inst['id']}] {inst['current_state']}")


def cmd_transition(args):
    user_id = require_role("create_instance")
    if user_id == 0:
        return
    if len(args) < 3:
        print("Usage: transition <instance_id> <action> [notes]")
        return
    inst_id = int(args[1])
    action = args[2]
    notes = args[3] if len(args) > 3 else ""
    result = instance.transition(inst_id, action, user_id, notes)
    error = result.get("error", "")
    if error == "invalid_transition":
        print("Error: Invalid transition from current state.")
        return
    if error == "conditions_not_met":
        print("Error: Transition conditions not met.")
        return
    if error == "not_found":
        print("Error: Instance not found.")
        return
    print(f"Instance {inst_id} transitioned to '{result['current_state']}'")


def cmd_set_data(args):
    user_id = require_role("create_instance")
    if user_id == 0:
        return
    if len(args) < 4:
        print("Usage: set-data <instance_id> <key> <value>")
        return
    inst_id = int(args[1])
    key = args[2]
    value = args[3]
    result = instance.set_data(inst_id, key, value)
    if result is False:
        print("Error: Instance not found.")
        return
    print(f"Instance {inst_id} data updated: {key} = {value}")


def cmd_cancel(args):
    user_id = require_role("cancel_instance")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: cancel <instance_id> [notes]")
        return
    inst_id = int(args[1])
    notes = args[2] if len(args) > 2 else ""
    result = instance.cancel(inst_id, user_id, notes)
    if result is False:
        print("Error: Instance not found.")
        return
    print(f"Instance {inst_id} cancelled.")


def cmd_history(args):
    user_id = require_role("view_history")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: history <instance_id>")
        return
    inst_id = int(args[1])
    entries = history.list_by_instance(inst_id)
    print(f"--- History for instance {inst_id} ({len(entries)}) ---")
    for e in entries:
        print(f"  {e['from_state']} -> {e['to_state']} ({e['notes']}) [{e['timestamp']}]")


def cmd_report_workflow(args):
    user_id = require_role("report_workflow")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: report-workflow <workflow_id>")
        return
    wf_id = int(args[1])
    counts = instance.report_workflow(wf_id)
    print(f"--- Workflow {wf_id} Report ---")
    for state, count in counts.items():
        print(f"  {state}: {count}")


def cmd_report_activity(args):
    user_id = require_role("report_activity")
    if user_id == 0:
        return
    entries = instance.report_activity()
    print(f"--- Activity (last 7 days): {len(entries)} transitions ---")
    for e in entries:
        print(f"  {e['from_state']} -> {e['to_state']} ({e['notes']}) [{e['timestamp']}]")


def cmd_export_workflows(args):
    user_id = require_role("export_import")
    if user_id == 0:
        return
    data = workflow_def.export()
    print(data)


def cmd_import_workflows(args):
    user_id = require_role("export_import")
    if user_id == 0:
        return
    if len(args) < 2:
        print("Usage: import-workflows <json_data>")
        return
    json_data = args[1]
    count = workflow_def.import_workflows(json_data)
    print(f"Imported {count} workflows.")


def cmd_help(args):
    print("Available commands:")
    print("  register <username> <email> <password>")
    print("  login <username> <password>")
    print("  logout")
    print("  create-workflow <name> <description> <state1,state2,...>")
    print("  add-transition <workflow_id> <from> <to> <action> [role]")
    print("  list-workflows")
    print("  view-workflow <id>")
    print("  delete-workflow <id>")
    print("  create-instance <workflow_id>")
    print("  view-instance <id>")
    print("  list-instances <workflow_id>")
    print("  list-my-instances")
    print("  transition <instance_id> <action> [notes]")
    print("  set-data <instance_id> <key> <value>")
    print("  cancel <instance_id> [notes]")
    print("  history <instance_id>")
    print("  report-workflow <workflow_id>")
    print("  report-activity")
    print("  export-workflows")
    print("  import-workflows <json_data>")
    print("  help")


COMMANDS = {
    "register": cmd_register,
    "login": cmd_login,
    "logout": cmd_logout,
    "create-workflow": cmd_create_workflow,
    "add-transition": cmd_add_transition,
    "list-workflows": cmd_list_workflows,
    "view-workflow": cmd_view_workflow,
    "delete-workflow": cmd_delete_workflow,
    "create-instance": cmd_create_instance,
    "view-instance": cmd_view_instance,
    "list-instances": cmd_list_instances,
    "list-my-instances": cmd_list_my_instances,
    "transition": cmd_transition,
    "set-data": cmd_set_data,
    "cancel": cmd_cancel,
    "history": cmd_history,
    "report-workflow": cmd_report_workflow,
    "report-activity": cmd_report_activity,
    "export-workflows": cmd_export_workflows,
    "import-workflows": cmd_import_workflows,
    "help": cmd_help,
}


def main():
    args = sys.argv[1:]
    if not args:
        print("Workflow Engine v1.0 (Python)")
        print("Usage: python -m apps.workflow_engine_py.main <command> [args...]")
        print("Type 'help' for available commands.")
        return
    command = args[0]
    if command in COMMANDS:
        COMMANDS[command](args)
    else:
        print(f"Unknown command: {command}. Type 'help' for available commands.")


if __name__ == "__main__":
    main()
