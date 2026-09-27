# Duo Endpoint

## Blurb

A device Duo has seen an authentication come from, and the posture Duo Desktop reported for it.

## Purpose

Device health is half of Duo's access decision in Advantage and Premier: a policy can require Duo Desktop, disk encryption, a firewall, or a Trusted Endpoint. The endpoint inventory is how an operator sees the posture of the devices actually reaching protected applications.

## Goals

- Show device-health posture across the devices that authenticate.
- Separate Trusted Endpoints from unmanaged ones.
- Keep 'Duo Desktop not reporting' distinct from 'reporting unhealthy'.

## Identity

Natural key: **`epkey`**. Observed-only. Without Duo Desktop an epkey is an aggregate (same user, OS and browser version), so counts over endpoints are counts of records, not machines.

Stamped `duo.surface: device_trust` by default ([`duo.surface`](dimensions/duo.surface.md)).

## Boundaries

- **Not a neutral device.** The machine is `computing_core__host`; the endpoint points at it with `REPRESENTS_HOST__computing_core` (declared in `OUTBOUND_EDGES`, `req-duo-host-link`), so a Duo endpoint and an MDM or EDR record of the same machine converge. Drawn by whoever knows the match, never inferred from `device_name`.
- **Not browsers and plugins detail.** Kept out until a view needs it.

## Neutrality

**Vendor-specific record of a neutral thing.** The device is general (`computing_core__host`, reached by `REPRESENTS_HOST__computing_core`); the epkey and posture strings are Duo's.

## Observability

**Not observed.** No collector exists (`req-duo-collector` is Backlog) and no Duo credential was available, so nothing below was established by an executed call. Everything here is *documented* — read from the Admin API reference — and must be re-verified from a call when the collector lands, including what a refused or under-permissioned Admin API application actually receives.

The documented read is the Admin API with an Admin API application granted *Grant read resource* (and *Grant administrators — read* for administrators, *Grant settings* for account settings). Every field is blank/null until read; blank means not observed, never empty.

## Authoritative Source

- **Source:** Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026'
- **Version:** Admin API v1/v2/v3 handlers as documented on that page
- **Retrieved:** 2026-09-22 (read from the published documentation; no call executed — no Duo access exists)

## Prior Art

- Cartography 0.141.0 `cartography/models/duo/` (2026) — `DuoEndpoint` (epkey; device fields; disk_encryption_status, firewall_status, password_status, trusted_endpoint, health_app_client_version) and `HAS_DUO_ENDPOINT` from the user by email.
- Duo Admin API (https://duo.com/docs/adminapi), page 'Last updated: September 8th, 2026' — Endpoints (`GET /admin/v1/endpoints`).

## Fields

- `epkey` — Duo's endpoint key. The natural key. With Duo Desktop installed it identifies one device; without it, Duo aggregates by user, OS version and browser version, so one epkey is not one machine.
- `device_name` — The device name, when Duo Desktop reports one.
- `endpoint_type` — Duo's `type`: the device class (e.g. laptop, desktop, phone).
- `os_family` — Operating-system family.
- `os_version` — Operating-system version.
- `model` — Device model.
- `trusted_endpoint` — Whether the device is a Trusted Endpoint (registered through a management integration). Null means not observed.
- `disk_encryption_status` — As Duo Desktop reports it.
- `firewall_status` — As Duo Desktop reports it.
- `password_status` — As Duo Desktop reports it.
- `health_app_client_version` — The Duo Desktop version; blank means Duo Desktop is not reporting, so the posture fields are not observed rather than failing.
- `health_data_last_collected` — When Duo Desktop last reported posture.
- `last_updated` — When Duo last updated the endpoint record.
