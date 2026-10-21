"""Broader fresh CPU-C comparison using the verified merchant/return policy."""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 pp=ROOT/'verification/native-formatter-C-fresh-pair-current.json';prior=json.loads(pp.read_text());assert prior['status']=='terminal_fresh_C_formatter_pair_equal'
 routep=ROOT/'verification/native-fast-core-wait-format-long-route-current.json';route=json.loads(routep.read_text());route_dir=Path(route['directory']);template=route_dir/'fresh-route.py';assert sha(template)==route['source_sha256'][str(template)]
 oldprobe=Path(prior['directory'])/'probe.py';assert sha(oldprobe)==prior['source_sha256'][str(oldprobe)]
 cp=ROOT/'verification/native-formatter-C-bridge-current.json';candidate=json.loads(cp.read_text());assert prior['CPU_bridge_proof_sha256']==sha(cp)
 out=ROOT/'verification/native-formatter-C-merchant-pair'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 # Reuse exactly the checked C gateway and CPU/state readers. It becomes
 # active only at4000 and does not seed any game state.
 text=template.read_text();old=oldprobe.read_text();a=old.index('        import biwn_fast_CPU_bridge as CPU_bridge');b=old.index('        rom =',a);install=old[a:b]
 a=text.index('        observer=c.CDLL(');b=text.index('        core.BIWNSetCPUExecOwner(native_observer,0)',a)+len('        core.BIWNSetCPUExecOwner(native_observer,0)');text=text[:a]+install+text[b:]
 text=text.replace('            observer.set_frame(current_frame)\n','')
 a=text.index('        observer.finish_observe.argtypes=');b=text.index("        report.update(status='terminal_fresh_libretro_CD_probe'",a)
 finish=old[old.index('        stats=finish_CPU()'):old.index("        report.update(status='terminal_fresh_libretro_CD_probe'")]
 finish+="        report['source_C_execution']=args.CPU_mode=='C'\n"
 text=text[:a]+finish+text[b:]
 marker='    args = parser.parse_args()';assert text.count(marker)==1;text=text.replace(marker,"    parser.add_argument('--CPU-mode',choices=['reference','C'],required=True)\n"+marker)
 marker="                       stage_sha256=hashlib.sha256(ram[0x4000:0x100000]).hexdigest())";assert text.count(marker)==1
 added="                       CPU_full=full_CPU(),\n                       full_RAM_sha256=hashlib.sha256(ram).hexdigest(),\n                       full_GPU_state_sha256=processor_digest('GPU'),\n                       full_DSP_state_sha256=processor_digest('DSP'),\n"
 text=text.replace(marker,added+marker);probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
 original=next(row['command']for row in route['commands']if row['lane']=='fast');commands=[]
 for lane in ['reference','C']:
  cmd=list(original);cmd[2]=str(probe);cmd[cmd.index('--output')+1]=str(out/lane);cmd+=['--CPU-mode',lane];commands.append((lane,cmd))
 state=dict(status='running_fresh_C_merchant_and_return_pair',pid=os.getpid(),directory=str(out),commands=[],source_route=str(routep),source_route_sha256=sha(routep),CPU_bridge_proof=str(cp),CPU_bridge_proof_sha256=sha(cp),source_sha256={str(p):sha(p)for p in [Path(__file__),pp,routep,template,oldprobe,cp,probe]},maximum_frames=35000,checkpoint_restores=0,host_guest_RAM_writes=0,adaptive_controller=True,identical_input_claim_requires_runtime_comparison=True,new_training=False,default_promoted=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-formatter-C-merchant-pair-active.json',state)
 mark();children=[]
 try:
  for lane,cmd in commands:
   log=(out/(lane+'.log')).open('w');child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=cmd));mark()
  codes={}
  for lane,child,log in children:codes[lane]=child.wait();log.close()
  state['exit_codes']=codes
  if any(codes.values()):state['status']='terminal_C_merchant_child_rejected';mark();print(json.dumps(codes),flush=True);return
  reports={lane:json.loads((out/lane/'report.json').read_text())for lane in ['reference','C']};rows={lane:value['frames']for lane,value in reports.items()};assert len(rows['C'])==len(rows['reference'])
  fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation'];comp={field:dict(different_frames=sum(a[field]!=b[field]for a,b in zip(rows['reference'],rows['C'])),first_different_frame=next((a['frame']for a,b in zip(rows['reference'],rows['C'])if a[field]!=b[field]),None))for field in fields}
  backend=reports['C']['C_CPU_backend'];assert backend['stats']['errors']==0 and backend['counts']['Original']==0 and backend['counts']['Rejected']==0
  results={}
  for lane,data in rows.items():
   last=data[-1];assert not any(int(row['CPU'],16)&1 for row in data)
   merchant=any(row['player_mode_word']==2 and row['floor_word']==2 and row['scene_word']==314 and abs(row['raw_player_X']-12832)<=16 and abs(row['raw_player_Z']-42385)<=16 for row in data);hold=(last.get('navigation')or{}).get('outdoor_hold',0)
   assert merchant and last['player_mode_word']==1 and last['floor_word']==0 and hold>=120
   results[lane]=dict(frames=len(data),merchant_reached=merchant,outdoor_hold=hold,final_X=last['raw_player_X'],final_Z=last['raw_player_Z'],nonzero_audio_samples=reports[lane]['audio']['nonzero_samples'])
  state.update(status='terminal_fresh_C_merchant_pair_equal'if not any(v['different_frames']for v in comp.values())else'terminal_fresh_C_merchant_pair_diverged',comparisons=comp,results=results,C_backend=backend,audio_PCM_equal=sha(out/'reference/frontend-PCM.s16le')==sha(out/'C/frontend-PCM.s16le'),report_sha256={lane:sha(out/lane/'report.json')for lane in reports},C_original_opcode_fallback_after_4000=0)
  mark();save(ROOT/'verification/native-formatter-C-merchant-pair-current.json',state);print(json.dumps(dict(status=state['status'],comparisons=comp,results=results,C_backend=backend),indent=2),flush=True)
 except BaseException as error:state.update(status='terminal_C_merchant_driver_rejected',error=repr(error));mark();raise
if __name__=='__main__':main()
