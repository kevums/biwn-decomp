#include <stddef.h>
/* Coordinator freestanding compiler support, not a recovered game function. */
void *memset(void *destination,int value,size_t count) {
 volatile unsigned char *p=destination;
 while(count--) *p++=(unsigned char)value;
 return destination;
}
