ENTRY(biwn_actor_group_invoke)
SECTIONS
{
    . = 0x1c8000;
    .text : { *(.text*) *(.rodata*) *(.data*) }
    .bss : { *(.bss*) *(COMMON) }
    /DISCARD/ : { *(.comment) *(.eh_frame*) }
    ASSERT(SIZEOF(.bss) == 0, "Declare mutable group state before integration")
    ASSERT(. < 0x1d0000, "Group overlaps fixture argument area")
}
biwn_actor_external_call = 0x1d1000;
