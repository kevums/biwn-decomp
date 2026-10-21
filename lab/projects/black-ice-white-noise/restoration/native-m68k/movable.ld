/* Relocation test layout. Runtime placement comes from the game allocator. */
ENTRY(biwn_native_button_digit)
SECTIONS {
  . = DEFINED(COMPONENT_BASE) ? COMPONENT_BASE : 0x10000;
  .text : { *(.text.biwn_native_button_digit) *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data) + SIZEOF(.bss) == 0, "Movable component must have no writable globals")
