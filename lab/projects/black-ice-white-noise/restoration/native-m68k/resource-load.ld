ENTRY(biwn_native_resource_load)
SECTIONS {
 . = 0x148000;
 .text : { KEEP(*(.text.biwn_native_resource_load)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"No writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x4000,"Isolated load limit")
