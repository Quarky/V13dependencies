# Foundry V13 Dependencies

Independent repository for **Foundry VTT v13 dependency modules**. This is the V13 companion to [Quarky/v14dependencies](https://github.com/Quarky/v14dependencies) and **does not install into V14**.

### Install in Foundry V13

In Foundry's **Add-on Modules > Install Module > Manifest URL** field, use:

`https://raw.githubusercontent.com/Quarky/V13dependencies/main/module.json`

Alternatively [download the V13 module ZIP](https://github.com/Quarky/V13dependencies/raw/refs/heads/main/v13dependencies.zip), extract it, and run `./install.sh` (no arguments), or double-click `Install.command` on macOS. Shut down Foundry before running manual installation.

By default, the installer skips already-installed modules. Use `./install.sh --update` to replace existing dependencies with timestamped backups and rollback, or `./install.sh --check` to check remote manifests without modifying anything.

**V13 install path:** `~/Library/Application Support/FoundryVTT/Data/modules`

**V14 install path, intentionally untouched:** `~/Library/Application Support/FoundryVTTV14/Data/modules`

No worlds, game systems, campaign packages, or actors are modified. CZEPEKU Universe requires an active Czepeku subscription to access content.

### Current V13 registry

| Module | V14 release | V13-compatible version |
|---|---|---|
| CZEPEKU Universe | 1.0.0 | **1.0.0** (v12–14) |
| Cartorium Archive | 1.0.8 | **1.0.8** (v13–14) |
| Complete Card Management | 3.0.3 | **2.1.2** (v13.351+) |
| Card Hands List | 2.2.7 | **2.2.7** (v13–14) |

[Registry](./dependencies-v13.json) is version-pinned; the installer checks that each manifest/archive still matches the expected V13-compatible release. The four modules here reflect only the dependencies already registered in V14, **not** all modules installed on the user's Mac.

### Export every installed V14 and V13 module as JSON

Double-click `Export-Module-Inventory.command`, or run `python3 export_modules.py`.

Two reports are written to the macOS Desktop:

- `foundry-v14-installed-modules.json`
- `foundry-v13-installed-modules.json`

The reports contain all module identifiers, installed versions, module titles, compatibility metadata, manifest links, and declared dependencies. These are installed modules, not per-world enabled/disabled lists. Please review any custom manifest URL that may contain an access token before sharing.

Compare the V14 JSON with the V13 one to research and register additional V13-compatible module releases. Never substitute V14-only releases when a V13 version is unavailable.

Sources: [CZEPEKU](https://foundryvtt.com/packages/czepeku) · [Cartorium](https://foundryvtt.com/packages/cartorium-browser) · [Complete Card Management](https://foundryvtt.com/packages/complete-card-management) · [Card Hands List](https://foundryvtt.com/packages/card-hands-list).
