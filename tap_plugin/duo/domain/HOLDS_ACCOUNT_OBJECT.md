# HOLDS_ACCOUNT_OBJECT

## Blurb

A Duo account holds one of its objects — the tenancy relationship, and the account's delete tree.

## Purpose

Every Duo object exists in exactly one account; which one is the first filter on every page ('this account's applications'). One edge carries it because it is one relationship: the Admin API returns every one of these lists per account, and they all end when the account does. Splitting it per target type would be eight names for the same fact.

## Goals

- Scope any Duo object to its account in one hop.
- Give the account a containment declaration its whole tree retires through.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not physical or network containment.** Tenancy only.
- **Not for WebAuthn credentials or bypass codes.** They are per-principal and retire with their user — see [`ENROLLS_WEBAUTHN_CREDENTIAL`](ENROLLS_WEBAUTHN_CREDENTIAL.md), [`HOLDS_BYPASS_CODE`](HOLDS_BYPASS_CODE.md).

## Neutrality

Vendor-specific (both ends are Duo types).

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `RESOURCE` from every Duo node to `DuoApiHost`: the same single tenancy relationship, pointing the other way.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoContains` from `DuoAccount` to every object.

## Endpoints

- **Sources:** `duo__duo_account`.
- **Targets:** `duo__duo_user`, `duo__duo_group`, `duo__duo_application`, `duo__duo_policy`, `duo__duo_administrator`, `duo__duo_phone`, `duo__duo_hardware_token`, `duo__duo_endpoint`.
- **Dimensions:** none — the edge spans every Duo surface, so no single `duo.surface` value is true of it.
- **Properties:** none.
