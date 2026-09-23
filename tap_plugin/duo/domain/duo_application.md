# Duo Application

## Blurb

Something Duo protects — or something that holds keys to Duo itself. The Admin Panel calls these applications; the API calls them integrations.

## Purpose

Applications are the front page of Duo: each one is a system that sends its users to Duo for a second factor (Okta, a VPN, SSH hosts, RDP) or that Duo SSO signs users into. For each, an operator needs who may use it and which policy it enforces. Admin API applications are different in kind — they are credentials *to* Duo — and their granted permissions are the most sensitive configuration in the account.

## Goals

- List every protected application with its type, user access and policy.
- Make Admin API applications and their grants visible as the standing credentials they are.
- Be the Duo end of the Okta relationship without depending on the okta plugin.

## Identity

Natural key: **`name`** — the design names the Okta application before it exists. `integration_key` is the stable id; the key moves to it with the collector. The secret key (`skey`) is never stored.

Stamped `duo.surface: access` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not the protected system.** Okta, a Linux host, a VPN appliance are other plugins' nodes; they point here with [`REQUESTS_SECOND_FACTOR`](REQUESTS_SECOND_FACTOR.md).
- **Not the secret key.** A live credential.
- **Not the legacy per-application enrollment and IP-allowlist fields** Duo has replaced with policy.
- **Not the service-provider metadata of a Duo SSO app** (ACS URLs, certificates); Backlog with Duo SSO depth.

## Neutrality

**Vendor-specific.** 'An application protected by MFA' is general; the integration types and Admin API grants are Duo's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoApplication` (type, integration_key) and `DuoHasAccessTo` from `user_access`/`groups_allowed`; borrowed the access semantics, rejected per-user access edges (derivable from `user_access` plus membership).
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Integrations (v3): `integration_key`, `type` (Integration Types list), `user_access`, `groups_allowed`, `adminapi_*` permission flags, `self_service_allowed`.
- Cartography 0.141.0 `cartography/models/duo/` (2026) — has no application node; its Duo module models only identities and devices, which is the gap this type fills.

## Fields

- `name` — The application's name in Duo. The natural key while applications are designed.
- `integration_key` — The integration key (`DI…`), Duo's stable id for the application. Blank until observed. The secret key is never stored.
- `integration_type` — Duo's integration type string, as reported: e.g. `okta` (Duo as Okta's authenticator), `sso-generic` / `sso-oidc-generic` (Duo SSO), `adminapi`, `authapi`, `websdk`, `rdp`, `unix`, `radius`, `ldapproxy`. An open set Duo extends; kept as a string, not an enum.
- `user_access` — Who may authenticate: `ALL_USERS`, `NO_USERS`, or `PERMITTED_GROUPS` (only members of the groups on `PERMITS_GROUP`). Blank means not observed.
- `adminapi_permissions` — For an `adminapi` application only: the permissions granted, by Duo's flag name (e.g. `adminapi_read_log`, `adminapi_read_resource`, `adminapi_write_resource`, `adminapi_admins`, `adminapi_integrations`, `adminapi_settings`). Null on other types or when not observed. An Admin API application is a standing credential to the MFA system itself; its grants are the blast radius.
- `self_service_allowed` — Whether users may manage their own devices through the self-service portal from this application. Null means not observed.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
