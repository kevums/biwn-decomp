OUTPUT_ARCH(m68k)
ENTRY(biwn_input_task_admit)
SECTIONS {
 . = 0x1c0000;
 .text : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
