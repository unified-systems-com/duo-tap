# MEMBER_OF_GROUP

## Blurb

A Duo user belongs to a Duo group.

## Purpose

Access restriction (`PERMITS_GROUP`) and group policies both name groups, so 'can this user reach this application, under which policy' is a walk through membership.

## Goals

- Make access and group-policy reach traversable from a user.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not directory-sync provenance** (Backlog).

## Neutrality

Neutral in shape; vendor-specific endpoints.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `MEMBER_OF_DUO_GROUP`.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoMemberOf`.

## Endpoints

- **Sources:** `duo__duo_user`.
- **Targets:** `duo__duo_group`.
- **Dimensions:** `duo.surface: directory`.
- **Properties:** none.
