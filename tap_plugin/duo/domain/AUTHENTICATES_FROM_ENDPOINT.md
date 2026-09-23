# AUTHENTICATES_FROM_ENDPOINT

## Blurb

A user has authenticated from this device.

## Purpose

Connects device posture to people: which users reach applications from unencrypted or untrusted devices.

## Goals

- Tie endpoint posture to the users behind it.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not every authentication.** The edge records that the association exists, not how often.
- **Matched by email in Duo's data**, so an endpoint whose email matches no user has no edge — absence is not 'no user'.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `HAS_DUO_ENDPOINT`, matched by email.

## Endpoints

- **Sources:** `duo__duo_user`.
- **Targets:** `duo__duo_endpoint`.
- **Dimensions:** `duo.surface: device_trust`.
- **Properties:** none.
