/* Isolated tests use original heap floor; installed bundle raises it. */
ENTRY(biwn_native_heap_allocate)
PROVIDE(biwn_native_heap_start = 0x15edc0);
SECTIONS {
 . = 0x140000;
 .text : { KEEP(*(.text.biwn_native_heap)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"No writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x2000,"Isolated native heap window exceeded")
