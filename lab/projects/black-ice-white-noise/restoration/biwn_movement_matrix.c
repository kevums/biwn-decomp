#include "biwn_movement_matrix.h"

/* Exact original quarter-wave coefficients; no floating-point substitution. */
static const uint32_t sine_table[65]={0u,405u,809u,1200u,1607u,2004u,2402u,2800u,3197u,3589u,3981u,4368u,4754u,5140u,5520u,5897u,6270u,6640u,7005u,7366u,7724u,8075u,8423u,8766u,9102u,9434u,9760u,10080u,10394u,10702u,11003u,11297u,11585u,11866u,12140u,12406u,12665u,12916u,13160u,13395u,13623u,13842u,14053u,14256u,14449u,14635u,14811u,14978u,15137u,15286u,15426u,15557u,15679u,15791u,15893u,15986u,16069u,16143u,16207u,16261u,16305u,16340u,16364u,16379u,16384u};
static uint32_t sx16(uint32_t value)
{value&=0xffffu;return value&0x8000u ? value|0xffff0000u : value;}
static uint32_t asr14(uint32_t value)
{return (value>>14)|(value&0x80000000u ? 0xfffc0000u : 0);}
static uint32_t imult(uint32_t a,uint32_t b)
{
    int32_t x=(int32_t)(a&0x7fffu)-(int32_t)(a&0x8000u);
    int32_t y=(int32_t)(b&0x7fffu)-(int32_t)(b&0x8000u);
    return (uint32_t)(x*y);
}
static uint32_t sine(uint32_t angle)
{
    uint32_t index=angle&0x7fu,value;
    if(index>64u)index=128u-index;
    value=sine_table[index];
    return angle&0x80u ? 0u-value : value;
}
static void rotate(uint32_t *a,uint32_t *b,uint32_t angle)
{
    uint32_t first=*a,second=*b,s=sine(angle),co=sine(angle+64u);
    *a=asr14(imult(co,first)-imult(s,second)+8192u);
    *b=asr14(imult(co,second)+imult(s,first)+8192u);
}

enum biwn_movement_status biwn_movement_matrix(struct biwn_movement_bus *bus,
    uint32_t base,uint32_t angle1,uint32_t angle2,uint32_t angle3,uint32_t speed,
    struct biwn_movement_result *output)
{
    struct biwn_movement_result result;
    uint32_t i,pointer=base;
    uint16_t word;
    if(!bus || !output || !bus->read16 || !bus->write16)return BIWN_MOVEMENT_BAD_ARGUMENT;
    for(i=0;i<9;i++) {
        if(bus->write16(bus->context,pointer,i%4u==0 ? 0x4000u : 0))return BIWN_MOVEMENT_BUS_ERROR;
        pointer+=2u;
    }
    for(i=0;i<12;i++) {
        if(!bus->read_budget)return BIWN_MOVEMENT_READ_LIMIT;
        bus->read_budget--;
        if(bus->read16(bus->context,base+i*2u,&word))return BIWN_MOVEMENT_BUS_ERROR;
        result.matrix_and_translation[i]=sx16(word);
    }
    if(angle2)for(i=0;i<3;i++)rotate(&result.matrix_and_translation[6+i],&result.matrix_and_translation[i],angle2);
    if(angle1)for(i=0;i<3;i++)rotate(&result.matrix_and_translation[3+i],&result.matrix_and_translation[6+i],angle1);
    if(angle3)for(i=0;i<3;i++)rotate(&result.matrix_and_translation[i],&result.matrix_and_translation[3+i],angle3);
    speed=sx16(speed);
    for(i=0;i<3;i++) {
        result.raw_products[i]=speed ? imult(result.matrix_and_translation[6+i],speed) : 0;
        if(speed)result.matrix_and_translation[9+i]+=asr14(result.raw_products[i]);
    }
    for(i=0;i<12;i++)if(bus->write16(bus->context,base+i*2u,(uint16_t)result.matrix_and_translation[i]))return BIWN_MOVEMENT_BUS_ERROR;
    for(i=0;i<3;i++)if(bus->write16(bus->context,base+26u+i*2u,(uint16_t)result.raw_products[i]))return BIWN_MOVEMENT_BUS_ERROR;
    /* Final jump's delay slot adds64 to the last store address. */
    result.final_pointer=base+94u;
    *output=result;
    return BIWN_MOVEMENT_OK;
}
