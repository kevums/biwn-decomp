ENTRY(biwn_marker_word_scan)
PROVIDE(biwn_marker_run = 0x1b100);
PROVIDE(biwn_marker_scan_failure = 0x1b122);
SECTIONS { .text 0x1b0ee : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }
ASSERT(SIZEOF(.text)==18,"Marker repair must remain18bytes")
