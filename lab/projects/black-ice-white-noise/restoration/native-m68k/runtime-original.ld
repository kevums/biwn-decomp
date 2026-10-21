ENTRY(biwn_runtime_multiply)
SECTIONS { . = 0xe540; .text : { KEEP(*(.text.biwn_original_runtime)) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }
ASSERT(SIZEOF(.text)==220,"Recovered runtime size changed")
