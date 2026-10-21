/* Read-only host observer for the native preview. Returns zero ownership. */
#include <stdint.h>
#include <stddef.h>
static const uint8_t *memory;
static uint32_t entry,done,gpu[8],gpu_done[8];
static uint64_t roots,native_roots,returns,old_steps,bad_ids,gpu_entries[8],gpu_returns[8];
static uint32_t get32(uint32_t p){return ((uint32_t)memory[p]<<24)|((uint32_t)memory[p+1]<<16)|((uint32_t)memory[p+2]<<8)|memory[p+3];}
void preview_observer_setup(const uint8_t *ram,uint32_t coordinate,uint32_t ret,const uint32_t *g,const uint32_t *r){
 memory=ram;entry=coordinate;done=ret;roots=native_roots=returns=old_steps=bad_ids=0;
 for(unsigned i=0;i<8;i++){gpu[i]=g[i];gpu_done[i]=r[i];gpu_entries[i]=gpu_returns[i]=0;}
}
int32_t preview_observer_own(uint32_t pc){
 if(pc==0x11d1a)roots++;
 if(pc==entry){native_roots++;uint32_t delta=get32(0xc0920)-0xc0928;if(delta>=0x19400||(delta&1023))bad_ids++;}
 if(pc==done)returns++;
 if(pc>0x11d1a&&pc<0x11e64)old_steps++;
 for(unsigned i=0;i<8;i++){if(pc==gpu[i])gpu_entries[i]++;if(pc==gpu_done[i])gpu_returns[i]++;}
 return 0;
}
uint64_t preview_observer_stat(unsigned n){
 if(n==0)return roots;if(n==1)return native_roots;if(n==2)return returns;if(n==3)return old_steps;if(n==4)return bad_ids;
 if(n<13)return gpu_entries[n-5];if(n<21)return gpu_returns[n-13];return 0;
}
