Original-facing actor movement: 13C9A..13F12

actor-move-reference.c adapts the existing high-level portable movement body to
native68000memory and original helper interfaces. actor-move-shim.S preserves
D2-D7/A2-A5and the original packed stack; four captures execute real13440direction,
E220GPUsubmission,13B5Aoutdoorcollision and13BB0indoorcollision where called.
The register context carries original workingSP(r15),SR(r16),Ccontinuation(r17).
The original40saved bytes and448private reserve place72context bytes atrootSP-488.
At helperentry, contextSP equals actualSP+4; it is not the original rootSP.

Build from this directory:
 make -f Makefile.actor-move actor-move ADDRESS=0x180000

The prototype and final-address matrices pass2,624cases/all192original sites.
Returned CPU/SR/banks, actual helper-entryCPU/SR/SP/args, ordered public accesses
and public2MBRAM compare. Actual13440/E588execute in the direction/linked matrix;
GPU/collision effects remain prescribed there. Four source/binary defects reject.
Private frames/installation/returnPC exclusions are explicit. Arbitrary faults,
concurrency, modifiedtables and real device outcomes remain outside this proof.
Final context oracle:5,248original/Croot executions, four decodedCPU/mirror-only
corruption controls reject. Monitor never writes actual nativeCPU/gameRAM.

Native code2,960bytes at0x16489C. Current experimental payload26,220bytes in a
28,544reservation, heap0x165D40/capacity369,344. Staging moved toF7000/clear28,672
endingFE000to preserve Atari trailer94nonzero bytes atFE520. NaiveF8000growth
would overwrite the trailer. Fullpayload96startup,heapinit192,nativecopy-blitter
3,392andordered3,392plus36capacity requests pass at the new floor.

Fresh emulator candidate24,996frames/control29,804both return outdoors. Only
13C9Aentry restored in the same-layoutcontrol. Candidate13,898native movement
returns,31,745actual helpercalls/context checks:13,898direction,13,898submission,
3,949outdoor collision,0indoor collision. All ABI/context/task-boundary errors
zero; movement672maximum private depth/min246taskheadroom on these observed
paths. Indoor movement collision and unclassified helper success/failure/rollback
outcomes need broader live coverage. No arbitrary stack bound is inferred.

Video/audio/state/timing differ. Existing interactive preview remains unchanged.
This is coordinator source/ABI/fixtures/integration, not new local Author code,
new training, whole-game speedup, complete readable same-console rebuild or
physical-console readiness. Follow the current reviewed integration report;
do not transfer older strict C-processor jobs to this disc.
