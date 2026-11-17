# mtg12-nx — Magic: The Gathering — Duels of the Planeswalkers 2012 for Nintendo Switch

<!-- magic-series:start -->
## Other Magic / Duels ports for Nintendo Switch

Each project uses its own game files and installation method. The two 2015 ports are
separate projects; Xbox 360 files cannot be used with the Android port or vice versa.

| Game | Original version | Project and installation guide |
|---|---|---|
| Duels of the Planeswalkers (2009) | Xbox 360 + required PC data | [m09-nx](https://github.com/IgnacioLeivaP/m09-nx#start-here) |
| Magic 2012 | Xbox 360 | [m12-nx](https://github.com/IgnacioLeivaP/m12-nx#start-here) |
| Magic 2013 | Xbox 360 | [m13-nx](https://github.com/IgnacioLeivaP/m13-nx#start-here) |
| Magic 2014 | Android 1.5.0 | [Duels14_nx](https://github.com/IgnacioLeivaP/Duels14_nx#start-here) |
| Magic 2015 | Android 1.4.4959 | [duels_nx](https://github.com/IgnacioLeivaP/duels_nx#start-here) |
| Magic 2015 | Xbox 360 | [m15-nx](https://github.com/IgnacioLeivaP/m15-nx#start-here) |

Otros años: los enlaces llevan a las instrucciones de cada port. Comprueba la versión
de origen antes de preparar los archivos; las versiones Android y Xbox 360 son distintas.
<!-- magic-series:end -->

A static recompilation of the Xbox 360 XBLA game, title `58410B3F`, with Title Update #3.
Built with ReXGlue and Renut's Direct3D renderer on deko3d. The PowerPC code is translated
to C++ on your PC and compiled into a native Switch `.nro`.

**This repository contains source code and an installer, not the game.** Supply your own
game, Title Update and optional DLC. No game data, generated game code, extracted menus,
translated shaders, NRO or NRO icon is distributed here.

## Start here

This is a **source release**: build the NRO on Windows from your own game before copying
anything to the Switch. Follow these steps in order:

1. [Check requirements](#step-1--check-requirements), including the exact game and TU.
2. [Prepare original files and dependencies](#step-2--prepare-your-inputs-and-dependencies).
3. [Run the installer](#step-3--build-the-switch-installation) from the repository root.
4. [Copy the generated folder and launch](#step-4--copy-to-sd-and-launch) using title takeover.

If a step fails, stop there and read its error; skipping shaders or other required build
stages does not produce a complete installation. Technical details: [docs/BUILD.md](docs/BUILD.md).

## Step 1 — check requirements

- Windows, Python 3.9+, LLVM clang, CMake 3.25+, Ninja, and bash.
- devkitPro with devkitA64, libnx and deko3d.
- Python packages: `py -3 -m pip install Pillow numpy xxhash zstandard`.
- Your base game files, including `default.xex`, `Data_Core.wad`, and its other WADs.
- Title Update #3: `default.xexp` and `Update001.wad`.
- Optional: Expansion Pack, Deck Packs 1–3, Multiplayer Pack, and your NRO icon.
- SDK dependencies: fetch with `py -3 tools/fetch_thirdparty.py`, or use
  `--source <local rexglue-sdk checkout>` to fill them from a local copy. The fetcher
  pins upstream commit `c94f5ebdcb3c9d1a460ca48e04f9758448f8d518`; it preserves fork files.
- A `--thirdparty` directory with the port-compatible `plume`, `uam`, `imgui` and
  `reblue-XenosRecomp` sources, including their submodules and XenosRecomp's DXC binaries/runtime DLLs. See [THIRD_PARTY.md](THIRD_PARTY.md).
- SPIRV-Cross sources supplied with `--spirv-cross-source` for the PC shader tools.

Use native Windows CMake/Ninja on Windows. The MSYS versions failed with a signal-pipe
error in the development environment. clang must support `-march=x86-64-v2`.

## Step 2 — prepare your inputs and dependencies

Download and extract this repository's source ZIP, or clone it with Git. Open a Windows
**cmd.exe** terminal in that folder; the examples use `^` for line continuation (not
PowerShell's syntax). Install the tools and Python modules listed in step 1.

Extract your own base game and Title Update into separate input folders. If you have
STFS packages rather than loose files, download the series' [standalone STFS extractor](https://github.com/IgnacioLeivaP/m13-nx/blob/main/tools/stfs_extract.py)
outside this repository, and run it for each package:

```bat
py -3 C:\tools\stfs_extract.py "C:\my-package" "C:\extracted-files"
```

Keep the originals unchanged. Check the required filenames and hashes against the game
profile linked below. Optional DLC can be omitted; the required Title Update cannot.

Fill the SDK dependencies before the first build:

```bat
py -3 tools/fetch_thirdparty.py
```

This fetch uses the network. To use an existing SDK checkout with its submodules,
add `--source "C:\local-rexglue-sdk"`. Separately prepare `--thirdparty` with the
port-compatible dependencies listed in [THIRD_PARTY.md](THIRD_PARTY.md). Fetching the
SDK libraries does not supply those application dependencies. Use a new output folder
outside this source repository; keep your source, input game and output folders separate.

## Step 3 — build the Switch installation

Run from a terminal with the tools above on PATH:

```bat
py -3 install/install.py --game mtg12 ^
  --data "C:\my-game" --xex "C:\my-game\default.xex" ^
  --xexp "C:\my-title-update\default.xexp" --tu "C:\my-title-update" ^
  --dlc "C:\my-dlc" --thirdparty "C:\port-dependencies" ^
  --spirv-cross-source "C:\SPIRV-Cross" --icon "C:\my-icon.jpg" ^
  --out "C:\mtg12-output" --jobs 6
```

`--dlc` and `--icon` are optional. `--tu` is unnecessary if `Update001.wad` is already in
the data folder. Use `--help` and `--list-steps` for details; `--dry-run` prints commands.
The output and staging folders must be outside this repository. A full install requires
a fresh staging folder. `--only` and `--skip` are recovery tools; they do not manufacture
missing results of earlier stages.

The installer verifies your files against `install/games/mtg12.json`, creates the button
icons and menus from your originals, translates shaders, runs ReXGlue, builds the NRO,
and produces `switch/mtg12-nx/` plus `SHA256_mtg12-nx.txt`.

## Step 4 — copy to SD and launch

Copy that folder to `sdmc:/switch/`. Preserve your existing saves and settings when updating.
Start it through title takeover: hold **R** while launching an installed game, then open
the Homebrew Menu. Album applet mode does not provide enough memory.

## Features and limitations

- Campaign, local game, deck management, base decks and five optional DLC packages.
- TU #3 and the worker idle-backoff fix required for reasonable match-loading speed.
- Language and Xbox / PlayStation / Switch button-icon settings, saved between runs.
- Menus hide the online, scoreboard, extras and download entries; startup content enumeration is hidden.
- Touch input, sound and Renut rendering; videos are skipped.
- The original Achievements entry remains and may do nothing.
- DLC status reports installed packages, not proof that every deck/campaign is usable.
- Icon changes require a restart; the menu does not yet show a dedicated restart notice.
- The functional development port was played on Switch. This newly prepared public installer
  has a separate validation status: see [docs/VALIDATION.md](docs/VALIDATION.md). Do not assume
  the development build's tests also certify a fresh installation from this repository.

## Layout and licenses

`app/` contains the port, `sdk/` its ReXGlue fork, `install/` the installer and game profile,
`tools/` the conversion/build tools, and `docs/` build and validation notes.

The port's own code is GPL-3.0-or-later, copyright Nispero 2026; see [LICENSE](LICENSE).
The SDK retains its BSD-3-Clause license and third-party notices. Renut reuse is recorded
in [THIRD_PARTY.md](THIRD_PARTY.md), together with the source projects and their licenses.
Shared engine/helper identifiers retain their upstream names; they do not include the
assets or complete ports of those other games.

Credits: ReXGlue/Xenia, StevenSND's Horizon layer, masterspike52's reNut, renderbag's plume,
hedge-dev's XenosRecomp, fincs/devkitPro's uam and deko3d, and the reference ports listed
in THIRD_PARTY.md.

This fan project is unaffiliated with Wizards of the Coast, Hasbro, Stainless Games,
Microsoft or Nintendo. The game and its trademarks belong to their respective owners.
Do not redistribute the game data or the generated installation folder.

