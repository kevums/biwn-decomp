.equ POOL_BASE,0xc0928
.equ POOL_BYTES,0x19400
.text
.macro root name,entry,offset,top
.globl biwn_v4_\name
biwn_v4_\name:
/* Eight guest scratch bytes, matching the smallest original save frame.
 * Keep SR in A0 while D0 validates the task; no extra guest word is dirtied. */
movem.l %d0/%a0,-(%sp)
move.w %sr,%d0
movea.l %d0,%a0
move.l 0xc0920,%d0
subi.l #POOL_BASE,%d0
cmpi.l #POOL_BYTES,%d0
bhs.w .Linvalid_\name
tst.b %d0
bne.w .Linvalid_\name
btst #8,%d0
bne.w .Linvalid_\name
btst #9,%d0
bne.w .Linvalid_\name
addi.l #(DECK_ARENA_BASE+\offset),%d0
exg %d0,%a0
tst.l 114(%a0)
bne.w .Lbusy_\name
move.w %d0,80(%a0)
movem.l %d1-%d7,8(%a0)
movem.l %a1-%a6,40(%a0)
move.l (%sp),4(%a0)
move.l 4(%sp),36(%a0)
lea 8(%sp),%a1
move.l %a1,64(%a0)
move.l #\entry,68(%a0)
clr.l 72(%a0)
clr.l 76(%a0)
btst #5,80(%a0)
beq.s 1f
move.l %a1,76(%a0)
bra.s 2f
1:move.l %a1,72(%a0)
2:move.l #1,114(%a0)
lea (\top-\offset)(%a0),%sp
move.l %a0,-(%sp)
jsr biwn_v4_\name\()_body
lea 4(%sp),%sp
lea -(\top-\offset)(%sp),%a0
tst.l 94(%a0)
bne.s .Lerror_\name
clr.l 114(%a0)
movea.l 64(%a0),%sp
move.w 80(%a0),%ccr
movem.l 4(%a0),%d0-%d7/%a0-%a6
.globl biwn_v4_\name\()_return
biwn_v4_\name\()_return:
rts
.Lerror_\name:illegal
.Linvalid_\name:
move.l %a0,%d0
.Lbusy_\name:
move.w %d0,%ccr
movem.l (%sp)+,%d0/%a0
jmp biwn_v4_\name\()_original_fallback
.endm
root coordinate,0x11d1a,16,1008
root input,0x11b4c,144,816
/* Input and face share one guarded frame; active forces original fallback. */
root face,0x1186a,144,816
root scan,0x11828,272,592
/* Geometry and coordinate share the active guard, with original fallback. */
root geometry,0x11ad4,16,1008
.globl biwn_v4_coordinate_original_fallback
biwn_v4_coordinate_original_fallback:
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 0x400f8,%d0
jmp 0x11d24
.globl biwn_v4_input_original_fallback
biwn_v4_input_original_fallback:
move.l %d3,-(%sp)
move.l %d2,-(%sp)
pea 0x11b56
jmp 0xe4c0
.globl biwn_v4_scan_original_fallback
biwn_v4_scan_original_fallback:
move.l %a2,-(%sp)
move.l %d2,-(%sp)
clr.w %d2
jmp 0x1182e
.globl biwn_v4_face_original_fallback
biwn_v4_face_original_fallback:
movem.l %d2-%d4/%a2-%a6,-(%sp)
movea.l 0x400e6,%a0
jmp 0x11874
.globl biwn_v4_geometry_original_fallback
biwn_v4_geometry_original_fallback:
move.l %d3,-(%sp)
move.l %d2,-(%sp)
move.w #7,-(%sp)
jmp 0x11adc
.macro capture name,target
.globl biwn_v4_capture_\name
biwn_v4_capture_\name:
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
capture gpu,0xe26c
capture math,0xe540
capture poll,0xe4c0
capture record,0x10c6e
capture first_texture,0x10e72
capture texture,0x10cb6
capture reset,0x1102a
capture input,0x11b4c
capture face,0x1186a
capture coordinate,0x11d1a
capture geometry_transform,0x110d4
capture geometry_setup,0x10968
capture geometry_objects,0x11384
capture geometry_bsp,0x10ba4
capture geometry_draw,0x1142e
capture geometry_finalize,0x10734
.macro helper_return name,offset
.globl biwn_v4_\name\()_helper_return
biwn_v4_\name\()_helper_return:
movea.l 0xc0920,%sp
adda.l #(DECK_ARENA_BASE+\offset-POOL_BASE),%sp
/* SP-only lookup preserves every returned register and CCR. Capture into
 * the in-place context rather than pushing a second 62-byte CPU copy. */
move.w %sr,80(%sp)
lea 64(%sp),%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea -4(%sp),%a0
move.l 106(%a0),64(%a0)
move.l #0,68(%a0)
movea.l 106(%a0),%a2
move.l 110(%a0),(%a2)
movea.l 98(%a0),%sp
.globl biwn_v4_\name\()_capture_end
biwn_v4_\name\()_capture_end:
movem.l (%sp)+,%d2-%d7/%a2-%a6
moveq #0,%d0
rts
.endm
helper_return coordinate,16
helper_return input,144
helper_return face,144
helper_return scan,272

helper_return geometry,16
