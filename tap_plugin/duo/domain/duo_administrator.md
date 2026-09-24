# Duo Administrator

## Blurb

A login to the Duo Admin Panel, with a role — the people who can change who has to do MFA.

## Purpose

Whoever administers Duo can put any user in bypass, issue bypass codes, or weaken the Global Policy. The administrator list, their roles, their status and — critically — whether *they* use a phishing-resistant factor is a standing FedRAMP question (privileged access, AC-2/IA-2(1)). Duo administrators are distinct accounts from Duo users, so they get their own node.

## Goals

- List every administrator with role and status.
- Show which administrators authenticate with WebAuthn versus phone or token.
- Keep administrators separate from users, as Duo does.

## Identity

Natural key: **`admin_id`**. Observed-only.

Stamped `duo.surface: administration` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not a separate role node.** Roles are a fixed vocabulary plus custom names that nothing else points at; a field (node test: nothing needs to point at it).
- **Not administrative units.** Backlog; the boolean records that a restriction exists.
- **Not the administrator log.**

## Neutrality

**Vendor-specific.** Role names and statuses are Duo's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoAdmin` with `role`, `status` and `DuoAdminTo` → account.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Administrators (`GET /admin/v1/admins`): role, role_id, status (Active/Disabled/Expired/Pending Activation), restricted_by_admin_units, hardtoken, webauthncredentials.
- Cartography 0.141.0 `cartography/models/duo/` (2026) — does not model administrators.

## Fields

- `admin_id` — Duo's administrator id (`DE…`). The natural key.
- `name` — The administrator's name.
- `email` — The administrator's email — their Admin Panel login. Not identity: the person behind the login is reached by `HELD_BY_HUMAN__identity_core` to `identity_core__human` (declared in `OUTBOUND_EDGES`), never by matching this address.
- `role` — The administrator's role as reported: `Owner`, `Administrator`, `Application Manager`, `User Manager`, `Security Analyst`, `Help Desk`, `Billing`, `Read-only`, or a custom role's name. Kept as a string because custom roles exist.
- `status` — As reported: `Active`, `Disabled`, `Expired` (blocked for inactivity), or `Pending Activation`. Blank means not observed.
- `last_login` — The administrator's last Admin Panel login.
- `restricted_by_admin_units` — Whether the administrator's reach is limited to administrative units. Null means not observed.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
