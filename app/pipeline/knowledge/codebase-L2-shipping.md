---
level: L2
scope: domain-deep-dive
domain: shipping
tokens_est: 700
load: on-demand
trigger_keywords: shipping, shipment, shipping rate, carrier, tracking, fulfillment, delivery, zone
boundary: "NOT inventory stock counts, NOT payment processing, NOT product catalog"
---

# Shipping Domain — Deep Dive

## Shipment State Machine (core/state_machines/shipment.rb)

```
pending → ready → shipped → delivered
  └── canceled (from any state)
```

## Shipment Model (shipment.rb — 371 LOC)

- Links Order ↔ StockLocation ↔ ShippingMethod
- Contains InventoryUnits (what physical items are in this shipment)
- `ship!` — transitions to shipped, triggers tracking notification
- `after_ship` — sends shipment confirmation email

## Shipping Rate Calculation

```
Order checkout (delivery step)
  → Stock::SimpleCoordinator — allocates items to stock locations
    → Stock::Estimator — calculates shipping rates per shipment
      → ShippingMethod.calculators — each method has a calculator
        → Results: list of ShippingRate objects with costs
```

Calculator types (in `calculator/shipping/`):
- `FlatRate` — fixed cost per order
- `FlatPercentItemTotal` — percentage of item total
- `FlexiRate` — first item + additional item pricing
- `PerItem` — cost per item
- `PriceSack` — weight-based price brackets

## Zones

`Spree::Zone` defines geographic regions for shipping eligibility:
- Zone has_many countries or states
- ShippingMethod scoped to zones via `shipping_method_zones`
- Rate only shown if delivery address is in zone

## Database Schema (spree_shipments table)

```
number:             string         — shipment reference (e.g., H12345678)
state:              string         — state machine state (pending/ready/shipped/delivered/canceled)
tracking:           string         — carrier tracking number (null until shipped)
cost:               decimal(10,2)  — shipping cost
shipped_at:         datetime       — null until shipped
order_id:           integer (FK)   — parent order
stock_location_id:  integer (FK)   — which warehouse ships this
adjustment_total:   decimal(10,2)  — shipping adjustments
```

Diagnostic queries:
- Stuck shipments: `SELECT number, state, tracking FROM spree_shipments WHERE state = 'ready' AND created_at < NOW() - INTERVAL '24 hours'`
- Missing tracking: `SELECT number, state FROM spree_shipments WHERE state = 'shipped' AND tracking IS NULL`

## Common Failure Modes

1. **No rates available**: Address not in any zone, or zone misconfiguration
2. **Calculator error**: Division by zero on empty cart, nil weight
3. **Carrier API timeout**: External shipping API slow/down (similar to payment gateway)
4. **Tracking not updating**: Webhook from carrier not received or processed
