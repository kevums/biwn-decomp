ENTRY(biwn_v4_coordinate)
SECTIONS {
 . = NATIVE_ADDRESS;
 .text : { *(.text*) *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment*) *(.eh_frame*) }
}
