/* Read-only gameplay trace. The retained core executes every instruction. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct cpu { uint32_t r[16],pc,usp,ssp; uint16_t sr; };
struct event { uint32_t frame,pc; struct cpu cpu; uint32_t X,Z,mode,floor,scene,tile; };
typedef char event_size_check[sizeof(struct event)==112?1:-1];
typedef void (*read_cpu_fn)(struct cpu *);
static const unsigned char *ram,*payload;
static uint32_t payload_size,frame,last_marker_frame;
static read_cpu_fn read_cpu;
static FILE *events;
static unsigned candidate,errors;
static uint64_t steps,entry_copies,copy_errors,heap_inits,resident_steps;
static uint64_t old_rng_steps,old_math_steps,old_keypad_steps,marker_steps,event_count;
static uint64_t rng_entries[8],math_entries[3],boundary_entries[4];
static uint32_t heap_base;
static const uint32_t rng[]={0x1a6e0,0x1a6f8,0x1a77c,0x1a7f4,0x1a87a,0x1a8c6,0x1a8e2,0x1a8f8,0x1a91e};
static const uint32_t math[]={0xe540,0xe588,0xe60a};
static const uint32_t boundaries[]={0x18e92,0x1a0f8,0x20f0c,0x20f78};

static uint32_t rd32(uint32_t address) {
    if(address>0x1ffffc){errors++;return 0;}
    return ((uint32_t)ram[address]<<24)|((uint32_t)ram[address+1]<<16)|
           ((uint32_t)ram[address+2]<<8)|ram[address+3];
}
static uint32_t rd16(uint32_t address) {
    if(address>0x1ffffe){errors++;return 0;}
    return ((uint32_t)ram[address]<<8)|ram[address+1];
}
int begin_observe(const void *memory,read_cpu_fn reader,int selected,
                  const void *code,uint32_t length,const char *path) {
    ram=memory;read_cpu=reader;candidate=(unsigned)selected;
    payload=code;payload_size=length;events=fopen(path,"wb");
    return events?0:1;
}
void set_frame(uint32_t value){frame=value;}
static void emit(uint32_t pc) {
    struct event record;
    memset(&record,0,sizeof(record));record.frame=frame;record.pc=pc;
    read_cpu(&record.cpu);record.X=rd32(0x49c50);record.Z=rd32(0x49c56);
    record.mode=rd16(0x49c60);record.floor=rd16(0x49c62);
    record.scene=rd16(0x49c64);record.tile=rd16(0x49c8c);
    if(fwrite(&record,sizeof(record),1,events)!=1)errors++;
    event_count++;
}
int32_t observe(uint32_t pc) {
    steps++;
    if(pc==0x400a){
        entry_copies++;
        if(candidate&&memcmp(ram+0x15edc0,payload,payload_size))copy_errors++;
    }
    if(pc==0x155c0){heap_inits++;heap_base=rd32(0x112d60);}
    if(pc>=0x15edc0&&pc<0x15edc0+payload_size)resident_steps++;
    if(pc>=rng[0]&&pc<rng[8]){
        for(unsigned i=0;i<8;i++){
            if(pc==rng[i]){rng_entries[i]++;emit(pc);}
            else if(pc>rng[i]&&pc<rng[i+1])old_rng_steps++;
        }
    }
    if(pc>=0xe540&&pc<0xe61c){
        int entry=0;
        for(unsigned i=0;i<3;i++)if(pc==math[i]){math_entries[i]++;entry=1;}
        if(!entry)old_math_steps++;
    }
    if(pc>=0x1b71e&&pc<0x1b780)old_keypad_steps++;
    if(pc==0x18e92||pc==0x1a0f8||pc==0x20f0c||pc==0x20f78){
        for(unsigned i=0;i<4;i++)if(pc==boundaries[i])boundary_entries[i]++;
        emit(pc);
    }
    if(pc==0x1b0ee){
        marker_steps++;
        if(last_marker_frame!=frame){last_marker_frame=frame;emit(pc);}
    }
    return 0;
}
static void array(FILE *file,const char *name,const uint64_t *values,unsigned count){
    fprintf(file,",\"%s\":[",name);
    for(unsigned i=0;i<count;i++)fprintf(file,"%s%llu",i?",":"",(unsigned long long)values[i]);
    fputc(']',file);
}
int finish_observe(const char *path){
    if(events&&fclose(events))errors++;
    FILE *file=fopen(path,"w");if(!file)return 1;
    fprintf(file,"{\"instructions\":%llu,\"entry_copies\":%llu,\"copy_errors\":%llu,"
        "\"heap_inits\":%llu,\"heap_base\":%u,\"resident_steps\":%llu,"
        "\"old_rng_steps\":%llu,\"old_math_steps\":%llu,\"old_keypad_steps\":%llu,"
        "\"marker_steps\":%llu,\"events\":%llu,\"event_record_bytes\":%u,\"errors\":%u",
        (unsigned long long)steps,(unsigned long long)entry_copies,(unsigned long long)copy_errors,
        (unsigned long long)heap_inits,heap_base,(unsigned long long)resident_steps,
        (unsigned long long)old_rng_steps,(unsigned long long)old_math_steps,(unsigned long long)old_keypad_steps,
        (unsigned long long)marker_steps,(unsigned long long)event_count,(unsigned)sizeof(struct event),errors);
    array(file,"rng_entries",rng_entries,8);array(file,"math_entries",math_entries,3);
    array(file,"boundary_entries",boundary_entries,4);fputs("}\n",file);
    return fclose(file)!=0;
}
