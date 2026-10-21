ENTRY(biwn_native_task_yield)
SECTIONS {
 .yield 0xdf60 : SUBALIGN(2) { *(.yield) }
 .remove 0xdf7a : SUBALIGN(2) { *(.remove) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.yield)==12,"Yield must retain exact12byte span")
ASSERT(SIZEOF(.remove)==2,"Removal trap must retain exact2byte span")
