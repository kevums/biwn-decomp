/* Isolated component address only; no game-image ownership claim. */
ENTRY(biwn_native_task_create)
SECTIONS {
 . = 0x140000;
 .text : { KEEP(*(.text.biwn_native_task_create)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"No writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<0x1000,"Component test window exceeded")
