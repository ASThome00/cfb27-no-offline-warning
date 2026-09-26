# Changelog

## 1.1.5 – 2026-09-26
- Rebuilt against the **September 26, 2026 title update**: fresh exports of `common/ui/node_cfm/hub/corenode.ast` and `common/ui/node_com/scriptpod.ast`, re-patched. Same two one-byte patches; no functional changes, online behavior unchanged.
- The update re-stamped both archives (new header IDs) but the ActionScript inside is byte-identical to September 3; patch sites unchanged (corenode @145869, scriptpod @1052548).
- Correction to 1.1.4: that build carried the September 3 copies of both files rather than fresh September 10 exports. Since the script has not changed since September 3, it behaved correctly.

## 1.1.4 – 2026-09-10
- Rebuilt against the **September 10, 2026 title update**: fresh exports of `common/ui/node_cfm/hub/corenode.ast` and `common/ui/node_com/scriptpod.ast` from the updated game, re-patched. Same two one-byte patches as v1.1.3 (Offline Warning + Account Error); no functional changes, online behavior unchanged.
- If you were on v1.1.3 and the September 10 update brought back either popup or broke a front-end screen with the mod enabled, update to this release.

## 1.1.3 – 2026-09-04
- **Fixes the blank EA Sports Network story cards** in Dynasty / Road to Glory after the September 3, 2026 update (thanks to pleasealonemeleave2 for the report).
- Root cause: v1.1.1 and v1.1.2 were re-exports of the same MMC project and still shipped the **August 25** copies of `common/ui/node_cfm/hub/corenode.ast` and `common/ui/node_com/scriptpod.ast`. MMC replaces the whole asset, so with the mod enabled the game was silently running the pre-update hub and script pod. The September 3 update changed both files (new hub screen-loader lifecycle, hint bar, Download Center filters, invite locks), and the new story-card screen depends on that updated hub code.
- Both assets re-exported from the updated game and re-patched. Same two one-byte changes as before (the patch sites moved +368 / +592 bytes); no functional changes to the mod itself, online behavior unchanged.
- The publish script now refuses to release when the project's embedded assets are byte-identical to the previous release, so a "rebuild" can no longer ship stale files.

## 1.1.2 – 2026-09-03
- Rebuilt against the **September 3, 2026 title update**. Same two one-byte patches as v1.1 / v1.1.1 (Offline Warning + Account Error); no functional changes, online behavior unchanged.
- If you were on v1.1.1 and the September 3 update brought back either popup, update to this release.

## 1.1.1 – 2026-08-27
- Rebuilt against **Title Update 3.5** (2026-08-27). Same two one-byte patches as v1.1 (Offline Warning + Account Error); no functional changes, online behavior unchanged.
- If you were on v1.1 and Title Update 3.5 brought back either popup, update to this release.

## 1.1 – 2026-08-25
- Also removes the **"ACCOUNT ERROR"** login-failure popup (the one MMC fills with *"Mods require being offline… -MMC/CFMC"*) that appears at boot and again when entering Dynasty / Road to Glory.
  One additional one-byte patch in `common/ui/node_com/scriptpod.ast` (`madden.online.module.Login._ShowLoginFailedPopup`).
- Fixed the source link in the mod description (`ASThome00`).
- Note: while the mod is active, *any* login-failure popup from that class is suppressed (there is no other user-visible effect; the login-failed callback still runs, so menus continue exactly as if you had pressed OK).

## 1.0 – 2026-08-25
- Initial release. Removes the Offline Warning popup on the Dynasty / Road to Glory week-hub Play button.
