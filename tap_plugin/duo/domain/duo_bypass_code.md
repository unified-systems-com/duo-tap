# Duo Bypass Code

## Blurb

A Duo bypass code a user holds right now — MFA satisfied by a passcode, no authenticator needed.

## Purpose

Bypass codes are the quiet MFA exemption: a user with `active` status and a strong enrolled factor can still sign in with a code a help-desk administrator read to them over the phone. A FedRAMP reviewer wants every outstanding code, how long it lives, and who issued it. A count on the user would hide all three.

## Goals

- List every outstanding bypass code with expiry, remaining uses and issuer.
- Make 'codes that never expire' a filter.

## Identity

Natural key: **`bypass_code_id`**. Observed-only; contained by its user.

Stamped `duo.surface: authenticators` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Never the code value.** Listing codes returns ids, not values; the value would be a live credential.
- **Not the issuing event.** Who issued it is kept as reported text; the administrator log is out of scope.

## Neutrality

**Vendor-specific.** Recovery codes exist everywhere; issuance by help desk with reuse counts is Duo's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Bypass codes (`GET /admin/v1/bypass_codes`, `GET /admin/v1/users/[user_id]/bypass_codes`): bypass_code_id, created, expiration, reuse_count, admin_email.
- Cartography 0.141.0 `cartography/models/duo/` (2026) and DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — neither models bypass codes; this corpus is ahead of both here, because the FedRAMP question needs them.

## Fields

- `bypass_code_id` — Duo's id for the code. The natural key. The code itself is never stored.
- `created` — When the code was issued.
- `expiration` — When the code expires. On an observed code, null is Duo's own null: the code does not expire. (A code node exists only once observed, so null here never means 'not observed'.)
- `reuse_count` — Remaining uses as Duo reports it; Duo's semantics for 0/null (unlimited) are recorded as reported, not reinterpreted.
- `admin_email` — The email of the administrator who created the code, as reported. Attribution text, not a link: email is not identity, so no edge to an administrator is drawn from it.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
