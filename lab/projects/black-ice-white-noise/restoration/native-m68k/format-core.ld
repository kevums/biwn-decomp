OUTPUT_ARCH(m68k)
ENTRY(biwn_native_format_core)
SECTIONS {
 . = 0x160000;
 .text : { *(.text.biwn_native_format_core) *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
