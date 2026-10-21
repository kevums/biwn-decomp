ENTRY(biwn_native_multiply)
SECTIONS {
 . = 0x15edc0;
 .text : { KEEP(*(.text.biwn_native_button_digit)) KEEP(*(.text.biwn_native_math)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"Native arithmetic must be reentrant with no writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x10000,"Native bundle too large for initial reservation plan")
