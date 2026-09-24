# Duo Plugin Specification

**Duo as grid vocabulary, seen the way a FedRAMP operator sees it: the account (commercial Duo or Duo Federal), its users and groups, the authenticators they enroll (phones, hardware tokens, WebAuthn credentials) and the bypass codes that stand in for them, the protected applications and the policies they enforce, the administrators who can change all of it, and the endpoints authentications come from — plus a reusable `/duo` operator page over them.**

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `duo` |
| Display name | TAP Duo |
| Description | Duo multi-factor authentication as grid vocabulary: the account, its users and groups, their authenticators (phones, hardware tokens, WebAuthn credentials, bypass codes), the protected applications and the policies they enforce, administrators and endpoints — and the /duo operator page over them. |
| Kind | Leaf plugin: Duo vocabulary. Depends only on the neutral substrates `identity_core` and `computing_core` (vocabulary dependencies: a Duo user or administrator is held by an `identity_core__human`, and a Duo endpoint represents a `computing_core__host`); every other edge toward another system has an open end. Consumed by instance plugins that place Duo in a design (highbar first) and, through its open-ended edges, by any plugin whose system uses Duo (an Okta org, a VPN). |

**Default dimensions**

| Dimension | Value | Why |
| --- | --- | --- |
| `duo.surface` | `directory` (user, group) · `authenticators` (phone, hardware token, WebAuthn credential, bypass code) · `access` (application, policy) · `administration` (administrator) · `device_trust` (endpoint) | Mirrors the Admin Panel's own sections so one filter selects a surface across types (`domain/dimensions/duo.surface.md`). Edges carry the surface of the relationship; `HOLDS_ACCOUNT_OBJECT__duo` spans every surface and carries none. |
| (none on `duo__duo_account`) | | The account spans every surface. |
| `dcom`, `deployment.environment.*` | never a type default | They belong to the observation, not the type: a seeded design node is `design`, a collected one `configuration`; the seeding bundle stamps them per node. |

## Philosophy

Duo is SaaS: there is no infrastructure to model, only Duo's own object model. The corpus is the part of that model a FedRAMP 20x operator must be able to answer questions about — *who is not actually doing MFA*, *with which factors*, *under which policy*, *who can change that*, and *from what devices* — and nothing else. Duo Federal (the `federal_mfa` and `federal_access` editions) is the FedRAMP-authorized service; the account records which edition it runs because the edition decides which policy controls exist at all.

What the plugin deliberately does not do: collect (Backlog), model event streams (the authentication, telephony and administrator logs — the grid's own history answers "when did this change"), or depend on any other vendor plugin. The Okta relationship points at an open end: `REQUESTS_SECOND_FACTOR__duo` has no declared source, so an Okta org (or a VPN, or an SSH host) draws the edge from its own node without duo naming its type.

Three states hold for every observed field: blank or null means *not observed*, never *empty* and never *false*. The page and the posture strip count not-observed values as their own number (users whose enrollment was never read are listed, never assumed enrolled).

**Provenance markers:** every claim about Duo's object model here is *documented* — read from the Duo Admin API reference (page "Last updated: September 8th, 2026", retrieved 2026-09-22) and cross-checked against Cartography 0.141.0's Duo module and DuoHound (2026-02-10). None is *observed*: no Duo credential exists and no call was executed. Design nodes seeded by an instance are *designed* (`dcom: design`). The collector, when it lands, re-verifies every field from a call, including what an under-permissioned Admin API application actually receives.

**Prior art and what it changed.** Cartography's Duo module (`DuoApiHost`, `DuoUser`, `DuoGroup`, `DuoEndpoint`, `DuoPhone`, `DuoToken`, `DuoWebAuthnCredential`; `RESOURCE`, `MEMBER_OF_DUO_GROUP`, `HAS_DUO_*`, and `(:Human)-[:IDENTITY_DUO]->(:DuoUser)` by email) supplied the identity and authenticator half almost field for field, and the single tenancy edge (`RESOURCE`, here `HOLDS_ACCOUNT_OBJECT__duo` pointing the containment way). DuoHound (SpecterOps' BloodHound OpenGraph extension) added what Cartography lacks — applications, administrators and access through `user_access`/`groups_allowed` — but materialises per-user access edges (users × applications), which this corpus rejects as derivable. Neither models policies, bypass codes, or what an application protects; those three are this corpus's own, because a FedRAMP front page without them cannot say whether MFA is actually enforced. Borrowed: keys (`user_id`, `phone_id`, `token_id`, `webauthnkey`, `epkey`, api hostname), field sets, one tenancy edge. Rejected: per-user access edges, one generic `HasMFADevice` edge (the kinds differ in strength, so each gets its own), Cartography's legacy per-group factor switches, the phone number (personal data with no consumer).

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | Designable | A design can place a Duo account, its protected applications (the Okta application first), its policies and groups before any access exists. |
| 2 | MFA Truth | Bypass (by status, by group, by code), non-enrollment and not-observed enrollment are each answerable as a filter. |
| 3 | Factor Strength | The factor mix separates phishable (SMS, voice, OTP) from phishing-resistant (WebAuthn) per user and per administrator. |
| 4 | Policy Reach | Which applications run under which policy — for everyone or for which groups — and which inherit the Global Policy. |
| 5 | No Vendor Coupling | Duo links to the systems it protects and signs into without depending on their plugins. |
| 6 | Operator Front Page | A reusable `/duo` page shows one account (or picks the only one) as an operator would open it in a live FedRAMP 20x environment. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | --- | --- |
| req-duo-account | [Duo Account](#duo-account) | Implemented | `duo__duo_account` |
| req-duo-user | [Duo User](#duo-user) | Implemented | `duo__duo_user` |
| req-duo-group | [Duo Group](#duo-group) | Implemented | `duo__duo_group` |
| req-duo-phone | [Duo Phone](#duo-phone) | Implemented | `duo__duo_phone` |
| req-duo-hardware-token | [Duo Hardware Token](#duo-hardware-token) | Implemented | `duo__duo_hardware_token` |
| req-duo-webauthn-credential | [Duo WebAuthn Credential](#duo-webauthn-credential) | Implemented | `duo__duo_webauthn_credential` |
| req-duo-bypass-code | [Duo Bypass Code](#duo-bypass-code) | Implemented | `duo__duo_bypass_code` |
| req-duo-application | [Duo Application](#duo-application) | Implemented | `duo__duo_application` |
| req-duo-policy | [Duo Policy](#duo-policy) | Implemented | `duo__duo_policy` |
| req-duo-administrator | [Duo Administrator](#duo-administrator) | Implemented | `duo__duo_administrator` |
| req-duo-endpoint | [Duo Endpoint](#duo-endpoint) | Implemented | `duo__duo_endpoint` |
| req-duo-edges | [Edges](#edges) | Implemented | The eleven edge types, their endpoints, properties and dimensions |
| req-duo-articles | [Domain Articles](#domain-articles) | Implemented | One article per node, edge and dimension under `tap_plugin/duo/domain/` |
| req-duo-page | [Page: Duo](#page-duo) | Implemented | `/duo`, parameterized by `?account=`; server-side render tested; browser render not yet observed |
| req-duo-panel-posture | [Panel: Posture](#panel-posture) | Implemented | The plugin's own panel type |
| req-duo-layout-account-map | [Layout: Account Map](#layout-account-map) | In Development | Reusable layout module; never executed in a browser yet |
| req-duo-record | [CI Record and Tests](#ci-record-and-tests) | Implemented | The in-package `ci` record now seeds the page bundle |
| req-duo-collector | [Collector](#collector) | Backlog | Observe real Duo state through the Admin API |
| req-duo-person-convergence | [Person Convergence](#person-convergence) | Implemented | Users and administrators declare `HELD_BY_HUMAN__identity_core` to `identity_core__human` |
| req-duo-host-link | [Host Link](#host-link) | Implemented | `duo__duo_endpoint` declares `REPRESENTS_HOST__computing_core` to `computing_core__host` |
| req-duo-directory-sync | [Directory Sync](#directory-sync) | Backlog | Where users and groups come from |
| req-duo-admin-units | [Administrative Units](#administrative-units) | Backlog | Scoped administration |
| req-duo-sso-depth | [Duo SSO Depth](#duo-sso-depth) | Backlog | Service-provider metadata and authentication sources |
| req-duo-nongoals | [Non-Goals](#non-goals) | Proposed | What this plugin will not model |

---

### Duo Account
----
RID: `req-duo-account`

Status: `Implemented`

A Duo account: one Duo tenant (commercial or Duo Federal) that enrolls users and their authenticators, holds the protected applications and the policies they enforce, and answers second-factor challenges for them.

Everything Duo does happens inside an account — users are enrolled in one, applications are protected by one, policies are defined in one, administrators administer one. For a FedRAMP operator the account also carries the facts a reviewer asks first: which service it is (commercial Duo or Duo Federal, the FedRAMP-authorized one), which edition (it decides which policy controls even exist), and the account-wide settings that govern bypass and lockout. It is the root of the delete tree: every object Duo keeps per account retires with it.

#### Implementation

`tap_plugin/duo/models/duo_account.py` defines `DuoAccount(BaseModel)` with `ENTITY_TYPE = "duo__duo_account"`, `ENTITY_ICON = "duo-account"`, default dimensions none (the account spans every surface; `dcom` is stamped per observation), and fields `name`, `api_hostname`, `edition`, `helpdesk_bypass`, `lockout_threshold`, `inactive_user_expiration`, `tags`. It has no free-form `configuration` field: the Admin API settings response has no reader here and can carry secret material or personal data, so only promoted columns are stored (migration `0003_drop_unused_configuration` removed it). `NATURAL_KEY = ('name',)` — Natural key: **`name`**. A design-phase account has no observed identifier, so its name is the only fact it carries. `api_hostname` is the real stable identifier; the key moves to it when `req-duo-collector` makes it observable (spec: `req-duo-account`). Two accounts with the same name would collide today — acceptable while every account on a grid is a designed one. `CONTAINMENT_EDGES = ('HOLDS_ACCOUNT_OBJECT__duo',)`. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_account.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-account-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `name` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-account-2 | Key Field Required | Implemented | A write without `name` is refused. | `test_required_field_enforced` |
| req-duo-account-3 | Surface Dimension | Implemented | New nodes carry default dimensions none (the account spans every surface; `dcom` is stamped per observation), and never `dcom`. | `test_surface_dimension` |
| req-duo-account-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('name',)`, every key a model field. | `test_every_key_is_a_field` |
| req-duo-account-5 | Edition Is Closed | Implemented | `edition` accepts Duo's editions (`essentials`, `advantage`, `premier`, `federal_mfa`, `federal_access`, `other`) or blank, and refuses anything else. | `test_account_edition_is_closed` |
| req-duo-account-6 | Contains Its Tree | Implemented | `delete_node(account, cascade="contained")` retires every object it holds through `HOLDS_ACCOUNT_OBJECT__duo` and, through each user and administrator, their WebAuthn credentials and bypass codes; another account's objects stay live. | `test_account_cascade_retires_its_tree` |
| req-duo-account-7 | No Free-Form Record | Implemented | The account declares no `configuration` field, and a `create_node` write carrying it is refused. | `test_no_free_form_record`, `test_configuration_write_is_refused` |

---
### Duo User
----
RID: `req-duo-user`

Status: `Implemented`

A person's account in Duo: the identity that enrolls authenticators and is challenged for a second factor. Carries Duo's status (active, bypass, disabled, locked out) and whether any authenticator is enrolled.

The two questions an operator asks of MFA daily are both about users: *who is not actually doing MFA* (status `bypass`, or no enrolled authenticator, or an outstanding bypass code) and *who is locked out*. Both are fields or one hop from this node. It is also the far end of every authenticator edge, so 'which factors does this person have' is a one-hop read.

#### Implementation

`tap_plugin/duo/models/duo_user.py` defines `DuoUser(BaseModel)` with `ENTITY_TYPE = "duo__duo_user"`, `ENTITY_ICON = "duo-user"`, default dimensions `{"duo.surface": "directory"}`, and fields `user_id`, `username`, `realname`, `email`, `status`, `is_enrolled`, `last_login`, `last_directory_sync`, `created`, `tags`. `NATURAL_KEY = ('user_id',)` — Natural key: **`user_id`**, Duo's `DU…` id, unique across Duo and stable across renames. Users are observed, never designed — a design has no reason to seed an individual user — so the id is `CREATE_REQUIRED`. Username is a mutable attribute and is deliberately not the key. `CONTAINMENT_EDGES = ('ENROLLS_WEBAUTHN_CREDENTIAL__duo', 'HOLDS_BYPASS_CODE__duo')`. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_user.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-user-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `user_id` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-user-2 | Key Field Required | Implemented | A write without `user_id` is refused. | `test_required_field_enforced` |
| req-duo-user-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "directory"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-user-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('user_id',)`, every key a model field. | `test_every_key_is_a_field` |
| req-duo-user-5 | Status Is Closed | Implemented | `status` accepts Duo's user statuses (`active`, `bypass`, `disabled`, `locked out`, `pending deletion`) or blank. | `test_user_status_is_closed` |
| req-duo-user-6 | Enrollment Is Three-State | Implemented | `is_enrolled` defaults to null (not observed), never false. | `test_enrollment_null_is_not_false` |

---
### Duo Group
----
RID: `req-duo-group`

Status: `Implemented`

A Duo group: a named set of users that an application can be restricted to and that a group policy targets. Its own status can put every member into bypass or disable them.

Groups are how Duo expresses 'who may use this application' (`PERMITTED_GROUPS` user access) and 'which users get this policy in this application' (group policies). A group's own status can also bypass or disable every member at once, which a user-by-user view never shows.

#### Implementation

`tap_plugin/duo/models/duo_group.py` defines `DuoGroup(BaseModel)` with `ENTITY_TYPE = "duo__duo_group"`, `ENTITY_ICON = "duo-group"`, default dimensions `{"duo.surface": "directory"}`, and fields `name`, `group_id`, `description`, `status`, `tags`. `NATURAL_KEY = ('name',)` — Natural key: **`name`** — a design knows a group's name before any exists. `group_id` is the stable id; the key moves to it with the collector. Names are unique within an account but not across accounts, a known limit of the design-phase key. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_group.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-group-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `name` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-group-2 | Key Field Required | Implemented | A write without `name` is refused. | `test_required_field_enforced` |
| req-duo-group-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "directory"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-group-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('name',)`, every key a model field. | `test_every_key_is_a_field` |
| req-duo-group-5 | Same Name, Two Accounts | Implemented | Two accounts each holding a group of the same name hold two entities; retiring one account leaves the other's group live. The name key is a design-phase key and is not consulted on the write path (req-grid-entity-natural-key-9); before identity is enforced on writes, the key moves to `group_id` with the collector. | `test_same_name_in_two_accounts_stays_two_objects` |

---
### Duo Phone
----
RID: `req-duo-phone`

Status: `Implemented`

A phone enrolled in Duo — a Duo Mobile device that can approve Duo Push, or a number that receives SMS passcodes or phone calls. Its capabilities decide which factors it can deliver.

Most Duo factors run through a phone, and the phone's capabilities are where factor strength lives: Duo Push with number matching resists casual phishing; SMS and voice do not. A phone can also be shared between users, which is why it hangs off the account and is linked to users rather than contained by one.

#### Implementation

`tap_plugin/duo/models/duo_phone.py` defines `DuoPhone(BaseModel)` with `ENTITY_TYPE = "duo__duo_phone"`, `ENTITY_ICON = "duo-phone"`, default dimensions `{"duo.surface": "authenticators"}`, and fields `phone_id`, `name`, `platform`, `phone_type`, `model`, `capabilities`, `activated`, `encrypted`, `fingerprint`, `screenlock`, `tampered`, `last_seen`, `tags`. `NATURAL_KEY = ('phone_id',)` — Natural key: **`phone_id`**. Observed-only; `CREATE_REQUIRED`. The phone number is deliberately not stored (personal data, and nothing on the grid needs it). What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_phone.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-phone-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `phone_id` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-phone-2 | Key Field Required | Implemented | A write without `phone_id` is refused. | `test_required_field_enforced` |
| req-duo-phone-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "authenticators"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-phone-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('phone_id',)`, every key a model field. | `test_every_key_is_a_field` |
| req-duo-phone-5 | Shared, Not Contained | Implemented | Deleting a user (contained) leaves a phone it enrolled live; its WebAuthn credential retires. | `test_shared_phone_survives_its_user` |

---
### Duo Hardware Token
----
RID: `req-duo-hardware-token`

Status: `Implemented`

An OTP hardware token registered in Duo (HOTP-6, HOTP-8, YubiKey AES, or Duo-D100) and assigned to users or administrators.

Hardware tokens are the factor of choice where phones are not allowed — secure rooms, some federal sites — and are commonly issued to administrators. They are OTP, so phishable; an inventory of who still relies on them is part of any move to phishing-resistant MFA.

#### Implementation

`tap_plugin/duo/models/duo_hardware_token.py` defines `DuoHardwareToken(BaseModel)` with `ENTITY_TYPE = "duo__duo_hardware_token"`, `ENTITY_ICON = "duo-hardware-token"`, default dimensions `{"duo.surface": "authenticators"}`, and fields `token_id`, `serial`, `token_type`, `totp_step`, `tags`. `NATURAL_KEY = ('token_id',)` — Natural key: **`token_id`**. Observed-only. `serial` is unique only within a token type, so it is not the key. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_hardware_token.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-hardware-token-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `token_id` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-hardware-token-2 | Key Field Required | Implemented | A write without `token_id` is refused. | `test_required_field_enforced` |
| req-duo-hardware-token-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "authenticators"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-hardware-token-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('token_id',)`, every key a model field. | `test_every_key_is_a_field` |

---
### Duo WebAuthn Credential
----
RID: `req-duo-webauthn-credential`

Status: `Implemented`

A WebAuthn/FIDO2 credential enrolled in Duo — a roaming security key or a platform authenticator (Touch ID, Windows Hello). The phishing-resistant factor.

FedRAMP 20x and OMB M-22-09 push toward phishing-resistant MFA; in Duo that means WebAuthn. Counting who has one — and which administrators do not — is the most direct measure of that posture Duo exposes. A credential belongs to exactly one principal and retires with it.

#### Implementation

`tap_plugin/duo/models/duo_webauthn_credential.py` defines `DuoWebauthnCredential(BaseModel)` with `ENTITY_TYPE = "duo__duo_webauthn_credential"`, `ENTITY_ICON = "duo-webauthn"`, default dimensions `{"duo.surface": "authenticators"}`, and fields `webauthnkey`, `credential_name`, `label`, `date_added`, `date_last_used`, `tags`. `NATURAL_KEY = ('webauthnkey',)` — Natural key: **`webauthnkey`**. Observed-only. Contained by its user (or administrator) — it never outlives them. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_webauthn_credential.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-webauthn-credential-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `webauthnkey` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-webauthn-credential-2 | Key Field Required | Implemented | A write without `webauthnkey` is refused. | `test_required_field_enforced` |
| req-duo-webauthn-credential-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "authenticators"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-webauthn-credential-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('webauthnkey',)`, every key a model field. | `test_every_key_is_a_field` |

---
### Duo Bypass Code
----
RID: `req-duo-bypass-code`

Status: `Implemented`

An outstanding Duo bypass code held by a user: a passcode that satisfies MFA without any enrolled authenticator, with its expiry, remaining uses and issuing administrator.

Bypass codes are the quiet MFA exemption: a user with `active` status and a strong enrolled factor can still sign in with a code a help-desk administrator read to them over the phone. A FedRAMP reviewer wants every outstanding code, how long it lives, and who issued it. A count on the user would hide all three.

#### Implementation

`tap_plugin/duo/models/duo_bypass_code.py` defines `DuoBypassCode(BaseModel)` with `ENTITY_TYPE = "duo__duo_bypass_code"`, `ENTITY_ICON = "duo-bypass-code"`, default dimensions `{"duo.surface": "authenticators"}`, and fields `bypass_code_id`, `created`, `expires`, `expiration`, `reuse_count`, `admin_email`, `tags`. `NATURAL_KEY = ('bypass_code_id',)` — Natural key: **`bypass_code_id`**. Observed-only; contained by its user. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_bypass_code.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-bypass-code-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `bypass_code_id` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-bypass-code-2 | Key Field Required | Implemented | A write without `bypass_code_id` is refused. | `test_required_field_enforced` |
| req-duo-bypass-code-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "authenticators"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-bypass-code-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('bypass_code_id',)`, every key a model field. | `test_every_key_is_a_field` |

---
### Duo Application
----
RID: `req-duo-application`

Status: `Implemented`

A protected application in Duo (an Admin API 'integration'): the Okta authenticator, a Duo SSO SAML/OIDC app, an RDP or Unix host, an Auth Proxy, or an Admin API application that can read or change Duo itself.

Applications are the front page of Duo: each one is a system that sends its users to Duo for a second factor (Okta, a VPN, SSH hosts, RDP) or that Duo SSO signs users into. For each, an operator needs who may use it and which policy it enforces. Admin API applications are different in kind — they are credentials *to* Duo — and their granted permissions are the most sensitive configuration in the account.

#### Implementation

`tap_plugin/duo/models/duo_application.py` defines `DuoApplication(BaseModel)` with `ENTITY_TYPE = "duo__duo_application"`, `ENTITY_ICON = "duo-application"`, default dimensions `{"duo.surface": "access"}`, and fields `name`, `integration_key`, `integration_type`, `user_access`, `adminapi_permissions`, `self_service_allowed`, `tags`. `NATURAL_KEY = ('name',)` — Natural key: **`name`** — the design names the Okta application before it exists. `integration_key` is the stable id; the key moves to it with the collector. The secret key (`skey`) is never stored. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_application.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-application-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `name` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-application-2 | Key Field Required | Implemented | A write without `name` is refused. | `test_required_field_enforced` |
| req-duo-application-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "access"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-application-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('name',)`, every key a model field. | `test_every_key_is_a_field` |

---
### Duo Policy
----
RID: `req-duo-policy`

Status: `Implemented`

A Duo policy: the Global Policy every application inherits, or a custom policy applied to applications or to groups within them — allowed authentication methods, new-user behaviour, remembered devices, device health, networks and location.

Policy is where Duo's security posture actually lives. The same application can be strong or weak depending entirely on the policy it enforces: allowing SMS, letting unenrolled users through (`no-mfa`), remembering devices for thirty days. A FedRAMP operator reviews the Global Policy and every override, and needs to see which applications each one reaches.

#### Implementation

`tap_plugin/duo/models/duo_policy.py` defines `DuoPolicy(BaseModel)` with `ENTITY_TYPE = "duo__duo_policy"`, `ENTITY_ICON = "duo-policy"`, default dimensions `{"duo.surface": "access"}`, and fields `name`, `policy_key`, `is_global`, `new_user_behavior`, `allowed_auth_methods`, `sections`, `tags`. `NATURAL_KEY = ('name',)` — Natural key: **`name`**. Duo itself permits duplicate policy names; the design-phase key does not, and `policy_key` replaces it with the collector. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_policy.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-policy-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `name` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-policy-2 | Key Field Required | Implemented | A write without `name` is refused. | `test_required_field_enforced` |
| req-duo-policy-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "access"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-policy-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('name',)`, every key a model field. | `test_every_key_is_a_field` |
| req-duo-policy-5 | New-User Behaviour Is Closed | Implemented | `new_user_behavior` accepts `enroll`, `no-mfa`, `deny`, or blank. | `test_policy_new_user_behavior_is_closed` |

---
### Duo Administrator
----
RID: `req-duo-administrator`

Status: `Implemented`

A Duo administrator: a separate login to the Admin Panel with a role (Owner, Administrator, Application Manager, User Manager, Security Analyst, Help Desk, Billing, Read-only, or a custom role) and its own authenticators.

Whoever administers Duo can put any user in bypass, issue bypass codes, or weaken the Global Policy. The administrator list, their roles, their status and — critically — whether *they* use a phishing-resistant factor is a standing FedRAMP question (privileged access, AC-2/IA-2(1)). Duo administrators are distinct accounts from Duo users, so they get their own node.

#### Implementation

`tap_plugin/duo/models/duo_administrator.py` defines `DuoAdministrator(BaseModel)` with `ENTITY_TYPE = "duo__duo_administrator"`, `ENTITY_ICON = "duo-administrator"`, default dimensions `{"duo.surface": "administration"}`, and fields `admin_id`, `name`, `email`, `role`, `status`, `last_login`, `restricted_by_admin_units`, `tags`. `NATURAL_KEY = ('admin_id',)` — Natural key: **`admin_id`**. Observed-only. `CONTAINMENT_EDGES = ('ENROLLS_WEBAUTHN_CREDENTIAL__duo',)`. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_administrator.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-administrator-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `admin_id` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-administrator-2 | Key Field Required | Implemented | A write without `admin_id` is refused. | `test_required_field_enforced` |
| req-duo-administrator-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "administration"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-administrator-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('admin_id',)`, every key a model field. | `test_every_key_is_a_field` |

---
### Duo Endpoint
----
RID: `req-duo-endpoint`

Status: `Implemented`

A device Duo has seen users authenticate from — laptop, desktop or mobile browser — with the posture Duo Desktop reports (disk encryption, firewall, password, OS) and whether it is a Trusted Endpoint.

Device health is half of Duo's access decision in Advantage and Premier: a policy can require Duo Desktop, disk encryption, a firewall, or a Trusted Endpoint. The endpoint inventory is how an operator sees the posture of the devices actually reaching protected applications.

#### Implementation

`tap_plugin/duo/models/duo_endpoint.py` defines `DuoEndpoint(BaseModel)` with `ENTITY_TYPE = "duo__duo_endpoint"`, `ENTITY_ICON = "duo-endpoint"`, default dimensions `{"duo.surface": "device_trust"}`, and fields `epkey`, `device_name`, `endpoint_type`, `os_family`, `os_version`, `model`, `trusted_endpoint`, `disk_encryption_status`, `firewall_status`, `password_status`, `health_app_client_version`, `health_data_last_collected`, `last_updated`, `tags`. `NATURAL_KEY = ('epkey',)` — Natural key: **`epkey`**. Observed-only. Without Duo Desktop an epkey is an aggregate (same user, OS and browser version), so counts over endpoints are counts of records, not machines. What each field means, what is deliberately left out and what populates it: `tap_plugin/duo/domain/duo_endpoint.md`.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-endpoint-1 | Created Through The Service Layer | Implemented | A `create_node` write carrying only `epkey` succeeds; every other field stays blank or null (not observed). | `test_created_with_only_its_required_field` |
| req-duo-endpoint-2 | Key Field Required | Implemented | A write without `epkey` is refused. | `test_required_field_enforced` |
| req-duo-endpoint-3 | Surface Dimension | Implemented | New nodes carry default dimensions `{"duo.surface": "device_trust"}`, and never `dcom`. | `test_surface_dimension` |
| req-duo-endpoint-4 | Keyed On Its Own Fields | Implemented | `NATURAL_KEY = ('epkey',)`, every key a model field. | `test_every_key_is_a_field` |

---
### Edges
----
RID: `req-duo-edges`

Status: `Implemented`

Eleven edge types, each one relationship, each named `<ACTION>_<OBJECT>`. Tenancy is one edge (`HOLDS_ACCOUNT_OBJECT__duo`) because the Admin API returns every per-account list the same way and all of them end with the account; authenticators get one edge per kind because the kinds differ in strength. The two edges toward other systems leave the foreign side open.

#### Implementation

`tap_plugin/duo/edges/*.edge.json`, registered under `[edges]` in `tap-plugin.toml`; each has an article in `tap_plugin/duo/domain/<EDGE>.md`. Property schemas are closed (`additionalProperties: false`). `REQUESTS_SECOND_FACTOR__duo` omits `sources` (the protected system — an Okta org, a VPN, an SSH host — is another plugin's node) and carries `mechanism` and `fail_mode` (`safe` = fail open, `secure` = fail closed; configured on the client, so absent means not observed). `ISSUES_SSO_ASSERTION__duo` omits `targets` (the service provider; no substrate owns a neutral type yet) and requires `protocol`. `ENFORCES_POLICY__duo` requires `apply_type` (`app` or `group_app`) and carries `group_names` and `group_position` for group policies; Global-Policy inheritance is derived, never stored. Model-side permission and containment: `DuoAccount` (tenancy, containment), `DuoUser` and `DuoAdministrator` (authenticators; WebAuthn credentials and bypass codes contained), `DuoApplication` (`PERMITS_GROUP`, `ENFORCES_POLICY`).

Endpoint lists are enforced under the grid's permission union (`tap_grid/constraints.py::validate_edge`): an edge is refused only when neither the node type's declared `OUTBOUND_EDGES`/`INBOUND_EDGES` nor the edge definition permits it, and a type that declares none is unconstrained on that side. So `MEMBER_OF_GROUP__duo` from a group to a user is accepted today (neither type constrains that direction); the tests prove refusal from a type that declares its outbound edges.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-edges-1 | Every Edge Seeds | Implemented | A two-account estate writes every edge type between its declared endpoints. | `test_estate_seeds` |
| req-duo-edges-2 | Undeclared Source Refused | Implemented | A user cannot emit `PERMITS_GROUP__duo`; it can emit `MEMBER_OF_GROUP__duo`. | `test_undeclared_source_refused` |
| req-duo-edges-3 | Policy Application Typed | Implemented | `ENFORCES_POLICY__duo` without `apply_type`, or with an unknown property, is refused. | `test_enforces_policy_needs_apply_type` |
| req-duo-edges-4 | Open Source For Second Factor | Implemented | Any node may request a second factor of a Duo application; `fail_mode` outside `safe`/`secure` is refused. | `test_requests_second_factor_open_source` |
| req-duo-edges-5 | Open Target For SSO | Implemented | A Duo application may assert to any node; `protocol` is required. | `test_issues_sso_assertion_open_target` |
| req-duo-edges-6 | Edge Surfaces | Implemented | Edges stamp `duo.surface`; tenancy stamps none. | `test_surface_on_edges` |

---

### Domain Articles
----
RID: `req-duo-articles`

Status: `Implemented`

Every node type, edge type and the `duo.surface` dimension has a domain article (`req-domain-articles-coverage`): what the concept is in Duo, why it is modelled this way, its identity, what it excludes, and — stated plainly — that nothing in it is observed yet.

#### Implementation

`tap_plugin/duo/domain/<stem>.md` per node and edge, `tap_plugin/duo/domain/dimensions/duo.surface.md`. Each pins its authoritative source (`Source` / `Version` / `Retrieved`) and explains every `FIELD_CRUD_SCHEMA` key.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-articles-1 | Coverage Clean | Implemented | `tap.domain_articles.findings_for_root` reports no finding for the package. | Run in the container, 2026-09-22 |

---

### Page: Duo
----
RID: `req-duo-page`

Status: `Implemented`

The operator's front page for one Duo account in a live FedRAMP 20x environment, reusable on any grid: the account map at the top, then the posture strip, the protected applications, the policy each enforces, the policies, the users not doing MFA (or not known to), outstanding bypass codes, administrators and device health. `?account=<account name>` selects an account; without it every account is shown, which is the single account on a grid that holds one, and the posture strip offers each account when there are several.

#### Implementation

`tap_plugin/duo/grift/duo-page.grift.json` (registered as `[grift] duo_page`): one batch (`duo page v0.2.0`) holding the page (`/duo`, full bleed, one column), nine panels, their searches, and the map's projection → elevation → layout. Slots, top to bottom: `map` (graph panel, `60vh`, projection `node_style: {"mode": "icon-badge"}`, `lock_nodes`, fitted), `posture` (`duo/panels/duo_posture.html`), and seven standard table panels — `applications`, `assignments`, `policies`, `users`, `bypass-codes`, `admins`, `endpoints` — each bound to a search this bundle owns (envelope mode for node tables, projection mode for the assignment and bypass-code rows). The map mounts seven scene searches, each naming the edge types it walks; none is an unfiltered edge search.

**The account parameter.** Every search declares `account` (string, default `""`) and filters `a.name STARTS_WITH $account AND a.name ENDS_WITH $account`. The account's natural key is its `name`, so `?account=` takes the name rather than the entity id: Gryphon has no param-absent predicate (tap#360) and `entity_id` admits no string operator (probed 2026-09-22: `STARTS_WITH` / `=~` on `a.entity_id` fail with `Unsupported lookup ... for OneToOneField`, and `= ""` fails UUID validation), so the name pair is the one predicate that selects every account when the input is empty and exactly one when it is set. The limit is real: a name that another account's name both starts and ends with (`A` beside `ABA`) makes the page's tables and map include both. The posture strip, which is Python, reads exactly (`a.name = $account`) whenever an account is named and raises an alert naming the colliding accounts, so the page never presents the mixed tables unannounced. Revisit when tap#360 lands: then every search becomes exact-or-all and `?account=` can take the entity id.

**Click-through.** The map's graph panel config carries one `nav_rules` entry (spec-viz-panel.md, `req-viz-panel-click-semantics-8`): an `okta__okta_org` node navigates to `/okta?org={data.name}`, the org page for the org that sends its users here. It is the narrow form: a page path named in this bundle's panel config. The generic form, where the plugin that owns a node type declares the page that answers for it, does not exist in tap_viz yet.

**What the page cannot say.** An application missing from the assignment table enforces no custom policy and runs under the Global Policy (OPTIONAL MATCH cannot yet express the left join over a traversal). Every table and tile counts only what the grid holds: on a designed account before a collector runs, zero means nothing observed.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-page-1 | Valid GRIFT | Implemented | The bundle validates against `grift-document.schema.json`. | `test_validates_against_the_grift_schema` |
| req-duo-page-2 | Slots Match Panels | Implemented | Layout `panel-id`s and `USES_PANEL` hotlink values agree exactly; the map is the first slot. | `test_every_slot_has_exactly_one_panel` |
| req-duo-page-3 | Icon-Badge Map, Named Edges | Implemented | The projection is icon-badge; every search names the edge types it walks. | `test_graph_is_icon_badge_and_edges_are_named` |
| req-duo-page-4 | Account Parameter | Implemented | Every search takes `account` with an empty default. | `test_every_search_takes_the_account_input` |
| req-duo-page-5 | Imports Cleanly | Implemented | The bundle imports into a grid with strict dangling-edge handling. | `test_imports_into_a_grid` |
| req-duo-page-6 | Account-Scoped Scene | Implemented | Each scene and table search returns the selected account's objects and none of another account's; empty selects all; an unknown name selects nothing. | `TestSearches` |
| req-duo-page-7 | Users In Three States | Implemented | The users table lists bypass, locked out, disabled, not enrolled and enrollment-not-observed users. | `test_users_attention_three_states` |
| req-duo-page-8 | Renders Server-Side | Implemented | `/duo?account=…` and its posture, table and graph fragments return 200 with the selected account's content and not the other's. | `test_page_and_fragments_render` (Django test client). Browser rendering (Cytoscape, Tabulator) not yet observed. |
| req-duo-page-9 | Okta Org Clicks Through | Implemented | The map's graph panel carries `nav_rules` routing an `okta__okta_org` node (the source of a `REQUESTS_SECOND_FACTOR__duo` edge) to `/okta?org=<its name>`; no other node navigates. The rule is panel config naming a page path, not a dependency: duo declares none on okta, and on a grid without okta no node matches. /okta carries the mirror rule to `/duo?account=`. | `test_okta_org_clicks_through_to_okta`; clicked in a browser on the highbar stack 2026-09-24. |

---

### Panel: Posture
----
RID: `req-duo-panel-posture`

Status: `Implemented`

The front of the account in one strip: five cards — MFA coverage, factor mix, access, administration, device trust — of counted tiles. The account header states edition, API host, help-desk bypass and lockout threshold. Counts over a field no collector has observed are their own tile in the not-observed tone (purple), never folded into zero.

#### Implementation

`tap_plugin/duo/panels/duo_posture/__init__.py` defines `DuoPosturePanelType` (`slug = "duo-posture"`, `view = "duo/panels/duo_posture.html"`, `css = ["duo/css/duo_posture.css"]`), registered in `DuoConfig.ready()`. `get_view_context` reads `?account=`, runs six inline Gryphon reads (`queries(account)` — exact `a.name = $account` when an account is named, every account when not: accounts, held objects, user and administrator WebAuthn credentials, bypass codes, policy enforcement) through `execute_gryphon_raw`, and folds them in `build_posture` (pure over envelopes). Tiles: users, in bypass, no authenticator, enrollment not observed, locked out, disabled, bypass codes (with never-expiring count), groups in bypass; Duo Push phones, SMS/voice-only phones, phone capability not observed, security keys, platform authenticators, hardware tokens, users with WebAuthn; protected applications, open to all users, on the Global Policy only, Admin API applications (with write grants), policies letting unenrolled users in, policies allowing SMS or voice; administrators, owners, administrators without WebAuthn, not active; endpoints, trusted, Duo Desktop reporting, posture not reported. A read failure renders an inline error, never a blank frame.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-panel-posture-1 | Account-Scoped Counts | Implemented | Every count is the selected account's. | `test_counts_for_one_account` |
| req-duo-panel-posture-2 | Not Observed Counted | Implemented | Null enrollment, null capabilities and unreported device health are their own counts in the look tone. | `test_counts_for_one_account` |
| req-duo-panel-posture-3 | Strength Split | Implemented | Phones split by Push capability; WebAuthn by security key versus platform. | `test_counts_for_one_account` |
| req-duo-panel-posture-4 | Several Accounts | Implemented | With several accounts and no `?account=`, the strip links each. | `test_several_accounts_without_a_choice` |
| req-duo-panel-posture-5 | Exact When Named | Implemented | With `?account=` set the strip reads exactly that account, and names any account the page's tables cannot separate from it (`A` beside `ABA`). | `test_named_account_is_exact_and_collision_is_reported` |
| req-duo-panel-posture-6 | Expiry Three-State | Implemented | A bypass code counts as never expiring only when `expires` is false; a code whose expiry was not observed is counted separately. | `test_unobserved_expiry_is_not_never` |

---

### Layout: Account Map
----
RID: `req-duo-layout-account-map`

Status: `In Development`

A reusable hub layout for any Duo account scene: the account at the centre; its applications in a column on the left, with whatever requests a second factor from them (an Okta org, a VPN) and whatever Duo SSO signs into further out; the policies they enforce on the right (Global Policy first); the groups they admit below; phones, WebAuthn credentials and hardware tokens folded into one tile per enrolled-device type above, each with its count. Tenancy edges are hidden (the hub is the tenancy); enforcement, group-access, second-factor and SSO edges are drawn in distinct styles. Anything unplaced is drawn under the picture and reported, never dropped.

**Status details.** The module parses (esprima, 2026-09-22) and the graph fragment that loads it renders server-side, but it has never executed in a browser: no JavaScript runtime or browser was available to this build. It stays `In Development` until a browser check counts nodes and edges in the live `cy` instance.

#### Implementation

`tap_plugin/duo/static/duo/js/projections/account-map.js`, the standard `execute(context)` layout contract, referenced by the bundle's layout node (`js_file`). It reads entity types and edges only — never entity ids — so it serves any account on any grid. The graph panel lifts no model fields onto cy nodes, so device tiles fold by type; the strength split within a type is the posture strip's, and the Global Policy is recognised by Duo's name for it.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-layout-account-map-1 | Hub Placement | In Development | With the seeded estate, the account is centred, applications left, policies right, groups below, device tiles above. | Browser check owed |
| req-duo-layout-account-map-2 | Nothing Dropped | In Development | A node the map does not place is drawn under the picture and reported as a warning. | Browser check owed |

---

### CI Record and Tests
----
RID: `req-duo-record`

Status: `Implemented`

The in-package `ci` boot record (`req-boot-bootstrap-ci-record`) and the tests that run in it.

#### Implementation

`tap_plugin/duo/boot/ci.boot.json` installs its `depends_on` closure (`identity_core`, pinned at the full commit of its `v0.1.3` tag, the `depends_on` floor) and duo and seeds its own GRIFT, offline and credential-free; the consumer flips self to editable. Tests: `test_duo_manifest.py` (validation, structure and strict), `test_duo_account.py`, `test_duo_corpus.py` (every model and edge), `test_duo_page.py` (bundle, searches over a seeded two-account estate from `tests/seed.py`, posture, server-side render).

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-record-1 | Record Declared | Implemented | The manifest declares the `ci` record with its sha256. | |
| req-duo-record-2 | Validates Strict | Implemented | `validate_plugin --strict` passes on the package. | |

---

### Collector
----
RID: `req-duo-collector`

Status: `Backlog`

Observe a real Duo account through the Admin API with a read-only Admin API application (*Grant read resource*, *Grant read information*, *Grant administrators — read*, *Grant settings — read*; never a write grant), landing every type above and moving the design-phase keys (account → `api_hostname`, group → `group_id`, application → `integration_key`, policy → `policy_key`). Owes: a probe of what a refused permission returns (the three-state question), `manage-secret` review of the integration key/secret, and FedRAMP boundary reasoning for Duo Federal hosts (`*.duofederal.com`).

### Person Convergence
----
RID: `req-duo-person-convergence`

Status: `Implemented`

Link a Duo user and a Duo administrator to the human they belong to, as Cartography's `(:Human)-[:IDENTITY_DUO]->(:DuoUser)` does. The human is `identity_core__human` (a neutral substrate type, keyed on an operator-assigned handle), and the link is identity_core's `HELD_BY_HUMAN__identity_core`, whose source is wildcard so no substrate depends upward on Duo. `DuoUser` and `DuoAdministrator` declare it in `OUTBOUND_EDGES` (`{"nodes": [{"type": "identity_core__human"}], "edges": [{"type": "HELD_BY_HUMAN__identity_core"}]}`), which makes `identity_core` a declared vocabulary dependency (`depends_on`, and the `ci` record installs it). Email is not identity: the edge is drawn by whoever knows the match (an operator's seed, an HR feed, a collector matching an immutable id) and records how in its `matched_on` property; nothing here joins on `email`. A user with no such edge is unmatched, and one with two is a shared account; both are access-review findings the graph shows rather than refuses.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-person-convergence-1 | Declared On Both Account Types | Implemented | `DuoUser` and `DuoAdministrator` declare `HELD_BY_HUMAN__identity_core` to `identity_core__human` in `OUTBOUND_EDGES`, and `identity_core` is in `depends_on` with `min_version = "0.1.3"`. | `test_person_convergence_is_declared` |
| req-duo-person-convergence-2 | Written Through The Service Layer | Implemented | A Duo user and an administrator each write `HELD_BY_HUMAN__identity_core` to a human with `matched_on`; an unknown property is refused. | `test_account_is_held_by_a_human` |
| req-duo-person-convergence-3 | Shared Account Recorded | Implemented | One Duo user may be held by two humans; both edges stand. | `test_shared_account_is_recorded` |

### Host Link
----
RID: `req-duo-host-link`

Status: `Implemented`

A Duo endpoint is Duo's record of a device a user authenticated from, not the machine itself. The machine is `computing_core__host`, a neutral substrate node
keyed on an operator-assigned asset tag, so the same laptop's Okta, Duo, Teleport, MDM and EDR records
converge on one node, and that host reaches the person it is issued to with computing_core's
`ASSIGNED_TO_HUMAN`. The link is computing_core's `REPRESENTS_HOST__computing_core`, whose source is
wildcard so the substrate never depends on this plugin (the pattern of `HELD_BY_HUMAN__identity_core`).

#### Implementation

`DuoEndpoint.OUTBOUND_EDGES` declares `{"nodes": [{"type": "computing_core__host"}], "edges": [{"type":
"REPRESENTS_HOST__computing_core"}]}`. Under the permission union (`req-grid-edge-constraints-3`) this adds a
permission and constrains nothing else. `computing_core` joins `depends_on` as a vocabulary dependency (no
Python import); the `ci` record pins it at `daa040dbfbe11a390c02d22c7e4947b39face4b7`, the tap-plugin-computing-core commit that adds
`host` and the edge. No tagged release carries them yet, so no `min_version` floor is declared; the floor
lands when computing_core is released. The edge is drawn by whoever knows the match and records how in
`matched_on` (a serial number, an asset tag, an operator seed); nothing joins on a hostname.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-host-link-1 | Declared On The Device Record | Implemented | `DuoEndpoint` declares `REPRESENTS_HOST__computing_core` to `computing_core__host`; `computing_core` is in `depends_on`; the record's own edges are still accepted. | `tests/test_duo_host.py::test_host_link_is_declared`, `::test_record_keeps_its_own_edges` |
| req-duo-host-link-2 | Written Through The Service Layer | Implemented | The record writes the edge to a host with `matched_on`; an unknown property is refused (on a fresh pair). | `tests/test_duo_host.py::test_record_represents_a_host`, `::test_unknown_property_is_refused` |

### Directory Sync
----
RID: `req-duo-directory-sync`

Status: `Backlog`

Where users and groups come from (Active Directory, Entra ID, OpenLDAP directory syncs) and which are managed by hand.

### Administrative Units
----
RID: `req-duo-admin-units`

Status: `Backlog`

Administrative units as the scope of a restricted administrator; today only the boolean `restricted_by_admin_units` is carried.

### Duo SSO Depth
----
RID: `req-duo-sso-depth`

Status: `Backlog`

Duo SSO applications' service-provider metadata (entity ids, ACS URLs, certificates) and Duo SSO's own authentication sources (AD, a SAML IdP).

### Non-Goals
----
RID: `req-duo-nongoals`

Status: `Proposed`

Not modelled, with the reason: the authentication, telephony and administrator logs (event streams; summaries land on fields such as `duo_user.last_login`, and the grid's history covers change); Trust Monitor events; telephony credits and billing; MSP subaccounts (the Accounts API integration type can no longer be created); phone numbers, bypass-code values and integration secret keys (personal data or live credentials); per-user application access edges (derivable from `user_access` and membership).

## Model catalog

Superseded by the manifest as of v0.2.0: the classes and `domain/` articles are the definition. The rows keep only the decisions the code cannot state.

| Model | Entity type | Category | Rationale |
| --- | --- | --- | --- |
| `DuoAccount` | `duo__duo_account` | account | One Duo tenant: the thing an Admin API application's `api_hostname` names, and the outer box every other Duo object sits inside. |
| `DuoUser` | `duo__duo_user` | directory | A person's account in one Duo tenant — who gets challenged, with what status, and whether anything is enrolled to challenge them with. |
| `DuoGroup` | `duo__duo_group` | directory | A named set of Duo users — the unit applications are restricted to and group policies target. |
| `DuoPhone` | `duo__duo_phone` | authenticators | A phone Duo can reach: a Duo Mobile device for Push and passcodes, or a number for SMS and voice. |
| `DuoHardwareToken` | `duo__duo_hardware_token` | authenticators | A physical one-time-passcode token Duo accepts: HOTP, YubiKey AES, or Duo's D-100. |
| `DuoWebauthnCredential` | `duo__duo_webauthn_credential` | authenticators | A FIDO2/WebAuthn credential registered to one Duo user or administrator: the phishing-resistant factor. |
| `DuoBypassCode` | `duo__duo_bypass_code` | authenticators | A Duo bypass code a user holds right now — MFA satisfied by a passcode, no authenticator needed. |
| `DuoApplication` | `duo__duo_application` | access | Something Duo protects — or something that holds keys to Duo itself. The Admin Panel calls these applications; the API calls them integrations. |
| `DuoPolicy` | `duo__duo_policy` | access | A named set of Duo access rules — which factors, what happens to unenrolled users, which devices and networks — applied to applications and to groups within them. |
| `DuoAdministrator` | `duo__duo_administrator` | administration | A login to the Duo Admin Panel, with a role — the people who can change who has to do MFA. |
| `DuoEndpoint` | `duo__duo_endpoint` | device_trust | A device Duo has seen an authentication come from, and the posture Duo Desktop reported for it. |

**Keys by phase.** Types a design places (account, group, application, policy) key on `name` because a design knows nothing else; each moves to its Duo id with the collector. Types only a collector can see (user, phone, token, WebAuthn credential, bypass code, administrator, endpoint) key on their Duo id from the start. **Bypass codes are nodes, not a count**, because expiry, remaining uses and issuer are the FedRAMP question. **Administrators are not users**: Duo keeps them as separate accounts.

## Edge types

Superseded by the manifest as of v0.2.0; decision rows only.

| Edge | From → To | Properties | Rationale |
| --- | --- | --- | --- |
| `HOLDS_ACCOUNT_OBJECT__duo` | `duo__duo_account` → `duo__duo_user`, `duo__duo_group`, `duo__duo_application`, `duo__duo_policy`, `duo__duo_administrator`, `duo__duo_phone`, `duo__duo_hardware_token`, `duo__duo_endpoint` | none. | A Duo account holds one of its objects — the tenancy relationship, and the account's delete tree. |
| `MEMBER_OF_GROUP__duo` | `duo__duo_user` → `duo__duo_group` | none. | A Duo user belongs to a Duo group. |
| `ENROLLS_PHONE__duo` | `duo__duo_user`, `duo__duo_administrator` → `duo__duo_phone` | none. | A user or administrator has this phone enrolled. |
| `ENROLLS_HARDWARE_TOKEN__duo` | `duo__duo_user`, `duo__duo_administrator` → `duo__duo_hardware_token` | none. | A user or administrator holds this OTP hardware token. |
| `ENROLLS_WEBAUTHN_CREDENTIAL__duo` | `duo__duo_user`, `duo__duo_administrator` → `duo__duo_webauthn_credential` | none. | A user or administrator has this WebAuthn credential enrolled. |
| `HOLDS_BYPASS_CODE__duo` | `duo__duo_user` → `duo__duo_bypass_code` | none. | A user holds this bypass code. |
| `AUTHENTICATES_FROM_ENDPOINT__duo` | `duo__duo_user` → `duo__duo_endpoint` | none. | A user has authenticated from this device. |
| `PERMITS_GROUP__duo` | `duo__duo_application` → `duo__duo_group` | none. | An application admits this group's members. |
| `ENFORCES_POLICY__duo` | `duo__duo_application` → `duo__duo_policy` | `apply_type` (required: `app` or `group_app`), `group_names` (group policy targets), `group_position` (group-policy stack order). | An application runs under this policy — for everyone, or for certain groups. |
| `REQUESTS_SECOND_FACTOR__duo` | open (any) → `duo__duo_application` | `mechanism` (how the system reaches Duo), `fail_mode` (`safe` = fail open, `secure` = fail closed; absent = not observed). | A system sends its users to Duo for MFA through this application — Okta, a VPN, SSH, RDP. |
| `ISSUES_SSO_ASSERTION__duo` | `duo__duo_application` → open (any) | `protocol` (required: `saml` or `oidc`). | A Duo SSO application signs users into this service provider. |

## Reference data

| Document | Contents | Seeded by |
| --- | --- | --- |
| `grift/duo-page.grift.json` | The `/duo` page, its nine panels, fourteen searches, and the account-map projection/elevation/layout. No instance data. | The `ci` record; any instance that installs duo |

Instance data (a designed Duo account, its Okta application, policies and groups) belongs to the instance plugin that designs it — highbar for the highbar environment — never to this plugin.

## Icons

Every icon is drawn for this plugin (64×64, square 24-unit viewBox, one green stroke): `duo-account` (a shield with a check), `duo-user`, `duo-group`, `duo-phone`, `duo-hardware-token`, `duo-webauthn`, `duo-bypass-code`, `duo-application`, `duo-policy`, `duo-administrator`, `duo-endpoint`. Duo's own logo shipped in v0 has been **removed**: Duo is a Cisco brand, and Cisco's logo guidelines (cisco.com/c/en/us/about/brand-center/logo-usage-guidelines.html, read 2026-09-22) state that Cisco generally does not grant permission for third parties to use its logos, requiring a written request per use. No reusable licence exists, so no vendor mark ships. The green is chosen to sit well beside Duo-coloured screenshots; it is not a trademark.
