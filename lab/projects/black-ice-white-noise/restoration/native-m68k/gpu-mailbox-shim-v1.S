.equ MAILBOX_PRIVATE_RESERVE,96
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
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,72(%a0)
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xe098
movem.l %a0-%a1,-(%sp)
move.w %sr,-(%sp)
lea (10-MAILBOX_PRIVATE_RESERVE)(%sp),%a0
movem.l %d0-%d7,(%a0)
move.l 2(%sp),32(%a0)
move.l 6(%sp),36(%a0)
movem.l %a2-%a6,40(%a0)
move.w (%sp),66(%a0)
movea.l 72(%a0),%sp
lea 4(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
rts
