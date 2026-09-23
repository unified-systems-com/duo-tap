# Duo Policy

## Blurb

A named set of Duo access rules — which factors, what happens to unenrolled users, which devices and networks — applied to applications and to groups within them.

## Purpose

Policy is where Duo's security posture actually lives. The same application can be strong or weak depending entirely on the policy it enforces: allowing SMS, letting unenrolled users through (`no-mfa`), remembering devices for thirty days. A FedRAMP operator reviews the Global Policy and every override, and needs to see which applications each one reaches.

## Goals

- Hold each policy's load-bearing settings as fields (new-user behaviour, allowed methods) and the rest verbatim.
- Make the Global Policy distinguishable from overrides.
- Be the target of `ENFORCES_POLICY`, so 'which applications run under this policy' is one hop.

## Identity

Natural key: **`name`**. Duo itself permits duplicate policy names; the design-phase key does not, and `policy_key` replaces it with the collector.

Stamped `duo.surface: access` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not the effective policy.** Duo evaluates Global → application policy → group policy section by section; the merged result per user and application is derived, not stored.
- **Not a policy history.** The grid's field history covers it.
- **No edge to the Global Policy from every application.** Inheritance is implicit in Duo and derived here; storing it would be the same fact twice.

## Neutrality

**Vendor-specific.** Conditional-access policy is general; Duo's sections and method names are not.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Policies v2 (`GET /admin/v2/policies`): policy_key, policy_name, is_global_policy, sections (Policy Section Data), policy_applies_to.
- Cartography 0.141.0 `cartography/models/duo/` (2026) and DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — neither models policy; this corpus adds it because a front page without it cannot say whether an application is protected well.

## Fields

- `name` — The policy's name (`policy_name`). The natural key while policies are designed. Duo does not require names to be unique; the design-phase key does.
- `policy_key` — Duo's policy key (`PO…`). Blank until observed.
- `is_global` — True for the account's Global Policy, which every application inherits section by section unless an application or group policy overrides it. Null means not observed.
- `new_user_behavior` — The New User Policy: what happens to an unenrolled user after primary authentication — `enroll` (Duo's default), `no-mfa` (let them in without MFA), or `deny`. Blank means not observed, or the section is inherited. `no-mfa` is a finding in any FedRAMP environment.
- `allowed_auth_methods` — The Authentication Methods section's allowed list, as Duo names methods: `duo-push`, `duo-passcode`, `webauthn-roaming`, `webauthn-platform`, `hardware-token`, `sms`, `phonecall`, `smart-card` (Duo Federal only), `bypass`, and the passwordless `-pwl` variants. Null means not observed or inherited; an empty list means nothing is allowed.
- `sections` — The policy's section data from the Policies API v2 verbatim (`authentication_methods`, `new_user`, `remembered_devices`, `duo_desktop`, `trusted_endpoints`, `authorized_networks`, `user_location`, `screen_lock`, `operating_systems`, `browsers`, …). Only sections the policy sets are present; an absent section is inherited. Empty means not observed.
- `tags` — TAP's tag map; derived annotations a collector or a design writes beside the observed fields.
