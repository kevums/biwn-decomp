.text
.globl biwn_marker_word_scan
biwn_marker_word_scan:
    CMP.L (A2)+,D2
    BEQ.S biwn_marker_run
    SUBQ.L #2,A2
    CMPA.L #0x1C7FFF,A2
    BCS.S biwn_marker_word_scan
    BRA.W biwn_marker_scan_failure
