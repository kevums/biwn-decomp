"""Read-only cold-game captures, then explicitly isolated native return checks.
No captured state is restored into a continuing game; isolated checks disable IRQ.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,struct
import check_biwn_scheduler as sched
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 tp=ROOT/'verification/native-free-timing-controls-current.json';control=json.loads(tp.read_text());cd=Path(control['directory']);source=cd/'timing-observer.c';template=cd/'fresh-timing-controls.py'
 for p in [source,template]:assert sha(p)==control['source_sha256'][str(p)]
 bp=ROOT/'verification/native-free-disc-build-current.json';build=json.loads(bp.read_text());assert sha(bp)==control['source_sha256'][str(bp)];variant=control['variants']['initializer_only'];disc=Path(variant['disc']);assert sha(disc)==variant['sha256']
 out=ROOT/'verification/native-free-captured-calls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);host=source.read_text();needle='static FILE *events;';assert host.count(needle)==1;host=host.replace(needle,needle+'\nstatic char case_prefix[2048];\nstatic unsigned captured_calls;')
 needle='    payload=code;payload_size=length;events=fopen(path,"wb");';assert host.count(needle)==1
 host=host.replace(needle,'    if(snprintf(case_prefix,sizeof(case_prefix),"%s",path)<0)return 1;\n'+needle)
 needle='    steps++;';assert host.count(needle)==1
 block='''
    if(pc==0x1545c&&captured_calls<2){
        char path[2304];struct cpu state;FILE *file;
        read_cpu(&state);
        if(snprintf(path,sizeof(path),"%s.free-%u-RAM.bin",case_prefix,captured_calls)<0){errors++;return 0;}
        file=fopen(path,"wb");if(!file){errors++;return 0;}
        if(fwrite(ram,1,0x200000,file)!=0x200000)errors++;
        if(fclose(file))errors++;
        if(snprintf(path,sizeof(path),"%s.free-%u-CPU.bin",case_prefix,captured_calls)<0){errors++;return 0;}
        file=fopen(path,"wb");if(!file){errors++;return 0;}
        if(fwrite(&state,sizeof(state),1,file)!=1)errors++;
        if(fclose(file))errors++;
        captured_calls++;
    }
'''
 host=host.replace(needle,needle+block);hs=out/'capture-observer.c';hs.write_text(host);lib=out/'libcapture-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(hs),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 text=template.read_text();old='        observer=c.CDLL('+repr(str(cd/'libtiming-observer.dylib'))+')';assert text.count(old)==1;text=text.replace(old,'        observer=c.CDLL('+repr(str(lib))+')');probe=out/'fresh-capture-probe.py';probe.write_text(text);compile(text,str(probe),'exec')
 core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';inputs=cd/'prefix-input.json';assert sha(core)==control['source_sha256'][str(core)]and sha(inputs)==control['source_sha256'][str(inputs)]
 command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','6400','--core',str(core),'--disc',str(disc),'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/'fresh')]
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),control_proof=str(tp),control_proof_sha256=sha(tp),command=command,source_sha256={str(p):sha(p)for p in [Path(__file__),source,template,hs,lib,probe,core,inputs,bp]},checkpoint_restores_into_game=0,host_guest_writes_in_fresh_game=0,isolated_call_IRQ_disabled=True,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-free-captured-calls-active.json',state)
 mark()
 try:
  with(out/'fresh.log').open('w')as log:
   child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state.update(status='running_read_only_fresh_capture',child_pid=child.pid);mark();print('PID',child.pid,flush=True);code=child.wait()
  assert code==0,code
  reference=json.loads((cd/'initializer_only/report.json').read_text())['frames'];captured=json.loads((out/'fresh/report.json').read_text())['frames'];assert captured==reference,'Capture changed deterministic frame rows'
  assert sha(out/'fresh/frontend-PCM.s16le')==sha(cd/'initializer_only/frontend-PCM.s16le')and sha(out/'fresh/RAM-final.bin')==sha(cd/'initializer_only/RAM-final.bin')
  obs=json.loads((out/'fresh/gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors'])and obs['free_entries']==2
  payload=Path(build['linked_component']).read_bytes();symbols=build['symbols'];BASE=build['resident_address'];n=sched.Native();results=[]
  def execute(image,cpu,original):
   n.device.seed(image,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,cpu['ssp']);l.m68k_set_reg(17,0);l.m68k_set_reg(15,cpu['usp']);l.m68k_set_reg(17,cpu['SR'])
   for i,v in enumerate(cpu['registers']):l.m68k_set_reg(i,v)
   l.m68k_set_reg(16,0x1545c);SP=cpu['registers'][15];stop=int.from_bytes(image[SP:SP+4],'big');minimum=SP;cycles=0;pcs=[]
   for _ in range(50000):
    pc=l.m68k_get_reg(None,16)
    if pc==stop:break
    assert(0x1545c<=pc<0x1557a)if original else(pc==0x1545c or BASE<=pc<BASE+len(payload)),hex(pc)
    minimum=min(minimum,l.m68k_get_reg(None,15));pcs.append(pc);cycles+=l.m68k_execute(1)
   else:raise AssertionError('Captured free call failed to return')
   outcpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17));outcpu['usp']=n.prefix[16]if outcpu['SR']&0x2000 else outcpu['registers'][15];outcpu['ssp']=outcpu['registers'][15]if outcpu['SR']&0x2000 else n.prefix[17];assert outcpu['registers'][15]==SP+4
   return n.device.ram(),outcpu,minimum,cycles,len(pcs)
  try:
   for i in range(2):
    prefix=out/'fresh'/('gameplay-events.bin.free-'+str(i));ram_path=Path(str(prefix)+'-RAM.bin');cpu_path=Path(str(prefix)+'-CPU.bin');image=ram_path.read_bytes();raw=struct.unpack('<19IH2x',cpu_path.read_bytes());cpu=dict(registers=list(raw[:16]),PC=raw[16],usp=raw[17],ssp=raw[18],SR=raw[19]);assert cpu['PC']==0x1545c and not(cpu['SR']&0xc000)
    candidate=bytearray(image);candidate[0x1545c:0x15464]=b'\x4e\xf9'+symbols['biwn_native_free'].to_bytes(4,'big')+b'\x4e\x71';assert image[BASE:BASE+len(payload)]==payload
    state['status']='isolated_captured_call_native_comparison';mark();left=execute(image,cpu,True);right=execute(candidate,cpu,False);SP=cpu['registers'][15];low=min(left[2],right[2]);task=int.from_bytes(image[0xc0920:0xc0924],'big');assert task+38<=low<=SP<=task+0x400,('outside task stack',hex(task),hex(low),hex(SP))
    normalized=bytearray(right[0]);normalized[0x1545c:0x15464]=left[0][0x1545c:0x15464];normalized[low:SP-8]=left[0][low:SP-8]
    assert left[1]==right[1]and normalized==left[0],('captured native return mismatch',i)
    assert right[0][BASE:BASE+len(payload)]==payload
    results.append(dict(case=i,source_RAM=str(ram_path),source_RAM_sha256=sha(ram_path),source_CPU=str(cpu_path),source_CPU_sha256=sha(cpu_path),incoming_CPU=cpu,original_return_CPU=left[1],compiled_return_CPU=right[1],original_cycles=left[3],compiled_cycles=right[3],original_instructions=left[4],compiled_instructions=right[4],current_task=task,task_stack_header_end=task+38,task_stack_top=task+0x400,entry_SP=SP,original_minimum_SP=left[2],compiled_minimum_SP=right[2],extra_private_stack_bytes=left[2]-right[2],full_CPU_public_RAM_and_original8save_bytes_match=True,private_scratch_inside_current_task_stack=True))
  finally:n.close()
  save(out/'isolated-results.json',results);state.update(status='terminal_two_live_captured_free_calls_match_isolated_native_returns',cases=2,results=results,fresh6400frame_rows_RAM_PCM_repeat=True,compiled_payload_sha256=sha(build['linked_component']),scope='Two original free inputs captured read-only from cold initializer-only control at frame5554. Fresh capture repeats prior6400frame rows/RAM/PCM. Original and source free compare in explicit IRQ-disabled isolated calls on actual capturedRAM/fullCPU; returns/publicRAM/original8save bytes match, source private scratch fits current1KBtask. Actual emulated cycle costs differ. This excludes an isolated return-state defect on these two inputs or overflow of their current task stack, but not live IRQ/device/concurrency/interleaving or other inputs. Captured state is never transplanted into a continuing game.')
  state['execution_dependencies_sha256']={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',Path(build['linked_component'])]};mark();save(ROOT/'verification/native-free-captured-calls-current.json',state);print(state['status'],[(x['original_cycles'],x['compiled_cycles'])for x in results],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
