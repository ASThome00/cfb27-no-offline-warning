# Changelog

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
