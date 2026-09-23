# REQUESTS_SECOND_FACTOR

## Blurb

A system sends its users to Duo for MFA through this application — Okta, a VPN, SSH, RDP.

## Purpose

This is the edge that connects Duo to everything it protects, including Okta: `okta_org REQUESTS_SECOND_FACTOR duo_application(type okta)` is 'Okta uses Duo as an authenticator', which is also 'Duo protects Okta'. The properties separate shape from severity: a client in `safe` fail mode skips MFA whenever Duo is unreachable, which is a very different claim from 'MFA is enforced'.

## Goals

- Link Duo to the systems it protects without depending on their plugins.
- Record the integration mechanism and the fail mode, which decides whether an outage is an MFA bypass.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not SSO.** Duo SSO signing users *into* a service provider is [`ISSUES_SSO_ASSERTION`](ISSUES_SSO_ASSERTION.md).
- **Not a closed list of sources.** Any protected system may appear; the okta plugin (or a design) creates the edge from its own node.

## Neutrality

**Neutral in shape** — any MFA service is called this way — with a Duo target. When a neutral MFA-service type exists in a substrate, this edge's target is the candidate to generalise.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Integration Types (`okta`, `radius`, `ldapproxy`, `unix`, `rdp`, `websdk`, `authapi`).
- Duo Unix and Authentication Proxy documentation (duo.com/docs/duounix, duo.com/docs/authproxy-reference, retrieved 2026-09-22) — `failmode = safe | secure`.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — models applications but not what they protect; this edge is new.

## Endpoints

- **Sources:** **open** (omitted) — see the description.
- **Targets:** `duo__duo_application`.
- **Dimensions:** `duo.surface: access`.
- **Properties:** `mechanism` (how the system reaches Duo), `fail_mode` (`safe` = fail open, `secure` = fail closed; absent = not observed).
