ENTRY(biwn_native_copy_source_first)
SECTIONS {
 . = 0x180000;
 .text : { KEEP(*(.text.biwn_native_copy)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"No writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x4000,"Native copy window exceeded")
