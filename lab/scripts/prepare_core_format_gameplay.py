"""Read-only full formatter gameplay observer; two-redirect same-layout control."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
OBSERVER=r'''
static uint64_t formatter_entries[2],compiled_formatter_calls[2],formatter_returns[2],formatter_user_observations[2],formatter_stack_outside[2];
static uint64_t original_formatter_body_steps[5],formatter_tracking_errors;
static uint32_t formatter_min_headroom[2]={0xffffffffu,0xffffffffu};
struct format_pending {unsigned live,kind;uint32_t sp,ret,task;};
static struct format_pending format_pending[64];
static void watch_formatter(uint32_t pc){
 int kind=pc==0x1b29cu?0:pc==0x1b45au?1:-1;unsigned any=0;
 if(pc==CORE_BODY)compiled_formatter_calls[0]++;
 if(pc==VAR_BODY)compiled_formatter_calls[1]++;
 const uint32_t lo[5]={0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a},hi[5]={0x1b1a0,0x1b200,0x1b29c,0x1b45a,0x1b478};
 for(unsigned j=0;j<5;j++)if(pc>lo[j]&&pc<hi[j])original_formatter_body_steps[j]++;
 for(unsigned j=0;j<64;j++)any|=format_pending[j].live;
 if(!any&&kind<0)return;
 struct cpu value;read_cpu(&value);uint32_t sp=value.r[15],task=rd32(0xc0920u);unsigned nested=0;
 for(unsigned j=0;j<64;j++)if(format_pending[j].live){
  if(pc==format_pending[j].ret&&sp==format_pending[j].sp+4u){formatter_returns[format_pending[j].kind]++;format_pending[j].live=0;}
  else if(task==format_pending[j].task)nested=1;
 }
 if(kind>=0){
  formatter_entries[kind]++;
  /* Original variadic wrapper nests core; candidate calls its C body directly.
     Track whole outer invocation, never invent a second original boundary. */
  if(!nested){unsigned j;for(j=0;j<64;j++)if(!format_pending[j].live)break;
   if(j==64){formatter_tracking_errors++;return;}
   format_pending[j]=(struct format_pending){1u,(unsigned)kind,sp,rd32(sp),task};}
 }
 for(unsigned j=0;j<64;j++)if(format_pending[j].live&&!(value.sr&0x2000u)&&task==format_pending[j].task){
  if((pc>=0x15edc0u&&pc<0x15edc0u+payload_size)||(pc>=0x1b160u&&pc<0x1b478u)){
   unsigned k=format_pending[j].kind;formatter_user_observations[k]++;
   if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)formatter_stack_outside[k]++;
   else if(sp-task-38u<formatter_min_headroom[k])formatter_min_headroom[k]=sp-task-38u;
  }
 }
}
'''
REPORT=r'''
    array(file,"formatter_entries",formatter_entries,2);array(file,"compiled_formatter_calls",compiled_formatter_calls,2);array(file,"formatter_returns",formatter_returns,2);
    array(file,"formatter_user_observations",formatter_user_observations,2);array(file,"formatter_stack_outside",formatter_stack_outside,2);array(file,"original_formatter_body_steps",original_formatter_body_steps,5);
    fprintf(file,",\"formatter_min_headroom\":[%u,%u],\"formatter_tracking_errors\":%llu",formatter_min_headroom[0],formatter_min_headroom[1],(unsigned long long)formatter_tracking_errors);
    unsigned pending=0;for(unsigned j=0;j<64;j++)pending+=format_pending[j].live;
    fprintf(file,",\"formatter_pending_at_finish\":%u",pending);
'''
CLASSIFY='''def classify_saved(out,state,build):
    assert all(code==0 for code in state['exit_codes'].values())
    observations={lane:json.loads((out/lane/'gameplay-observation.json').read_text())for lane in ['candidate','control']}
    reports={lane:json.loads((out/lane/'report.json').read_text())for lane in observations};payload=Path(build['component']).read_bytes();heap={}
    for lane,obs in observations.items():
        assert not obs['errors']and not obs['copy_errors']and obs['entry_copies']==1
        memory=(out/lane/'RAM-final.bin').read_bytes();assert sha(out/lane/'RAM-final.bin')==reports[lane]['final_RAM_sha256']
        heap[lane]=int.from_bytes(memory[0x112d60:0x112d64],'big');assert heap[lane]==build['heap_start']
        assert memory[build['resident_address']:build['resident_address']+len(payload)]==payload
        assert obs['formatter_stack_outside']==[0,0]and not obs['formatter_tracking_errors']and not obs['formatter_pending_at_finish']
    a,b=observations['candidate'],observations['control']
    assert a['original_formatter_body_steps']==[0]*5 and b['compiled_formatter_calls']==[0,0]
    assert a['formatter_entries'][1]==a['compiled_formatter_calls'][1]==a['formatter_returns'][1]>0
    assert a['compiled_formatter_calls'][0]==a['formatter_entries'][0]+a['compiled_formatter_calls'][1]
    assert a['formatter_returns'][0]==a['formatter_entries'][0]
    assert b['formatter_returns'][1]==b['formatter_entries'][1]>0 and b['original_formatter_body_steps'][3]>0 and b['original_formatter_body_steps'][4]>0
    left,right=reports['candidate']['frames'],reports['control']['frames'];assert len(left)==len(right)==state['frames']
    fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256']
    comparisons={k:dict(different_frames=sum(x[k]!=y[k]for x,y in zip(left,right)),first_different_frame=next((x['frame']for x,y in zip(left,right)if x[k]!=y[k]),None))for k in fields}
    state.update(status='terminal_fresh_native_formatter_deck_pair_classified',observations=observations,comparisons=comparisons,final_RAM_heap_starts=heap,final_resident_payload_preserved=True,PCM_equal=sha(out/'candidate/frontend-PCM.s16le')==sha(out/'control/frontend-PCM.s16le'),report_sha256={lane:sha(out/lane/'report.json')for lane in reports},timing_vs_algorithm_cause_resolved=False,scope='2600fresh HLEframes per lane,same fixed ordinary pad schedule and same38declared-byte selector repairs. Same-layout control restores only core/variadic JMPs; new compiled math/number/pad/string stay installed. Observer returns0, no guestRAM writes/checkpoint restore. Candidate original five formatter body steps0; Ccore body is counted inside variadic C,outer root returns/task stacks observed. Legacy original-address heap hook misses native initializer; final report-boundRAM verifies real floor/payload. No frame,cycle,whole-game or physical equivalence.')
    state.pop('error',None);save(out/'protocol.json',state);save(ROOT/'verification/native-core-entry-selector-deck-pair-active.json',state);save(ROOT/'verification/native-core-entry-selector-deck-pair-current.json',state)
    print(state['status'],a['compiled_formatter_calls'],json.dumps(comparisons),flush=True)
'''
def main():
 out=ROOT/'verification/native-core-gameplay-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 old=ROOT/'scripts/run_biwn_native_number_entry_deck_pair.py';text=old.read_text().replace('native-number-format','native-core-format').replace('native-number-entry','native-core-entry')
 start=text.index('def classify_saved(');end=text.index('\ndef main():',start);text=text[:start]+CLASSIFY+'\n'+text[end:]
 start=text.index("    source=ROOT/'scripts/native_gameplay_observer.c'");end=text.index("    original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'",start)
 replacement="""    source=ROOT/'scripts/native_gameplay_observer.c';text=source.read_text()
    observer_helper=Path(__file__).with_name('prepare_core_format_gameplay.py')
    from prepare_core_format_gameplay import OBSERVER,REPORT
    watched=OBSERVER.replace('CORE_BODY',hex(build['symbols']['biwn_native_format_core_body'])+'u').replace('VAR_BODY',hex(build['symbols']['biwn_native_format_variadic_body'])+'u')
    marker='int32_t observe(uint32_t pc) {';assert text.count(marker)==1;text=text.replace(marker,watched+'\\n'+marker)
    marker='    steps++;';assert text.count(marker)==1;text=text.replace(marker,marker+'\\n    watch_formatter(pc);')
    marker='    array(file,"rng_entries",rng_entries,8);';assert text.count(marker)==1;text=text.replace(marker,REPORT+'\\n'+marker)
    observer=out/'core-observer.c';observer.write_text(text);library=out/'libcore-observer.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'observer-build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
"""
 text=text[:start]+replacement+text[end:];text=text.replace('for address in [0x1b212]:','for address in [0x1b29c,0x1b45a]:').replace('0<pair_changed==differences<=6','0<pair_changed==differences<=12')
 text=text.replace('Only the6byte number-conversion redirect restored','Only core and variadic6byte redirects restored').replace('only the number-conversion redirect','only core/variadic redirects').replace('one number-conversion redirect','two core/variadic redirects')
 target=ROOT/'scripts/run_biwn_native_core_entry_deck_pair.py';compile(text,str(target),'exec');target.write_text(text);(out/'parent-deck.py').write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes())
 oldlong=ROOT/'scripts/run_format_number_long_routes.py';long=oldlong.read_text().replace("[('parent','native-unsigned-format'),('number','native-number-format')]","[('parent','native-number-format'),('core','native-core-format')]").replace("builds['number']","builds['core']").replace('native-number-format-long-route','native-core-format-long-route')
 longtarget=ROOT/'scripts/run_format_core_long_routes.py';compile(long,str(longtarget),'exec');longtarget.write_text(long);(out/'parent-long.py').write_bytes(oldlong.read_bytes());(out/longtarget.name).write_bytes(longtarget.read_bytes())
 state=dict(status='native_core_fresh_gameplay_drivers_prepared',directory=str(out),dependencies_sha256={str(p):sha(p)for p in [Path(__file__),old,oldlong,target,longtarget]},default_promoted=False,new_training=False)
 save(out/'preparation.json',state);save(ROOT/'verification/native-core-gameplay-preparation-current.json',state);print(out)
if __name__=='__main__':main()
