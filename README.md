# mtg12-nx — Magic: The Gathering — Duels of the Planeswalkers 2012 for Nintendo Switch

A static recompilation of the Xbox 360 XBLA game, title `58410B3F`, with Title Update #3.
Built with ReXGlue and Renut's Direct3D renderer on deko3d. The PowerPC code is translated
to C++ on your PC and compiled into a native Switch `.nro`.

**This repository contains source code and an installer, not the game.** Supply your own
game, Title Update and optional DLC. No game data, generated game code, extracted menus,
translated shaders, NRO or NRO icon is distributed here.

## Requirements

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

## Install

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
