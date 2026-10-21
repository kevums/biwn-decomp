/* Read CPU/main RAM/GPU work RAM only; retained core executes instructions. */
static char movement_prefix[4096];
static FILE *movement_file;
static const unsigned char *movement_gpu;
static uint32_t movement_sequence,world_sequence;
void configure_movement(const void *gpu_memory){movement_gpu=gpu_memory;}
static uint32_t movement_gpu32(unsigned offset){
    if(!movement_gpu||offset>0xffcu){errors++;return 0;}
    return ((uint32_t)movement_gpu[offset]<<24)|((uint32_t)movement_gpu[offset+1]<<16)|((uint32_t)movement_gpu[offset+2]<<8)|movement_gpu[offset+3];
}
static void diagnose_movement(uint32_t pc){
    struct cpu s;char name[4352];unsigned selected=0,save_memory=0;
    if(pc==0x1a188u)world_sequence++;
    if(frame<9850u||frame>10050u)return;
    switch(pc){
        case 0x1a188u:case 0x1a26cu:case 0x1a2c2u:case 0x1a542u:
        case 0xe4c0u:case 0xe504u:case 0xe7d4u:selected=1;break;
        case 0xe220u:
            read_cpu(&s);
            if(s.r[15]<=0x1ffffcu&&rd32(s.r[15])==0x1a2c2u)selected=1;
            break;
        default:break;
    }
    if(!selected)return;
    read_cpu(&s);
    if(!movement_file){
        if(snprintf(name,sizeof(name),"%s.movement.jsonl",movement_prefix)<0){errors++;return;}
        movement_file=fopen(name,"w");if(!movement_file){errors++;return;}
    }
    fprintf(movement_file,"{\"sequence\":%u,\"world_sequence\":%u,\"frame\":%u,\"pc\":%u,\"task\":%u,\"clock\":%u,\"previous_clock\":%u,\"delta_clock\":%u,\"registers\":[",movement_sequence,world_sequence,frame,pc,rd32(0xc0920u),rd32(0x778ccu),rd32(0x46252u),rd32(0x4c24cu));
    for(unsigned i=0;i<16;i++)fprintf(movement_file,"%s%u",i?",":"",s.r[i]);
    fprintf(movement_file,"],\"sr\":%u,\"usp\":%u,\"ssp\":%u,\"exception_return_pc\":%u,\"player\":[%u,%u,%u,%u,%u,%u],\"heading\":%u,\"speed\":%u,\"mode\":%u,\"floor\":%u,\"scene\":%u,\"pad_49ba4\":%u,\"pad_49bac\":%u,\"deltas\":[%u,%u,%u,%u,%u,%u],\"gpu_packet\":[",
        s.sr,s.usp,s.ssp,s.ssp<=0x1ffffau?rd32(s.ssp+2u):0,
        rd32(0x49c50u),rd16(0x49c54u),rd32(0x49c56u),rd16(0x49c5au),rd16(0x49c5cu),rd16(0x49c5eu),ram[0x49cbau],rd32(0x49cc4u),
        rd16(0x49c60u),rd16(0x49c62u),rd16(0x49c64u),rd32(0x49ba4u),rd32(0x49bacu),
        rd16(0x49cdeu),rd16(0x49ce0u),rd16(0x49ce2u),rd16(0x49ce6u),rd16(0x49ce8u),rd16(0x49ceau));
    for(unsigned i=0;i<8;i++)fprintf(movement_file,"%s%u",i?",":"",movement_gpu32(0x204u+4u*i));
    fputc(']',movement_file);
    save_memory=frame>=9915u&&frame<=9923u&&(pc==0x1a188u||pc==0x1a26cu||pc==0x1a2c2u||pc==0x1a542u);
    if(save_memory){
        int n=snprintf(name,sizeof(name),"%s.move-%08u-%06x-%06u.ram",movement_prefix,frame,pc,movement_sequence);
        if(n<0||(size_t)n>=sizeof(name))errors++;
        else{
            FILE *snapshot=fopen(name,"wb");if(!snapshot)errors++;
            else{if(fwrite(ram,1,0x200000u,snapshot)!=0x200000u)errors++;if(fclose(snapshot))errors++;}
            fprintf(movement_file,",\"RAM\":\"%s\"",name);
        }
    }
    fputs("}\n",movement_file);movement_sequence++;
}
