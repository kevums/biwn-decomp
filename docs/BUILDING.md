# Build and restore

The standalone current modules use an `m68k-elf-` GCC toolchain. The preserved Mac toolchain reports GCC 15.2.0. It is not included in this repository.

The original Makefiles accept `PREFIX` and `BUILD` overrides. For example, from the repository root:

```sh
make -C lab/projects/black-ice-white-noise/restoration/native-m68k/actor-phased-fixed-v2 \
  PREFIX=/absolute/path/to/m68k-elf- MODULE=dispatch ADDRESS=0x163788 BUILD=/tmp/biwn-dispatch
make -C lab/projects/black-ice-white-noise/restoration/native-m68k/actor-phased-fixed-v2 \
  PREFIX=/absolute/path/to/m68k-elf- MODULE=initialize ADDRESS=0x1639c4 BUILD=/tmp/biwn-initialize
make -C lab/projects/black-ice-white-noise/restoration/native-m68k/frame-acquire-phased-split-v2 \
  PREFIX=/absolute/path/to/m68k-elf- ADDRESS=0x162724 TAIL_ADDRESS=0x17f31c BUILD=/tmp/biwn-frame
```

The actor addresses above are module block starts. Use `actor_phased_symbols` and `frame_phased_symbols` from the current build metadata for internal entries and returns; inherited historical symbols may be superseded. The original Makefiles' default addresses are not necessarily the integrated v41 addresses.

Building these modules does not rebuild a complete game. Integration still requires the original BIWN #23 disc, resident image/provider dependencies, the recorded layout and the relevant tooling/evidence. Restore the original CDI, if needed, to `lab/projects/black-ice-white-noise/originals/BIWN#23.cdi` from the separate backup or the user's original copy. Restore firmware and test artifacts separately; none is downloaded by this repository.

The copied scripts primarily come from a Python 3.12 macOS workspace. Individual checks use additional libraries, including Unicorn, and native emulator/toolchain components. There is no newly validated universal dependency lockfile or Windows installer. The separate handover and preserved build receipts describe the original environment.

## Historical paths

The original lab root was:

```text
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab
```

It maps to `lab/` in this repository. Do not globally rewrite preserved evidence JSON or copied source and then expect its original hashes to match. Adapt paths in a new working copy or in the replay environment, keeping the archived snapshot intact.

## Checks recorded for this publication

`snapshot/publication-checks.json` records the source-manifest check, credential-pattern scan and standalone module rebuild comparison performed for this publication. These checks are separate from the historical game tests. Historical tests have not all been rerun by preparing this repository, and no whole-game fidelity or console claim is added.
