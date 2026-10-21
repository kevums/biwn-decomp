"""Fresh ordinary-pad route to catalogued matrix-flagged indoor record268.
Existing v34image/monitors are retained. No checkpoint,gueststate or code repair.
An optional host JSON supplies only indoor waypoints,never guest addresses/values.
"""
import argparse,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');args=ap.parse_args();lane='control'if args.control else'candidate'
 qp=V/'record-matrix-route-watch-actual-CPU-v1-current.json';q=read(qp);assert q['status']=='terminal_original_native_record_matrix_callsite_actual_CPU_lanes_pass' and q['CPU_lanes']==128
 for p,h in q['source_sha256'].items():assert sha(p)==h,p
 bp=V/'native-record-strides-disc-build-v1-current.json';b=read(bp);jp=V/f'native-record-strides-fresh-v2-{lane}-current.json';job=read(jp);assert job['status']=='terminal_fresh_scene17_route_pending_review'
 for p,h in job['source_sha256'].items():assert sha(p)==h,p
 planp=V/'record-matrix-268-disc-plan-v1.json';plan=read(planp);assert plan['gate']['target']==268 and len(plan['points'])==34
 old=Path(job['directory']);out=V/'record-matrix-268-fresh-route-v1'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+lane);out.mkdir(parents=True)
 prefix=(old/'observer.c').read_text();assert prefix.count('int32_t observe(uint32_t pc)')==1 and prefix.count('int observer_quiescent(void)')==1
 renamed=prefix.replace('int32_t observe(uint32_t pc)','static int32_t matrix_prior_observe(uint32_t pc)').replace('int observer_quiescent(void)','static int matrix_prior_quiescent(void)')
 watch=ROOT/'scripts/record_matrix_route_watch_v1.inc.c';suffix=watch.read_text().replace('MR_HELPER_RETURN',str(b['shared_Deck_symbols']['biwn_v4_scene_helper_return'])+'u').replace('MR_ARENA',str(b['deck_arena_address'])+'u')
 source=out/'observer.c';source.write_text(renamed+'\n'+suffix+'\nint32_t observe(uint32_t pc){int32_t result=matrix_prior_observe(pc);mr_watch(pc);return result;}\nint observer_quiescent(void){return matrix_prior_quiescent()&&!mr_pending_total();}\n')
 lib=out/'observer.dylib';direction=old/'direction-shadow-model.c';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),str(direction),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 controls=out/'indoor-controls.json';save(controls,dict(waypoints=[[6240,35424]],purpose='Catalogued record268west entrance region3 connects east to region4 at X6208 and key4;cross into matrix-object region through ordinary controls. No guest-state writes.',source_region_bounds=[6144,6208,35328,35456],target_region_bounds=[6208,6592,35072,35648],source_group_key=4,source_group_flags='0xc700'))
 text=(old/'probe.py').read_text();assert text.count(str(old/'observer.dylib'))==1;text=text.replace(str(old/'observer.dylib'),str(lib))
 a=text.index('                if scene_change_frame is not None:',text.index('            if navigation_enabled and current_frame >= 600:'));z=text.index('                navigation_inputs =',a)
 replacement='''                mode=int.from_bytes(before[0x49c60:0x49c62],'big')
                scene=int.from_bytes(before[0x49c64:0x49c66],'big')
                if mode==2:
                    buttons=[];restoration_phase='hold_indoor_matrix_observation'
                    if scene==268:
                        control_file=Path(INDOOR_CONTROLS_PATH)
                        raw_control=control_file.read_bytes();digest=hashlib.sha256(raw_control).hexdigest()
                        if digest!=matrix_controls_sha:
                            value=json.loads(raw_control);points=value['waypoints'];assert len(points)<=128 and all(isinstance(p,list)and len(p)==2 and all(type(v)is int and 0<=v<65536 for v in p)for p in points)
                            matrix_indoor_points=points;matrix_indoor_index=0;matrix_controls_sha=digest
                            (out/('consumed-controls-'+digest+'.json')).write_bytes(raw_control)
                            matrix_control_history.append(dict(frame=current_frame,sha256=digest))
                        if matrix_indoor_index<len(matrix_indoor_points):
                            tx,tz=matrix_indoor_points[matrix_indoor_index]
                            if (tx-x)**2+(tz-z)**2<=64:
                                matrix_indoor_index+=1
                                if matrix_indoor_index<len(matrix_indoor_points):tx,tz=matrix_indoor_points[matrix_indoor_index]
                            if matrix_indoor_index<len(matrix_indoor_points):
                                dx,dz=tx-x,tz-z;target=round(math.atan2(-dx,dz)*128/math.pi)%256;error=(target-heading+128)%256-128
                                buttons=['L']if error>2 else['R']if error< -2 else['U'];restoration_phase='ordinary_indoor_waypoints'
                if current_frame>=args.frames-512:buttons=[];restoration_phase='bounded_release'
'''.replace('INDOOR_CONTROLS_PATH',repr(str(controls)))
 text=text[:a]+replacement+text[z:]
 anchor='    restoration_phase=\'approach\'';assert text.count(anchor)==1
 text=text.replace(anchor,anchor+"\n    matrix_entered_frame=None;matrix_counts={};matrix_controls_sha=None;matrix_indoor_points=[];matrix_indoor_index=0;matrix_control_history=[]")
 a=text.index('            if deck_trial_start is not None:\n');z=text.index('            core.retro_run()',a);text=text[:a]+text[z:]
 a=text.index('            if deck_trial_start is None and outdoor_hold>=120');z=text.index('        if DSP_owner:',a)
 stop='''            if row['player_mode_word']==2 and row['scene_word']==268:
                if matrix_entered_frame is None:
                    matrix_entered_frame=current_frame;(out/'RAM-indoor-entry.bin').write_bytes(ram)
                if i%60==0:
                    temp=out/'RAM-indoor-latest.tmp';temp.write_bytes(ram);temp.replace(out/'RAM-indoor-latest.bin')
                    save(out/'indoor-observation.json',dict(frame=current_frame,scene=268,player_X=row['raw_player_X'],player_Z=row['raw_player_Z'],region=int.from_bytes(ram[0x49c76:0x49c78],'big'),RAM_sha256=hashlib.sha256(ram).hexdigest(),controls_history=matrix_control_history))
            if i%60==0:
                observer.matrix_route_dump.argtypes=[c.c_char_p];observer.matrix_route_dump.restype=c.c_int
                assert observer.matrix_route_dump(str(out/'matrix-route-live.json').encode())==0
                matrix_counts=json.loads((out/'matrix-route-live.json').read_text())
            wanted=matrix_counts.get('original_returns'if MATRIX_CONTROL else'native_returns',0)
            if matrix_entered_frame is not None and current_frame-matrix_entered_frame>=300 and wanted>0 and observer.observer_quiescent():break
            if current_frame>=args.frames-512 and observer.observer_quiescent():break
'''.replace('MATRIX_CONTROL',repr(args.control))
 text=text[:a]+stop+text[z:]
 anchor="        report['ordinary_Deck_input_trial']=";a=text.index(anchor);z=text.index('\n',a)
 text=text[:a]+"        observer.matrix_route_dump.argtypes=[c.c_char_p];observer.matrix_route_dump.restype=c.c_int\n        assert observer.matrix_route_dump(str(out/'matrix-route-observation.json').encode())==0\n        report['matrix_route_trial']=dict(target=268,entered_frame=matrix_entered_frame,controls_history=matrix_control_history,ordinary_pad_only=True,guest_RAM_writes=0,source_plan="+repr(str(planp))+")\n"+text[z:]
 probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
 command=list(job['command']);command[2]=str(probe);command[command.index('--navigate-waypoints')+1]=str(planp);command[command.index('--frames')+1]='40000';command[command.index('--stop-after-scene-change')+1]='0';command[command.index('--output')+1]=str(out/'measurement')
 for flag in ['--post-scene-navigate-actor','--post-scene-navigation-offset','--post-scene-waypoints']:
  index=command.index(flag);del command[index:index+2]
 state=dict(status='running_fresh_matrix_route',directory=str(out),pid=os.getpid(),child_pid=None,lane=lane,command=command,indoor_controls=str(controls),new_predictions=0,new_training=False,guest_RAM_writes=0,snapshot_restores=0,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,jp,qp,planp,old/'observer.c',old/'probe.py',watch,source,lib,probe,direction]})
 pointer=V/f'record-matrix-268-fresh-{lane}-current.json'
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark()
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait(timeout=900)
  state['child_pid']=None;state['exit_code']=code;state['report']=str(out/'measurement/report.json');assert code==0,(out/'runtime.log').read_text()[-3000:]
  report=read(state['report']);obs=read(out/'measurement/matrix-route-observation.json');assert obs['errors']==obs['pending']==0,obs
  observations={name:read(out/'measurement'/(name+'-observation.json'))for name in ['gameplay','shared','face','geometry','outer','reset','rotation','clear','display','records']}
  faults={name:{key:value for key,value in row.items()if isinstance(value,(int,float))and any(tag in key.lower()for tag in ['errors','pending','outside','corruption','collision'])}for name,row in observations.items()}
  assert not any(value for row in faults.values()for value in row.values()),faults
  assert observations['records']['matrix_entries']==observations['records']['matrix_returns']==obs['native_entries']==obs['native_returns']
  state['observations']=observations;state['all_monitors_clear_and_quiescent']=True
  wanted=obs['original_returns'if args.control else'native_returns'];state.update(status='terminal_fresh_matrix_route_coverage_pass_pending_review'if report['matrix_route_trial']['entered_frame']is not None and wanted>0 else'terminal_fresh_matrix_route_coverage_missing',frames=len(report['frames']),matrix_observation=obs,entered_frame=report['matrix_route_trial']['entered_frame']);mark();print(state['status'],obs,flush=True)
 except BaseException as error:state.update(status='observation_timeout_child_may_be_live'if isinstance(error,subprocess.TimeoutExpired)else'terminal_matrix_route_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
