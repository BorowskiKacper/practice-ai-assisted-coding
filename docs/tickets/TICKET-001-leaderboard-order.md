# TICKET-001 — Leaderboard shows the weakest player at rank one

**Severity:** Medium

For a company and mode with ratings 1200, 1000, and 800, the leaderboard endpoint returns 800 first. Rankings should put the highest rated player first, with deterministic handling for ties.

**Acceptance criteria:** the endpoint returns ratings in descending order and preserves the existing company/mode scope.
