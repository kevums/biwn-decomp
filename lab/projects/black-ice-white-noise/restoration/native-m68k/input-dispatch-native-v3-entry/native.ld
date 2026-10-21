ENTRY(biwn_native_input_entry)
SECTIONS {
 . = 0x1c0000;
 .text : { KEEP(*(.text.biwn_native_input_fixture)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 .native_entry ALIGN(2) : { KEEP(*(.native_entry)) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"Input prototype must have no writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x10000,"Input prototype exceeds fixture reservation")
