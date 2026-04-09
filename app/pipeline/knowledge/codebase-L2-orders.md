---
level: L2
scope: domain-deep-dive
domain: orders
tokens_est: 800
load: on-demand
trigger_keywords: order, checkout, cart, line item, place order, order stuck, address, delivery
boundary: "NOT payment gateway calls, NOT stock counts, NOT shipping carrier API"
---

# Orders Domain — Deep Dive

## Order State Machine (core/state_machines/order.rb)

```
cart → address → delivery → payment → confirm → complete
  └── (any state) → canceled
```

- L21: `state_machine initial: :cart`
- Each step validated before transition (address valid, shipping selected, payment authorized)
- `complete` transition triggers: inventory allocation, shipment creation, confirmation email

## Order Model (order.rb — 892 LOC, largest model)

Key methods:
- `checkout_steps` — returns ordered list of checkout states
- `update_totals` — recalculates item_total, adjustment_total, total
- `finalize!` — called on completion, triggers side effects
- `payments` association — one-to-many, managed via `order/payments.rb`

## Line Items (line_item.rb — 201 LOC)

- Links Order ↔ Variant with quantity and price
- `amount = price * quantity`
- Adjustments (promotions, tax) attached to line items

## Order Updater (order_updater.rb — 251 LOC)

Recalculates all totals when cart changes:
- item_total (sum of line_item amounts)
- adjustment_total (promotions + tax)
- shipment_total
- total = item_total + adjustment_total + shipment_total

## Database Schema (spree_orders table)

```
number:             string(32)     — order reference (e.g., R123456789)
state:              string         — state machine state (cart/address/delivery/payment/confirm/complete)
total:              decimal(10,2)  — final total
item_total:         decimal(10,2)  — sum of line items
payment_total:      decimal(10,2)  — sum of payments
adjustment_total:   decimal(10,2)  — promotions + tax
shipment_total:     decimal(10,2)  — shipping cost
payment_state:      string         — paid/balance_due/credit_owed/failed
shipment_state:     string         — pending/ready/shipped/partial
email:              string         — customer email
completed_at:       datetime       — null until order completes
canceled_at:        datetime       — null unless canceled
```

Diagnostic queries:
- Stuck orders: `SELECT number, state, payment_state FROM spree_orders WHERE state != 'complete' AND created_at < NOW() - INTERVAL '1 hour'`
- Payment mismatch: `SELECT number, total, payment_total FROM spree_orders WHERE total != payment_total AND state = 'complete'`

## Common Failure Modes

1. **Checkout stuck**: State machine won't advance — usually a validation error not surfaced to user
2. **Total mismatch**: OrderUpdater not called after line_item change
3. **Payment step failure**: Cascades from payment domain — order stays in `payment` state
