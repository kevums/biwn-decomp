"""Fresh equal-frame fixed-input measurement,not ordinary-route acceptance.
Exact recorded frontend buttons override all feedback decisions. Read-only
observers may end inside a valid live call;pending is recorded,not normalized.
No guest RAM/CPU state injection,restore or repair.
"""
import argparse,os,subprocess,json
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');ap.add_argument('--frames',type=int,default=1000);args=ap.parse_args();assert 600<=args.frames<=24962
 lane='control'if args.control else'candidate';sourcep=V/'native-scene17-wait-fresh-v2-control-current.json';record=read(sourcep);source=Path(record['directory'])/'probe.py';original=read(record['report']);frames=original['frames'][:args.frames];assert all(x['frame']==i+1 for i,x in enumerate(frames))
 schedule=[dict(frame=x['frame'],buttons=(x.get('navigation')or{}).get('buttons',[]))for x in frames]
 out=V/'scene17-wait-fixed-prefix-v1'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+lane);out.mkdir(parents=True);schedulep=out/'fixed-inputs.json';save(schedulep,schedule);save(out/'source-control-job.json',record)
 text=source.read_text();start=text.index('            if navigation_enabled and current_frame >= 600:');stop=text.index('            core.retro_run()',start)
 text=text[:start]+'''            buttons=fixed_buttons[current_frame-1]['buttons']
            navigation_inputs={button_ids[name]for name in buttons if name in button_ids}
            navigation_keyboard_inputs={KEYBOARD_BUTTONS[name]for name in buttons if name in KEYBOARD_BUTTONS}
            navigation={'fixed_input_replay':True,'buttons':buttons,'no_guest_memory_writes':True}
''' +text[stop:]
 anchor='        frame_loop_started = time.monotonic()';assert text.count(anchor)==1;text=text.replace(anchor,"        fixed_buttons=json.loads(Path("+repr(str(schedulep))+ ").read_text());assert len(fixed_buttons)==args.frames\n"+anchor)
 start=text.index('            if deck_trial_start is None and outdoor_hold>=120');stop=text.index('        if DSP_owner:',start);text=text[:start]+text[stop:]
 assert text.count('        assert retained_finish==0')==1;text=text.replace('        assert retained_finish==0',"        report['fixed_prefix_retained_finish_status']=retained_finish\n        report['fixed_input_replay']=dict(schedule="+repr(str(schedulep))+",schedule_sha256="+repr(sha(schedulep))+",frames=args.frames,source_control_report="+repr(record['report'])+",feedback_disabled=True,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,scope='Fixed equal-frame measurement;mayendwithinvalidlivecall.Noclaimofordinaryroutecompletionorquiescence.')")
 # The existing end-of-probe report save comes after observer dumps.
 probe=out/'probe.py';probe.write_text(text);command=list(record['command']);command[2]=str(probe);command[command.index('--frames')+1]=str(args.frames);command[command.index('--output')+1]=str(out/'measurement')
 current=read(V/f'native-scene17-wait-fresh-v2-{lane}-current.json');command[command.index('--disc')+1]=read(V/'native-scene17-wait-disc-build-v1-current.json')['derived_disc']if lane=='candidate'else record['command'][record['command'].index('--disc')+1]
 state=dict(status='running_fixed_frontend_prefix',directory=str(out),pid=os.getpid(),child_pid=None,lane=lane,command=command,frames=args.frames,schedule=str(schedulep),schedule_sha256=sha(schedulep),new_predictions=0,new_training=False,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0)
 pointer=V/f'scene17-wait-fixed-prefix-v1-{lane}-current.json'
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark()
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait(timeout=900)
  state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-4000:]
  report=read(out/'measurement/report.json');assert len(report['frames'])==args.frames
  assert report['fixed_input_replay']['schedule_sha256']==sha(schedulep)
  assert [dict(frame=x['frame'],buttons=x['navigation']['buttons'])for x in report['frames']]==schedule
  observers={name:read(out/'measurement'/file)for name,file in [('shared','shared-observation.json'),('geometry','geometry-observation.json'),('outer','outer-observation.json'),('reset','reset-observation.json'),('retained','gameplay-observation.json')]}
  faults={}
  for name,obs in observers.items():
   faults[name]={k:x for k,x in obs.items()if isinstance(x,(int,float))and any(word in k.lower()for word in ['error','outside','corrupt','collision'])}
   assert not any(faults[name].values()),(name,faults[name])
  state.update(status='terminal_fixed_frontend_prefix_measurement_pass_not_route_acceptance',report=str(out/'measurement/report.json'),report_sha256=sha(out/'measurement/report.json'),observers=observers,retained_finish_status=report['fixed_prefix_retained_finish_status'],faults=faults,source_sha256={str(p):sha(p)for p in [Path(__file__),sourcep,source,schedulep,probe,Path(report['core']),out/'measurement/report.json']},scope=__doc__);mark();print(state['status'],lane,args.frames,flush=True)
 except BaseException as e:state.update(status='terminal_fixed_prefix_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
