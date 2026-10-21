/* Recovered M68000 compiler-runtime assembly from verified original instructions.
 * Labels and mnemonics replace raw machine bytes; exact same-address linking is checked. */
.section .text.biwn_original_runtime,"ax",@progbits
.globl biwn_runtime_multiply,biwn_runtime_division,biwn_runtime_remainder
biwn_runtime_multiply:
L_e540:
 movea.l %d2, %a0
L_e542:
 movea.l %d3, %a1
L_e544:
 movem.w 0x4(%a7), %d0-%d3
L_e54a:
 move.w %d0, -(%a7)
L_e54c:
 bpl.w L_e554
L_e550:
 neg.w %d1
L_e552:
 negx.w %d0
L_e554:
 tst.w %d2
L_e556:
 bpl.w L_e560
L_e55a:
 neg.w %d3
L_e55c:
 negx.w %d2
L_e55e:
 not.w (%a7)
L_e560:
 ext.l %d0
L_e562:
 beq.w L_e568
L_e566:
 mulu.w %d3, %d0
L_e568:
 tst.w %d2
L_e56a:
 beq.w L_e572
L_e56e:
 mulu.w %d1, %d2
L_e570:
 add.w %d2, %d0
L_e572:
 swap %d0
L_e574:
 clr.w %d0
L_e576:
 mulu.w %d3, %d1
L_e578:
 add.l %d1, %d0
L_e57a:
 move.l %a1, %d3
L_e57c:
 move.l %a0, %d2
L_e57e:
 tst.w (%a7)+
L_e580:
 bpl.w L_e586
L_e584:
 neg.l %d0
L_e586:
 rts
biwn_runtime_division:
L_e588:
 movea.l %d2, %a0
L_e58a:
 movea.l %d3, %a1
L_e58c:
 clr.w -(%a7)
L_e58e:
 clr.l %d0
L_e590:
 move.l 0xa(%a7), %d2
L_e594:
 beq.w L_e606
L_e598:
 bpl.w L_e5a0
L_e59c:
 neg.l %d2
L_e59e:
 not.w (%a7)
L_e5a0:
 move.l 0x6(%a7), %d1
L_e5a4:
 bpl.w L_e5ac
L_e5a8:
 neg.l %d1
L_e5aa:
 not.w (%a7)
L_e5ac:
 cmp.l %d2, %d1
L_e5ae:
 bcs.w L_e5ee
L_e5b2:
 tst.w 0xa(%a7)
L_e5b6:
 bne.w L_e5d8
L_e5ba:
 move.w %d1, %d3
L_e5bc:
 clr.w %d1
L_e5be:
 swap %d1
L_e5c0:
 beq.w L_e5c6
L_e5c4:
 divu.w %d2, %d1
L_e5c6:
 move.w %d1, %d0
L_e5c8:
 swap %d0
L_e5ca:
 move.w %d3, %d1
L_e5cc:
 divu.w %d2, %d1
L_e5ce:
 move.w %d1, %d0
L_e5d0:
 clr.w %d1
L_e5d2:
 swap %d1
L_e5d4:
 bra.w L_e5ee
L_e5d8:
 moveq #0x1f, %d3
L_e5da:
 add.l %d1, %d1
L_e5dc:
 addx.l %d0, %d0
L_e5de:
 cmp.l %d2, %d0
L_e5e0:
 bcs.w L_e5e8
L_e5e4:
 sub.l %d2, %d0
L_e5e6:
 addq.w #0x1, %d1
L_e5e8:
 dbra %d3, L_e5da
L_e5ec:
 exg %d0, %d1
L_e5ee:
 tst.w 0x6(%a7)
L_e5f2:
 bpl.w L_e5f8
L_e5f6:
 neg.l %d1
L_e5f8:
 tst.w (%a7)+
L_e5fa:
 bpl.w L_e600
L_e5fe:
 neg.l %d0
L_e600:
 move.l %a1, %d3
L_e602:
 move.l %a0, %d2
L_e604:
 rts
L_e606:
 divu.w %d2, %d1
L_e608:
 bra.s L_e5ee
biwn_runtime_remainder:
L_e60a:
 move.l 0x8(%a7), -(%a7)
L_e60e:
 move.l 0x8(%a7), -(%a7)
L_e612:
 bsr.w L_e588
L_e616:
 addq.l #0x8, %a7
L_e618:
 move.l %d1, %d0
L_e61a:
 rts
