ENTRY(biwn_outer_entry)
SECTIONS {
 . = NATIVE_ADDRESS;
 .text : { *(.text*) *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment*) *(.eh_frame*) }
}
