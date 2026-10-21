Original-facing sprite creator: 137E0

sprite-create-reference.c is the coordinator's high-level C reconstruction.
sprite-create-shim.S preserves the packed original call stack, D2-D7/A2-A6,
full helper-entry CPU/SR, original helper SP and returned caller registers/SR.
It calls real guest105DA,152A2andE2B8; no original137E0body is delegated.
Original callback-table WORD reads remain ordered guest data reads. Unknown
modified targets trap. The source is intended for the finite checked original
RAM/table contract; arbitrary faults/concurrency are not reconstructed here.

Build from this directory:
 make -f Makefile.sprite-create sprite-create ADDRESS=0x180000

Prototype: 2,180bytes,448-byte private reserve,596maximum private stack in the
1,228case matrix. Final address in the23,260byte experimental resident payload
is0x164018. Existing24,512reservation,heap0x164D80and373,376capacity remain fixed.
Original-facing13AE0/134DC/137E0together pass2,084cases/max630private bytes.
All184original executable sites are covered;70inlinecallback-table bytes are
data. C99functionality with a generic ABI already existed in actor-group-restored.c;
this is original-interface reconstruction/integration, not a new logical count.

Authoritative commands run from the lab root with its.venv/bin/python:
 scripts/check_biwn_native_sprite_create.py
 scripts/check_biwn_native_sprite_create_linked.py --parent-build verification/native-actor-initialize-disc-build-current.json --address 0x164018
 scripts/check_biwn_native_actor_triple.py
 scripts/qualify_biwn_native_sprite_create_v2.py
 scripts/check_sprite_create_final_startup.py
 scripts/check_sprite_create_live_contexts.py

The component matrix runs original-versus-C with ordered public RAM accesses
and native CPU replay of all returned registers/SR/banks and actual helper-entry
CPU/SP/SR/arguments. Shared105DAexecutes (original in prototype, previously
compiled in final layout); four other external leaf helpers are prescribed in
the coupled actor group. Selected changing handle rereads are included.
The read-only oracle matrix additionally checks actual saved contexts around
helpers and the decoder's leftover allocator stack argument. 8,672original/C
root executions and five decoded-CPU/mirror-only corruption controls pass.
Four source/binary missing-body/helper-X/callback/original-delegation defects
are rejected separately. Fullpayloadstartup passes96cases.

Live gameplay, actual allocator/decoder resource behavior, observed task-stack
limits and media differences are separate evidence. See the current reviewed
sprite integration receipt when present. Neither this README nor a passing
component matrix establishes a complete game, timing/media equality, a physical
Jaguar CD rebuild or easy native LMStudioChat inference. Default interactive
preview is a separate older checkpoint and is not replaced by these commands.
