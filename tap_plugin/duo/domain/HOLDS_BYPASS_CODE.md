# HOLDS_BYPASS_CODE

## Blurb

A user holds this bypass code.

## Purpose

Makes 'which users can skip MFA with a code right now' one hop, beside the users whose status is `bypass`.

## Goals

- Attribute every outstanding code to its user.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not issuance.** The issuing administrator is text on the code, not an edge.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — `GET /admin/v1/users/[user_id]/bypass_codes`.

## Endpoints

- **Sources:** `duo__duo_user`.
- **Targets:** `duo__duo_bypass_code`.
- **Dimensions:** `duo.surface: authenticators`.
- **Properties:** none.
