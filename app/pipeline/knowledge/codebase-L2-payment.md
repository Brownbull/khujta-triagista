---
level: L2
scope: domain-deep-dive
domain: payment
tokens_est: 800
load: on-demand
trigger_keywords: payment, charge, gateway, stripe, timeout, refund, authorize, capture
boundary: "NOT shipping rates, NOT tax calculation"
---

# Payment Domain — Deep Dive

## State Machine (core/state_machines/payment.rb)

```
checkout → started_processing → processing
  ├── complete → completed
  ├── failure → failed
  ├── pend → pending
  ├── void → void
  └── invalidate → invalid (from checkout only)
```

Key transitions:
- L21: `state_machine initial: :checkout`
- L27: `event :started_processing` — from checkout/pending/completed/processing → processing
- L31: `event :failure` — from pending/processing → **failed** (this is the timeout path)
- L39: `event :complete` — from processing/pending/checkout → completed
- L42: `event :void` — from pending/processing/completed/checkout → void

## Processing Methods (payment/processing.rb)

| Method | Line | What It Does |
|--------|------|-------------|
| `authorize!` | L37 | Calls gateway `authorize()`. On success → completes/pends payment. On timeout → GatewayError |
| `purchase!` | L53 | Calls gateway `purchase()` (auth+capture in one step) |
| `capture!` | L73 | Captures previously authorized payment. Takes optional amount |

## Error Handling

- L232: `raise Core::GatewayError.new(message)` — wraps all gateway errors
- `GatewayError` defined at `core/lib/spree/core.rb#L89` as `class GatewayError < RuntimeError`
- No retry logic built-in — failure transitions immediately to `:failed` state
- No charge verification on timeout — payment marked failed without checking gateway

## Critical Failure Mode

**Timeout race condition**: Gateway processes charge → our timeout fires first → payment transitions to `failed` → charge exists on gateway but no matching order. Results in orphaned charges.

**Missing safeguard**: No idempotency key on authorize! calls. Retry after timeout can create duplicate charges.

## Database Schema (spree_payments table)

```
amount:             decimal(10,2)  — payment amount
state:              string         — current state machine state (checkout/pending/processing/completed/failed/void)
response_code:      string         — gateway response code (useful for debugging)
avs_response:       string         — address verification response
cvv_response_code:  string         — CVV check result
number:             string         — payment reference number
order_id:           integer (FK)   — link to spree_orders
payment_method_id:  integer (FK)   — which gateway
source_id/type:     polymorphic    — CreditCard, StoreCredit, etc.
```

Diagnostic queries: `SELECT state, response_code, avs_response FROM spree_payments WHERE order_id = ?`

## Key Associations

- `Payment belongs_to :order` — order.payments is one-to-many
- `Payment belongs_to :payment_method` — gateway configuration
- `Payment belongs_to :source` (polymorphic) — CreditCard, StoreCredit, etc.
- `PaymentMethod` L208: preferences hash stores gateway timeout, API keys
