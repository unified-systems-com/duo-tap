# ENROLLS_HARDWARE_TOKEN

## Blurb

A user or administrator holds this OTP hardware token.

## Purpose

Tokens are assigned, often to administrators; this edge is how the OTP share of the factor mix is counted per principal.

## Goals

- Attribute each token to its holder.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not containment.** A token is reassignable and outlives its holder.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `HAS_DUO_TOKEN`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — token `users` list; administrator `hardtoken`.

## Endpoints

- **Sources:** `duo__duo_user`, `duo__duo_administrator`.
- **Targets:** `duo__duo_hardware_token`.
- **Dimensions:** `duo.surface: authenticators`.
- **Properties:** none.
