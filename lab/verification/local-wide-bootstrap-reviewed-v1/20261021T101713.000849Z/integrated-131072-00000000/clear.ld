SECTIONS { . = 0x17eda0; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }
