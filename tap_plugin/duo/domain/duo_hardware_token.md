# Duo Hardware Token

## Blurb

A physical one-time-passcode token Duo accepts: HOTP, YubiKey AES, or Duo's D-100.

## Purpose

Hardware tokens are the factor of choice where phones are not allowed — secure rooms, some federal sites — and are commonly issued to administrators. They are OTP, so phishable; an inventory of who still relies on them is part of any move to phishing-resistant MFA.

## Goals

- Inventory OTP tokens and who holds them.
- Separate OTP hardware from phishing-resistant WebAuthn keys in the factor mix.

## Identity

Natural key: **`token_id`**. Observed-only. `serial` is unique only within a token type, so it is not the key.

Stamped `duo.surface: authenticators` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not token secrets or counters.** Never readable, never wanted.
- **Not WebAuthn security keys.** A YubiKey used over WebAuthn is a [`duo_webauthn_credential`](duo_webauthn_credential.md); only YubiKey *AES OTP* mode is a hardware token.

## Neutrality

**Vendor-specific** type vocabulary over a general concept (an OTP token).

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoToken` (token_id, serial, type, totp_step) and `HAS_DUO_TOKEN`.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoToken`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Tokens (`GET /admin/v1/tokens`), types h6/h8/yk/d1.

## Fields

- `token_id` — Duo's token id (`DH…`). The natural key.
- `serial` — The token's serial number.
- `token_type` — Duo's `type`: `h6` (HOTP-6), `h8` (HOTP-8), `yk` (YubiKey AES), `d1` (Duo-D100). Blank means not observed.
- `totp_step` — The TOTP time step in seconds, for time-based tokens; null for counter-based or not observed.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
