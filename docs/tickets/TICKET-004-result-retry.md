# TICKET-004 — Retried result reports change ratings twice

**Severity:** High

Clients retry after timeouts. Posting the identical match result twice currently increases the winner's rating twice and decreases the loser's rating twice.

**Acceptance criteria:** a match result is applied once; a retry returns a clear, stable response; conflicting results for a completed match are rejected.
