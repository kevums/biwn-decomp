"""Fresh number-entry observer and same-layout single-redirect control."""
from datetime import datetime,timezone
from pathlib import Path
import json
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
OBSERVER=r'''
static uint64_t number_entries[1],compiled_number_calls[1],old_number_body_steps[1];
struct number_pending {unsigned live;uint32_t sp,ret,task;};
static struct number_pending number_pending[64];
static uint64_t number_returns[1],number_user_observations[1],number_stack_outside[1],number_tracking_errors;
static uint32_t number_min_headroom[1]={0xffffffffu};
static void watch_number(uint32_t pc){
 unsigned entry=pc==0x1b212u,any=0;
 for(unsigned j=0;j<64;j++)any|=number_pending[j].live;
 if(!any&&!entry)return;
 struct cpu value;read_cpu(&value);uint32_t sp=value.r[15],task=rd32(0xc0920u);
 for(unsigned j=0;j<64;j++)if(number_pending[j].live&&pc==number_pending[j].ret&&sp==number_pending[j].sp+4u){number_returns[0]++;number_pending[j].live=0;}
 if(entry){
  unsigned j;for(j=0;j<64;j++)if(!number_pending[j].live)break;
  if(j==64){number_tracking_errors++;return;}
  number_pending[j]=(struct number_pending){1u,sp,rd32(sp),task};
 }
 for(unsigned j=0;j<64;j++)if(number_pending[j].live&&!(value.sr&0x2000u)&&task==number_pending[j].task){
  if((pc>=0x15edc0u&&pc<0x15edc0u+payload_size)||(pc>=0x1b212u&&pc<0x1b29cu)){
   number_user_observations[0]++;
   if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)number_stack_outside[0]++;
   else if(sp-task-38u<number_min_headroom[0])number_min_headroom[0]=sp-task-38u;
  }
 }
}
'''
REPORT=r'''
    array(file,"number_entries",number_entries,1);array(file,"compiled_number_calls",compiled_number_calls,1);array(file,"old_number_body_steps",old_number_body_steps,1);
    array(file,"number_returns",number_returns,1);array(file,"number_user_observations",number_user_observations,1);array(file,"number_stack_outside",number_stack_outside,1);
    fprintf(file,",\"number_min_headroom\":[%u],\"number_tracking_errors\":%llu",number_min_headroom[0],(unsigned long long)number_tracking_errors);
    unsigned pending=0;for(unsigned j=0;j<64;j++)pending+=number_pending[j].live;
    fprintf(file,",\"number_pending_at_finish\":%u",pending);
'''
def main():
 out=ROOT/'verification/native-number-gameplay-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 bp=ROOT/'verification/native-number-format-disc-build-current.json';build=json.loads(bp.read_text())
 old=ROOT/'scripts/run_biwn_native_unsigned_math_deck_pair.py';text=old.read_text().replace('native-unsigned-format','native-number-format').replace('native-unsigned-math','native-number-entry').replace('unsigned','number')
 # Replace the entire old two-math observer builder; no old range remapping.
 begin=text.index("    source=ROOT/'scripts/native_gameplay_observer.c'");end=text.index("    original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'",begin)
 replacement="""    source=ROOT/'scripts/native_gameplay_observer.c';text=source.read_text()
    observer_helper=Path(__file__).with_name('prepare_number_format_gameplay.py')
    from prepare_number_format_gameplay import OBSERVER,REPORT
    marker='int32_t observe(uint32_t pc) {';assert text.count(marker)==1;text=text.replace(marker,OBSERVER+'\\n'+marker)
    marker='    steps++;';assert text.count(marker)==1
    extra='\\n    watch_number(pc);\\n    if(pc==0x1b212u)number_entries[0]++;\\n    if(pc=='+hex(build['symbols']['biwn_native_format_number'])+'u)compiled_number_calls[0]++;\\n    if(pc>0x1b212u&&pc<0x1b29cu)old_number_body_steps[0]++;\\n'
    text=text.replace(marker,marker+extra)
    marker='    array(file,"rng_entries",rng_entries,8);';assert text.count(marker)==1;text=text.replace(marker,REPORT+'\\n'+marker)
    observer=out/'number-observer.c';observer.write_text(text);library=out/'libnumber-observer.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'observer-build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
"""
 text=text[:begin]+replacement+text[end:]
 text=text.replace('for address in [0xe61c,0xe67c]:','for address in [0x1b212]:').replace('pair_changed==differences==11','0<pair_changed==differences<=6').replace('[0,0]','[0]')
 text=text.replace("assert a['number_entries']==a['compiled_number_calls']","assert a['number_entries']==a['compiled_number_calls']==a['number_returns'] and all(a['number_entries'])\n    for obs in observations.values():assert obs['number_stack_outside']==[0] and not obs['number_tracking_errors'] and not obs['number_pending_at_finish']")
 text=text.replace("recipe_path,overlay_path,out/'shared-selector-repair-build.json'","recipe_path,overlay_path,observer_helper,out/'shared-selector-repair-build.json'")
 text=text.replace('Only two6byte number arithmetic redirects restored','Only the6byte number-conversion redirect restored').replace('only two number arithmetic redirects','only the number-conversion redirect').replace('two number arithmetic redirects','one number-conversion redirect').replace('both_helpers_exercised','number_helper_exercised').replace('2600fresh','2600fresh')
 target=ROOT/'scripts/run_biwn_native_number_entry_deck_pair.py';compile(text,str(target),'exec');target.write_text(text)
 (out/'parent-deck-runner.py').write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes())
 # Unrepaired adaptive full route on immediate parent and new candidate.
 oldlong=ROOT/'scripts/run_format_unsigned_long_routes.py';long=oldlong.read_text().replace("[('parent','native-ccr-format'),('unsigned','native-unsigned-format')]","[('parent','native-unsigned-format'),('number','native-number-format')]").replace("builds['unsigned']","builds['number']").replace('native-unsigned-format-long-route','native-number-format-long-route')
 longtarget=ROOT/'scripts/run_format_number_long_routes.py';compile(long,str(longtarget),'exec');longtarget.write_text(long);(out/'parent-long-runner.py').write_bytes(oldlong.read_bytes());(out/longtarget.name).write_bytes(longtarget.read_bytes())
 state=dict(status='number_fresh_gameplay_drivers_prepared',directory=str(out),build_proof=str(bp),build_proof_sha256=sha(bp),dependencies_sha256={str(p):sha(p)for p in [Path(__file__),old,oldlong,target,longtarget]},new_training=False,default_promoted=False)
 save(out/'preparation.json',state);save(ROOT/'verification/native-number-gameplay-preparation-current.json',state);print(out)
if __name__=='__main__':main()
