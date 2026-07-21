"""Test Level 0 foundation modules for the inventory app."""

from __future__ import annotations

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter, Severity
from compiler.runtime.interpreter import Runtime


def _run_inventory(source: str):
    """Compile and run an AILang source string and return the main result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession()
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        if reporter.error_count > 0:
            err_msgs = [
                f"{d.error_code.code}: {d.message} (line {d.line})"
                for d in reporter.diagnostics
                if d.severity == Severity.ERROR
            ]
            assert False, f"Compilation errors: {err_msgs}"

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return runtime.execute(bundle.module_irs[entry_module])


def test_helpers_level_0() -> None:
    """Test helpers work correctly."""
    result = _run_inventory("""
import string;
import list;
import map;
import time;
import convert;

fn helpers_repeat_char(inChar, inCount, inAcc) {
    if (inCount <= 0) {
        return inAcc;
    }
    return helpers_repeat_char(inChar, inCount - 1, inAcc + inChar);
}

fn helpers_pad_number(padNum, padDigits) {
    let padStr = convert.to_string(padNum);
    let padLen = string.length(padStr);
    if (padLen >= padDigits) {
        return padStr;
    }
    let padZeros = helpers_repeat_char("0", padDigits - padLen, "");
    return padZeros + padStr;
}

fn helpers_current_timestamp() {
    return time.now();
}

fn helpers_unix_timestamp() {
    return time.timestamp();
}

fn helpers_safe_string(strValue) {
    if (strValue == false) {
        return "";
    }
    return convert.to_string(strValue);
}

fn helpers_copy_map_iter(hmKeys, hmSource, hmTarget, hmIdx) {
    if (hmIdx >= list.len(hmKeys)) {
        return hmTarget;
    }
    let hmKey = list.get(hmKeys, hmIdx);
    let hmValue = map.get(hmSource, hmKey);
    map.set(hmTarget, hmKey, hmValue);
    return helpers_copy_map_iter(hmKeys, hmSource, hmTarget, hmIdx + 1);
}

fn helpers_copy_map(hmSource) {
    let hmKeys = map.keys(hmSource);
    let hmResult = map.new();
    return helpers_copy_map_iter(hmKeys, hmSource, hmResult, 0);
}

fn helpers_find_in_list_rec(frItems, frKey, frValue, frIdx) {
    if (frIdx >= list.len(frItems)) {
        return false;
    }
    let frItem = list.get(frItems, frIdx);
    if (map.has(frItem, frKey)) {
        if (map.get(frItem, frKey) == frValue) {
            return frItem;
        }
    }
    return helpers_find_in_list_rec(frItems, frKey, frValue, frIdx + 1);
}

fn helpers_list_contains_rec(lcItems, lcValue, lcIdx) {
    if (lcIdx >= list.len(lcItems)) {
        return false;
    }
    if (list.get(lcItems, lcIdx) == lcValue) {
        return true;
    }
    return helpers_list_contains_rec(lcItems, lcValue, lcIdx + 1);
}

fn helpers_format_currency(amount) {
    return "$" + convert.to_string(amount);
}

fn helpers_string_to_number(stValue) {
    let stTrimmed = string.trim(stValue);
    if (stTrimmed == "") {
        return 0;
    }
    return convert.to_int(stTrimmed);
}

fn helpers_get_map_value_safe(gvMap, gvKey, gvDefault) {
    if (map.has(gvMap, gvKey)) {
        return map.get(gvMap, gvKey);
    }
    return gvDefault;
}

fn main() {
    let padResult = helpers_pad_number(5, 4);
    if (padResult != "0005") {
        return 0;
    }
    let safeResult = helpers_safe_string("hello");
    if (safeResult != "hello") {
        return 0;
    }
    let safeFalse = helpers_safe_string(false);
    if (safeFalse != "") {
        return 0;
    }
    let srcMap = map.new();
    map.set(srcMap, "a", 1);
    map.set(srcMap, "b", 2);
    let copyResult = helpers_copy_map(srcMap);
    if (map.get(copyResult, "a") != 1) {
        return 0;
    }
    if (map.get(copyResult, "b") != 2) {
        return 0;
    }
    let currencyResult = helpers_format_currency(42);
    if (currencyResult != "$42") {
        return 0;
    }
    let parseResult = helpers_string_to_number("42");
    if (parseResult != 42) {
        return 0;
    }
    let safeGetResult = helpers_get_map_value_safe(srcMap, "a", 99);
    if (safeGetResult != 1) {
        return 0;
    }
    let safeGetMissing = helpers_get_map_value_safe(srcMap, "missing", 99);
    if (safeGetMissing != 99) {
        return 0;
    }
    let items = list.new();
    let item1 = map.new();
    map.set(item1, "id", "1");
    map.set(item1, "name", "alice");
    let item2 = map.new();
    map.set(item2, "id", "2");
    map.set(item2, "name", "bob");
    list.append(items, item1);
    list.append(items, item2);
    let foundItem = helpers_find_in_list_rec(items, "name", "bob", 0);
    if (foundItem == false) {
        return 0;
    }
    if (map.get(foundItem, "id") != "2") {
        return 0;
    }
    let numItems = list.new();
    list.append(numItems, 10);
    list.append(numItems, 20);
    let containsResult = helpers_list_contains_rec(numItems, 10, 0);
    if (containsResult != true) {
        return 0;
    }
    return 1;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_storage_level_0() -> None:
    """Test storage CRUD operations."""
    result = _run_inventory("""
import file;
import json;
import path;
import list;
import map;
import string;

let STORAGE_DATA_DIR = "data";

fn storage_collection_path(collName) {
    return path.join(STORAGE_DATA_DIR, collName + ".json");
}

fn storage_find_first_rec(ffItems, ffKey, ffValue, ffIdx) {
    if (ffIdx >= list.len(ffItems)) {
        return false;
    }
    let ffItem = list.get(ffItems, ffIdx);
    if (map.has(ffItem, ffKey)) {
        if (map.get(ffItem, ffKey) == ffValue) {
            return ffItem;
        }
    }
    return storage_find_first_rec(ffItems, ffKey, ffValue, ffIdx + 1);
}

fn storage_apply_changes(acTarget, acSource, acKeys, acIdx) {
    if (acIdx >= list.len(acKeys)) {
        return acTarget;
    }
    let acKey = list.get(acKeys, acIdx);
    map.set(acTarget, acKey, map.get(acSource, acKey));
    return storage_apply_changes(acTarget, acSource, acKeys, acIdx + 1);
}

fn storage_load(collName) {
    let collPath = storage_collection_path(collName);
    if (file.exists(collPath) == false) {
        let emptyResult = list.new();
        return emptyResult;
    }
    let collContent = file.read(collPath);
    let collParsed = json.parse(collContent);
    if (collParsed == false) {
        let emptyResult = list.new();
        return emptyResult;
    }
    return collParsed;
}

fn storage_save(collName, collItems) {
    let collPath = storage_collection_path(collName);
    let collJson = json.stringify(collItems);
    file.write(collPath, collJson);
    return collItems;
}

fn storage_add(collName, addItem) {
    let addItems = storage_load(collName);
    list.append(addItems, addItem);
    return storage_save(collName, addItems);
}

fn storage_list(collName) {
    return storage_load(collName);
}

fn storage_get_by_id(collName, getId) {
    let getItems = storage_load(collName);
    return storage_find_first_rec(getItems, "id", getId, 0);
}

fn storage_update_rec(urItems, urId, urChanges, urIdx) {
    if (urIdx >= list.len(urItems)) {
        return false;
    }
    let urItem = list.get(urItems, urIdx);
    if (map.get(urItem, "id") == urId) {
        let urKeys = map.keys(urChanges);
        storage_apply_changes(urItem, urChanges, urKeys, 0);
        return urItems;
    }
    return storage_update_rec(urItems, urId, urChanges, urIdx + 1);
}

fn storage_update(collName, updId, updChanges) {
    let updItems = storage_load(collName);
    let updResult = storage_update_rec(updItems, updId, updChanges, 0);
    if (updResult == false) {
        return false;
    }
    return storage_save(collName, updResult);
}

fn storage_delete_rec(dlItems, dlId, dlResult, dlIdx) {
    if (dlIdx >= list.len(dlItems)) {
        return dlResult;
    }
    let dlItem = list.get(dlItems, dlIdx);
    if (map.get(dlItem, "id") != dlId) {
        list.append(dlResult, dlItem);
    }
    return storage_delete_rec(dlItems, dlId, dlResult, dlIdx + 1);
}

fn storage_delete(collName, delId) {
    let delItems = storage_load(collName);
    let delFiltered = list.new();
    return storage_save(collName, storage_delete_rec(delItems, delId, delFiltered, 0));
}

fn main() {
    let testId = "test-001";

    let item1 = map.new();
    map.set(item1, "id", testId);
    map.set(item1, "name", "test-item");

    let item2 = map.new();
    map.set(item2, "id", "test-002");
    map.set(item2, "name", "test-item-2");

    storage_add("test_storage", item1);
    storage_add("test_storage", item2);

    let allItems = storage_list("test_storage");
    if (list.len(allItems) != 2) {
        return 0;
    }

    let foundItem = storage_get_by_id("test_storage", testId);
    if (foundItem == false) {
        return 0;
    }
    let foundName = map.get(foundItem, "name");
    if (foundName != "test-item") {
        return 0;
    }

    let changes = map.new();
    map.set(changes, "name", "updated-item");
    storage_update("test_storage", testId, changes);

    let updatedItem = storage_get_by_id("test_storage", testId);
    let updatedName = map.get(updatedItem, "name");
    if (updatedName != "updated-item") {
        return 0;
    }

    storage_delete("test_storage", "test-002");
    let remainingItems = storage_load("test_storage");
    if (list.len(remainingItems) != 1) {
        return 0;
    }

    file.remove("data/test_storage.json");

    return 1;
}
""")
    assert result == 1, f"Expected 1, got {result}"
