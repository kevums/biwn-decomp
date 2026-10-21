/* Complete high-level CPU command wrappers; actual E098 wait retained. */
#include "gpu-mailbox-native.h"
void biwn_native_gpu_mailbox_body(uint32_t *r)
{
 uint32_t command=r[17]==0xe220u?0x4320u:0x4b00u;
 unsigned count=r[17]==0xe220u?5u:3u;
 biwn_native_gpu_mailbox_wait_capture(r);
 for(unsigned i=0;i<count;i++){
  uint32_t value=GMR32(r[15]+4u+4u*i);
  GMW32(0xf0320cu+4u*i,value);gpu_mailbox_move_flags(r,value);
 }
 GMW32(0xf03204u,command);gpu_mailbox_move_flags(r,command);
 for(;;){
  uint32_t value=GMR32(0xf03204u);gpu_mailbox_compare_flags(r,value,command);
  if(value!=command)break;
 }
 biwn_native_gpu_mailbox_wait_capture(r);
}
