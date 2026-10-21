ENTRY(biwn_native_deck_input)
SECTIONS {
 . = NATIVE_ADDRESS;
 .text : { *(.text*) *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment*) *(.eh_frame*) }
}
