# TAP Duo Plugin Specification

**Duo multi-factor authentication as grid vocabulary: v0 carries one outer node, the Duo account, so a design can place it before anything is collected.**

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `duo` |
| Display name | TAP Duo |
| Description | Duo multi-factor authentication as grid vocabulary: v0 carries one outer node, the Duo account, so a design can place it before anything is collected. |
| Kind | Leaf plugin: Duo vocabulary. Consumes nothing in v0; consumed by instance plugins that place it in a design (highbar first). |

**Default dimensions**

| Dimension | Value | Why |
| --- | --- | --- |
| (none) | | `duo__duo_account` declares no default dimension in v0. The only candidate is the `dcom` axis, and its value is a property of the observation, not the type: a seeded design node is `design`, the same type observed by a future collector is `configuration`. The seeding bundle stamps it per node. |

## Philosophy

This is a thin v0 (ruled 2026-09-22 for the highbar starter set): it exists to put the piece on the board so a design can reference it, not to model the domain. The full `create-plugin-spec` interview, prior-art search and requirement buy-in run when this plugin grows past v0; nothing here pre-empts them.

The one type, `duo__duo_account`, is the outermost thing a reader of a diagram recognises for Duo. Everything inside it (users, groups, policies, projects, sessions) is later vocabulary, added when something observes or designs it.

Three states hold for every observed field: blank means *not observed*, never *empty*. A design-phase node carries only its name; its identifiers stay blank until a collector reads them.

**Provenance markers:** every node of this type seeded in v0 is *designed* (stamped `dcom: design` by the bundle that seeds it). No field is *observed* until the collector (`req-duo-collector`, Backlog) exists.

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | On The Board | Exist as an installable plugin so the highbar stack can boot with it. |
| 2 | Designable | Let a design place the Duo outer node before any access exists. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | --- | --- |
| req-duo-model | [Duo Account Model](#duo-account-model) | Implemented | The one outer node: its fields, natural key, icon and display |
| req-duo-record | [CI Record and Tests](#ci-record-and-tests) | Implemented | The in-package `ci` boot record and the manifest/behaviour tests |
| req-duo-collector | [Collector](#collector) | Backlog | Observe real Duo state onto the grid; deferred until access exists |

---

### Duo Account Model
----
RID: `req-duo-model`

Status: `Implemented`

A Duo account: one Duo Security tenant that enrolls users and devices and answers second-factor challenges for integrated applications.

#### Implementation

`tap_plugin/duo/models/duo_account.py` defines `DuoAccount(BaseModel)` with `ENTITY_TYPE = "duo__duo_account"`, `ENTITY_ICON = "duo-account"` (SVG at `static/duo/icons/duo-account.svg`), no default dimensions, and fields `name` (required), `api_hostname` (The account's API hostname (api-XXXXXXXX.duosecurity.com). Blank until observed.), `configuration` (object) and `tags` (object). `NATURAL_KEY = ("name",)`: a design-phase node has no observed identifier, so its name is the only fact it carries; the key is revisited when `req-duo-collector` makes `api_hostname` observable.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-duo-model-1 | Created Through The Service Layer | Implemented | A `create_node` write with only `name` succeeds and the row carries it. | |
| req-duo-model-2 | Name Required | Implemented | A `create_node` write without `name` is refused. | |
| req-duo-model-3 | Keyed By Name | Implemented | `NATURAL_KEY` is `("name",)` and every key field is a model field. | |

---

### CI Record and Tests
----
RID: `req-duo-record`

Status: `Implemented`

The in-package `ci` boot record (`req-boot-bootstrap-ci-record`) and the tests that run in it.

#### Implementation

`tap_plugin/duo/boot/ci.boot.json` installs this plugin alone (it declares no dependencies), offline and credential-free; the consumer flips self to editable. `tap_plugin/duo/tests/test_duo_manifest.py` runs `validate_plugin` at structure and strict levels; `tests/test_duo_account.py` covers `req-duo-model`.

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

Observe real Duo state onto the grid; deferred until access exists.

## Model catalog

| Model | Entity type | Category | Rationale |
| --- | --- | --- | --- |
| `DuoAccount` | `duo__duo_account` | Outer node | The one node a reader recognises as Duo; everything else nests inside it later. |

## Icons

`duo-account` is Duo's own mark, used nominatively to identify the vendor on diagrams. The mark remains its owner's trademark; it is not covered by this repository's licence.
