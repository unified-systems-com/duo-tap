# ENROLLS_WEBAUTHN_CREDENTIAL

## Blurb

A user or administrator has this WebAuthn credential enrolled.

## Purpose

The phishing-resistant half of the factor mix, per principal. For administrators it is the privileged-access question.

## Goals

- Count phishing-resistant enrollment per principal.
- Retire credentials with their owner.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **One owner only**, which is what makes it containment.

## Neutrality

Neutral-capable (WebAuthn is a standard); vendor-specific endpoints.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `HAS_DUO_WEB_AUTHN_CREDENTIAL`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — `webauthncredentials` on users and administrators.

## Endpoints

- **Sources:** `duo__duo_user`, `duo__duo_administrator`.
- **Targets:** `duo__duo_webauthn_credential`.
- **Dimensions:** `duo.surface: authenticators`.
- **Properties:** none.
