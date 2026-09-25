# Duo WebAuthn Credential

## Blurb

A FIDO2/WebAuthn credential registered to one Duo user or administrator: the phishing-resistant factor.

## Purpose

FedRAMP 20x and OMB M-22-09 push toward phishing-resistant MFA; in Duo that means WebAuthn. Counting who has one — and which administrators do not — is the most direct measure of that posture Duo exposes. A credential belongs to exactly one principal and retires with it.

## Goals

- Count phishing-resistant enrollment by user and by administrator.
- Separate roaming security keys from platform authenticators.

## Identity

Natural key: **`webauthnkey`**. Observed-only. Contained by its user (or administrator) — it never outlives them.

Stamped `duo.surface: authenticators` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not the attestation or public key.** Not exposed by the Admin API and not needed.
- **Not the legacy U2F tokens** (`u2ftokens`), which Duo has retired in favour of WebAuthn.

## Neutrality

**Neutral-capable.** WebAuthn is a W3C standard; any MFA service holds credentials of the same shape. Vendor-specific here only in id and label.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoWebAuthnCredential` (webauthnkey, credential_name, label, date_added) and `HAS_DUO_WEB_AUTHN_CREDENTIAL`.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoWebAuthnCredential` with `authenticator_type`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — WebAuthn credentials in the user and administrator responses (`webauthncredentials`, including `date_last_used`).

## Fields

- `webauthnkey` — Duo's credential key (`WA…`). The natural key.
- `credential_name` — The name the user gave the credential (e.g. `YubiKey C`).
- `label` — Duo's kind label, e.g. `Security Key` (roaming) or `Touch ID` / `Windows Hello` (platform). The roaming/platform split in the factor mix reads from here.
- `date_added` — When the credential was enrolled.
- `date_last_used` — When the credential was last used; null if never used or not observed.
