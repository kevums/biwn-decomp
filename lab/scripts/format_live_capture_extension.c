/* Inserted into the read-only observer; no guest writes or CPU ownership. */
static char capture_root[4096];
static FILE *capture_events;
static unsigned capture_errors;
static unsigned selected_call(unsigned kind,unsigned ordinal){
    if(kind)return ordinal<=8u||ordinal==16u||ordinal==32u||ordinal==64u||ordinal==96u||ordinal==112u;
    if(ordinal<=12u)return 1u;
    const unsigned samples[]={30,50,70,71,72,100,150,200,300,500,700,1000,1500,2000,3000,4000,5000};
    for(unsigned j=0;j<sizeof(samples)/sizeof(samples[0]);j++)if(ordinal==samples[j])return 1u;
    return 0u;
}
static int capture_begin(const char *path){
    if(snprintf(capture_root,sizeof(capture_root),"%s-calls",path)>=(int)sizeof(capture_root))return 1;
    if(mkdir(capture_root,0700))return 1;
    char name[4200];snprintf(name,sizeof(name),"%s/events.jsonl",capture_root);
    capture_events=fopen(name,"w");return !capture_events;
}
static void capture_event(unsigned entering,const struct format_pending *pending,const struct cpu *value){
    if(!pending->selected)return;
    char name[4200];snprintf(name,sizeof(name),"%s/%u-%u-%s.ram",capture_root,pending->kind,pending->ordinal,entering?"entry":"return");
    FILE *file=fopen(name,"wb");
    if(!file){capture_errors++;return;}
    if(fwrite(ram,0x200000,1,file)!=1)capture_errors++;
    if(fclose(file))capture_errors++;
    fprintf(capture_events,"{\"event\":\"%s\",\"kind\":%u,\"ordinal\":%u,\"frame\":%u,\"step\":%llu,\"entry_sp\":%u,\"return_PC\":%u,\"task\":%u,\"supervisor_excursions\":%u,\"supervisor_steps\":%u,\"other_task_steps\":%u,\"first_supervisor_PC\":%u,\"registers\":[",
        entering?"entry":"return",pending->kind,pending->ordinal,frame,(unsigned long long)steps,pending->sp,pending->ret,pending->task,
        pending->supervisor_excursions,pending->supervisor_steps,pending->other_task_steps,pending->first_supervisor_PC);
    for(unsigned j=0;j<16;j++)fprintf(capture_events,"%s%u",j?",":"",value->r[j]);
    fprintf(capture_events,"],\"PC\":%u,\"SR\":%u,\"usp\":%u,\"ssp\":%u,\"ram_file\":\"%u-%u-%s.ram\"}\n",
        value->pc,(unsigned)value->sr,value->usp,value->ssp,pending->kind,pending->ordinal,entering?"entry":"return");
    if(fflush(capture_events))capture_errors++;
}
