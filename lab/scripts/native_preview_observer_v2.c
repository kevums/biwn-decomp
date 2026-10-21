/* Read-only preview counters. Returning zero leaves CPU execution unchanged. */
#include <stdint.h>
#include <stddef.h>
static const uint8_t *memory;
static uint32_t entry[3],done[3],gpu[8],gpu_done[8];
static const uint32_t roots[3]={0x11d1a,0x11b4c,0x11828};
static const uint32_t ends[3]={0x11e64,0x11d1a,0x1186a};
static uint64_t public_entries[3],native_entries[3],returns[3],old_steps[3],bad_ids,gpu_entries[8],gpu_returns[8],face_entries,face_returns;
static uint32_t get32(uint32_t p){return ((uint32_t)memory[p]<<24)|((uint32_t)memory[p+1]<<16)|((uint32_t)memory[p+2]<<8)|memory[p+3];}
void preview_observer_setup(const uint8_t *ram,const uint32_t *native,const uint32_t *ret,const uint32_t *g,const uint32_t *r){
 memory=ram;bad_ids=face_entries=face_returns=0;
 for(unsigned i=0;i<3;i++){entry[i]=native[i];done[i]=ret[i];public_entries[i]=native_entries[i]=returns[i]=old_steps[i]=0;}
 for(unsigned i=0;i<8;i++){gpu[i]=g[i];gpu_done[i]=r[i];gpu_entries[i]=gpu_returns[i]=0;}
}
int32_t preview_observer_own(uint32_t pc){
 for(unsigned i=0;i<3;i++){
  if(pc==roots[i])public_entries[i]++;
  if(pc==entry[i]){native_entries[i]++;uint32_t delta=get32(0xc0920)-0xc0928;if(delta>=0x19400||(delta&1023))bad_ids++;}
  if(pc==done[i])returns[i]++;
  if(pc>roots[i]&&pc<ends[i])old_steps[i]++;
 }
 for(unsigned i=0;i<8;i++){if(pc==gpu[i])gpu_entries[i]++;if(pc==gpu_done[i])gpu_returns[i]++;}
 if(pc==0x1186a)face_entries++;
 if(pc==0x11ad2)face_returns++;
 return 0;
}
uint64_t preview_observer_stat(unsigned n){
 if(n<3)return public_entries[n];
 if(n<6)return native_entries[n-3];
 if(n<9)return returns[n-6];
 if(n<12)return old_steps[n-9];
 if(n==12)return bad_ids;
 if(n<21)return gpu_entries[n-13];
 if(n<29)return gpu_returns[n-21];
 if(n==29)return face_entries;
 if(n==30)return face_returns;
 return 0;
}
