"""Fresh failed-control replay with read-only pre/post-68000 memory tracing.

The diagnostic observes existing core data directly, avoiding MMIO read side
effects. No replacement instructions, clock changes, guest writes or restores.
"""
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save

TRACE = r'''
static const unsigned char *trace_blitter;
static size_t (*trace_gpu_save)(unsigned char *);
struct trace_record {
 uint32_t frame,phase,dispatch,cycles;struct cpu cpu;
 unsigned char world[16],opcode[8],blitter[256];
};
static struct trace_record trace_ring[128];
static unsigned trace_count,trace_captured;
void configure_corruption_trace(const void *blitter,size_t (*save_gpu)(unsigned char *)){
 trace_blitter=blitter;trace_gpu_save=save_gpu;
}
static void trace_cpu_json(FILE *f,const struct cpu *value){
 fprintf(f,"{\"registers\":[");
 for(unsigned i=0;i<16;i++)fprintf(f,"%s%u",i?",":"",value->r[i]);
 fprintf(f,"],\"pc\":%u,\"sr\":%u,\"usp\":%u,\"ssp\":%u}",value->pc,value->sr,value->usp,value->ssp);
}
static void trace_hex(FILE *f,const unsigned char *bytes,unsigned size){
 fputc('"',f);for(unsigned i=0;i<size;i++)fprintf(f,"%02x",bytes[i]);fputc('"',f);
}
static void trace_memory(unsigned phase,uint32_t pc,int32_t cycles){
 if(frame<1400u||trace_captured)return;
 struct trace_record *v=&trace_ring[trace_count%128u];memset(v,0,sizeof(*v));
 v->frame=frame;v->phase=phase;v->dispatch=pc;v->cycles=(uint32_t)cycles;
 read_cpu(&v->cpu);memcpy(v->world,ram+0x49c50,16);
 if(pc<=0x1ffff8u)memcpy(v->opcode,ram+pc,8);
 memcpy(v->blitter,trace_blitter,256);trace_count++;
 /* Recorded route coordinates fit16bits. This trigger is diagnostic only. */
 if(rd32(0x49c50u)<=0xffffu&&rd32(0x49c56u)<=0xffffu)return;
 trace_captured=1;char path[4096];FILE *f;
 snprintf(path,sizeof(path),"TRACE_DIRECTORY/first-corruption-RAM.bin");f=fopen(path,"wb");
 if(f){fwrite(ram,1,0x200000,f);fclose(f);}
 unsigned char gpu[65536];size_t gpu_size=trace_gpu_save(gpu);
 snprintf(path,sizeof(path),"TRACE_DIRECTORY/first-corruption-GPU.bin");f=fopen(path,"wb");
 if(f){fwrite(gpu,1,gpu_size,f);fclose(f);}
 snprintf(path,sizeof(path),"TRACE_DIRECTORY/first-corruption.json");f=fopen(path,"w");if(!f)return;
 fprintf(f,"{\"frame\":%u,\"phase\":%u,\"dispatch_PC\":%u,\"trace_count\":%u,\"GPU_bytes\":%zu,\"history\":[",frame,phase,pc,trace_count,gpu_size);
 unsigned start=trace_count>128u?trace_count-128u:0;
 for(unsigned i=start;i<trace_count;i++){
  const struct trace_record *row=&trace_ring[i%128u];
  fprintf(f,"%s{\"frame\":%u,\"phase\":%u,\"dispatch_PC\":%u,\"cycles\":%u,\"CPU\":",i==start?"":",",row->frame,row->phase,row->dispatch,row->cycles);
  trace_cpu_json(f,&row->cpu);fprintf(f,",\"world_hex\":");trace_hex(f,row->world,16);
  fprintf(f,",\"opcode_hex\":");trace_hex(f,row->opcode,8);
  fprintf(f,",\"blitter_hex\":");trace_hex(f,row->blitter,256);fputc('}',f);
 }
 fprintf(f,"]}\n");fclose(f);
}
void trace_retired(uint32_t pc,int32_t cycles){trace_memory(1u,pc,cycles);}
'''

def main():
    source_proof = ROOT/'verification/native-fast-core-entry-selector-deck-pair-current.json'
    parent = json.loads(source_proof.read_text()); parent_dir = Path(parent['directory'])
    original_command = next(row['command'] for row in parent['commands'] if row['lane']=='control')
    core = Path(original_command[original_command.index('--core')+1])
    disc = Path(original_command[original_command.index('--disc')+1])
    assert sha(disc)==parent['control_disc_sha256']
    for path in [core, parent_dir/'core-observer.c', parent_dir/'fresh-format-probe.py', parent_dir/'input.json']:
        assert sha(path)==parent['source_sha256'][str(path)], str(path)
    symbols = {}
    for line in subprocess.check_output(['nm',str(core)],text=True).splitlines():
        parts=line.split()
        if len(parts)==3 and parts[2] in ['_blitter_ram','_GPUStateSave','_gpu_pc']:
            symbols[parts[2]]=int(parts[0],16)
    assert len(symbols)==3
    out=ROOT/'verification/native-fast-core-first-corruption'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    text=(parent_dir/'core-observer.c').read_text()
    marker='int32_t observe(uint32_t pc) {';assert text.count(marker)==1
    text=text.replace(marker,TRACE.replace('TRACE_DIRECTORY',str(out))+'\n'+marker)
    marker='    steps++;';assert text.count(marker)==1
    text=text.replace(marker,marker+'\n    trace_memory(0u,pc,0);')
    observer=out/'observer.c';observer.write_text(text);library=out/'observer.dylib'
    result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True)
    (out/'compile.log').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
    probe=out/'probe.py';text=(parent_dir/'fresh-format-probe.py').read_text()
    marker=str(parent_dir/'libcore-observer.dylib');assert text.count(marker)==1;text=text.replace(marker,str(library))
    marker='        core.BIWNSetCPUExecOwner(native_observer,0)';assert text.count(marker)==1
    install=f'''
        # Resolve hidden raw data by the pinned Mach-O's ASLR slide. No MMIO reads.
        slide=c.cast(core.GPUStateSave,c.c_void_p).value-{symbols['_GPUStateSave']}
        assert c.cast(c.pointer(c.c_uint32.in_dll(core,'gpu_pc')),c.c_void_p).value==slide+{symbols['_gpu_pc']}
        observer.configure_corruption_trace.argtypes=[c.c_void_p,c.c_void_p]
        observer.configure_corruption_trace(slide+{symbols['_blitter_ram']},c.cast(core.GPUStateSave,c.c_void_p))
        RETIRED=c.CFUNCTYPE(None,c.c_uint32,c.c_int32)
        retired_trace=RETIRED(('trace_retired',observer))
        core.BIWNSetCPURetiredObserver.argtypes=[RETIRED]
        core.BIWNSetCPURetiredObserver(retired_trace)
'''
    text=text.replace(marker,marker+install);compile(text,str(probe),'exec');probe.write_text(text)
    inputs=out/'input-prefix.json';windows=json.loads((parent_dir/'input.json').read_text())['windows']
    clipped=[dict(row,stop_frame=min(row['stop_frame'],1441))for row in windows if row['start_frame']<1441]
    save(inputs,dict(windows=clipped))
    command=list(original_command);command[2]=str(probe)
    command[command.index('--frame-controller-script')+1]=str(inputs)
    command[command.index('--frames')+1]='1440';command[command.index('--output')+1]=str(out/'control')
    state=dict(status='running_readonly_first_corruption_trace',directory=str(out),pid=os.getpid(),source_proof=str(source_proof),source_proof_sha256=sha(source_proof),command=command,phase_definition={'0':'before68000instruction','1':'after68000instruction_before_remainingCycle_update'},trigger='Afterframe1400 first playerX or Z above65535; finite route diagnostic,not universal game invariant',hidden_data_symbols=symbols,input_prefix_unchanged_through_frame1440=True,host_guest_RAM_writes=0,checkpoint_restores=0,core_binary_modified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),source_proof,parent_dir/'core-observer.c',parent_dir/'fresh-format-probe.py',parent_dir/'input.json',inputs,core,disc,observer,library,probe]},goal_complete=False)
    def mark():
        save(out/'protocol.json',state);save(ROOT/'verification/native-fast-core-first-corruption-active.json',state)
    mark()
    with (out/'control.log').open('w')as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
    capture=out/'first-corruption.json'
    state.update(status='terminal_readonly_first_corruption_trace_completed'if not code else'terminal_failed',exit_code=code,capture_found=capture.exists(),output_sha256={str(p):sha(p)for p in [capture,out/'first-corruption-RAM.bin',out/'first-corruption-GPU.bin',out/'control/report.json']if p.exists()})
    mark()
    if not code:save(ROOT/'verification/native-fast-core-first-corruption-current.json',state)
    print(json.dumps(dict(status=state['status'],capture_found=state['capture_found'])),flush=True);assert not code

if __name__=='__main__':main()
