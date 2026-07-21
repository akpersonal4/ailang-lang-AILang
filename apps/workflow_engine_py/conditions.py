"""Built-in condition evaluation for workflow transitions."""


def evaluate(condition, instance):
    parts = condition.split(":")
    cond_type = parts[0]
    if cond_type == "data_has_key":
        key = parts[1]
        return key in instance.get("data", {})
    if cond_type == "data_equals":
        key = parts[1]
        value = parts[2]
        data = instance.get("data", {})
        return data.get(key, "") == value
    if cond_type == "data_not_empty":
        key = parts[1]
        data = instance.get("data", {})
        val = data.get(key, "")
        return val != ""
    if cond_type == "created_by":
        return True
    return True


def check(condition_list, instance):
    for cond in condition_list:
        if not evaluate(cond, instance):
            return False
    return True
