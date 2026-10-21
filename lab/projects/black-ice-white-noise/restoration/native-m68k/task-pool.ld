ENTRY(biwn_native_task_pool_initialize)
SECTIONS {
 . = NATIVE_ADDRESS;
 .text : { *(.text*) *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
