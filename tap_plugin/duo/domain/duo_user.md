# Duo User

## Blurb

A person's account in one Duo tenant — who gets challenged, with what status, and whether anything is enrolled to challenge them with.

## Purpose

The two questions an operator asks of MFA daily are both about users: *who is not actually doing MFA* (status `bypass`, or no enrolled authenticator, or an outstanding bypass code) and *who is locked out*. Both are fields or one hop from this node. It is also the far end of every authenticator edge, so 'which factors does this person have' is a one-hop read.

## Goals

- Make bypass, lockout and non-enrollment answerable as a filter.
- Anchor every authenticator and bypass code to a person.
- Carry the email a future neutral person node converges on, without keying on it.

## Identity

Natural key: **`user_id`**, Duo's `DU…` id, unique across Duo and stable across renames. Users are observed, never designed — a design has no reason to seed an individual user — so the id is `CREATE_REQUIRED`. Username is a mutable attribute and is deliberately not the key.

Stamped `duo.surface: directory` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not a person.** A Duo user is one identity source's record; converging it with the same human's Okta user or GitHub account needs a neutral person type that no substrate owns yet (named as a gap in the spec).
- **Not aliases.** Up to four aliases per user; a field-level concern for a collector, not modelled.
- **Bypass codes are not a field here.** They have their own identity, expiry and issuer — see [`duo_bypass_code`](duo_bypass_code.md).
- **Not the authentication log.** `last_login` is the one summary this node carries.

## Neutrality

**Vendor-specific.** The status vocabulary (`bypass` especially) and the enrollment model are Duo's. The neutral half — a human — is the gap.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoUser` (id `user_id`; email, status, is_enrolled, last_login, last_directory_sync) and the `(:Human)-[:IDENTITY_DUO]->(:DuoUser)` link by email.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoUser` with `status` and `is_enrolled`, the two fields its example queries lead with.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Users (`GET /admin/v1/users`), status values.

## Fields

- `user_id` — Duo's user id (`DU…`, 20 characters). The natural key.
- `username` — The username Duo matches at primary authentication. Display name of the node. Aliases are not modelled.
- `realname` — The user's full name as Duo holds it.
- `email` — The user's email as Duo holds it. Not identity (email is not identity): it is the fact a future neutral person node would match on, as Cartography's `Human` does, and nothing here keys on it.
- `status` — Duo's user status, as reported: `active` (must complete MFA), `bypass` (skips MFA), `disabled`, `locked out`, or `pending deletion`. Blank means not observed. `bypass` is the single most important value on this node for a FedRAMP reviewer.
- `is_enrolled` — Whether the user has at least one authenticator enrolled (Duo's `is_enrolled`). Null means not observed — never read it as false.
- `last_login` — Duo's last successful login for the user. Null means not observed, or never logged in; Duo reports null for both, so a collector records which.
- `last_directory_sync` — When a directory sync last updated the user; null for a user managed by hand in Duo, or not observed.
- `created` — When the user was created in Duo.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
