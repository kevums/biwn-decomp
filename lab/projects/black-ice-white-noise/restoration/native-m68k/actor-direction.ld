ENTRY(biwn_native_actor_direction)
SECTIONS
{
 . = DEFINED(NATIVE_ADDRESS) ? NATIVE_ADDRESS : 0x180000;
 .text : { *(.text*) *(.rodata*) }
 .data : { *(.data*) }
 .bss (NOLOAD) : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
