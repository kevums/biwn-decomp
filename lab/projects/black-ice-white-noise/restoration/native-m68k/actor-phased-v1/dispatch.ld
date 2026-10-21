ENTRY(biwn_native_actor_dispatch)
SECTIONS {
 .text NATIVE_ADDRESS : SUBALIGN(2) { *(.text*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "No writable globals")
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
