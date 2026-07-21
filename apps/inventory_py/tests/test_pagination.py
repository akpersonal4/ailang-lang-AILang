from core.pagination import (
    pagination_has_next,
    pagination_page_info,
    pagination_page_items,
    pagination_paginate,
    pagination_total_pages,
)


def test_pagination_basic():
    tp_items = ["a", "b", "c", "d", "e"]
    tp_result = pagination_paginate(tp_items, 1, 2)
    if len(tp_result) != 2:
        print("FAIL: expected 2 items, got " + str(len(tp_result)))
        return False
    tp_first = tp_result[0]
    if tp_first != "a":
        print("FAIL: expected 'a', got " + tp_first)
        return False
    print("PASS: pagination_basic")
    return True


def test_pagination_page_2():
    tp_items = ["a", "b", "c", "d", "e"]
    tp_result = pagination_paginate(tp_items, 2, 2)
    if len(tp_result) != 2:
        print("FAIL: expected 2 items for page 2, got " + str(len(tp_result)))
        return False
    tp_first = tp_result[0]
    if tp_first != "c":
        print("FAIL: expected 'c', got " + tp_first)
        return False
    print("PASS: pagination_page_2")
    return True


def test_pagination_out_of_range():
    tp_items = ["a", "b"]
    tp_result = pagination_paginate(tp_items, 999, 10)
    if len(tp_result) != 0:
        print("FAIL: expected empty list for out-of-range page")
        return False
    print("PASS: pagination_out_of_range")
    return True


def test_pagination_total_pages():
    tp_items = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    tp_total = pagination_total_pages(tp_items, 3)
    if tp_total != 4:
        print("FAIL: expected 4 pages, got " + str(tp_total))
        return False
    print("PASS: pagination_total_pages")
    return True


def test_pagination_page_info():
    tp_items = ["a", "b", "c"]
    tp_info = pagination_page_info(tp_items, 1, 2)
    tp_items_result = pagination_page_items(tp_info)
    if len(tp_items_result) != 2:
        print("FAIL: page_info items count wrong")
        return False
    tpHN = pagination_has_next(tp_info)
    if tpHN != True:
        print("FAIL: expected has_next true")
        return False
    print("PASS: pagination_page_info")
    return True


def main():
    tp1 = test_pagination_basic()
    if tp1 == False:
        return 1
    tp2 = test_pagination_page_2()
    if tp2 == False:
        return 1
    tp3 = test_pagination_out_of_range()
    if tp3 == False:
        return 1
    tp4 = test_pagination_total_pages()
    if tp4 == False:
        return 1
    tp5 = test_pagination_page_info()
    if tp5 == False:
        return 1
    print("ALL PAGINATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
