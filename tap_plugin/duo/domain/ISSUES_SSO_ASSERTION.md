# ISSUES_SSO_ASSERTION

## Blurb

A Duo SSO application signs users into this service provider.

## Purpose

Duo SSO makes Duo an identity provider, not just a second factor. When an Okta org (or any service) trusts Duo SSO, compromise of Duo is compromise of that service — the reverse direction of `REQUESTS_SECOND_FACTOR`, and worth drawing separately.

## Goals

- Show which services trust Duo as their identity provider.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not the SAML metadata** (entity ids, certificates, ACS URLs). Backlog with Duo SSO depth.

## Neutrality

Neutral in shape (any IdP issues assertions); a neutral service-provider type would be its natural target (gap).

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Integration Types `sso-generic`, `sso-oidc-generic`.

## Endpoints

- **Sources:** `duo__duo_application`.
- **Targets:** **open** (omitted) — see the description.
- **Dimensions:** `duo.surface: access`.
- **Properties:** `protocol` (required: `saml` or `oidc`).
