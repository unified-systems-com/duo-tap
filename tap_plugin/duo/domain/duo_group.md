# Duo Group

## Blurb

A named set of Duo users — the unit applications are restricted to and group policies target.

## Purpose

Groups are how Duo expresses 'who may use this application' (`PERMITTED_GROUPS` user access) and 'which users get this policy in this application' (group policies). A group's own status can also bypass or disable every member at once, which a user-by-user view never shows.

## Goals

- Be the target of application access restriction and of group policies.
- Carry the group status that can exempt a whole population from MFA.

## Identity

Natural key: **`name`** — a design knows a group's name before any exists. `group_id` is the stable id; the key moves to it with the collector. Names are unique within an account but not across accounts, a known limit of the design-phase key.

Stamped `duo.surface: directory` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not directory-sync provenance.** Whether a group is synced from Active Directory, Entra ID or OpenLDAP is Backlog with directory sync.
- **Not the legacy per-group factor switches** (`push_enabled`, `sms_enabled`, …) Cartography still carries; Duo now expresses factor choice in policy.

## Neutrality

**Vendor-specific in status, neutral in shape.** Every identity system has groups; `Bypass` as a group status is Duo's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoGroup` (group_id, name, desc, status).
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoGroup`, `DuoMemberOf`, and group-to-application `DuoHasAccessTo` from `groups_allowed`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Groups (`GET /admin/v1/groups`).

## Fields

- `name` — The group's name. The natural key while groups are designed.
- `group_id` — Duo's group id (`DG…`). Blank until observed.
- `description` — The group's description (`desc`).
- `status` — The group's status as Duo reports it: `Active`, `Bypass` or `Disabled`. Blank means not observed. A group in `Bypass` exempts every member from MFA — the quieter sibling of a user in bypass.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
