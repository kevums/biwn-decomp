/* Component test address only; this is not a BIWN game-image memory map. */
ENTRY(biwn_native_button_digit)
SECTIONS {
  . = 0x10000;
  .text : { *(.text.biwn_native_button_digit) *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.text) < 0x10000, "Component exceeds test code window")
