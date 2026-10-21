ENTRY(biwn_native_button_digit)
PROVIDE (biwn_runtime_multiply = 0xe540);
PROVIDE (biwn_runtime_division = 0xe588);
PROVIDE (biwn_runtime_remainder = 0xe60a);
SECTIONS {
 . = 0x15edc0;
 .text : { KEEP(*(.text.biwn_native_button_digit)) KEEP(*(.text.biwn_native_startup_finalize)) KEEP(*(.text.biwn_native_rng)) KEEP(*(.text.biwn_rng_fast_math)) KEEP(*(.text.biwn_native_controller_poll)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"Native bundle cannot carry writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0xe00,"Native RNG bundle exceeds temporary disc staging budget")
