ENTRY(biwn_native_button_digit)
PROVIDE (biwn_native_heap_start = 0x160bc0);
PROVIDE (biwn_runtime_multiply = 0xe540);
PROVIDE (biwn_runtime_division = 0xe588);
PROVIDE (biwn_runtime_remainder = 0xe60a);
SECTIONS {
 . = 0x15edc0;
 .text : { KEEP(*(.text.biwn_native_button_digit)) KEEP(*(.text.biwn_native_startup_finalize)) KEEP(*(.text.biwn_native_rng)) KEEP(*(.text.biwn_rng_fast_math)) KEEP(*(.text.biwn_native_controller_poll)) KEEP(*(.text.biwn_native_task_create)) KEEP(*(.text.biwn_native_scheduler)) KEEP(*(.text.biwn_native_heap)) KEEP(*(.text.biwn_native_copy)) KEEP(*(.text.biwn_native_free)) KEEP(*(.text.biwn_native_heap_initialize)) KEEP(*(.text.biwn_native_resource_release)) KEEP(*(.text.biwn_native_resource_acquire)) KEEP(*(.text.biwn_native_resource_load)) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
ASSERT(SIZEOF(.data)+SIZEOF(.bss)==0,"Native bundle cannot carry writable globals")
ASSERT(SIZEOF(.text)+SIZEOF(.rodata)<=0x1e00,"Native loader bundle exceeds7680byte resident budget")
