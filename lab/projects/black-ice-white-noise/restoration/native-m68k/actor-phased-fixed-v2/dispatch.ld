ENTRY(biwn_native_actor_dispatch)
SECTIONS {
 .body 0x163788 : SUBALIGN(2) { *native.o(.text*) }
 .shim 0x1638c8 : SUBALIGN(2) { *shim.o(.text*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 ASSERT(ADDR(.body) + SIZEOF(.body) <= ADDR(.shim), "C body exceeds old block")
 ASSERT(ADDR(.shim) + SIZEOF(.shim) <= 0x1639c4, "Shim exceeds old block")
 ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "No writable globals")
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
