/* Isolated component test only. */
ENTRY(biwn_native_scheduler_dispatch)
SECTIONS {
 . = 0x140000;
 .text : { KEEP(*(.text.biwn_native_scheduler)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"No writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x1000,"Scheduler test window exceeded")
