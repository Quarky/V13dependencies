# Foundry V13 Dependencies

This is the **Foundry VTT V13** dependency installer, independent of [Quarky/v14dependencies](https://github.com/Quarky/v14dependencies). It installs V13-compatible releases of third-party add-ons used in the user's Foundry V14 collection, **not V14-only versions**.

## Install

Foundry V13 > Add-on Modules > Install Module > Manifest URL:

`https://raw.githubusercontent.com/Quarky/V13dependencies/main/module.json`

Or download [v13dependencies.zip](./v13dependencies.zip) and double-click `Install.command` on macOS; `./install.sh` needs no arguments. Run the installer while Foundry is closed. V13 data root: `~/Library/Application Support/FoundryVTT`. V14 root `~/Library/Application Support/FoundryVTTV14` is never touched.

`./install.sh --check` checks pinned manifests without installing; `./install.sh --verify-archives` downloads and checks the embedded ID/version of every archive **without installing**; and `./install.sh --update` updates with timestamped backups and rollback. **Manual installer validates the downloaded archive's embedded module ID/version before installation** and skips previously installed add-ons by default. Versioned [pinned manifests](./pinned-manifests) avoid upstream `releases/latest` silently switching to V14. With the no-argument installer, installed package manifest URLs are also rewritten to their pinned V13 URLs to keep later Foundry updates from upgrading them to V14.

## V13-compatible automatic dependencies

| Add-on | V14 installed | V13 version |
|---|---|---|
| CZEPEKU Universe | 1.0.0 | **1.0.0** |
| Cartorium Archive | 1.0.8 | **1.0.8** |
| Complete Card Management | 3.0.3 | **2.1.2** (V13.351+) |
| Card Hands List | 2.2.7 | **2.2.7** |
| libWrapper | 1.13.5.1 | **1.13.4.0** |
| socketlib | 1.1.4 | **1.1.3** |
| Wall Height | — | **7.0.8** |
| Levels | 7.0.3 | **6.1.0** |
| 3D Canvas | 9.0.35 | **8.0.14** |
| 3D to Isometric | 0.5.0 | **0.4.0** |
| 5e Item Importer | 14.1.2 | **13.9.1** |
| Advanced Magic — Spell Points | 3.3.14 | **3.2.40** |
| Argon Combat HUD Core | 5.0.1 | **4.1.2** |
| Argon Combat HUD D&D5e | 5.2.2 | **5.1.5** |
| Isometric Perspective | 14.0.3 | **0.9.7** |
| Multiple Document Selection | 14.01 | **13.03** |
| Whisper Box | 3.0.8 | **3.0.6** |
| Plutonium | 2.18.3.v14 | **2.18.3.v13** (V13-specific release) |
| Soundscape | 1.2.0 | **1.2.0** (V13 alternative audio module) |

All auto-install entries use V13 compatible declared versions. For the ten additions after the initial V13 stack, versioned manifest copies pin publisher release ZIP URLs. No publisher source code or premium content is bundled in this repository.

**Validation limit:** Published Foundry version listings and tagged module source metadata were checked. The two Argon project source tags still report stale internal versions (3.1.0 for core tag 4.1.2; 4.0 for DnD5e tag 5.1.5), despite their official Foundry release listings. Our metadata uses Foundry's published version numbers and versioned GitHub release ZIP paths. Confirm the actual archives before treating this pair as runtime-verified. No Foundry instances were launched during this work.

## Foundry V14 modules without a matching V13 release — real alternatives

| V14 module | V13 alternative | Note |
|---|---|---|
| Ambience Forge 0.4.1 | **Soundscape 1.2.0** | Soundscape supports layered audio/soundboards, but is **not** a drop-in API replacement. If a custom module declares a hard requirement on `ambience-forge`, that custom module needs to be adapted to remove/change the dependency. |
| Jornie's D&D5e HUD 0.4.1 | **Argon Core 4.1.2 + D&D5e HUD 5.1.5** | A different V13-supported D&D5e HUD, with different UI/behavior. |
| Soundbrett 1.1.0 | **Soundscape 1.2.0** | A V13 soundboard alternative, not a same-ID port. |

## Published V13 map packs that need provider/Foundry installation

- **Forgotten Adventures Battlemaps:** Publisher has a V13-compatible **1.1.x** release; downloads are Foundry-license exclusive and not served as a publicly downloadable ZIP. Select the proper older version in the Foundry package browser. Don't add V14-only 1.2.x.
- **The MAD Cartographer — Phandelver & Below:** Publisher lists **13.0.2** for V13, at `https://themadcartographer.com/downloads/theme/phandelverv13/module.json`. The publisher currently returns **403 Forbidden** to anonymous automated requests. Use the publisher's supported login/install flow. It is recorded in [registry](./dependencies-v13.json) but excluded from automatic installation until access is confirmed.

The dependency meta-module does not and must not contain campaign modules, maps, NPCs, game worlds or other user-made Foundry content. These two provider packs are recorded but intentionally excluded from the automatic `requires` list.

## Export the installed V13/V14 packages

Double-click `Export-Module-Inventory.command` or run `python3 export_modules.py`. JSON files on Desktop:

- `foundry-v14-installed-modules.json`
- `foundry-v13-installed-modules.json`

Includes IDs, versions, compatibility data, and required/recommended relationships. Does not report per-world enabled module state. Review custom provider manifest URLs before sharing.

## Source references

- [Foundry package registry](https://foundryvtt.com/packages/)
- [3D to Isometric](https://foundryvtt.com/packages/3d-to-iso)
- [5e Item Importer](https://foundryvtt.com/packages/5e-item-importer)
- [Advanced Magic – Spell Points](https://foundryvtt.com/packages/dnd5e-spellpoints)
- [Argon Core](https://foundryvtt.com/packages/enhancedcombathud) / [Argon D&D5e](https://foundryvtt.com/packages/enhancedcombathud-dnd5e)
- [Isometric Perspective](https://foundryvtt.com/packages/isometric-perspective)
- [Multiple Document Selection](https://foundryvtt.com/packages/multiple-document-selection)
- [Whisper Box](https://foundryvtt.com/packages/WhisperBox)
- [Plutonium V13 manifest source](https://github.com/TheGiddyLimit/plutonium-next/blob/v2.18.3/module-foundry13.json)
- [Soundscape](https://foundryvtt.com/packages/soundscape)
- [Forgotten Adventures Battlemaps](https://foundryvtt.com/packages/fa-battlemaps)
- [MAD Cartographer Phandelver](https://foundryvtt.com/packages/mad-phandelver)
