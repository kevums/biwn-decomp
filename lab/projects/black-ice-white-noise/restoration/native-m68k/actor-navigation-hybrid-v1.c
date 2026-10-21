#define biwn_native_actor_navigation_body coordinator_navigation_body
#include "actor-navigation-reference-v2.c"
#undef biwn_native_actor_navigation_body
#include "actor-navigation-left-hybrid-v1.c"
void biwn_native_actor_navigation_body(uint32_t *r){if(r[17]==0x13f12u){biwn_native_actor_nav_left(r);return;}coordinator_navigation_body(r);}
