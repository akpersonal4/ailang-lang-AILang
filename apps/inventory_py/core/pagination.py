from core.helpers import helpers_get_map_value_safe

def pagination_paginate(pgItems, pgPageNum, pgPageSize):
    pgStart = (pgPageNum - 1) * pgPageSize
    pgEnd = pgStart + pgPageSize
    if pgStart >= len(pgItems):
        return []
    return list(pgItems[pgStart:pgEnd])

def pagination_total_pages(tpItems, tpPageSize):
    if len(tpItems) == 0:
        return 0
    tpCount = 1
    while tpCount * tpPageSize < len(tpItems):
        tpCount = tpCount + 1
    return tpCount

def pagination_page_info(piItems, piPageNum, piPageSize):
    piSubset = pagination_paginate(piItems, piPageNum, piPageSize)
    piTotalPages = pagination_total_pages(piItems, piPageSize)
    piTotalItems = len(piItems)
    piHasPrev = piPageNum > 1
    piHasNext = piPageNum < piTotalPages
    return {
        "items": piSubset,
        "page": piPageNum,
        "page_size": piPageSize,
        "total_pages": piTotalPages,
        "total_items": piTotalItems,
        "has_prev": piHasPrev,
        "has_next": piHasNext,
    }

def pagination_page_items(pimInfo):
    return helpers_get_map_value_safe(pimInfo, "items", [])

def pagination_has_next(phnInfo):
    return helpers_get_map_value_safe(phnInfo, "has_next", False)
