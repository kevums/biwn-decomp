ENTRY(biwn_native_button_digit)
SECTIONS {
 . = 0x15edc0;
 .text : { KEEP(*(.text.biwn_native_button_digit)) KEEP(*(.text.biwn_native_math)) KEEP(*(.text.biwn_native_startup_finalize)) KEEP(*(.text.biwn_native_rng)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"Native bundle cannot carry writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0xe00,"Native RNG bundle exceeds temporary disc staging budget")
