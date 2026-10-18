# TICKET-002 — Queue workers can create duplicate matches

**Severity:** Critical

When two application instances call `POST /queue/match` simultaneously for the same company and mode, the same players can appear in multiple matches. This is a race condition in the Redis queue workflow.

**Acceptance criteria:** two players can be claimed by only one match; concurrent workers receive either distinct players or an insufficient-player response; the solution works across processes.
