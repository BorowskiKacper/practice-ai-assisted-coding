# TICKET-003 — Match detail can cross company boundaries

**Severity:** High

An authenticated caller scoped to one company can request a known match ID from another company through the company match-detail route and receive it.

**Acceptance criteria:** the route returns a match only when its company matches the route's `company_id`; a cross-company request returns 404.
