/* Original DD40..DDCC initializer; privileged CPU operations have ASM source. */
#include "task-pool-native.h"
void biwn_native_task_pool_body(uint32_t*r){
 TPW32(0x80u,0xde08u);task_pool_move_flags(r,0xde08u,32);
 TPW32(0x88u,0xdeb6u);task_pool_move_flags(r,0xdeb6u,32);
 TPW32(0x8cu,0xdee2u);task_pool_move_flags(r,0xdee2u,32);
 TPW32(0x90u,0xdef6u);task_pool_move_flags(r,0xdef6u,32);
 TPW32(0x20u,0xddfeu);task_pool_move_flags(r,0xddfeu,32);
 r[0]=(r[0]&0xffff0000u)|98u;task_pool_move_flags(r,98u,16);
 r[8]=0xc0d28u;
 do{
  r[9]=r[8]+0x400u;TPW32(r[8],r[9]);task_pool_move_flags(r,r[9],32);r[8]=r[9];
  r[0]=(r[0]&0xffff0000u)|(uint16_t)((uint16_t)r[0]-1u);
 }while((uint16_t)r[0]!=0xffffu);
 TPW32(r[8],0);task_pool_move_flags(r,0,32);
 TPW32(0xc0924u,0xc0d28u);task_pool_move_flags(r,0xc0d28u,32);
 r[8]=0xc0928u;TPW32(0xc0920u,r[8]);task_pool_move_flags(r,r[8],32);
 TPW32(r[8],r[8]);task_pool_move_flags(r,r[8],32);
 TPW32(r[8]+4u,r[8]);task_pool_move_flags(r,r[8],32);
 r[9]=r[8]+0x400u;TPW32(r[8]+12u,r[9]);task_pool_move_flags(r,r[9],32);
 biwn_native_task_pool_set_usp(r[9]);r[17]=r[9];
 TPW16(r[8]+20u,0);task_pool_move_flags(r,0,16);
 TPW32(r[8]+26u,0);task_pool_move_flags(r,0,32);
 TPW32(r[8]+22u,0);task_pool_move_flags(r,0,32);
 TPW32(r[8]+34u,0);task_pool_move_flags(r,0,32);
 TPW32(r[8]+8u,0xddccu);task_pool_move_flags(r,0xddccu,32);
}
