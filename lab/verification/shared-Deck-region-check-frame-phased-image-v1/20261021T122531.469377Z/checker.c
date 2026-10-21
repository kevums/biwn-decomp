#include <stdint.h>
#include <string.h>
static uint8_t o6_used[101];
static unsigned native_deck_regions(const uint8_t *memory,const uint8_t *expected,const uint8_t *used){
 unsigned errors=0;
 if(memcmp(memory+1437120u,expected,34816u))errors++;
 if(memcmp(memory+1498048u,expected+60928u,72192u))errors++;
 for(unsigned i=0;i<101;i++){
  uint32_t p=1570240u+i*1024u;
  if(memcmp(memory+p,expected+p-1437120u,16)||memcmp(memory+p+1008u,expected+p+1008u-1437120u,16))errors++;
  if(memcmp(memory+p+136u,expected+p+136u-1437120u,8u))errors++;
  if(memcmp(memory+p+264u,expected+p+264u-1437120u,8u))errors++;
  if(memcmp(memory+p+400u,expected+p+400u-1437120u,16u))errors++;
  if(memcmp(memory+p+592u,expected+p+592u-1437120u,16u))errors++;
  if(memcmp(memory+p+816u,expected+p+816u-1437120u,16u))errors++;
  if(!used[i]&&memcmp(memory+p,expected+p-1437120u,1024))errors++;
 }

 for(unsigned i=0;i<101;i++){
  uint32_t p=1673664u+i*384u;
  if(memcmp(memory+p,expected+p-1437120u,16)||memcmp(memory+p+136u,expected+p+136u-1437120u,8)||memcmp(memory+p+368u,expected+p+368u-1437120u,16))errors++;
  if(!o6_used[i]&&memcmp(memory+p,expected+p-1437120u,384))errors++;
  uint32_t q=1570240u+i*1024u+392u;
  if(memcmp(memory+q,expected+q-1437120u,4))errors++;
 }
 return errors;
}


unsigned check(const uint8_t *a,const uint8_t *b,const uint8_t *u,const uint8_t *o){memcpy(o6_used,o,101);return native_deck_regions(a,b,u);}
