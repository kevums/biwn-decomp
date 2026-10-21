.equ POOL_BASE,0xc0928
.equ POOL_BYTES,0x19400
.text
.globl biwn_outer_entry
biwn_outer_entry:
/* Original LINK and local initializers overwrite these eight scratch bytes.
 * The deployed redirect must cover twelve whole original bytes. */
movem.l %d0/%a0,-(%sp)
move.w %sr,%d0
movea.l %d0,%a0
move.l 0xc0920,%d0
subi.l #POOL_BASE,%d0
cmpi.l #POOL_BYTES,%d0
bhs.w .Linvalid
tst.b %d0
bne.w .Linvalid
btst #8,%d0
bne.w .Linvalid
btst #9,%d0
bne.w .Linvalid
lsr.l #8,%d0
lsr.l #2,%d0
mulu.w #384,%d0
addi.l #(OUTER_ARENA_BASE+16),%d0
exg %d0,%a0
tst.l 114(%a0)
bne.w .Lbusy
move.w %d0,80(%a0)
movem.l %d1-%d7,8(%a0)
movem.l %a1-%a6,40(%a0)
move.l (%sp),4(%a0)
move.l 4(%sp),36(%a0)
lea 8(%sp),%a1
move.l %a1,64(%a0)
move.l #0x11e6c,68(%a0)
clr.l 72(%a0)
clr.l 76(%a0)
btst #5,80(%a0)
beq.s 1f
move.l %a1,76(%a0)
bra.s 2f
1:move.l %a1,72(%a0)
2:move.l #1,114(%a0)
bra.w .Lbody
.Linvalid:
move.l %a0,%d0
.Lbusy:
move.w %d0,%ccr
movem.l (%sp)+,%d0/%a0
jmp biwn_outer_original_fallback
.globl biwn_outer_original_fallback
biwn_outer_original_fallback:
link.w %a6,#-8
move.l 0x11e64,-8(%a6)
jmp 0x11e78

.globl biwn_outer_resume
biwn_outer_resume:
/* No scratch push at internal boundaries: the original loop did not push
 * registers here. A checked immutable pointer in each existing Deck slot
 * permits SP-only lookup of a compact384-byte outer frame. */
movea.l 0xc0920,%sp
adda.l #(DECK_ARENA_BASE+392-POOL_BASE),%sp
movea.l (%sp),%sp
move.w %sr,80(%sp)
lea 64(%sp),%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea -4(%sp),%a0
.Lbody:
lea 352(%a0),%sp
move.l %a0,-(%sp)
bsr.w biwn_outer_body
lea 4(%sp),%sp
lea -352(%sp),%a0
tst.l 94(%a0)
beq.s .Lcomplete
cmpi.l #6,94(%a0)
bne.s .Lerror
cmpi.l #0x11e86,68(%a0)
beq.s .Literation
cmpi.l #0x11f50,68(%a0)
bne.s .Lerror
movea.l 64(%a0),%sp
move.w 80(%a0),%ccr
movem.l 4(%a0),%d0-%d7/%a0-%a6
.globl biwn_outer_wait_boundary
biwn_outer_wait_boundary:
bra.w biwn_outer_resume
.Literation:
movea.l 64(%a0),%sp
move.w 80(%a0),%ccr
movem.l 4(%a0),%d0-%d7/%a0-%a6
.globl biwn_outer_iteration_boundary
biwn_outer_iteration_boundary:
bra.w biwn_outer_resume
.Lcomplete:
clr.l 114(%a0)
movea.l 64(%a0),%sp
move.w 80(%a0),%ccr
movem.l 4(%a0),%d0-%d7/%a0-%a6
.globl biwn_outer_return
biwn_outer_return:
rts
.Lerror:illegal

.macro capture name,target
.globl biwn_outer_capture_\name
biwn_outer_capture_\name:
movem.l %d2-%d7/%a2-%a6,-(%sp)
movea.l 48(%sp),%a0
movea.l 52(%sp),%a1
move.l %sp,98(%a0)
move.l %a1,102(%a0)
move.l 60(%a1),106(%a0)
movea.l 60(%a1),%a2
move.l (%a2),110(%a0)
move.l 56(%sp),(%a2)
movea.l %a2,%sp
move.w 76(%a1),%ccr
movem.l (%a1),%d0-%d7/%a0-%a6
jmp \target
.endm
capture initialize,0x10990
capture scan,0x11828
capture clear,0xe03a
capture record,0x10c6e
capture reset,0x1102a
capture geometry,0x11ad4
capture mail,0x16bf4
capture texture,0x10e72
capture coordinate,0x11d1a
capture display_begin,0xe19e
capture display_submit,0xe202
capture display_end,0xe098
capture tail,0x17f14

.globl biwn_outer_helper_return
biwn_outer_helper_return:
movea.l 0xc0920,%sp
adda.l #(DECK_ARENA_BASE+392-POOL_BASE),%sp
movea.l (%sp),%sp
move.w %sr,80(%sp)
lea 64(%sp),%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea -4(%sp),%a0
move.l 106(%a0),64(%a0)
move.l #0,68(%a0)
movea.l 106(%a0),%a2
move.l 110(%a0),(%a2)
movea.l 98(%a0),%sp
.globl biwn_outer_capture_end
biwn_outer_capture_end:
movem.l (%sp)+,%d2-%d7/%a2-%a6
moveq #0,%d0
rts
.globl biwn_outer_asm_end
biwn_outer_asm_end:
