/* Read-only counters for the five-caller preview. Never claims CPU execution. */
#include <stdint.h>
static const uint8_t *memory;
static uint32_t entry[5], done[5], gpu[8], gpu_done[8];
static const uint32_t roots[5]={0x11d1a,0x11b4c,0x1186a,0x11828,0x11ad4};
static const uint32_t ends[5]={0x11e64,0x11d1a,0x11ad4,0x1186a,0x11b4c};
static uint64_t public_entries[5],native_entries[5],returns[5],old_steps[5],bad_ids,gpu_entries[8],gpu_returns[8];
static uint32_t get32(uint32_t p){return ((uint32_t)memory[p]<<24)|((uint32_t)memory[p+1]<<16)|((uint32_t)memory[p+2]<<8)|memory[p+3];}
void preview_observer_setup(const uint8_t *ram,const uint32_t *native,const uint32_t *ret,const uint32_t *g,const uint32_t *r){
 memory=ram;bad_ids=0;
 for(unsigned i=0;i<5;i++){entry[i]=native[i];done[i]=ret[i];public_entries[i]=native_entries[i]=returns[i]=old_steps[i]=0;}
 for(unsigned i=0;i<8;i++){gpu[i]=g[i];gpu_done[i]=r[i];gpu_entries[i]=gpu_returns[i]=0;}
}
int32_t preview_observer_own(uint32_t pc){
 for(unsigned i=0;i<5;i++){
  if(pc==roots[i])public_entries[i]++;
  if(pc==entry[i]){native_entries[i]++;uint32_t delta=get32(0xc0920)-0xc0928;if(delta>=0x19400||(delta&1023))bad_ids++;}
  if(pc==done[i])returns[i]++;
  if(pc>roots[i]&&pc<ends[i])old_steps[i]++;
 }
 for(unsigned i=0;i<8;i++){if(pc==gpu[i])gpu_entries[i]++;if(pc==gpu_done[i])gpu_returns[i]++;}
 return 0;
}
uint64_t preview_observer_stat(unsigned n){
 if(n<5)return public_entries[n];
 if(n<10)return native_entries[n-5];
 if(n<15)return returns[n-10];
 if(n<20)return old_steps[n-15];
 if(n==20)return bad_ids;
 if(n<29)return gpu_entries[n-21];
 if(n<37)return gpu_returns[n-29];
 return 0;
}
