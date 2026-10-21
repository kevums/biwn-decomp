OUTPUT_ARCH(m68k)
ENTRY(biwn_native_unsigned_divide)
SECTIONS {
 . = 0x160000;
 .text : { *(.text.biwn_native_unsigned_math) *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
