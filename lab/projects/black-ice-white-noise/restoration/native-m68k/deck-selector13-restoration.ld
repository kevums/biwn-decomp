OUTPUT_ARCH(m68k)
ENTRY(biwn_restored_deck_group_selector)
biwn_original_deck_failure = 0x10ba0;
SECTIONS {
  .selector13 0x10ac2 : { *(.text.deck_selector13) }
  .frame_count 0x464a6 : { *(.rodata.deck_frame_count) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
