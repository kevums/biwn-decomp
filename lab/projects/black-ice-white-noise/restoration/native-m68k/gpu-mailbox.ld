ENTRY(biwn_native_gpu_submit_4320)
SECTIONS
{
 . = DEFINED(NATIVE_ADDRESS) ? NATIVE_ADDRESS : 0x180000;
 .text : { *(.text*) *(.rodata*) }
 .data : { *(.data*) }
 .bss (NOLOAD) : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
