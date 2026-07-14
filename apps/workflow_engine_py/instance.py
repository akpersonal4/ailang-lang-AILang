"""Instance management with state transitions and reporting."""
import time
import json
from . import storage
from . import workflow_def
from . import conditions
from . import history


def create(workflow_id, created_by, data_json):
    defn = workflow_def.find_by_id(workflow_id)
    if defn is False:
        return False
    initial_state = defn["initial_state"]
    data = json.loads(data_json)
    inst = {
        "id": storage.next_id("instances"),
        "workflow_id": workflow_id,
        "current_state": initial_state,
        "data": data,
        "created_by": created_by,
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
    }
    storage.append("instances", inst)
    history.add(inst["id"], "start", initial_state, created_by, "Instance created")
    return inst


def find_by_id(instance_id):
    return storage.find_by_id("instances", instance_id)


def list_all():
    return storage.load("instances")


def list_by_workflow(workflow_id):
    all_insts = storage.load("instances")
    return [i for i in all_insts if i["workflow_id"] == workflow_id]


def list_by_user(user_id):
    all_insts = storage.load("instances")
    return [i for i in all_insts if i["created_by"] == user_id]


def transition(instance_id, action, performed_by, notes):
    inst = find_by_id(instance_id)
    if inst is False:
        return {"error": "not_found"}
    def_id = inst["workflow_id"]
    current_state = inst["current_state"]
    trans = workflow_def.validate_transition(def_id, current_state, action)
    if trans is False:
        return {"error": "invalid_transition"}
    cond_result = conditions.check(trans["conditions"], inst)
    if cond_result is False:
        return {"error": "conditions_not_met"}
    to_state = trans["to_state"]
    inst["current_state"] = to_state
    inst["updated_at"] = int(time.time())
    storage.update_field("instances", instance_id, "current_state", to_state)
    storage.update_field("instances", instance_id, "updated_at", int(time.time()))
    history.add(instance_id, current_state, to_state, performed_by, notes)
    return inst


def set_data(instance_id, key, value):
    inst = find_by_id(instance_id)
    if inst is False:
        return False
    inst["data"][key] = value
    storage.update_field("instances", instance_id, "data", inst["data"])
    return True


def cancel(instance_id, performed_by, notes):
    inst = find_by_id(instance_id)
    if inst is False:
        return False
    current_state = inst["current_state"]
    inst["current_state"] = "cancelled"
    inst["updated_at"] = int(time.time())
    storage.update_field("instances", instance_id, "current_state", "cancelled")
    storage.update_field("instances", instance_id, "updated_at", int(time.time()))
    history.add(instance_id, current_state, "cancelled", performed_by, notes)
    return True


def report_workflow(workflow_id):
    instances = list_by_workflow(workflow_id)
    counts = {}
    for inst in instances:
        state = inst["current_state"]
        counts[state] = counts.get(state, 0) + 1
    return counts


def report_activity():
    all_history = storage.load("history")
    now = int(time.time())
    cutoff = now - 604800
    return [h for h in all_history if h["timestamp"] >= cutoff]
