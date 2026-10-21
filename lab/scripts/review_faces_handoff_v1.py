"""Verify trace nonintrusion and localize the final inventory-selection difference."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 out=V/'faces-handoff-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 build=read(V/'native-Deck-faces-disc-build-v1-current.json');facts={};bound=[Path(__file__),V/'native-Deck-faces-disc-build-v1-current.json'];images=[]
 for lane in ['candidate','control']:
  p=V/f'native-Deck-faces-handoff-v1-{lane}-current.json';job=read(p);assert job['status']=='terminal_fresh_faces_handoff_route_pending_review'
  for file,h in job['source_sha256'].items():assert sha(file)==h,file
  basep=V/f'native-Deck-faces-geometry-v1-{lane}-current.json';base=read(basep);a=read(job['report']);b=read(base['report']);assert a['frames']==b['frames']and len(a['frames'])==24967,'Trace changed recorded execution'
  assert not job['snapshot_restores']and not job['host_guest_RAM_writes']and not job['host_CPU_or_task_seeds']
  folder=Path(job['report']).parent;tracep=folder/'handoff-observation.json';trace=read(tracep);assert trace['overflow']==0
  start=a['ordinary_Deck_input_trial']['start_frame'];rows=[x for x in trace['events']if x['frame']>=start]
  returns=[x for x in rows if x['pc']==build['outer_symbols']['biwn_outer_return']];assert len(returns)==1
  after=[x for x in rows if x['pc']==0x1a1f0 and x['frame']>=returns[0]['frame']];assert after
  zero=[x for x in rows if x['pc']and x['held']&16]
  changes=[];last=None
  for row in rows:
   key=(row['inventory_start'],row['inventory_selected'],row['Deck_mode'])
   if key!=last:changes.append(dict(offset=row['frame']-start,pc=hex(row['pc']),held=row['held'],inventory_start=key[0],inventory_selected=key[1],Deck_mode=key[2]));last=key
  ram=(folder/'RAM-final.bin').read_bytes();facts[lane]=dict(frames=len(a['frames']),nonintrusion_recorded_frames=len(a['frames']),trace_events=len(trace['events']),outer_return_offset=returns[0]['frame']-start,first_inventory_handler_after_return_offset=after[0]['frame']-start,inventory_handler_zero_events=[dict(x,offset=x['frame']-start)for x in zero],state_changes=changes,final_inventory_start=int.from_bytes(ram[0x49d54:0x49d56],'big'),final_inventory_selected=int.from_bytes(ram[0x49d56:0x49d58],'big'),final_player_X=a['frames'][-1]['raw_player_X'],final_player_Z=a['frames'][-1]['raw_player_Z'])
  images.append(folder/'original-emulator-final-frame.png');bound.extend([p,basep,Path(job['report']),Path(base['report']),tracep,folder/'RAM-final.bin',images[-1]])
 assert facts['candidate']['final_inventory_selected']==0 and facts['control']['final_inventory_selected']==9
 assert not facts['candidate']['inventory_handler_zero_events']
 assert any(x['pc']==0x1b718 and x['offset']==226 for x in facts['control']['inventory_handler_zero_events'])
 assert any(x['inventory_selected']==9 and x['offset']==227 for x in facts['control']['state_changes'])
 assert facts['candidate']['final_player_X']==facts['control']['final_player_X']and facts['candidate']['final_player_Z']==facts['control']['final_player_Z']
 a,b=[Image.open(p).convert('RGB')for p in images];diff=ImageChops.difference(a,b);box=diff.getbbox();left,right=a.tobytes(),b.tobytes();pixels=sum(left[i:i+3]!=right[i:i+3]for i in range(0,len(left),3))
 assert box==(228,61,319,216)and pixels==5190
 assert not ImageChops.difference(a.crop((0,40,224,218)),b.crop((0,40,224,218))).getbbox()
 assert not ImageChops.difference(a.crop((0,0,320,61)),b.crop((0,0,320,61))).getbbox()
 source=ROOT/'projects/black-ice-white-noise/restoration/biwn_inventory_select.c';bound.append(source)
 report=ROOT/'reports/Five Helper Inventory Handoff Difference.txt'
 report.write_text('FIVE-HELPER CANDIDATE — INVENTORY HANDOFF DIFFERENCE\n\nThe extra trace left every recorded frame unchanged versus its earlier same-image run:24,967frames in each lane. No trace rows overflowed. Existing acceptance monitors remain byte-identical;the added logger reads RAM/registers and writes only host storage. This proves nonintrusion at the recorded frame boundaries,not arbitrary midframe timing.\n\nThe candidate outer Deck task returns at trial offset '+str(facts['candidate']['outer_return_offset'])+';the original-geometry control returns at '+str(facts['control']['outer_return_offset'])+'. The inventory handler resumes at offsets '+str(facts['candidate']['first_inventory_handler_after_return_offset'])+'and'+str(facts['control']['first_inventory_handler_after_return_offset'])+'respectively. The prescribed keypad0window is225..233. Only the control enters inventory selection with held bit0x10 at226;its digit helper executes and selection changes from0to9at227. The candidate sees no keypad0in that handler and keeps0.\n\nThe existing recovered1A1F0selection block maps keypad0to start slot9. Thus the trace directly explains this final menu difference as input reaching a different context after a different Deck-return schedule. It does not establish that all339differing video frames share this cause,or prove the new candidate faithful. The earlier assumption that keypad0caused both Deck exits was wrong:both outer tasks had already returned.\n\nFinal player coordinates match. The final scene region and top HUD match;all5,190different RGB pixels lie in the right inventory panel,bounding box(228,61)-(319,216). Both images are326x240. Other active-frame render/state/timing differences remain. Do not erase this result by adjusting test inputs or accepting only a matching subregion.\n\nThe installed preview remains unchanged. Next:identify and reduce the new helper path timing difference while preserving complete CPU/RAM/call contracts;then repeat a separately qualified candidate/control comparison. Full game/source/physical/audio/IRQ fidelity remains incomplete.\n')
 bound.append(report);state=dict(status='terminal_readonly_trace_localizes_inventory_context_handoff_difference',directory=str(out),report=str(report),facts=facts,final_image_difference=dict(size=list(a.size),bbox=list(box),different_pixels=pixels,scene_region_equal=True,top_HUD_equal=True),all_recorded_same_image_frames_equal=True,test_inputs_unchanged=True,preview_changed=False,game_fidelity_verified=False,source_sha256={str(p):sha(p)for p in bound})
 save(out/'review.json',state);save(V/'faces-handoff-reviewed-v1-current.json',state);print(out);print({lane:{k:facts[lane][k]for k in ['outer_return_offset','first_inventory_handler_after_return_offset','final_inventory_selected']}for lane in facts})
if __name__=='__main__':main()
