# ENFORCES_POLICY

## Blurb

An application runs under this policy — for everyone, or for certain groups.

## Purpose

An application's strength is its policy. The edge carries *how* the policy applies, because 'this policy applies to Okta' and 'this policy applies to the contractors group in Okta' are different claims, and a view that cannot tell them apart overstates coverage.

## Goals

- Say which applications each policy reaches, and for whom.
- Keep Global-Policy inheritance derived rather than stored.

## Identity

Assigned uuid7 id; edges carry no natural key today (tap#458). At most one edge of this type between one pair is intended.

## Boundaries

- **Not the effective per-user policy.** Derived from Global → app → group stacking.
- **No Global Policy edges.** Every application without an `app` edge inherits it; storing that would be a second copy of an implicit fact.

## Neutrality

Vendor-specific.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Policies v2 `policy_applies_to` (app_name, app_integration_key, apply_type app/group_app, group_position, groups) and `apply_to_apps` / `apply_to_groups_in_apps`.
- Cartography 0.141.0 `cartography/models/duo/` (2026) and DuoHound (github.com/julian1j/DuoHound @ 50cccb1, 2026-02-10), a BloodHound OpenGraph collector — no policy edges.

## Endpoints

- **Sources:** `duo__duo_application`.
- **Targets:** `duo__duo_policy`.
- **Dimensions:** `duo.surface: access`.
- **Properties:** `apply_type` (required: `app` or `group_app`), `group_names` (group policy targets), `group_position` (group-policy stack order).
