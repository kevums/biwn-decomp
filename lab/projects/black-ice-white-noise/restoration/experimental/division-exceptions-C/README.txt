BIWN DIVISION EXCEPTION ENTRY — EXPERIMENTAL HOST C COMPONENT

Run make here to compile the standalone exception-entry helper. This uses the restoration bus/CPU header contracts two directories above. It is a host virtual-CPU component, not an original-console ABI entry or a complete game port.

The C source is the unedited local Code Author compact response, supplied an explicit pinned-emulator contract. Null/missing callbacks and unsupported SR bits return1. Failed callbacks return2 with the caller CPU unchanged and prior bus writes retained. Success clears V, switches the active stack if needed, pushes resumePC then oldSR, reads vector5 at address20, and returns11 for the host prefetch flush. The vector is read after the writes, unlike the separate IRQ entry.

Separate coordinator code handles the28 fixed DIVU/DIVS entries and cost-model edge cases. Component CPU/RAM/cost checks and strict owner exception/RTE checks are separate from fresh gameplay. No new original-game function coverage, whole-game timing, physical console or training claim.

Exact prompt/response:
/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/runs/divzero-Code-Author-compact-20261018T233916.591909Z/prompts-and-responses.txt
