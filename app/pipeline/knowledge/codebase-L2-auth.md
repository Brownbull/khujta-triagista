---
level: L2
scope: domain-deep-dive
domain: auth-users
tokens_est: 600
load: on-demand
trigger_keywords: login, auth, password, session, token, permission, unauthorized, role, user, devise
boundary: "NOT product access, NOT API rate limiting, NOT payment authorization"
---

# Auth & Users Domain — Deep Dive

## Authentication

Solidus uses Devise for authentication (plugged via `spree_auth_devise` or custom):
- Session-based for web (cookies)
- Token-based for API (`Spree.user_class.generate_spree_api_key!`)
- API auth via `X-Spree-Token` header or `?token=` param

## Authorization (CanCanCan)

`ability.rb` defines permissions using CanCanCan:
- `Spree::Ability` — base ability class, checks user roles
- 13 permission sets in `permission_sets/`:
  - `super_user.rb` — all permissions
  - `default_customer.rb` — read own orders, manage own account
  - `order_display.rb` / `order_management.rb` — order access
  - `stock_display.rb` / `stock_management.rb` — inventory access
  - `product_display.rb` / `product_management.rb` — catalog access

## Roles

- `Spree::Role` — role model
- `Spree::RoleUser` — join table (user has_many roles)
- Default roles: `admin`, custom roles per permission set

## API Authentication (api/base_controller.rb)

- `before_action :authenticate_user` — checks token validity
- Returns 401 on invalid/expired token
- API keys stored on user model

## Database Schema (spree_users table)

```
email:                    string     — login identifier
crypted_password:         string     — hashed password (Devise)
login_count:              integer    — total successful logins
failed_login_count:       integer    — failed attempts (lockout tracking)
last_request_at:          datetime   — session activity tracking
current_login_at:         datetime   — current session start
last_login_at:            datetime   — previous session start
current_login_ip:         string     — current IP
last_login_ip:            string     — previous IP
persistence_token:        string     — "remember me" token
single_access_token:      string     — API key (X-Spree-Token header)
perishable_token:         string     — password reset token
```

Diagnostic queries:
- Locked accounts: `SELECT email, failed_login_count FROM spree_users WHERE failed_login_count > 5`
- Recent login failures: `SELECT email, last_login_at, failed_login_count FROM spree_users WHERE failed_login_count > 0 ORDER BY last_login_at DESC LIMIT 20`

## Common Failure Modes

1. **Session expiry**: Token TTL change or session store (Redis) down → mass logout
2. **Permission escalation**: Role misconfiguration giving customers admin access
3. **API key leak**: Token exposed in logs or client-side code
