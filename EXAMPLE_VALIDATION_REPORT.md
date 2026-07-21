# Example Validation Report

**Date:** 2026-07-21
**Version:** v1.1.1

---

## Summary

All 41 example directories now have README.md files. 19 examples had stale "not yet in AILang" comments that were corrected.

---

## Example Inventory

| Directory | Has README | Stale Comment Fixed | Status |
|-----------|:----------:|:-------------------:|--------|
| age_calc | ✅ | ✅ Updated | Valid |
| attendance | ✅ | ✅ Removed | Valid |
| banking | ✅ | ✅ Removed (earlier) | Valid |
| bmi_calc | ✅ | ✅ Updated | Valid |
| calculator | ✅ | — | Valid |
| config_loader | ✅ | — | Valid |
| csv_reader | ✅ | — | Valid |
| currency_converter | ✅ | ✅ Updated | Valid |
| date_validate | ✅ | ✅ Updated | Valid |
| dir_tree | ✅ | — | Valid |
| electricity_bill | ✅ | ✅ Removed | Valid |
| expr_eval | ✅ | ✅ Removed | Valid |
| fibonacci | ✅ | — | Valid |
| file_copy | ✅ | — | Valid |
| functions | ✅ | — | Valid |
| hello_world | ✅ | — | Valid |
| http_client | ✅ | — | Valid |
| if_else | ✅ | — | Valid |
| income_tax | ✅ | ✅ Updated | Valid |
| ini_parser | ✅ | — | Valid |
| integration | ✅ | — | Valid |
| invoice_gen | ✅ | ✅ Removed | Valid |
| json_parser | ✅ | — | Valid |
| library_mgr | ✅ | ✅ Updated | Valid |
| loan_emi | ✅ | ✅ Removed | Valid |
| markdown_parser | ✅ | — | Valid |
| modules | ✅ | — | Valid |
| num_stats | ✅ | ✅ Removed | Valid |
| password_validate | ✅ | ✅ Updated | Valid |
| patterns | ✅ | — | Valid |
| payroll | ✅ | ✅ Removed | Valid |
| prime_checker | ✅ | — | Valid |
| recursion | ✅ | — | Valid |
| rule_engine | ✅ | ✅ Updated | Valid |
| salary_calc | ✅ | ✅ Removed | Valid |
| shopping_cart | ✅ | ✅ Removed | Valid |
| student_records | ✅ | ✅ Removed | Valid |
| text_search | ✅ | — | Valid |
| variables | ✅ | — | Valid |
| voting_eligibility | ✅ | ✅ Updated | Valid |
| word_counter | ✅ | — | Valid |

---

## Stale Comment Corrections

### Removed (features now exist in stdlib)
- attendance: file I/O + collections → exist (io.ail, array.ail, list.ail, map.ail)
- electricity_bill: file I/O → exists (io.ail, file.ail)
- invoice_gen: string formatting + file I/O → both exist
- expr_eval: collections/stack + string parsing → both exist
- loan_emi: stdlib math → exists (math.ail)
- num_stats: dynamic arrays + stdlib math + file I/O → all exist
- student_records: arrays + stdlib → both exist
- salary_calc: file I/O + arrays → both exist
- payroll: file I/O + arrays → both exist
- shopping_cart: file I/O → exists

### Updated (partial availability)
- age_calc: time module exists, hardcoded year → noted
- bmi_calc: math exists, user input → runtime support needed
- date_validate: time exists, regex → not yet in stdlib
- currency_converter: HTTP → runtime support needed
- income_tax: file I/O exists, user input → runtime support needed
- library_mgr: time module exists → updated
- password_validate: string exists, regex → not yet in stdlib
- rule_engine: JSON + file I/O exist, database → runtime support needed
- voting_eligibility: HTTP + database → runtime support needed

---

## AILang Stdlib Modules (Current)

| Module | Capabilities |
|--------|-------------|
| array | Dynamic arrays, append, len, get |
| csv | CSV parsing |
| convert | Type conversion (to_number, to_string, to_bool) |
| environment | Environment variable access |
| file | File read/write/copy/delete/list |
| io | I/O operations (print, read) |
| json | JSON parse/stringify |
| list | List operations (sort, filter, map, reduce) |
| map | Map operations (get, set, has, keys, values) |
| math | Math functions (abs, min, max, sqrt, floor, ceil) |
| path | Path manipulation |
| random | Random number generation |
| set | Set operations |
| string | String operations (len, concat, split, join, substr) |
| time | Time/date operations |
| system | System operations |
