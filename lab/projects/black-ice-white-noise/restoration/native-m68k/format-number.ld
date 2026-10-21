OUTPUT_ARCH(m68k)
ENTRY(biwn_native_format_number)
SECTIONS {
 . = 0x160000;
 .text : { *(.text.biwn_native_format_number) *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
