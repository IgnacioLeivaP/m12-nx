# Validation of the public source release

Prepared and checked on 2026-11-17. The development port was previously played on
Nintendo Switch. These checks concern the newly separated source distribution.

| Check | Result |
|---|---|
| Python syntax, installer help and complete dry run | Passed |
| Base XEX, TU patch, data WADs, five DLC packages | SHA256 verification passed |
| Main carousel and content-enumeration patches | Byte-identical to the development port's tested files |
| Settings wrapper | Passed host Lua 5.1 tests with original instructions after binary-container conversion: original callbacks/reset retained; new controls and commands work |
| Button variants | PS and Switch each contain 209 entries, matching the tested variants' paths; all 179 original TU entries remain byte-identical |
| Shader extraction from base and TU WADs | 425 distinct containers; no invalid containers found |
| Fresh code generation from user XEX/TU | Passed; worker backoff applied and repeat run is idempotent |
| Switch configuration and full NRO compilation/link | Passed with devkitA64 GCC 15.2.0, Ninja, 6 jobs, LTO off |
| NRO metadata | Magic 2012 / Nispero / 1.0.0, checked from the NRO asset section |
| Complete installer from an empty PC/work tree | Not run |
| Console playthrough of this newly built NRO and Settings wrapper | Not run |

The build used the public application and SDK source, a fresh generated game tree,
and complete locally available external dependencies. The host generator, shader tools,
and shader release cache came from the working development environment. This validates
compilation and linkage of the prepared source; it does not certify the automatic host
tool/dependency bootstrap or a freshly translated shader package.

Publication packaging runs both `tools/check_clean.py` (including original-file SHA256
comparisons) and `tools/check_includes.py` and aborts if either fails. The release ZIP
contains only the source distribution and installer. No generated NRO, shaders, data
pack, original Lua, DLC or game art is included.

The new Settings wrapper and geometrically generated icons preserve the tested menu
operations and texture coverage but still need a visual test on hardware. No console
delivery was performed as part of preparing this source release.
