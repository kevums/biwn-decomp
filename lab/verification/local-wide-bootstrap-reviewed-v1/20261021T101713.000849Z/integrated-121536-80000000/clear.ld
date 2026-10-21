SECTIONS { . = 0x17c860; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }
