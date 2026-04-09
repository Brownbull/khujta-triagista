---
level: L2
scope: domain-deep-dive
domain: search-catalog
tokens_est: 800
load: on-demand
trigger_keywords: search, product, catalog, not found, no results, variant, price, promotion, taxonomy
boundary: "NOT order processing, NOT payment, NOT inventory counts"
---

# Search & Catalog Domain — Deep Dive

## Search Architecture

Default search: `core/lib/spree/core/search/base.rb`
- L6: `class Base` — base searcher, overridable via `Spree::Config.searcher_class`
- L23: `retrieve_products` — builds ActiveRecord scope chain

Search flow:
```
User query → Spree::Core::Search::Base#retrieve_products
  → Product.available scope (filters by available_on date)
    → in_name_or_keywords scope (LIKE match on name + meta_keywords)
      → Pagination → Results
```

## Product Scopes (product/scopes.rb — 258 LOC)

- L136: `in_name_or_keywords` — `WHERE name LIKE '%query%' OR meta_keywords LIKE '%query%'`
- L26-28: `ascend_by_updated_at`, `ascend_by_name` — sorting scopes
- L31: `ascend_by_master_price` — price-based sorting

## Product Model (product.rb — 376 LOC)

- `available` scope: `where('available_on <= ?', Time.current)` + not discontinued
- `discontinue_on` — date after which product is hidden
- `has_many :variants` — each variant has its own price and stock
- `has_many :taxons, through: :classifications` — category browsing path

## Two Different Query Paths (why search ≠ browse)

| Path | Mechanism | Data Source |
|------|-----------|-------------|
| **Search** | `in_name_or_keywords` (LIKE query) | name + meta_keywords columns |
| **Category browse** | `Product.in_taxon(taxon)` | classifications table (taxon_id) |

**Key insight**: If a search extension (searchkick, algolia) is installed, search queries go to the external index instead of the database. Category browse always hits the database directly.

## Database Schema (spree_products table)

```
name:               string         — product name (indexed, searched by in_name_or_keywords)
description:        text           — product description
slug:               string         — URL slug (unique index)
available_on:       datetime       — null = not yet available. Filtered by `available` scope
deleted_at:         datetime       — soft delete
meta_keywords:      string         — searched by in_name_or_keywords (if empty, search misses)
meta_description:   text           — SEO description
meta_title:         string         — SEO title
tax_category_id:    integer (FK)
shipping_category_id: integer (FK)
promotionable:      boolean        — default true
```

Diagnostic queries:
- Not searchable: `SELECT name, available_on, meta_keywords FROM spree_products WHERE available_on IS NULL OR available_on > NOW()`
- Missing keywords: `SELECT name FROM spree_products WHERE meta_keywords IS NULL OR meta_keywords = ''`

## Common Failure Modes

1. **Stale search index**: External search engine not reindexed after product add (PAT-SRC-001)
2. **available_on in future**: Product exists but filtered by `available` scope (PAT-SRC-002)
3. **Empty meta_keywords**: Product name matches but search also checks meta_keywords — if empty, partial match may fail
