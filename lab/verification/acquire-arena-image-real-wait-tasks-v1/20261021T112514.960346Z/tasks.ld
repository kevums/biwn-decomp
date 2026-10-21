SECTIONS { .text 0x6100 : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }
