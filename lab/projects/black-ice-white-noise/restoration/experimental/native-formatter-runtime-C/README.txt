Experimental source for the tested formatter runtime

The local Code Author wrote biwn_GPU_wait_repair.c. This is its unedited guided revision, not the initial draft: the first draft failed 832 of 1,024 native CPU cases. The coordinator supplied explicit SR bit positions and stack-bank feedback; the revision passes 8,192 instruction fixtures across all CCR values, interrupt masks and both CPU modes, plus seven host-error checks. This is six fixed entries implementing a coordinator-authored restoration repair, not a newly recovered original BIWN function or a weight-training result.

This C API performs one instruction per call. It requires the exact repaired 14,690-byte image: E098 jumps to162708, and the other five instruction entries are162708,162712,162714,16271E and162720. PC values are part of this frozen program contract; a relink requires a new mapping and validation. The API uses virtual D/A registers and logical bus callbacks. It is a host-side instruction-provider component, not a self-contained native-console game.

Build this component with make wait. The complete experimental host CPU provider is constructed by scripts/build_native_formatter_C_bridge.py, using the coordinate/static providers and the native-image translation already in the lab. Other added instruction cases were emitted by the coordinator's deterministic build-time translator. Their 414 new instruction forms pass79,488 controlled native CPU cases; the static catalogue size is not original-game function coverage.

The complete host backend owns every68000 instruction after mainstage4000 in the checked runs. The fresh1,600frame test and24,975frame merchant/outdoor route match the same repaired-disc native reference at every recorded frame for full CPU,2MBRAM,GPU/DSPstate and video. The long run also matches captured PCM and recorded navigation. These are finite frame-boundary checks, not proof of arbitrary aliases, faults, IRQ interleavings, other scenes, physical timing or whole-game completeness. Pre-mainstage bootstrap,GPU,DSP,devices and IRQ event services remain retained emulator providers.

Proofs:
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/GPU-wait-local-C-check-current.json
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-formatter-C-new-forms-current.json
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-formatter-C-fresh-pair-current.json
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-formatter-C-merchant-pair-current.json

Exact local model prompts and responses:
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/runs/GPU-wait-Code-Author-revision-20261018T230347.713918Z

No default preview or model weight was promoted. The original disc and existing game sources were preserved.
