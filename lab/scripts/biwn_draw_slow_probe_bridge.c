/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-only comparison: pinned core's disabled-fast-blitter mode.
 * Does not replace or modify existing libraries/core/settings. */
#define lab_device_open lab_original_device_open
#include "biwn_draw_probe_bridge.c"
#undef lab_device_open
int lab_device_open(const char *core,const char *bios,int fast)
{
    (void)fast;
    return lab_original_device_open(core,bios,0);
}
