ENTRY(biwn_native_actor_collision_outdoor)
SECTIONS {
 . = DEFINED(NATIVE_ADDRESS) ? NATIVE_ADDRESS : 0x180000;
 .text : { *(.text*) *(.rodata*) *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 ASSERT(SIZEOF(.bss) == 0, "No zero-initialized runtime state")
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
