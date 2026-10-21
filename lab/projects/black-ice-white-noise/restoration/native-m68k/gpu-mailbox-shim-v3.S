/*124bytes: logical CPU76 + Ccallee saves44 +4bytes for original E098 JSR.
 * Actual original/pending-repair E098 changes CCR, preserves every D/A register.
 * The fixed helper's preservation is checked against original/native execution.
 * Ccallee saves reside in context, not a second44byte stack frame. */
.equ MAILBOX_PRIVATE_RESERVE,124
.text
.macro mailbox_root symbol,entry
.globl \symbol
\symbol:
lea -MAILBOX_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea MAILBOX_PRIVATE_RESERVE(%sp),%a0
move.l %a0,60(%sp)
move.l #\entry,68(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_gpu_mailbox_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea MAILBOX_PRIVATE_RESERVE(%sp),%sp
.globl \symbol\()_return
\symbol\()_return:
rts
.endm
mailbox_root biwn_native_gpu_submit_4320,0xe220
mailbox_root biwn_native_gpu_submit_4b00,0xe2b8
.globl biwn_native_gpu_mailbox_wait_capture
biwn_native_gpu_mailbox_wait_capture:
movea.l 4(%sp),%a0
movem.l %d2-%d7/%a2-%a6,76(%a0)
move.l %sp,72(%a0)
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xe098
move.w %sr,-(%sp)
lea (2-MAILBOX_PRIVATE_RESERVE)(%sp),%a0
move.w (%sp),66(%a0)
movea.l 72(%a0),%sp
movem.l 76(%a0),%d2-%d7/%a2-%a6
rts
