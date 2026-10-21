ENTRY(biwn_frame_phased_entry)
SECTIONS {
 .text NATIVE_ADDRESS : SUBALIGN(2) {
  *shim.o(.text*)
  *native.o(.text.biwn_frame_phased_start)
  *native.o(.text.biwn_frame_phased_after_first_divs)
  *native.o(.text.biwn_frame_phased_after_group_divs)
 }
 .tail TAIL_ADDRESS : SUBALIGN(2) { *native.o(.text.biwn_frame_phased_after_load) }
 .data : { *(.data*) *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.text)<=1600,"Phased early code exceeds old frame-acquire block")
ASSERT(SIZEOF(.data)==0,"Phased frame acquire has writable globals")
