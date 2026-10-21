# Black Ice / White Noise — partial decompilation

Recovered Atari Jaguar CD source, native integration experiments and verification records. The current saved checkpoint is **v41, `native-actor-phased-v41-experimental`**, dated 21 October 2026. It remains unpromoted and is not a complete source-built game.

## Current result

The fresh native-input route completed 25,024 frames; the original-input control completed 25,011. Both completed the tested outdoor/indoor/Deck route and returned outdoors. Each lane recorded 15/15 actor-dispatch returns, 13/13 initializer returns, 18/18 initializer-helper returns and 124/124 frame-acquire returns, with the recorded monitors clear and quiescent.

This is a finite route pass. The runs used different adaptive input schedules, differed on 6,950 paired video samples, and both audio captures were silent. Fixed-input fidelity, working audio, a complete readable-source rebuild and physical-console validation remain open. Earlier failed versions and historical results are labelled in their original records.

## Start here

- [Current decompilation status](lab/CURRENT%20DECOMPILATION.txt)
- [v41 technical report](lab/reports/BIWN%20v41%20Phased%20Actors%20and%20Fresh%20Route%20Pass.txt)
- [Detailed handover](lab/transfer-handover-2026-10-21/BIWN%20AND%20LOCAL%20AI%20-%20TRANSFER%20HANDOVER.txt)
- [Latest publication facts](lab/verification/actor-phased-image-delivered-v1/20261021T150727.853550Z/facts.json)
- [Build and restore instructions](docs/BUILDING.md)

Older READMEs inside the preserved source tree describe earlier checkpoints. The status and report linked above take precedence for the current snapshot.

## Layout

| Path | Contents |
| --- | --- |
| `lab/projects/black-ice-white-noise/restoration/` | Recovered C, assembly, headers, linker scripts and historical source profiles |
| `lab/projects/black-ice-white-noise/restoration/native-m68k/actor-phased-fixed-v2/` | Current phased actor source |
| `lab/projects/black-ice-white-noise/restoration/native-m68k/frame-acquire-phased-split-v2/` | Current phased frame-acquire source |
| `lab/projects/black-ice-white-noise/analysis/` | Selected static reverse-engineering exports and maps |
| `lab/scripts/` | Game analysis, reconstruction, integration and verification scripts, with local script dependencies |
| `lab/reports/` | Game reports and recorded limitations |
| `lab/verification/`, `lab/builds/` | Selected textual evidence and build metadata |
| `snapshot/` | Source hashes, packaging record and external-artifact index |

## Scope and preservation

This Git repository preserves a source/research snapshot. The full model-excluded archival backup is a separate approximately 210 GB compressed transfer, expanding to approximately 1.6 TB. This repository does not replace it.

Disc images, BIOS/ROM payloads, raw RAM and video/audio captures, compiled binaries, downloaded tools, AI models, training weights, advertising research and account credentials are outside this repository's scope. Small textual evidence is selected; it is not the entire historical verification corpus. See `snapshot/external-artifacts.json` for referenced artifacts omitted from the source snapshot.

Original copied files are byte-preserved. Historical absolute paths and hashes intentionally remain unchanged. Some scripts depend on the original workspace and external artifacts; cloning alone does not make every historical run reproducible. Restore those dependencies and adapt a working copy's paths before replaying runs.

Run `python3 tools/verify_snapshot.py` to verify the copied source hashes. No additional decompilation, model inference or training is performed by this check.
