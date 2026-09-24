# Duo Account

## Blurb

One Duo tenant: the thing an Admin API application's `api_hostname` names, and the outer box every other Duo object sits inside.

## Purpose

Everything Duo does happens inside an account — users are enrolled in one, applications are protected by one, policies are defined in one, administrators administer one. For a FedRAMP operator the account also carries the facts a reviewer asks first: which service it is (commercial Duo or Duo Federal, the FedRAMP-authorized one), which edition (it decides which policy controls even exist), and the account-wide settings that govern bypass and lockout. It is the root of the delete tree: every object Duo keeps per account retires with it.

## Goals

- Let a design place a Duo tenant before any access exists.
- Carry the edition and the account-wide bypass and lockout settings a reviewer checks first.
- Be the containment root for every Duo object the corpus models.

## Identity

Natural key: **`name`**. A design-phase account has no observed identifier, so its name is the only fact it carries. `api_hostname` is the real stable identifier; the key moves to it when `req-duo-collector` makes it observable (spec: `req-duo-account`). Two accounts with the same name would collide today — acceptable while every account on a grid is a designed one.

No default dimension; the seeding bundle or collector stamps `dcom` per node.

## Boundaries

- No free-form `configuration` field: the Admin API settings response has no reader here and can carry secret material or personal data, so only promoted columns are stored.
- **Not the Duo Federal authorization itself.** That the service is FedRAMP-authorized is a fact about Duo the vendor; this node records only which edition the account runs.
- **Not billing or telephony credit.** Operational, event-shaped, and not asked of the account graph.
- **Not MSP subaccounts.** The Accounts API integration type can no longer be created (Admin API, 2026-06-11); parent/child accounts are left out until a real consumer has one.
- **Not the logs.** Authentication, telephony and administrator logs are event streams; the grid's own history answers 'when did this change', and a future collector summarises logs onto fields (e.g. `duo_user.last_login`).

## Neutrality

**Vendor-specific.** Every MFA service has a tenant, but the edition ladder, the settings and the `api_hostname` shape are Duo's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoApiHost`, keyed on the API hostname, is Cartography's account node; borrowed as the future key.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoAccount` with `api_hostname` and `account_type`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Settings (`GET /admin/v1/settings`: `helpdesk_bypass`, `lockout_threshold`, `inactive_user_expiration`) and the edition-dependent policy sections.

## Fields

- `name` — The account's name as the design or the Admin Panel gives it. The natural key today, because a design knows nothing else about an account before access exists.
- `api_hostname` — The account's API hostname — `api-XXXXXXXX.duosecurity.com` for a commercial account, `api-XXXXXXXX.duofederal.com` for Duo Federal. Blank until observed. The stable identifier the key moves to when a collector lands.
- `edition` — The Duo edition the account is licensed for: `essentials`, `advantage`, `premier` (commercial), `federal_mfa`, `federal_access` (Duo Federal, the FedRAMP-authorized service), or `other`. Blank means not observed. Edition decides which policy sections exist at all (Essentials has seven; Advantage and Premier have all).
- `helpdesk_bypass` — Whether Help Desk administrators may generate bypass codes: `allow` (Duo's default), `limit`, or `deny`. From the account settings. Blank means not observed. A FedRAMP reviewer asks this before anything else about bypass.
- `lockout_threshold` — Consecutive failed authentications before a user's status becomes `locked out`. Null means not observed.
- `inactive_user_expiration` — Days of inactivity after which Duo deletes a user, from the account settings. Null means not observed; Duo reports null as well when the setting is off, so a collector must record which it saw.
