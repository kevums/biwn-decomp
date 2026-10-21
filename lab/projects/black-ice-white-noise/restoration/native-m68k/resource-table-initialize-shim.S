.text
.globl biwn_native_resource_table_initialize
biwn_native_resource_table_initialize:
movem.l %d1/%a1,-(%sp)
bsr.w biwn_resource_table_initialize_body
movem.l (%sp)+,%d1/%a1
move.w #50,%d1
move.l #588,%d0
lea 0x15b534,%a0
move.w #0,%ccr
.globl biwn_native_resource_table_initialize_return
biwn_native_resource_table_initialize_return:
rts
