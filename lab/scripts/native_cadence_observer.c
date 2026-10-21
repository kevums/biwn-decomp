/* Read-only change observations. A previous CPU PC is a writer candidate,
 * not proof of authorship when a device can also alter RAM between callbacks. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
struct change {
    uint32_t frame,pc,previous_pc,previous_frame;
    uint64_t ordinal;
    struct cpu cpu;
    uint32_t before[12],after[12];
    uint32_t mode,floor,scene,tick;
    uint16_t previous_opcode,opcode_in_RAM;
};
typedef char record_size[sizeof(struct change)==224?1:-1];
typedef char fields_offset[offsetof(struct change,before)==104?1:-1];
typedef void(*read_cpu_fn)(struct cpu*);
static const unsigned char*RAM;static read_cpu_fn read_cpu;
static uint32_t frame,previous_frame,previous_pc,old[12];
static uint64_t ordinal,records,old_math_steps,old_rng_steps,resident_steps;
static unsigned errors;static FILE*events;
static const uint32_t addresses[]={0x49d6c,0x49d70,0x49d76,0x49dd8,
    0x49e3a,0x49e3e,0x49e44,0x49ea6,0x49c50,0x49c56,0x49cba,0x4c24c};
static const unsigned widths[]={2,4,4,2,2,4,4,2,4,4,1,4};
static const uint32_t rng_entries[]={0x1a6e0,0x1a6f8,0x1a77c,0x1a7f4,0x1a87a,0x1a8c6,0x1a8e2,0x1a8f8};
static uint32_t read_value(uint32_t a,unsigned n){
    uint32_t value=0;
    if(a+n>0x200000){errors++;return 0;}
    for(unsigned i=0;i<n;i++)value=(value<<8)|RAM[a+i];
    return value;
}
int begin_observe(const void*memory,read_cpu_fn reader,int selected,
                  const void*code,uint32_t length,const char*path){
    (void)selected;(void)code;(void)length;RAM=memory;read_cpu=reader;
    for(unsigned i=0;i<12;i++)old[i]=read_value(addresses[i],widths[i]);
    events=fopen(path,"wb");return events?0:1;
}
void set_frame(uint32_t value){frame=value;}
int32_t observe(uint32_t pc){
    uint32_t current[12];unsigned different=0;ordinal++;
    if(pc>=0xe540&&pc<0xe61c&&pc!=0xe540&&pc!=0xe588&&pc!=0xe60a)old_math_steps++;
    if(pc>=0x1a6e0&&pc<0x1a91e){
        unsigned entry=0;for(unsigned i=0;i<8;i++)if(pc==rng_entries[i])entry=1;
        if(!entry)old_rng_steps++;
    }
    if(pc>=0x15edc0&&pc<0x15edc0+3516)resident_steps++;
    for(unsigned i=0;i<12;i++){current[i]=read_value(addresses[i],widths[i]);different|=current[i]!=old[i];}
    if(different){
        struct change record;memset(&record,0,sizeof(record));
        record.frame=frame;record.pc=pc;record.previous_pc=previous_pc;record.previous_frame=previous_frame;record.ordinal=ordinal;
        read_cpu(&record.cpu);memcpy(record.before,old,sizeof(old));memcpy(record.after,current,sizeof(current));
        record.mode=read_value(0x49c60,2);record.floor=read_value(0x49c62,2);record.scene=read_value(0x49c64,2);record.tick=read_value(0x778cc,4);
        if(previous_pc<=0x1ffffe){record.previous_opcode=(uint16_t)read_value(previous_pc,2);record.opcode_in_RAM=1;}
        if(fwrite(&record,sizeof(record),1,events)!=1)errors++;records++;
        memcpy(old,current,sizeof(old));
    }
    previous_pc=pc;previous_frame=frame;return 0;
}
int finish_observe(const char*path){
    if(events&&fclose(events))errors++;
    FILE*f=fopen(path,"w");if(!f)return 1;
    fprintf(f,"{\"instructions\":%llu,\"records\":%llu,\"event_record_bytes\":224,\"errors\":%u,"
        "\"old_math_steps\":%llu,\"old_rng_steps\":%llu,\"resident_steps\":%llu}\n",
        (unsigned long long)ordinal,(unsigned long long)records,errors,(unsigned long long)old_math_steps,
        (unsigned long long)old_rng_steps,(unsigned long long)resident_steps);
    return fclose(f)!=0;
}
