"""Fresh fixed-input equal-frame measurement with explicit live-boundary checks.
Not route/quiescence acceptance. Original observer counts are retained;only
expected active-arena end counts are classified using independent guard checks.
No host guest RAM/CPU injection, checkpoint restore or repairs.
"""
import argparse,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from extract_biwn_stage import swap16
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
EXTRA=r'''
int fixed_prefix_boundary(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"pre_finish_arena_errors\":%llu,\"region_errors\":%u,\"deck_open_at_end\":%u",(unsigned long long)arena_errors,native_deck_regions(ram,payload,deck_used),deck_valid_entries!=deck_native_returns);
 fputs(",\"active\":[",f);for(unsigned i=0;i<102;i++)fprintf(f,"%s%u",i?",":"",arena_active[i]);fputs("],\"used\":[",f);for(unsigned i=0;i<102;i++)fprintf(f,"%s%u",i?",":"",arena_used[i]);fputs("]}\n",f);return fclose(f)!=0;
}
'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');ap.add_argument('--frames',type=int,default=1000);ap.add_argument('--profile',choices=['wait','direct-poll','rotation','clear','display-list'],default='display-list');args=ap.parse_args();assert 600<=args.frames<=24962
 lane='control'if args.control else'candidate';family='scene17-'+args.profile;sourcep=V/'native-scene17-wait-fresh-v2-control-current.json';record=read(sourcep);source=Path(record['directory'])/'probe.py';original=read(record['report']);frames=original['frames'][:args.frames];schedule=[dict(frame=x['frame'],buttons=(x.get('navigation')or{}).get('buttons',[]))for x in frames]
 bp=V/('native-'+family+'-disc-build-v1-current.json');b=read(bp);final=read(V/('native-Deck-'+family+'-final-v1-current.json'));assert final['status']=='terminal_deeper_candidate_final_component_startup_heap_gates_pass'and final['build_sha256']==sha(bp)
 g=read(V/(family+'-geometry-observer-qualified-v1-current.json'));observer_src=Path(g['observer']);observer_text=observer_src.read_text();assert sha(observer_src)==g['source_sha256'][str(observer_src)]
 out=V/(family+'-fixed-prefix-v5')/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+lane);out.mkdir(parents=True);schedulep=out/'fixed-inputs.json';save(schedulep,schedule);save(out/'build-as-run.json',b)
 cfile=out/'observer.c';cfile.write_text(observer_text+'\n'+EXTRA);assert cfile.read_text().startswith(observer_text);lib=out/'observer.dylib';direction=Path(record['directory'])/'direction-shadow-model.c';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cfile),str(direction),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 disc=Path(b['derived_disc'])
 if args.control:
  disc=out/'same-layout-original-scene.cdi';subprocess.run(['/bin/cp','-c',b['derived_disc'],str(disc)],check=True,capture_output=True);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);offset=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']+0x17e0e-0x4000;before=Path(b['derived_stage']).read_bytes()[0x17e0e-0x4000:0x17e18-0x4000];original_bytes=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x17e0e:0x17e18]
  with disc.open('r+b')as f:f.seek(offset);assert f.read(10)==swap16(before);f.seek(offset);f.write(swap16(original_bytes));f.flush();os.fsync(f.fileno())
  save(out/'control-delta.json',dict(address='0x17e0e',bytes=10,before=before.hex(),after=original_bytes.hex(),parent_sha256=b['derived_disc_sha256'],control_sha256=sha(disc)))
 text=source.read_text().replace(str(Path(record['directory'])/'observer.dylib'),str(lib));assert str(lib)in text;text=text.replace(str(read(V/'native-scene17-wait-disc-build-v1-current.json')['component']),b['component'])
 a=text.index('            if navigation_enabled and current_frame >= 600:');z=text.index('            core.retro_run()',a);text=text[:a]+'''            buttons=fixed_buttons[current_frame-1]['buttons']
            navigation_inputs={button_ids[name]for name in buttons if name in button_ids}
            navigation_keyboard_inputs={KEYBOARD_BUTTONS[name]for name in buttons if name in KEYBOARD_BUTTONS}
            navigation={'fixed_input_replay':True,'buttons':buttons,'no_guest_memory_writes':True}
'''+text[z:]
 anchor='        frame_loop_started = time.monotonic()';text=text.replace(anchor,'        fixed_buttons=json.loads(Path('+repr(str(schedulep))+').read_text());assert len(fixed_buttons)==args.frames\n'+anchor)
 a=text.index('            if deck_trial_start is None and outdoor_hold>=120');z=text.index('        if DSP_owner:',a);text=text[:a]+text[z:]
 anchor="        retained_finish=observer.finish_observe(str(out/'gameplay-observation.json').encode())";assert text.count(anchor)==1;text=text.replace(anchor,"        observer.fixed_prefix_boundary.argtypes=[c.c_char_p];observer.fixed_prefix_boundary.restype=c.c_int\n        assert observer.fixed_prefix_boundary(str(out/'prefix-boundary.json').encode())==0\n"+anchor)
 rotation_anchor="        assert observer.reset_dump(str(out/'reset-observation.json').encode())==0"
 if args.profile in ['rotation','clear','display-list']:
  assert text.count(rotation_anchor)==1
  text=text.replace(rotation_anchor,rotation_anchor+"\n        observer.rotation_dump.argtypes=[c.c_char_p];observer.rotation_dump.restype=c.c_int\n        assert observer.rotation_dump(str(out/'rotation-observation.json').encode())==0")
 if args.profile in ['clear','display-list']:
  clear_anchor="        assert observer.rotation_dump(str(out/'rotation-observation.json').encode())==0";assert text.count(clear_anchor)==1
  text=text.replace(clear_anchor,clear_anchor+"\n        observer.clear_dump.argtypes=[c.c_char_p];observer.clear_dump.restype=c.c_int\n        assert observer.clear_dump(str(out/'clear-observation.json').encode())==0")
 if args.profile=='display-list':
  display_anchor="        assert observer.clear_dump(str(out/'clear-observation.json').encode())==0";assert text.count(display_anchor)==1
  text=text.replace(display_anchor,display_anchor+"\n        observer.display_dump.argtypes=[c.c_char_p];observer.display_dump.restype=c.c_int\n        assert observer.display_dump(str(out/'display-observation.json').encode())==0")
 text=text.replace('        assert retained_finish==0',"        report['fixed_prefix_retained_finish_status']=retained_finish\n        report['fixed_input_replay']=dict(schedule_sha256="+repr(sha(schedulep))+",frames=args.frames,feedback_disabled=True,host_guest_RAM_writes=0,scope='Exactframe-countmeasurement;activecallsarenotcomplete-routeacceptance.')")
 probe=out/'probe.py';probe.write_text(text);command=list(record['command']);command[2]=str(probe);command[command.index('--frames')+1]=str(args.frames);command[command.index('--output')+1]=str(out/'measurement');command[command.index('--disc')+1]=str(disc)
 state=dict(status='running_fixed_frontend_prefix',directory=str(out),pid=os.getpid(),child_pid=None,lane=lane,profile=args.profile,command=command,frames=args.frames,schedule=str(schedulep),schedule_sha256=sha(schedulep),new_predictions=0,new_training=False,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0)
 pointer=V/(family+'-fixed-prefix-v5-'+lane+'-current.json')
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark()
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait(timeout=900)
  state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-4000:];report=read(out/'measurement/report.json');assert len(report['frames'])==args.frames and report['fixed_input_replay']['schedule_sha256']==sha(schedulep)
  assert [dict(frame=x['frame'],buttons=x['navigation']['buttons'])for x in report['frames']]==schedule
  observers={name:read(out/'measurement'/file)for name,file in [('shared','shared-observation.json'),('geometry','geometry-observation.json'),('outer','outer-observation.json'),('reset','reset-observation.json'),('retained','gameplay-observation.json')]};
  if args.profile in ['rotation','clear','display-list']:observers['rotation']=read(out/'measurement/rotation-observation.json')
  if args.profile in ['clear','display-list']:observers['clear']=read(out/'measurement/clear-observation.json')
  if args.profile=='display-list':observers['display']=read(out/'measurement/display-observation.json')
  boundary=read(out/'measurement/prefix-boundary.json');assert boundary['pre_finish_arena_errors']==boundary['region_errors']==0
  memory=(out/'measurement/RAM-final.bin').read_bytes();payload=Path(b['component']).read_bytes();base=b['resident_address'];arena=b['arena_address'];assert b['arena_slots']==102 and b['arena_slot_stride']==256
  for i in range(102):
   at=arena+i*256
   assert memory[at:at+16]==memory[at+240:at+256]==bytes([0xa5])*16,('GPUarena fence',i)
   if not boundary['used'][i]:assert memory[at:at+256]==payload[at-base:at-base+256],('unused GPUarena',i)
  expected_end_only_errors=sum(bool(x)for x in boundary['active'])+boundary['deck_open_at_end'];assert observers['retained']['arena_errors']==expected_end_only_errors
  faults={}
  for name,obs in observers.items():
   faults[name]={k:x for k,x in obs.items()if isinstance(x,(int,float))and k!='arena_errors'and any(word in k.lower()for word in ['error','outside','corrupt','collision'])};assert not any(faults[name].values()),(name,faults[name])
  state.update(status='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance',report=str(out/'measurement/report.json'),report_sha256=sha(out/'measurement/report.json'),observers=observers,boundary=boundary,expected_end_only_arena_errors=expected_end_only_errors,raw_arena_errors_retained=observers['retained']['arena_errors'],source_sha256={str(p):sha(p)for p in [Path(__file__),bp,sourcep,source,observer_src,cfile,lib,schedulep,probe,out/'measurement/report.json',out/'measurement/prefix-boundary.json']},scope=__doc__);mark();print(state['status'],args.profile,lane,args.frames,flush=True)
 except BaseException as e:state.update(status='terminal_fixed_prefix_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
