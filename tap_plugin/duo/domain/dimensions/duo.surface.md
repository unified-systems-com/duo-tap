# `duo.surface`

## Blurb

Which part of Duo an object or relationship belongs to — directory, authenticators, access, administration, or device trust — stamped by default on every Duo type except the account.

## Purpose

A Duo page groups its content by these five surfaces, and so does Duo's own Admin Panel (Users, 2FA Devices, Applications and Policies, Administrators, Endpoints). One filter selects a surface across several types — "every authenticator of any kind" — without enumerating type slugs, which is what a factor-mix view needs.

## Goals

- Select a Duo surface across types with one dimension filter.
- Mirror the Admin Panel's own sections, so the vocabulary is the one an operator already speaks.

## Identity

Key `duo.surface`, namespaced by the vendor vocabulary it describes. Values are a closed set of five. Declared as a type default, so it is a property of the type, not of an observation; it never duplicates the entity type (several types share each value).

## Boundaries

- **Not the account.** `duo__duo_account` spans every surface and carries no value.
- **Not dcom or environment.** Those are observation facts and are never type defaults.
- **Not tenancy.** Which account an object is in is the `HOLDS_ACCOUNT_OBJECT__duo` edge, which carries no surface for the same reason.

## Neutrality

Vendor-specific: the grouping follows Duo's Admin Panel.

## Observability

Declared, never fetched: applied from `DEFAULT_DIMENSIONS` and edge `default_dimensions` at creation.

## Authoritative Source

- **Source:** Duo Admin Panel navigation and Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** as documented
- **Retrieved:** 2026-09-22

## Prior Art

- github_core's `github.surface` (2026-09) — the same device: a vendor-namespaced surface dimension over many types.

## Values

- `directory` — Users and groups — who Duo knows about.
- `authenticators` — Phones, hardware tokens, WebAuthn credentials and bypass codes — what a principal proves possession with.
- `access` — Applications and policies — what Duo protects and under which rules.
- `administration` — Administrators — who can change the above.
- `device_trust` — Endpoints — the devices authentications come from and their posture.
