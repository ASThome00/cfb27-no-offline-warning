# CFB 27 – No Offline Warning

A mod for **EA Sports College Football 27 (PC)** that removes the nag popups you get when playing offline / not logged in (for example, with mods enabled):

**1. The "Offline Warning"** shown before every **Dynasty** and **Road to Glory** game:

> **OFFLINE WARNING**
> You will be ineligible to earn trophy and mascot rewards when you are not logged in. Do you wish to continue?
> [Proceed Without Rewards] [Cancel]

**2. (v1.1) The "Account Error"** login-failure popup shown at boot and again every time you enter Dynasty or Road to Glory — with MMC this is the one that reads:

> **ACCOUNT ERROR**
> Mods require being offline. You won't be able to sign in or access modes like Superstar/Online Dynasty while modding. Enjoy!! -MMC/CFMC
> [OK]

With this mod the **Play Game** button goes straight into the game flow, and the menus no longer stop for the account-error dialog. If you like using the MMC notice as a "my mods loaded" indicator, stay on v1.0 — it only removes the first popup.

Made by **ASThome**.

## Download

Grab the latest `NoOfflineWarning_vX.Y.fbmod` from this repo (or the [Releases](../../releases) page).

## Install

1. Open **MMC Mod Manager** (the College Football 27 fork of Frosty Mod Manager).
2. Import the `.fbmod` (remove or disable any older version).
3. Enable it and launch the game through the mod manager as usual.

Load order does not matter unless another mod also replaces one of the two files below (unusual — they are front-end UI script files).

## What it changes

Exactly **two legacy assets**, one byte each:

| File | Class / function | Byte | Effect |
|---|---|---|---|
| `common/ui/node_cfm/hub/corenode.ast` (v1.0) | `art_control.button.DynastyPlayButton` press handler | `0x73 → 0x74` @ 145501 | skips the Offline Warning |
| `common/ui/node_com/scriptpod.ast` (v1.1) | `madden.online.module.Login._ShowLoginFailedPopup` | `0x49 → 0x48` @ 1051956 | never opens the login-failed popup |

These files are EA APT archives (Flash-style ActionScript 2 bytecode).

### Offline Warning (v1.0)

The `DynastyPlayButton` press handler contains logic equivalent to:

```actionscript
if (!LoginService.IsLoggedIn() && !PopupManager.IsPopupShowing(EXIT_POPUP)) {
    // show "OFFLINE_WARNING_POPUP"
} else {
    // start the game normally
}
```

A `push true` (`0x73`) becomes `push false` (`0x74`) in the second condition, so when you are offline the check evaluates false and the normal "start the game" path runs. Online behaviour is unchanged — when you are logged in, the first condition already short-circuits and the patched byte is never reached.

### Account Error (v1.1)

Every login failure in the front end ends up in one function of the shared `Login` module:

```actionscript
_ShowLoginFailedPopup(title, message, reason) {
    _LoginFailedCallback(reason);           // tells the waiting screen "login failed, carry on"
    if (mShowLoginFailedPopup == true) {    // <-- patched
        popup = PopupManager.MakeGenericPopup(LOGIN_FAILED_POPUP_NAME);
        popup.SetTitle(LocalizeText(title));      // "OSDK_ACC_ERR" = "Account Error"
        popup.SetMessage(LocalizeText(message));  // the reason string the login adapter reports
        popup.AddButton(LocalizeText("OSDK_OK"));
        popup.Open();
    }
    mShowLoginFailedPopup = true;
}
```

The `Equals2` opcode in the `if` (`0x49`) becomes `Less2` (`0x48`), turning the gate into `true < mShowLoginFailedPopup`, which is never true. The callback that lets the calling screen continue runs *before* the gate and is untouched, so the game behaves exactly as if you had pressed OK — just without the dialog. (Flipping the `true` literal instead would have inverted the behaviour for callers that deliberately set the flag to `false`, e.g. silent sign-in attempts.)

* No text, strings, or other UI elements are modified. The message text itself is not stored in the game files — it is supplied at runtime by whatever breaks the sign-in.
* The mod does **not** spoof login state. Other online features are unaffected.
* Side effect: while the mod is active, *any* login-failure popup from this module is suppressed (e.g. a genuine "EA servers unavailable" message). Since mods require playing offline anyway, this has no practical impact.

## Scope / known limitations

* Covers the **Dynasty** and **Road to Glory** week-hub Play button — the only place in the career/front-end UI scripts that shows the Offline Warning (all 27 career and front-end UI nodes were scanned; it exists only in `node_cfm/hub`). The similar-looking Offline Warning on **Play Now** (main menu → Play → Play Now) is shown by the game's native code rather than by the UI scripts, so it is out of reach for this kind of mod and is **not** removed.
* The account-error patch covers the login-failed dialog at boot and on Dynasty/RTG entry. Other MMC-related notices (if any are added in future MMC versions) are separate.
* Ultimate Team is online-only and is not touched.
* Title updates that change either file require the mod to be rebuilt from a **fresh export** of both assets (v1.1.3 → September 3, 2026 update). Because MMC replaces the whole asset, an out-of-date build silently rolls those two files back to an older version — v1.1.1/v1.1.2 did exactly that and broke the EA Sports Network story cards. If a popup returns, or a new front-end feature stops working after a patch, open an issue.

## Building from source

`OfflineWarningMod.fbproject` is the MMC Editor project. Open it in **MMC Editor** (College Football 27 profile) and use **File → Export to Mod** to produce the `.fbmod`.

To reproduce the patches from a clean game install:

1. In MMC Editor → Legacy Explorer, export `common/ui/node_cfm/hub/corenode.ast` and `common/ui/node_com/scriptpod.ast`.
2. Run `python tools/build_patch.py <exported.AST> <patched.AST>` on each. The script finds the patch site by byte pattern (falling back to the known offset), flips the byte, recompresses (zlib level 9, or [zopfli](https://pypi.org/project/zopfli/) when the zlib stream no longer fits the original slot) and rewrites the archive with the original header/TOC untouched. It refuses to write anything ambiguous.
3. Legacy Explorer → right-click the asset → **Import** the patched file, save the project, and export the mod.

Byte patterns, if the offsets move after a title update:

* Offline Warning: `49 12 4C B8 00 00 00 10 00 00 00 17 [73] B9 01 AF`
* Account Error: `5A B9 01 B2 E6 73 B9 01 AF 48 [49] B8 00 00 7A 00 00 00`

### Why this approach

The `IsLoggedIn()` check and the login-failure handling come from services shared by many screens. Spoofing login state globally would make other UI think you are online and trigger server errors, so this mod patches only the two specific spots that show the dialogs.

## Disclaimer

Not affiliated with or endorsed by EA. Use mods offline only, per the College Football modding community rules. Use at your own risk.

## License

[MIT](LICENSE)
