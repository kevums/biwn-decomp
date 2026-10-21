ENTRY(biwn_native_actor_initialize)
SECTIONS {
 .body 0x1639c4 : SUBALIGN(2) { *native.o(.text*) }
 .shim 0x163eec : SUBALIGN(2) { *shim.o(.text*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 ASSERT(ADDR(.body) + SIZEOF(.body) <= ADDR(.shim), "C body exceeds old block")
 ASSERT(ADDR(.shim) + SIZEOF(.shim) <= 0x164014, "Shim exceeds old block")
 ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "No writable globals")
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
