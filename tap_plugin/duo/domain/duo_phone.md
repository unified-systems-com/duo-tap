# Duo Phone

## Blurb

A phone Duo can reach: a Duo Mobile device for Push and passcodes, or a number for SMS and voice.

## Purpose

Most Duo factors run through a phone, and the phone's capabilities are where factor strength lives: Duo Push with number matching resists casual phishing; SMS and voice do not. A phone can also be shared between users, which is why it hangs off the account and is linked to users rather than contained by one.

## Goals

- Make the factor mix — push-capable versus SMS/voice-only — countable.
- Carry the device-posture fields Duo Mobile reports (encryption, screen lock, tamper).
- Represent a shared phone once, linked to every user who enrolled it.

## Identity

Natural key: **`phone_id`**. Observed-only; `CREATE_REQUIRED`. The phone number is deliberately not stored (personal data, and nothing on the grid needs it).

Stamped `duo.surface: authenticators` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not the number.** Personal data with no consumer here.
- **Not activation or SMS-passcode delivery history** (`sms_passcodes_sent`); event-shaped.
- **Not the endpoint.** A phone is an authenticator; the laptop the user signs in from is a [`duo_endpoint`](duo_endpoint.md).

## Neutrality

**Vendor-specific.** A phone as an authenticator is general; capabilities and posture strings are Duo Mobile's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoPhone` (phone_id, activated, capabilities, encrypted, fingerprint, screenlock, tampered, platform, type, model, last_seen) and `HAS_DUO_PHONE`.
- DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — `DuoPhone` via `DuoHasMFADevice`.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Phones (`GET /admin/v1/phones`): types Mobile/Landline, capabilities auto/push/sms/phone/mobile_otp.

## Fields

- `phone_id` — Duo's phone id (`DP…`). The natural key.
- `name` — The phone's free-form name, if an administrator set one.
- `platform` — As reported: e.g. `Apple iOS`, `Google Android`, `Unknown`.
- `phone_type` — Duo's `type`: `Mobile` or `Landline`. Blank means not observed.
- `model` — The device model Duo Mobile reports.
- `capabilities` — What the phone can deliver, as reported: `push`, `sms`, `phone`, `mobile_otp`, `auto`. Null means not observed; an empty list means Duo reported none. This is the factor-mix fact: a phone with `sms`/`phone` but no `push` is a phishable factor.
- `activated` — Whether Duo Mobile is activated on the phone. Null means not observed.
- `encrypted` — Device encryption as Duo Mobile reports it (e.g. `Encrypted`, `Unencrypted`, `Unknown`).
- `fingerprint` — Biometric configuration as Duo Mobile reports it (e.g. `Configured`, `Disabled`, `Unknown`).
- `screenlock` — Screen lock as Duo Mobile reports it (e.g. `Locked`, `Unlocked`, `Unknown`).
- `tampered` — Jailbreak/root detection as Duo Mobile reports it (e.g. `Not tampered`, `Tampered`, `Unknown`).
- `last_seen` — When Duo last saw the phone.
