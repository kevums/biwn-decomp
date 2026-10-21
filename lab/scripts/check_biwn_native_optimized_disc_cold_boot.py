"""Fresh-load original/derived CDI, native read-only execution observer.
No savestate, host RAM/code patch, injected allocation, or CPU seed. Emulator
HLE/device providers are retained and explicitly reported. Partial game build.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess,ctypes
from check_biwn_native_button_digit import ROOT,sha,save

OBSERVER='\n#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};\ntypedef void(*read_cpu)(struct cpu*);\nstatic read_cpu readstate;static const unsigned char*RAM;static int candidate;\nstatic uint64_t instructions,entries,staging,copy_checks,copy_errors,resident_steps,old_body_steps,heap_inits;\nstatic uint64_t arithmetic_entries[3],arithmetic_original_steps;\nstatic uint32_t heap_base;static unsigned active,count,errors;static uint32_t return_pc,return_sp;\nstruct pair {struct cpu before,after;uint32_t mask;};static struct pair pairs[128];\nstatic const unsigned char payload[]={PAYLOAD};\nstatic uint32_t rd32(uint32_t a){if(a>0x1ffffc){errors++;return 0;}return((uint32_t)RAM[a]<<24)|((uint32_t)RAM[a+1]<<16)|((uint32_t)RAM[a+2]<<8)|RAM[a+3];}\nvoid begin_observe(const void*ram,read_cpu f,int selected){RAM=ram;readstate=f;candidate=selected;}\nint32_t observe(uint32_t pc){\n struct cpu s;instructions++;\n if(pc==0xe540)arithmetic_entries[0]++;\n if(pc==0xe588)arithmetic_entries[1]++;\n if(pc==0xe60a)arithmetic_entries[2]++;\n if(pc>=0xe540&&pc<0xe61c&&pc!=0xe540&&pc!=0xe588&&pc!=0xe60a)arithmetic_original_steps++;\n if(pc==0x4000)entries++;\n if(pc==0xff000)staging++;\n if(pc==0x400a){copy_checks++;if(candidate&&memcmp(RAM+0x15edc0,payload,sizeof(payload)))copy_errors++;}\n if(pc==0x155c0){heap_inits++;heap_base=rd32(0x112d60);}\n if(pc>=0x15edc0&&pc<0x15edc0+sizeof(payload))resident_steps++;\n if(pc>=0x1b71e&&pc<0x1b780)old_body_steps++;\n if(active&&pc==return_pc){readstate(&s);if(s.r[15]==return_sp){pairs[count].after=s;count++;active=0;}}\n if(pc==0x1b718){\n  if(active||count>=128){errors++;return 0;}readstate(&s);pairs[count].before=s;\n  return_pc=rd32(s.r[15]);return_sp=s.r[15]+4;pairs[count].mask=rd32(s.r[15]+4);active=1;\n }\n return 0;\n}\nstatic void cpu_json(FILE*f,const struct cpu*s){unsigned i;fprintf(f,"{\\"registers\\":[");for(i=0;i<16;i++)fprintf(f,"%s%u",i?",":"",s->r[i]);fprintf(f,"],\\"PC\\":%u,\\"USP\\":%u,\\"SSP\\":%u,\\"SR\\":%u}",s->pc,s->usp,s->ssp,s->sr);}\nint finish_observe(const char*path){unsigned i;FILE*f=fopen(path,"w");if(!f)return 1;\n fprintf(f,"{\\"instructions\\":%llu,\\"mainstage_entries\\":%llu,\\"new_staging_entries\\":%llu,\\"copy_checks\\":%llu,\\"copy_errors\\":%llu,\\"resident_steps\\":%llu,\\"old_body_steps\\":%llu,\\"heap_inits\\":%llu,\\"heap_base\\":%u,\\"pending_call\\":%u,\\"errors\\":%u,\\"arithmetic_original_steps\\":%llu,\\"arithmetic_entries\\":[%llu,%llu,%llu],\\"calls\\":[",(unsigned long long)instructions,(unsigned long long)entries,(unsigned long long)staging,(unsigned long long)copy_checks,(unsigned long long)copy_errors,(unsigned long long)resident_steps,(unsigned long long)old_body_steps,(unsigned long long)heap_inits,heap_base,active,errors,(unsigned long long)arithmetic_original_steps,(unsigned long long)arithmetic_entries[0],(unsigned long long)arithmetic_entries[1],(unsigned long long)arithmetic_entries[2]);\n for(i=0;i<count;i++){fprintf(f,"%s{\\"mask\\":%u,\\"before\\":",i?",":"",pairs[i].mask);cpu_json(f,&pairs[i].before);fprintf(f,",\\"after\\":");cpu_json(f,&pairs[i].after);fprintf(f,"}");}fprintf(f,"]}\\n");return fclose(f)!=0;}\n'
INSTALL='''
        observer=c.CDLL(str(Path(%(library)r)))
        observer.begin_observe.argtypes=[c.c_void_p,c.c_void_p,c.c_int]
        observer.begin_observe(ram_pointer,c.cast(core.BIWNReadCPUState,c.c_void_p),int(disc!=Path(%(original)r)))
        OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32)
        native_observer=OWNER(('observe',observer))
        core.BIWNSetCPUExecOwner.argtypes=[OWNER,c.c_int]
        core.BIWNSetCPUExecOwner(native_observer,0)
'''
FINISH='''
        observer.finish_observe.argtypes=[c.c_char_p];observer.finish_observe.restype=c.c_int
        assert observer.finish_observe(str(out/'native-observation.json').encode())==0
        report['native_observation']=str(out/'native-observation.json')
        report['observer_scope']='Read-only native host observer; retained original CPU emulator executes game and compiled component. No source CPU owner or host guest-state writes.'
'''
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=24000);args=parser.parse_args()
 out=ROOT/'verification/native-optimized-disc-cold-boot'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 mathproof=json.loads((ROOT/'verification/native-optimized-math-current.json').read_text());assert mathproof['status']=='terminal_native_arithmetic_full_ABI_and_zero_exception_pass'
 bpath=ROOT/'verification/native-optimized-disc-build-current.json';build=json.loads(bpath.read_text());assert sha(build['derived_disc'])==build['derived_disc_sha256']
 epath=ROOT/'verification/native-optimized-disc-entry-current.json';entry=json.loads(epath.read_text());assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(bpath)
 payload=Path(build['component']).read_bytes();source=out/'native_observer.c';source.write_text(OBSERVER.replace('PAYLOAD',','.join(str(x)for x in payload)));library=out/'libnative-observer.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)];p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'observer-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 original_probe=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';text=original_probe.read_text();text='import sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\n'+text
 marker='ROOT = Path(__file__).resolve().parents[1]';assert text.count(marker)==1;text=text.replace(marker,'ROOT = Path('+repr(str(ROOT))+')')
 marker='    args = parser.parse_args()';text=text.replace(marker,"    parser.add_argument('--disc',type=Path,required=True)\n"+marker,1)
 text=text.replace("    disc = ROOT / 'projects/black-ice-white-noise/originals/BIWN#23.cdi'","    disc = args.disc.resolve()",1)
 text=text.replace("    button_ids = {'U': 4, 'D': 5, 'L': 6, 'R': 7, 'A': 8,\n                  'B': 0, 'C': 1, 'OPTION': 3, 'PAUSE': 2}","    from biwn_controller import JOYPAD_BUTTONS\n    button_ids=JOYPAD_BUTTONS",1)
 marker='        assert ram_pointer';assert text.count(marker)==1;text=text.replace(marker,marker+'\n'+INSTALL%dict(library=str(library),original=build['original_disc']))
 marker="        report.update(status='terminal_fresh_libretro_CD_probe', frames=rows,";assert text.count(marker)==1;text=text.replace(marker,FINISH+'\n'+marker)
 marker="                       stage_sha256=hashlib.sha256(ram[0x4000:0x100000]).hexdigest())";assert text.count(marker)==1;text=text.replace(marker,"                       video_sha256=hashlib.sha256(video.get('raw',b'')).hexdigest(),\n"+marker)
 probe=out/'fresh_native_disc_probe.py';probe.write_text(text)
 # Ordinary inputs after the previously verified merchant arrival. No scene,
 # position, inventory or task values are injected.
 windows=[dict(start_frame=23545,stop_frame=23553,buttons=['1']),dict(start_frame=23580,stop_frame=23588,buttons=['B','C']),dict(start_frame=23700,stop_frame=23708,buttons=['2']),dict(start_frame=23740,stop_frame=23748,buttons=['B','C']),dict(start_frame=23800,stop_frame=23808,buttons=['3'])]
 windows=[x for x in windows if x['stop_frame']<=args.frames+1];inputs=out/'ordinary-input.json';save(inputs,dict(windows=windows))
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames_requested=args.frames,build_proof=str(bpath),build_proof_sha256=sha(bpath),entry_proof=str(epath),entry_proof_sha256=sha(epath),whole_game_complete=False,physical_console_verified=False,new_disc_build=True,host_RAM_patches=0,checkpoint_restores=0,host_CPU_seeds=0,commands=[],game_byte_repairs_beyond_native_layout=0,arithmetic_bundle_proof=str(ROOT/'verification/native-optimized-math-current.json'),arithmetic_bundle_proof_sha256=sha(ROOT/'verification/native-optimized-math-current.json'))
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-optimized-disc-cold-boot-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';children=[]
  for lane,disc in [('reference',build['original_disc']),('candidate',build['derived_disc'])]:
   run=[str(ROOT/'.venv/bin/python'),str(probe),'--boot','hle','--frames',str(args.frames),'--core',str(core),'--disc',disc,'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
   log=(out/(lane+'.log')).open('w');child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=run))
  state['status']='running_fresh_disc_pair';checkpoint();print('PIDs',[child.pid for _,child,_ in children],flush=True)
  codes={}
  for lane,child,log in children:codes[lane]=child.wait();log.close()
  state['exit_codes']=codes;assert not any(codes.values()),codes
  reports={lane:json.loads((out/lane/'report.json').read_text())for lane,_,_ in children};observations={lane:json.loads((out/lane/'native-observation.json').read_text())for lane,_,_ in children}
  a=observations['reference'];b=observations['candidate'];assert not a['errors']and not b['errors']and not b['copy_errors']
  assert b['new_staging_entries']==b['copy_checks']==1 and b['heap_base']==build['heap_start']
  assert a['heap_base']==build['resident_address']and a['new_staging_entries']==0
  video_equal=sum(x['video_sha256']==y['video_sha256']for x,y in zip(reports['reference']['frames'],reports['candidate']['frames']))
  gamefields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word']
  field_equal=sum(all(x[k]==y[k]for k in gamefields)for x,y in zip(reports['reference']['frames'],reports['candidate']['frames']))
  call_equal=a['calls']==b['calls'];save(out/'call-comparison.json',dict(equal=call_equal,reference=a['calls'],candidate=b['calls']))
  equal={name:sha(out/'reference'/name)==sha(out/'candidate'/name)for name in ['video-final.xrgb8888','frontend-PCM.s16le']}
  newram=(out/'candidate/RAM-final.bin').read_bytes();assert newram[build['resident_address']:build['resident_address']+len(payload)]==payload
  if args.frames>=24000:assert b['calls']and b['resident_steps']>0 and not b['old_body_steps']
  assert b['arithmetic_original_steps']==0 and all(x>0 for x in b['arithmetic_entries'])
  state.update(status='terminal_fresh_native_optimized_disc_observed',frames_per_lane=args.frames,observations=observations,video_frames_equal=video_equal,game_state_frames_equal=field_equal,all_call_boundaries_equal=call_equal,final_artifacts_equal=equal,native_component_calls=len(b['calls']),native_component_instructions=b['resident_steps'],payload_retained_at_end=True,derived_disc_sha256=build['derived_disc_sha256'],runtime_dependencies_sha256={str(path):sha(path)for path in [core,original_probe,source,library,probe,inputs,Path(__file__)]},scope='Ordinary fresh libretro load of original and derived CDI; no restored machine or host guest-state patch/seed. New native mainstage entry copies four-entry bundle into explicit reservation, then resident finalizer clears4096temporary staging bytes; patched original heap excludes it. Original CPU/GPU/DSP/device emulator and HLE/CD bootstrap/drive remain providers. This is a partial mixed native game build, not whole decompilation, authenticated hardware boot or physical console test.')
  checkpoint();save(ROOT/'verification/native-optimized-disc-cold-boot-current.json',state);print(json.dumps({k:state[k]for k in ['status','frames_per_lane','video_frames_equal','game_state_frames_equal','native_component_calls','native_component_instructions','all_call_boundaries_equal','final_artifacts_equal']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
