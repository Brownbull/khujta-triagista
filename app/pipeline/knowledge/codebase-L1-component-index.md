---
level: L1
scope: component-index
tokens_est: 1500
load: always
boundary: "NOT method implementations, NOT code snippets, NOT line numbers"
---

# Component Index — Keyword → Files → Team

> Match incident keywords against this index. Load the matching L2 domain file.
> Boundary field = what this component is NOT about (skip if query matches boundary).

## PAYMENT

- **Keywords**: payment, charge, checkout payment, gateway, stripe, timeout, refund, credit card, transaction, authorize, capture, void
- **Boundary**: NOT shipping rates, NOT product prices, NOT tax calculation
- **Primary files**:
  - `core/app/models/spree/payment.rb` (238 LOC) — Payment model, associations, scopes
  - `core/app/models/spree/payment/processing.rb` (252 LOC) — authorize!, capture!, purchase!, gateway calls
  - `core/app/models/spree/payment_method.rb` (208 LOC) — Gateway config, preferences
  - `core/app/models/spree/core/state_machines/payment.rb` — checkout→pending→processing→completed/failed/void
  - `core/lib/spree/core.rb#L89` — `GatewayError < RuntimeError`
  - `core/app/models/spree/credit_card.rb` (173 LOC) — CC storage, tokenization
  - `core/app/models/spree/refund.rb` — Refund processing
- **Team**: TEAM-PAY (payments-team)
- **Patterns**: PAT-PAY-001, PAT-PAY-002
- **L2 file**: `codebase-L2-payment.md`

## INVENTORY

- **Keywords**: stock, inventory, out of stock, oversell, count_on_hand, backorder, warehouse, stock location, quantity
- **Boundary**: NOT shipping rates, NOT product catalog, NOT search
- **Primary files**:
  - `core/app/models/spree/stock_item.rb` — count_on_hand, adjust_count_on_hand, backorderable?, can_supply?
  - `core/app/models/spree/stock/quantifier.rb` — Total stock across locations
  - `core/app/models/spree/stock/availability.rb` — on_hand + backorderable by location
  - `core/app/models/spree/order_inventory.rb` — Stock allocation on order (verify method)
  - `core/app/models/spree/stock_location.rb` — Physical warehouse locations
  - `core/app/models/spree/stock_movement.rb` — Stock movement tracking
  - `core/app/models/spree/variant.rb` (444 LOC) — can_supply? delegation to StockItem
- **Team**: TEAM-FUL (fulfillment-team)
- **Patterns**: PAT-INV-001, PAT-INV-002
- **L2 file**: `codebase-L2-inventory.md`

## ORDERS

- **Keywords**: order, checkout, cart, line item, place order, order stuck, order state, address, delivery
- **Boundary**: NOT payment gateway calls, NOT stock decrement logic, NOT shipping carrier API
- **Primary files**:
  - `core/app/models/spree/order.rb` (892 LOC) — Order model, checkout flow, totals
  - `core/app/models/spree/core/state_machines/order.rb` — cart→address→delivery→payment→confirm→complete
  - `core/app/models/spree/line_item.rb` (201 LOC) — Cart items, price, quantity
  - `core/app/models/spree/order/payments.rb` — Payment integration on order
  - `core/app/models/spree/adjustment.rb` — Price adjustments (promotions, tax)
  - `core/app/models/spree/order_updater.rb` (251 LOC) — Recalculate totals
- **Team**: TEAM-PLT (platform-team)
- **Patterns**: PAT-ORD-001
- **L2 file**: `codebase-L2-orders.md`

## SEARCH & CATALOG

- **Keywords**: search, product, catalog, not found, no results, variant, price, promotion, taxonomy, taxon, category
- **Boundary**: NOT order processing, NOT payment, NOT inventory counts
- **Primary files**:
  - `core/lib/spree/core/search/base.rb` — Default search (DB LIKE queries via retrieve_products)
  - `core/app/models/spree/product.rb` (376 LOC) — Product model, available scope
  - `core/app/models/spree/product/scopes.rb` (258 LOC) — in_name_or_keywords, sorting scopes
  - `core/app/models/spree/variant.rb` (444 LOC) — SKU, price, stock delegation
  - `core/app/models/spree/price.rb` — Pricing logic
  - `core/app/models/spree/promotion.rb` — Promotion rules and actions
- **Team**: TEAM-PLT (platform-team)
- **Patterns**: PAT-SRC-001, PAT-SRC-002
- **L2 file**: `codebase-L2-search.md`

## AUTH & USERS

- **Keywords**: login, auth, password, session, token, permission, unauthorized, role, user, devise, ability
- **Boundary**: NOT product access, NOT API rate limiting, NOT payment authorization
- **Primary files**:
  - `core/app/models/spree/ability.rb` — CanCanCan abilities (permissions)
  - `core/app/models/spree/role.rb` — User roles
  - `core/app/models/spree/permission_sets/` — 13 permission set files
  - `api/app/controllers/spree/api/base_controller.rb` — API authentication
- **Team**: TEAM-SEC (security-team)
- **Patterns**: PAT-AUTH-001
- **L2 file**: `codebase-L2-auth.md`

## SHIPPING

- **Keywords**: shipping, shipment, shipping rate, carrier, tracking, fulfillment, shipping method, zone, delivery
- **Boundary**: NOT inventory stock counts, NOT payment processing, NOT product catalog
- **Primary files**:
  - `core/app/models/spree/shipment.rb` (371 LOC) — Shipment model, state machine
  - `core/app/models/spree/shipping_method.rb` — Carrier configuration
  - `core/app/models/spree/shipping_rate.rb` — Rate calculation
  - `core/app/models/spree/core/state_machines/shipment.rb` — pending→ready→shipped→delivered
  - `core/app/models/spree/stock/estimator.rb` — Shipping cost estimation
  - `core/app/models/spree/stock/simple_coordinator.rb` — Stock-to-shipment allocation
- **Team**: TEAM-FUL (fulfillment-team)
- **Patterns**: PAT-SHP-001
- **L2 file**: `codebase-L2-shipping.md`
