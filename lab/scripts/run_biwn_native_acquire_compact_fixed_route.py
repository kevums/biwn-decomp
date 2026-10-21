"""Fresh native23/native26 ordinary-pad replay from actual native23 inputs.
No checkpoint, state transplant, guest writes or adaptive steering in either run.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,argparse
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--prepared-route',type=Path);args=parser.parse_args()
 rp=args.prepared_route or ROOT/'verification/native-acquire-compact-route-current.json';route=json.loads(rp.read_text());assert route['status']=='terminal_fresh_native26_native27compact_acquire_routes_classified'or(args.prepared_route and route['status']=='running_fresh_native26_native27compact_acquire_routes')
 directory=Path(route['directory']);template=directory/'fresh-acquire-route.py';observer=directory/'libacquire-observer.dylib'
 for p in [template,observer]:assert sha(p)==route['source_sha256'][str(p)]
 bp=Path(route['build_proof']);oldbp=Path(route['baseline_build_proof']);new=json.loads(bp.read_text());old=json.loads(oldbp.read_text())
 assert sha(bp)==route['build_proof_sha256']and sha(oldbp)==route['baseline_build_proof_sha256']
 lanes={'native26_fixed':old,'native27compact_fixed':new}
 for b in lanes.values():assert sha(b['derived_disc'])==b['derived_disc_sha256']and sha(b['component'])==b['component_sha256']
 prior_fixed_path=ROOT/'verification/native-resource-fixed-route-current.json';prior_fixed=json.loads(prior_fixed_path.read_text());prior_directory=Path(prior_fixed['directory']);prior_inputs=json.loads((prior_directory/'recorded-controller-input.json').read_text())
 source_report=Path(prior_inputs['source_report']);assert sha(source_report)==prior_inputs['source_report_sha256'];rows=json.loads(source_report.read_text())['frames'];frames=prior_fixed['frames'];assert len(rows)==frames==29783
 from biwn_controller import JOYPAD_BUTTONS
 masks=[];windows=[];start=1;prior=None
 for frame,row in enumerate(rows,1):
  assert row['frame']==frame;names=sorted((row.get('navigation')or{}).get('buttons',[]));assert all(n in JOYPAD_BUTTONS for n in names)
  masks.append(sum(1<<JOYPAD_BUTTONS[n]for n in names))
  if names!=prior:
   if prior is not None:windows.append(dict(start_frame=start,stop_frame=frame,buttons=prior))
   start=frame;prior=names
 windows.append(dict(start_frame=start,stop_frame=frames+1,buttons=prior))
 out=ROOT/'verification/native-acquire-compact-fixed-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 route_snapshot=out/'source-route-preparation-snapshot.json';save(route_snapshot,route);rp=route_snapshot
 inputs=out/'recorded-controller-input.json';save(inputs,dict(windows=windows,provenance='Actual per-frame normal pad buttons from prior native23 adaptive route; no navigation in new runs.',source_report=str(source_report),source_report_sha256=sha(source_report)))
 source=template.read_text()
 needle="    core_path = args.core or ROOT / 'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'";assert source.count(needle)==1
 source=source.replace(needle,"""    fixed_input_ids=[set()for _ in range(args.frames+1)]
    for window in input_windows:
        for frame in range(window['start_frame'],window['stop_frame']):fixed_input_ids[frame].update(window['ids'])
"""+needle)
 needle="            pressed = port == 0 and device == 1 and index == 0 and any(\n                w['start_frame'] <= current_frame < w['stop_frame'] and button in w['ids']\n                for w in input_windows)";assert source.count(needle)==1
 source=source.replace(needle,"            pressed = port == 0 and device == 1 and index == 0 and button in fixed_input_ids[current_frame]")
 source=source.replace('    navigation = None','    input_seen_mask=0;input_pressed_mask=0\n    navigation = None',1)
 source=source.replace('        nonlocal input_sample_count','        nonlocal input_sample_count,input_seen_mask,input_pressed_mask',1)
 needle='        if pressed:\n            pressed_input_samples';assert source.count(needle)==1
 source=source.replace(needle,"        if port==0 and device==1 and index==0 and 0<=button<32:\n            input_seen_mask|=1<<button\n            if pressed:input_pressed_mask|=1<<button\n"+needle)
 needle='            core.retro_run()';assert source.count(needle)==1
 source=source.replace(needle,'            input_seen_mask=0;input_pressed_mask=0\n'+needle)
 needle='                       navigation=navigation,';assert source.count(needle)==1
 source=source.replace(needle,needle+"\n                       fixed_buttons=sorted(name for name,button in button_ids.items()if button in fixed_input_ids[current_frame]),\n                       input_seen_mask=input_seen_mask,input_pressed_mask=input_pressed_mask,")
 probe=out/'fresh-fixed-free-route.py';probe.write_text(source);compile(source,str(probe),'exec')
 core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';assert sha(core)==route['source_sha256'][str(core)]
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames=frames,source_route_proof=str(rp),source_route_proof_sha256=sha(rp),prior_fixed_proof=str(prior_fixed_path),prior_fixed_proof_sha256=sha(prior_fixed_path),build_proofs={str(p):sha(p)for p in [bp,oldbp]},commands=[],source_sha256={str(p):sha(p)for p in [Path(__file__),template,probe,observer,inputs,source_report,core,ROOT/'scripts/biwn_controller.py']},checkpoint_restores=0,host_guest_RAM_writes=0,host_CPU_seeds=0,adaptive_navigation=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-acquire-compact-fixed-route-active.json',state)
 mark();children=[]
 try:
  for lane,b in lanes.items():
   command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames',str(frames),'--core',str(core),'--disc',b['derived_disc'],'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
   log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
  state['status']='running_equal_duration_fixed_pad_pair';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
  for lane,child,log in children:codes[lane]=child.wait();log.close()
  state['exit_codes']=codes;assert not any(codes.values()),codes;results={};raw={}
  for lane,_,_ in children:
   report=json.loads((out/lane/'report.json').read_text());assert report['executed_frames']==frames and report['frame_controller_script']==str(inputs)and not report['navigation_waypoints'];actual=report['frames'];assert len(actual)==frames
   assert all(x['input_pressed_mask']==(mask&x['input_seen_mask'])for x,mask in zip(actual,masks))
   assert all(x['navigation']is None for x in actual)
   obs=json.loads((out/lane/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);raw[lane]=actual
   results[lane]=dict(executed_frames=frames,nonzero_audio_samples=report['audio']['nonzero_samples'],audio_stereo_frames=report['audio']['frames'],final_fields={k:actual[-1][k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},observation=obs,report_sha256=sha(out/lane/'report.json'),all_actual_pad_callbacks_match_declared_schedule=True)
  excluded={'navigation','fixed_buttons','input_seen_mask','input_pressed_mask'};same=lambda x:{k:v for k,v in x.items()if k not in excluded}
  previous_rows=json.loads((prior_directory/'native26_fixed/report.json').read_text())['frames']
  baseline_different=sum(same(x)!=same(y)for x,y in zip(previous_rows,raw['native26_fixed']));baseline_PCM_equal=sha(prior_directory/'native26_fixed/frontend-PCM.s16le')==sha(out/'native26_fixed/frontend-PCM.s16le')
  state.update(status='terminal_equal_duration_fixed_pad_pair_pending_analysis',results=results,native26_prior_game_rows_different=baseline_different,native26_prior_PCM_equal=baseline_PCM_equal,finished_at=datetime.now(timezone.utc).isoformat(),scope='Native26/27CDI profiles fresh-load/HLE in same retained core with identical per-frame recordedpad masks for29783frames. Actual input callbacks checked. Original engine/GPU/DSP/CD/devices remain; no guest state intervention or source execution owner. Baseline repeat and cross-profile video/audio/state require separate analysis; fixed-input does not imply deterministic equivalence.')
  mark();save(ROOT/'verification/native-acquire-compact-fixed-route-current.json',state);print(state['status'],'baseline differing rows',baseline_different,'PCM equal',baseline_PCM_equal,flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
