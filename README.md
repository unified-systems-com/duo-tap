# duo-tap

Duo multi-factor authentication as grid vocabulary: the account, its users and groups, their authenticators (phones, hardware tokens, WebAuthn credentials, bypass codes), the protected applications and the policies they enforce, administrators and endpoints — and the /duo operator page over them.

## What this plugin owns

Eleven node types — `duo__duo_account`, `duo__duo_user`, `duo__duo_group`, `duo__duo_phone`, `duo__duo_hardware_token`, `duo__duo_webauthn_credential`, `duo__duo_bypass_code`, `duo__duo_application`, `duo__duo_policy`, `duo__duo_administrator`, `duo__duo_endpoint` — and eleven edge types between them, including two with an open end so another plugin's system (an Okta org, a VPN) can point at Duo without Duo depending on it: `REQUESTS_SECOND_FACTOR__duo` and `ISSUES_SSO_ASSERTION__duo`.

The `/duo` page is the operator's front page for one account: the account map (icon-badge graph, `account-map.js`), a posture strip (MFA coverage, factor mix, access, administration, device trust), and tables for protected applications, policy assignments, policies, users not doing MFA, bypass codes, administrators and device health. `?account=<account name>` picks the account; without it the page shows the only account.

No collector yet: every node is designed (seeded by an instance plugin) until `req-duo-collector` lands.

## Read first

- `specs/spec-duo-v0.md` — the spec: requirements, prior art (Cartography's Duo module, DuoHound), and what was left out.
- `tap_plugin/duo/domain/` — one article per node, edge and dimension: what the concept is in Duo, its identity, its boundaries.

## Stand it up

From a TAP core checkout:

```bash
scripts/spawn-session.sh <label> cli --from 'git+https://github.com/unified-systems-com/duo-tap@<rev>#ci' --dev-plugins duo
```
