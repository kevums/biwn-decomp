/* Inherited checked CPU operation primitives; coordinator bus/work wrapper. */
static uint32_t dl_sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t dl_sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static void dl_bank(struct biwn_deck_context *s){if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];}
static void dl_pop(struct biwn_deck_context *s,uint32_t n){s->cpu.registers[15]+=n;dl_bank(s);}
static void dl_put(struct biwn_deck_context *s,unsigned r,unsigned width,uint32_t v){uint32_t mask=width==4?0xffffffffu:(1u<<(width*8))-1u;s->cpu.registers[r]=(s->cpu.registers[r]&~mask)|(v&mask);if(r==15)dl_bank(s);}
static void dl_nz(struct biwn_deck_context *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static uint32_t dl_alu(struct biwn_deck_context *s,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,ov;a&=mask;b&=mask;r=(sub?a-b:a+b)&mask;carry=sub?a<b:r<a;ov=sub?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;dl_nz(s,r,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0)|(ov?2u:0));return r;}
static void dl_shift(struct biwn_deck_context *s,unsigned r,unsigned bits,unsigned n,int left){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v=s->cpu.registers[r]&mask;unsigned c=0,ov=0,i;
 for(i=0;i<n;i++){if(left){uint32_t old=v;c=(v&sign)!=0;v=(v<<1)&mask;ov|=((old^v)&sign)!=0;}else{c=v&1u;v=(v>>1)|(v&sign);}}
 dl_put(s,r,bits/8,v);dl_nz(s,v,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(n?0x13u:3u))|(c?(n?0x11u:1u):0)|(ov?2u:0));}
static int dl_read_value(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t *v){*v=deck_read(s,a,w);return s->error;}
static int dl_write_value(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){deck_write(s,a,w,v);return s->error;}
static int dl_push(struct biwn_deck_context *s,uint32_t v,unsigned w){s->cpu.registers[15]-=w;deck_bank(s);deck_write(s,s->cpu.registers[15],w,v);return s->error;}
#ifndef SCENE_DISPLAY_BEGIN
#define SCENE_DISPLAY_BEGIN(s) ((void)(s))
#define SCENE_DISPLAY_END(s) ((void)(s))
#endif
#define DL_CHECK(e) do{int dl_status=(e);if(dl_status){s->error=dl_status;return;}}while(0)
#ifdef SCENE_DISPLAY_NATIVE_DIRECT
#define DL_WORK() ((void)0)
#else
#define DL_WORK() do{if(!s->budget){s->error=4;return;}s->budget--;}while(0)
#endif
