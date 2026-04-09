---
level: L2
scope: domain-deep-dive
domain: inventory
tokens_est: 800
load: on-demand
trigger_keywords: stock, inventory, out of stock, oversell, count_on_hand, backorder, warehouse
boundary: "NOT shipping rates, NOT search, NOT product catalog"
---

# Inventory Domain — Deep Dive

## Core Model: StockItem (stock_item.rb)

The `count_on_hand` field is the single source of truth for available inventory per variant per stock location.

| Method | Line | What It Does |
|--------|------|-------------|
| `adjust_count_on_hand(value)` | L37 | Increments/decrements count_on_hand, triggers backorder processing |
| `set_count_on_hand(value)` | L50 | Sets absolute value (used by imports — **dangerous if import data is wrong**) |
| `in_stock?` | L59 | `count_on_hand > 0` |
| `can_supply?(quantity)` | L64 | `in_stock? \|\| backorderable?` |
| `reduce_count_on_hand_to_zero` | L70 | Emergency zero-out |

Validation at L13: `validates :count_on_hand >= 0` **unless** `backorderable?` — backorderable items can go negative.

## Stock Decrement Pipeline

```
Order finalized
  → OrderInventory#verify (L20)
    → Checks each line_item quantity vs allocated units
      → add_to_shipment (L73) — creates InventoryUnit, decrements StockItem
      → remove_from_shipment (L99) — reverses on cancellation
```

**Critical point**: `verify` is the ONLY place stock gets decremented on order. If it doesn't fire, `count_on_hand` stays inflated.

## Availability Check

`stock/availability.rb`:
- L21: `on_hand_by_stock_location_id` — aggregates count_on_hand across locations
- L39: `backorderable_by_stock_location_id` — which locations accept backorders

`stock/quantifier.rb`: Calculates total available across all locations for a variant.

## Database Schema (spree_stock_items table)

```
count_on_hand:      integer        — current stock count (the SSOT for availability)
stock_location_id:  integer (FK)   — which warehouse
variant_id:         integer (FK)   — which product variant
backorderable:      boolean        — default false. If true, can_supply? returns true even at 0
deleted_at:         datetime       — soft delete (stock item disabled, not removed)
```

Key index: `UNIQUE(variant_id, stock_location_id) WHERE deleted_at IS NULL`
Diagnostic query: `SELECT count_on_hand, backorderable FROM spree_stock_items WHERE variant_id = ?`

## Common Failure Modes

1. **Import overwrites**: `set_count_on_hand` resets to import value, wiping real decrements
2. **Backorderable flag**: If accidentally `true`, orders accepted even at 0 stock
3. **verify not firing**: OrderInventory#verify depends on order finalization — if order gets stuck pre-complete, stock never decrements
