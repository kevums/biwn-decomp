SECTIONS { .text 0x15f292 : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }
