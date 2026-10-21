#include <stdint.h>
/* Complete 1AEDA..1AF02 initializer. Preserve four ordered WORD writes per
 * 12-byte slot; handle/address bytes at offsets2..5 stay untouched. */
void biwn_resource_table_initialize_body(void)
{
    volatile uint16_t *entry=(volatile uint16_t *)0x15b534u;
    for(unsigned i=0;i<50;i++,entry+=6) {
        entry[0]=0xffffu;
        entry[3]=0;
        entry[5]=0;
        entry[4]=0;
    }
}
