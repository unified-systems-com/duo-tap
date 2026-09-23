# PERMITS_GROUP

## Blurb

An application admits this group's members.

## Purpose

Who can authenticate to an application is `user_access` plus, when it is `PERMITTED_GROUPS`, this list. Together they answer 'who can reach Okta through Duo'.

## Goals

- Resolve application reach through groups.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **No per-user access edges.** Derivable from `user_access` and membership; DuoHound materialises them, which multiplies users by applications.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoHasAccessTo` from groups (and, materialised, from users).
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — `groups_allowed`, `user_access`.

## Endpoints

- **Sources:** `duo__duo_application`.
- **Targets:** `duo__duo_group`.
- **Dimensions:** `duo.surface: access`.
- **Properties:** none.
