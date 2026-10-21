"""Read-only A2-base writer provenance and a captured failing blit launch."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

EXTRA=r'''
static size_t (*handoff_blitter_save)(unsigned char *);
static uint32_t handoff_previous_base=0xffffffffu,handoff_previous_pc,handoff_previous_phase;
static unsigned handoff_launch_captured;
void configure_handoff(size_t (*blitter_save)(unsigned char *)){handoff_blitter_save=blitter_save;}
static void handoff_blob(const char *name,const unsigned char *memory,size_t size){
 char path[4096];snprintf(path,sizeof(path),"HANDOFF_DIRECTORY/%s",name);
 FILE *f=fopen(path,"wb");if(f){fwrite(memory,1,size,f);fclose(f);}
}
static void handoff_watch(unsigned phase,uint32_t pc){
 if(frame<1400u||trace_captured)return;
 uint32_t base=((uint32_t)trace_blitter[0x24]<<24)|((uint32_t)trace_blitter[0x25]<<16)|((uint32_t)trace_blitter[0x26]<<8)|trace_blitter[0x27];
 if(base!=handoff_previous_base){
  FILE *f=fopen("HANDOFF_DIRECTORY/A2-base-writers.jsonl","a");
  if(f){struct cpu cpu;read_cpu(&cpu);fprintf(f,"{\"frame\":%u,\"phase\":%u,\"PC\":%u,\"previous_phase\":%u,\"previous_PC\":%u,\"before_base\":%u,\"after_base\":%u,\"CPU_PC\":%u,\"CPU_SR\":%u,\"task\":%u}\n",frame,phase,pc,handoff_previous_phase,handoff_previous_pc,handoff_previous_base,base,cpu.pc,cpu.sr,rd32(0xc0920));fclose(f);}
  handoff_previous_base=base;
 }
 /* Exact failing launch from the preceding read-only GPU trace. */
 if(phase==2u&&frame==1429u&&pc==0xf03aaeu&&base==0x44168u&&trace_bank0[8]==0xd4u&&!handoff_launch_captured){
  handoff_launch_captured=1;unsigned char buffer[65536];size_t size;
  handoff_blob("launch-before-RAM.bin",ram,0x200000);
  size=trace_gpu_save(buffer);handoff_blob("launch-before-GPU.bin",buffer,size);
  size=handoff_blitter_save(buffer);handoff_blob("launch-before-blitter.bin",buffer,size);
 }
 handoff_previous_pc=pc;handoff_previous_phase=phase;
}
'''

def main():
    source_proof=ROOT/'verification/native-fast-core-GPU-corruption-current.json'
    parent=json.loads(source_proof.read_text());source_dir=Path(parent['directory'])
    assert parent['status']=='terminal_readonly_first_corruption_trace_completed'and parent['capture_found']
    core=Path(parent['command'][parent['command'].index('--core')+1])
    for p,h in parent['source_sha256'].items():assert sha(p)==h,p
    symbols={}
    for line in subprocess.check_output(['nm',str(core)],text=True).splitlines():
        fields=line.split()
        if len(fields)==3 and fields[2]in['_BlitterStateSave','_GPUStateSave']:symbols[fields[2]]=int(fields[0],16)
    assert len(symbols)==2
    out=ROOT/'verification/native-fast-core-blitter-handoff'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    text=(source_dir/'observer.c').read_text()
    marker='static void trace_memory(unsigned phase,uint32_t pc,int32_t cycles){';assert text.count(marker)==1
    text=text.replace(marker,EXTRA.replace('HANDOFF_DIRECTORY',str(out))+'\n'+marker+'\n handoff_watch(phase,pc);')
    text=text.replace(str(source_dir),str(out));observer=out/'observer.c';observer.write_text(text);library=out/'observer.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True)
    (out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    text=(source_dir/'probe.py').read_text();assert text.count(str(source_dir/'observer.dylib'))==1;text=text.replace(str(source_dir/'observer.dylib'),str(library))
    marker='        core.BIWNSetGPUBundleOwner(gpu_trace)';assert text.count(marker)==1
    text=text.replace(marker,marker+f'''\n        observer.configure_handoff.argtypes=[c.c_void_p]\n        observer.configure_handoff(slide+{symbols['_BlitterStateSave']})\n''')
    probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    command=list(parent['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'control')
    state=dict(status='running_readonly_blitter_handoff_capture',directory=str(out),pid=os.getpid(),source_proof=str(source_proof),source_proof_sha256=sha(source_proof),command=command,host_guest_RAM_writes=0,checkpoint_restores=0,core_binary_modified=False,GPU_callback_return=0,hidden_symbols=symbols,source_sha256={str(p):sha(p)for p in [Path(__file__),source_proof,source_dir/'observer.c',source_dir/'probe.py',core,observer,library,probe]},goal_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-fast-core-blitter-handoff-active.json',state)
    mark()
    with(out/'control.log').open('w')as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
    artifacts=[p for p in out.glob('*')if p.is_file()and p.name not in ['protocol.json']]
    state.update(status='terminal_readonly_blitter_handoff_capture_completed'if not code else'terminal_failed',exit_code=code,capture_found=(out/'launch-before-RAM.bin').exists(),output_sha256={str(p):sha(p)for p in artifacts})
    mark()
    if not code:save(ROOT/'verification/native-fast-core-blitter-handoff-current.json',state)
    print(json.dumps(dict(status=state['status'],capture_found=state['capture_found'])),flush=True);assert not code

if __name__=='__main__':main()
