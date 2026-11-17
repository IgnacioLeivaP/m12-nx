# Building Magic 2012

For first-time installation, follow the [numbered README steps](../README.md#start-here).
Prepare original files and dependencies first, build next, then copy only the generated
installation to the SD card. Commands with `^` use Windows **cmd.exe**, not PowerShell.
Other Xbox 360 years are linked in the [series index](../README.md#other-magic--duels-ports-for-nintendo-switch).

The installer runs the pipeline in `install/install.py`. It reads the 2012-specific
profile `install/games/mtg12.json`; the 2013 profile and plaintext-Lua patches do not apply.

1. Verify the base XEX, TU patch, WADs and optional DLC by SHA256.
2. Create an external work tree containing `app/`, `tools/`, `assets/game_root/` and `out/`.
3. Generate PS/Switch button textures and WAD variants from the user's textures.
4. Patch the user's compiled Lua carousel and content-enumeration scripts. Build a text
   Settings wrapper that loads the user's original BASIC.LOB and adds the port controls.
   No original bytecode or reconstructed original menu source is stored in this repository.
5. Build and verify the asset pack.
6. Build the host ReXGlue generator from the SDK, then translate the patched user XEX.
   `tools/prepare_codegen.py` adds the empty-worker polling backoff to the generated C++.
   A changed worker layout stops this stage. Automatic host codegen also runs this tool.
7. Extract shader containers, configure the host renderer, build `renut_shader_cache_gen`,
   build SPIRV-Cross/uam, translate to SPIR-V and GLSL, and assemble the deko3d package.
8. Configure the Switch build with devkitA64 and build the NRO.
9. Assemble the SD folder and write its SHA256 manifest.

The generator uses clang and `-march=x86-64-v2`. Host tools are not built with devkitA64.
The Switch uses Renut/deko3d; the old native Vulkan renderer and hand-translated hot
functions from other games are excluded. Shared engine helpers and attribution stay.

The SDK source is included. Its large dependencies are fetched separately, preserving
existing fork files. Four app dependencies must be provided separately through
`--thirdparty`; use port-compatible forks and initialized submodules rather than assuming
any current upstream checkout is interchangeable. SPIRV-Cross is supplied explicitly.

`--sdk` may point to an external SDK for local diagnostics. The default uses this repository's
fork. CMake output stays in the work tree; neither the base game nor the development `nx/`
tree is modified. Optional `--icon` is converted locally to a 256x256 JPEG.

The small handwritten shared-return compatibility hooks are specific to the 2012 TU.
The large worker function is generated from the user's executable and patched locally.

## Publication checks

```bat
py -3 tools/check_clean.py
py -3 tools/check_includes.py
py -3 tools/make_release_zip.py --version v1.0.0
```

The ZIP tool runs both audits again and aborts if either fails. The ZIP goes to
`../work/release/mtg12-nx-v1.0.0.zip`, outside the public tree. It contains source and
the installer, never a prebuilt NRO or game assets. Keep the validation status current.

