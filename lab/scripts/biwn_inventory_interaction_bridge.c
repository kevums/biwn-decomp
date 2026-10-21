/* SPDX-License-Identifier: GPL-3.0-or-later
 * Selection basic block linked to the checked inventory rendering pipeline.
 * Deliberately separate library: existing render bridge/checks stay pinned.
 */
#include "biwn_inventory_device_bridge.c"
#include "../projects/black-ice-white-noise/restoration/biwn_inventory_select.h"

static int selection_redraw(void *unused)
{
    (void)unused;
    return lab_device_run_C(100000u);
}

int lab_device_input_step(uint32_t input, uint32_t *registers)
{
    struct biwn_ui_bus bus = {lab_device_read8,lab_device_read16,
        lab_device_read32,lab_device_write16,selection_redraw,NULL};
    struct biwn_selection_cpu cpu;
    int result;
    if (!opened || !use_C_decoder || !registers) return 1;
    /* Input is a supplied game-memory word, not physical controller polling. */
    if (lab_device_write32(NULL,0x49bacu,input)) return 2;
    cpu.d0=registers[0];cpu.d1=registers[1];cpu.a0=registers[2];
    result=biwn_inventory_select(&bus,&cpu);
    registers[0]=cpu.d0;registers[1]=cpu.d1;registers[2]=cpu.a0;
    return result;
}
