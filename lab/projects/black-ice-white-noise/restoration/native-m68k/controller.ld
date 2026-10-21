ENTRY(biwn_native_controller_poll)
SECTIONS {
 . = 0x100000;
 .text : { KEEP(*(.text.biwn_native_controller_poll)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"Controller component cannot carry writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x1000,"Controller component exceeded component-test window")
