ENTRY(biwn_frame_phased_entry)
SECTIONS {
 .text NATIVE_ADDRESS : SUBALIGN(2) { *(.text*) }
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
