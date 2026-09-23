# ENROLLS_PHONE

## Blurb

A user or administrator has this phone enrolled.

## Purpose

Factor mix per principal: which users and administrators rely on a phone, and — through its capabilities — on Push versus SMS and voice.

## Goals

- Make a principal's phone factors one hop away.
- Represent a shared phone once.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not containment.** A shared phone must not retire with the first user deleted.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `HAS_DUO_PHONE`.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoHasMFADevice`; one edge per authenticator kind here instead, because the kinds differ in strength.

## Endpoints

- **Sources:** `duo__duo_user`, `duo__duo_administrator`.
- **Targets:** `duo__duo_phone`.
- **Dimensions:** `duo.surface: authenticators`.
- **Properties:** none.
