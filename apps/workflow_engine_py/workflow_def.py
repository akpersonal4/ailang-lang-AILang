"""Workflow definition CRUD and validation."""

import json
import time

from . import storage


def find_by_name(name):
    defs = storage.load("workflow_defs")
    for d in defs:
        if d["name"] == name:
            return d
    return False


def find_by_id(def_id):
    return storage.find_by_id("workflow_defs", def_id)


def list_all():
    return storage.load("workflow_defs")


def create(name, description, states_json, transitions_json):
    if find_by_name(name) is not False:
        return False
    states = json.loads(states_json)
    transitions = json.loads(transitions_json)
    initial_state = states[0]
    defn = {
        "id": storage.next_id("workflow_defs"),
        "name": name,
        "description": description,
        "states": states,
        "initial_state": initial_state,
        "transitions": transitions,
        "created_at": int(time.time()),
    }
    storage.append("workflow_defs", defn)
    return defn


def create_with_data(name, description, states, initial_state, transitions):
    if find_by_name(name) is not False:
        return False
    defn = {
        "id": storage.next_id("workflow_defs"),
        "name": name,
        "description": description,
        "states": states,
        "initial_state": initial_state,
        "transitions": transitions,
        "created_at": int(time.time()),
    }
    storage.append("workflow_defs", defn)
    return defn


def delete(def_id):
    instances = storage.load("instances")
    for inst in instances:
        if inst["workflow_id"] == def_id:
            return False
    storage.delete_by_id("workflow_defs", def_id)
    return True


def find_transition(def_id, action):
    defn = find_by_id(def_id)
    if defn is False:
        return False
    for t in defn["transitions"]:
        if t["action"] == action:
            return t
    return False


def validate_transition(def_id, from_state, action):
    trans = find_transition(def_id, action)
    if trans is False:
        return False
    if trans["from_state"] == from_state:
        return trans
    return False


def export():
    defs = storage.load("workflow_defs")
    return json.dumps(defs)


def import_workflows(json_data):
    defs = json.loads(json_data)
    count = 0
    for d in defs:
        if find_by_name(d["name"]) is False:
            storage.append("workflow_defs", d)
            count += 1
    return count
