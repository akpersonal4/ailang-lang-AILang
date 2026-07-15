# AI Usage Guide: Inventory Management Lite

## Key Patterns Demonstrated

### 1. Map-Based Product Records

Products are stored as maps with consistent key names. This is AILang's equivalent of structs/objects.

```ailang
fn create_product(id, name, price, stock) {
    let product = map.new();
    map.set(product, "id", id);
    map.set(product, "name", name);
    map.set(product, "price", price);
    map.set(product, "stock", stock);
    return product
}
```

**Rule**: Always use `map.has` before `map.get` when keys are uncertain. Here, keys are guaranteed by `create_product`, so direct `map.get` is safe.

### 2. Recursive Search Pattern

Linear search through a list with early termination on match. The `_helper` suffix carries the accumulator/index parameter.

```ailang
fn find_product_helper(products, id, index) {
    if (index >= list.len(products)) { return none }
    let item = list.get(products, index);
    if (map.get(item, "id") == id) { return item }
    return find_product_helper(products, id, index + 1)
}

fn find_product(products, id) {
    return find_product_helper(products, id, 0)
}
```

**Pattern**: Base case returns sentinel value (`none`), recursive case advances index.

### 3. Stock Arithmetic with Mutation

Stock in/out modifies the product map in place. The `if (item != none)` guard prevents null dereference.

```ailang
fn stock_in(products, id, qty) {
    let item = find_product(products, id);
    if (item != none) {
        let current = map.get(item, "stock");
        map.set(item, "stock", current + qty)
    };
    return item
}
```

### 4. Recursive Aggregation

Count and sum use the same pattern: base case returns zero, recursive case adds current value to tail call result.

```ailang
fn total_value_helper(products, idx) {
    if (idx >= list.len(products)) { return 0.0 }
    let item = list.get(products, idx);
    let prc = map.get(item, "price");
    let stk = map.get(item, "stock");
    return (prc * stk) + total_value_helper(products, idx + 1)
}
```

### 5. JSON Persistence

Full inventory round-trip using `json.stringify`/`json.parse` and `file.write`/`file.read`.

```ailang
fn save_inventory(filename, products) {
    let data = json.stringify(products);
    file.write(filename, data);
    return filename
}

fn load_inventory(filename) {
    let data = file.read(filename);
    let loaded = json.parse(data);
    return loaded
}
```

## Common Mistakes

1. **Missing guard**: Forgetting `if (item != none)` before accessing stock leads to runtime errors
2. **Variable reuse**: Using `i` in both `count_products_helper` and `total_value_helper` violates unique naming
3. **Wrong order**: Defining `find_product` before `find_product_helper` causes forward reference error
4. **Missing initializer**: `let x;` is invalid; must be `let x = value;`
