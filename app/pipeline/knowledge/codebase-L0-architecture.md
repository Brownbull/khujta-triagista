---
level: L0
scope: architecture-overview
tokens_est: 500
load: always
boundary: "NOT individual file contents, NOT method signatures, NOT code"
---

# Solidus E-Commerce — Architecture Overview

**Platform**: Ruby on Rails modular e-commerce engine
**Repo**: https://github.com/Brownbull/hackathon-ecommerce
**Scale**: 1,446 Ruby files, ~104K LOC, 114 core models

## Gem Structure (4 gems)

| Gem | Purpose | Key Directory |
|-----|---------|--------------|
| **core/** | All business logic, models, state machines, DB schema | `core/app/models/spree/` |
| **api/** | REST API endpoints (v1 + v2 storefront) | `api/app/controllers/spree/api/` |
| **admin/** | New admin dashboard (ViewComponents + Stimulus) | `admin/app/controllers/solidus_admin/` |
| **backend/** | Legacy admin (being replaced by admin/) | `backend/app/controllers/spree/admin/` |

## 6 Business Domains

| Domain | What It Does | Entry Point |
|--------|-------------|-------------|
| **Payment** | Gateway calls, charge/refund, state machine | `Spree::Payment` |
| **Orders** | Checkout flow, cart, line items, state machine | `Spree::Order` |
| **Inventory** | Stock counts, locations, allocation, availability | `Spree::StockItem` |
| **Shipping** | Shipments, rates, carriers, fulfillment | `Spree::Shipment` |
| **Search/Catalog** | Products, variants, pricing, search, taxonomy | `Spree::Product` |
| **Auth/Users** | Devise auth, roles, permissions, abilities | `Spree::User` |

## Data Flow (happy path)

```
Customer browses → Spree::Product/Variant
  → Adds to cart → Spree::Order + LineItem
    → Checkout → Address → Shipping rates → Payment
      → Spree::Payment#authorize! → Gateway API call
        → Spree::Shipment created → StockItem decremented
          → Carton shipped → Order completed
```

## State Machines (6 total)

Order, Payment, Shipment, InventoryUnit, Reimbursement, ReturnAuthorization.
All defined in `core/app/models/spree/core/state_machines/`.

## SSOT Documents

- Architecture: `docs/architecture.md`
- Component map: `docs/component-map.md`
- Incident patterns: `docs/incident-patterns.md`
- Team routing: `docs/team-routing.md`
