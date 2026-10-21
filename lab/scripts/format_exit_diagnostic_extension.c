/* Host-only observation. No CPU/RAM writes and no replacement execution. */
static char diagnostic_prefix[4096];
static FILE *diagnostic_file;
static uint32_t diagnostic_sequence;
static void diagnose_exit(uint32_t pc) {
    struct cpu s;
    const uint32_t actor=0x49d6cu+3u*206u;
    unsigned selected=0,save_memory=0;
    char name[4352];
    if(frame<24000u)return;
    if(pc==0x1c9e8u||pc==0x131c8u||pc==0x131e2u){selected=1;save_memory=pc!=0x131e2u;}
    if((frame>=24100u&&frame<=24250u)||(frame>=28950u&&frame<=28990u)){
        if(pc==0x12f90u||pc==0x13122u||pc==0x131beu||pc==0x1a188u||pc==0x1a26cu||pc==0x1a422u||pc==0x1a542u||pc==0x191f4u)selected=1;
    }
    if(!selected)return;
    read_cpu(&s);
    if((pc>=0x12f00u&&pc<=0x13420u)&&s.r[11]!=actor)return;
    if(!diagnostic_file){
        if(snprintf(name,sizeof(name),"%s.diagnostic.jsonl",diagnostic_prefix)<0){errors++;return;}
        diagnostic_file=fopen(name,"w");
        if(!diagnostic_file){errors++;return;}
    }
    fprintf(diagnostic_file,"{\"sequence\":%u,\"frame\":%u,\"pc\":%u,\"clock\":%u,\"task\":%u,\"registers\":[",diagnostic_sequence,frame,pc,rd32(0x778ccu),rd32(0xc0920u));
    for(unsigned i=0;i<16;i++)fprintf(diagnostic_file,"%s%u",i?",":"",s.r[i]);
    fprintf(diagnostic_file,"],\"sr\":%u,\"usp\":%u,\"ssp\":%u,\"return_pc\":%u,\"stack_word4\":%u,\"player\":[%u,%u],\"heading\":%u,\"actor3\":[%u,%u,%u,%u,%u],\"mode\":%u,\"floor\":%u,\"media_flag\":%u,\"media_state\":%u,\"pad_49ba4\":%u,\"pad_49bac\":%u,\"deltas\":[%u,%u,%u,%u,%u,%u]",
        s.sr,s.usp,s.ssp,s.r[15]<=0x1ffffau?rd32(s.r[15]):0,s.r[15]<=0x1ffffau?rd16(s.r[15]+4u):0,
        rd32(0x49c50u),rd32(0x49c56u),ram[0x49cbau],
        rd16(actor),rd32(actor+4u),rd32(actor+10u),rd16(actor+108u),rd16(actor+20u),
        rd16(0x49c60u),rd16(0x49c62u),rd16(0x47b82u),rd16(0xbd85cu),rd32(0x49ba4u),rd32(0x49bacu),
        rd16(0x49cdeu),rd16(0x49ce0u),rd16(0x49ce2u),rd16(0x49ce6u),rd16(0x49ce8u),rd16(0x49ceau));
    if(save_memory){
        int n=snprintf(name,sizeof(name),"%s.diag-%08u-%06x-%06u.ram",diagnostic_prefix,frame,pc,diagnostic_sequence);
        if(n<0||(size_t)n>=sizeof(name)){errors++;}
        else{
            FILE *snapshot=fopen(name,"wb");
            if(!snapshot){errors++;}
            else{if(fwrite(ram,1,0x200000u,snapshot)!=0x200000u)errors++;if(fclose(snapshot))errors++;}
            fprintf(diagnostic_file,",\"RAM\":\"%s\"",name);
        }
    }
    fputs("}\n",diagnostic_file);
    diagnostic_sequence++;
}
