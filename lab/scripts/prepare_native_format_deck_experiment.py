"""Source-derived ordinary-input Deck/debug experiment; outcomes are not assumed."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GLOBALS=r'''
struct format_pending {unsigned live,kind;uint32_t sp,ret,task;};
static struct format_pending fp[64];
static uint64_t format_returns[2],format_user_observations[2],format_stack_outside[2],format_tracking_errors;
static uint32_t format_min_headroom[2]={0xffffffffu,0xffffffffu};
'''
WATCH=r'''
static void watch_format(uint32_t pc){
 unsigned isentry=(pc==0x1b160u||pc==0x1b1a8u),any=0;
 for(unsigned j=0;j<64;j++)any|=fp[j].live;
 if(!any&&!isentry)return;
 struct cpu value;read_cpu(&value);uint32_t sp=value.r[15],task=rd32(0xc0920u);
 for(unsigned j=0;j<64;j++)if(fp[j].live&&pc==fp[j].ret&&sp==fp[j].sp+4u){format_returns[fp[j].kind]++;fp[j].live=0;}
 if(isentry){
  unsigned j;for(j=0;j<64;j++)if(!fp[j].live)break;
  if(j==64){format_tracking_errors++;return;}
  fp[j]=(struct format_pending){1u,pc==0x1b1a8u,sp,rd32(sp),task};
 }
 for(unsigned j=0;j<64;j++)if(fp[j].live&&!(value.sr&0x2000u)&&task==fp[j].task){
  unsigned kind=fp[j].kind;
  /* Watch only the same user task while it executes this helper's original
     body or resident code. Supervisor IRQ code/other tasks are excluded. */
  if((pc>=0x15edc0u&&pc<0x15edc0u+payload_size)||
     (kind==0u?pc>=0x1b160u&&pc<0x1b1a0u:pc>=0x1b1a8u&&pc<0x1b200u)){
   format_user_observations[kind]++;
   if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)format_stack_outside[kind]++;
   else if(sp-task-38u<format_min_headroom[kind])format_min_headroom[kind]=sp-task-38u;
  }
 }
}
'''
FINISH=r'''
    array(file,"format_returns",format_returns,2);array(file,"format_user_observations",format_user_observations,2);array(file,"format_stack_outside",format_stack_outside,2);
    fprintf(file,",\"format_min_headroom\":[%u,%u],\"format_tracking_errors\":%llu",format_min_headroom[0],format_min_headroom[1],(unsigned long long)format_tracking_errors);
    unsigned pending=0;for(unsigned j=0;j<64;j++)pending+=fp[j].live;
    fprintf(file,",\"format_pending_at_finish\":%u",pending);
'''
def main():
    parent=ROOT/'scripts/run_biwn_native_format_fresh_pair.py';text=parent.read_text()
    text=text.replace('native-format-fresh-pair','native-format-deck-pair').replace('fresh_format_pair','fresh_format_deck_pair')
    assert text.count('frames=1600;')==1
    text=text.replace('frames=1600;','frames=2600;').replace('1600fresh HLEboot','2600fresh HLEboot')
    needle="windows=[dict(w,stop_frame=min(w['stop_frame'],frames+1))for w in json.loads(prefix.read_text())['windows']if w['start_frame']<=frames]"
    assert text.count(needle)==1
    replacement="windows=[dict(w,stop_frame=min(w['stop_frame'],1601))for w in json.loads(prefix.read_text())['windows']if w['start_frame']<=1600];windows += [dict(start_frame=1630,stop_frame=1640,buttons=['1']),dict(start_frame=1660,stop_frame=1670,buttons=['B','C']),dict(start_frame=1800,stop_frame=2000,buttons=['OPTION']),dict(start_frame=2100,stop_frame=2104,buttons=['0'])]"
    text=text.replace(needle,replacement)
    needle="text=text.replace(marker,marker+'\\nstatic uint64_t format_entries[2],compiled_format_calls[2],old_format_body_steps[2];')"
    assert text.count(needle)==1
    text=text.replace(needle,needle+"\n    text=text.replace('static uint32_t heap_base;','static uint32_t heap_base;'+"+repr(GLOBALS)+")\n    text=text.replace('int32_t observe(uint32_t pc) {',"+repr(WATCH)+"+'\\nint32_t observe(uint32_t pc) {')\n    text=text.replace('    steps++;','    steps++;\\n    watch_format(pc);')\n    text=text.replace('    array(file,\\\"rng_entries\\\",rng_entries,8);',"+repr(FINISH)+"+'    array(file,\\\"rng_entries\\\",rng_entries,8);')")
    needle="probe.write_text(make_probe(ROOT/'scripts/probe_biwn_fresh_CD_boot.py',library,original,Path(build['component'])));compile(probe.read_text(),str(probe),'exec')"
    assert text.count(needle)==1
    added="\n    probe_text=probe.read_text();probe_marker=\"floor_word=int.from_bytes(ram[0x49c62:0x49c64],'big'),\";assert probe_text.count(probe_marker)==1;probe_text=probe_text.replace(probe_marker,probe_marker+\"\\n                       debug_overlay_word=int.from_bytes(ram[0x403cc:0x403ce],'big'),\\n                       editor_state_word=int.from_bytes(ram[0x403d6:0x403d8],'big'),\\n                       held_input_long=int.from_bytes(ram[0x49ba4:0x49ba8],'big'),\");probe.write_text(probe_text);compile(probe_text,str(probe),'exec')\n"
    text=text.replace(needle,needle+added)
    target=ROOT/'scripts/run_biwn_native_format_deck_pair.py';compile(text,str(target),'exec');target.write_text(text)
    report=dict(status='ordinary_input_Deck_Option_experiment_prepared',parent=str(parent),parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),driver=str(target),driver_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),frames=2600,input_policy='First1600frames retain previous movement,then stop. Keypad1 1630..1639;B+C1660..1669;OPTION1800..1999;keypad0 2100..2103. Same in candidate/control, no checkpoint/guest writes. Expected entry/drawing/string outcome is not assumed.',source_reason='Preserved initial inventory item1=0x41; original dispatcher calls11E6C for item0x41 with B/C. Editor poll11B4C copies heldOption bit9 into403CC; 10734 uses%s at10730 when403CCnonzero. Decompiled comments are evidence,not instructions.',watch_scope='Read-only pending call/return tracking and task-header/SP checks for the same user task in original helper/resident code. Supervisor IRQ and other-task instructions excluded; no arbitrary memory-write observation or physical proof.')
    (ROOT/'verification/native-format-deck-experiment-preparation-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['driver'])
if __name__=='__main__':main()
