# CFB 27 – No Offline Warning

A mod for **EA Sports College Football 27 (PC)** that removes the **"Offline Warning"** popup shown before every **Dynasty** and **Road to Glory** game when you are playing offline / not logged in:

> **OFFLINE WARNING**
> You will be ineligible to earn trophy and mascot rewards when you are not logged in. Do you wish to continue?
> [Proceed Without Rewards] [Cancel]

If you play offline (for example, with mods enabled), this popup costs you one extra click every single game. With this mod the **Play Game** button goes straight into the game flow instead.

Made by **ASThome**.

## Download

Grab `NoOfflineWarning_v1.0.fbmod` from this repo (or the [Releases](../../releases) page).

## Install

1. Open **MMC Mod Manager** (the College Football 27 fork of Frosty Mod Manager).
2. Import `NoOfflineWarning_v1.0.fbmod`.
3. Enable it and launch the game through the mod manager as usual.

Load order does not matter unless another mod also replaces `common/ui/node_cfm/hub/corenode.ast` (unusual – that file is the Dynasty / RTG week-hub UI).

## What it changes

Exactly **one legacy asset**: `common/ui/node_cfm/hub/corenode.ast` — the career week-hub UI shared by Dynasty and Road to Glory (the node carries both the Dynasty and the `RTG_HUB` screens).

That file is an EA APT archive (Flash-style ActionScript bytecode). The `DynastyPlayButton` press handler contains logic equivalent to:

```actionscript
if (!LoginService.IsLoggedIn() && !PopupManager.IsPopupShowing(EXIT_POPUP)) {
    // show "OFFLINE_WARNING_POPUP"
} else {
    // start the game normally
}
```

The mod flips a single byte in that bytecode — a `push true` (`0x73`) becomes `push false` (`0x74`) in the second condition — so when you are offline the check evaluates false and the normal "start the game" path runs. Nothing else in the file is touched.

* **Online behaviour is unchanged.** When you are logged in, the first condition already short-circuits and the patched byte is never reached.
* No text, strings, or other UI elements are modified.
* The mod does **not** spoof login state. It only skips this one warning, so other online features are unaffected.

## Scope / known limitations

* Covers the **Dynasty** and **Road to Glory** week-hub Play button — the only place in the game's career/front-end UI that shows this popup. All 27 career and front-end UI nodes were scanned for the same check (`GetOfflineWarningInfo` / `OFFLINE_WARNING_POPUP`); it exists only in `node_cfm/hub`. Play Now has no such gate.
* Ultimate Team is online-only and is not touched.
* Title updates that change `common/ui/node_cfm/hub/corenode.ast` may require the mod to be rebuilt. If the popup returns after a patch, open an issue.

## Building from source

`OfflineWarningMod.fbproject` is the MMC Editor project. Open it in **MMC Editor** (College Football 27 profile) and use **File → Export to Mod** to produce the `.fbmod`.

To reproduce the patch from a clean game install:

1. In MMC Editor → Legacy Explorer, export `common/ui/node_cfm/hub/corenode.ast`.
2. Double-click the asset to open the AST editor and export the `DAT` entry (the decompressed `Apt Data:1:8:8` bytecode, 575,758 bytes for the v1.0 game build).
3. Change the byte at offset **145501** from `0x73` to `0x74`.
4. Re-import the entry (or re-pack the archive with zlib level 9 – it reproduces EA's original compressed size exactly), save the project, and export the mod.

The offset is specific to the game build the project was made against. If it moves after a title update, look for the byte pattern `49 12 4C B8 00 00 00 10 00 00 00 17 73 B9 01 AF` — the `73` is the byte to flip.

### Why this approach

The `IsLoggedIn()` check comes from a `LoginService` shared by many screens. Spoofing it globally would make other UI think you are online and trigger server errors, so this mod patches only the single caller that shows the warning.

## Disclaimer

Not affiliated with or endorsed by EA. Use mods offline only, per the College Football modding community rules. Use at your own risk.

## License

[MIT](LICENSE)
