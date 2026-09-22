# duo-tap

Duo multi-factor authentication as grid vocabulary: v0 carries one outer node, the Duo account, so a design can place it before anything is collected.

## What this plugin owns

One type in v0: `duo__duo_account` — a Duo account: one Duo Security tenant that enrolls users and devices and answers second-factor challenges for integrated applications. A design can place it before any access exists; everything inside it is later vocabulary.

## Read first

`specs/spec-duo-v0.md` — this is a thin v0 that puts the piece on the board; the full spec interview runs when the plugin grows.

## Stand it up

From a TAP core checkout:

```bash
scripts/spawn-session.sh <label> cli --from 'git+https://github.com/unified-systems-com/duo-tap@<rev>#ci' --dev-plugins duo
```
