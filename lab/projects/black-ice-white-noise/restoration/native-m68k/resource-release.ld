ENTRY(biwn_native_resource_release)
SECTIONS {
 . = 0x140000;
 .text : { KEEP(*(.text.biwn_native_resource_release)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"No writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x4000,"Resource release isolated limit")
