"""Review the fresh23260disc/control, full component matrix and unchanged parent."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-sprite-create-disc-build-current.json';build=read(bp);assert build['linked_component_bytes']==23260 and build['component_bytes']==24512 and build['heap_start']==0x164d80
 parent=read(build['parent_build']);assert Path(build['linked_component']).read_bytes()[:21080]==Path(parent['linked_component']).read_bytes();assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
 names=['native-sprite-create-linked-current.json','native-actor-triple-current.json','native-sprite-create-negatives-current.json','sprite-create-final-startup-current.json','sprite-create-live-contexts-current.json'];gates={n:read(v/n)for n in names};component=gates[names[0]];joint=gates[names[1]];negative=gates[names[2]];startup=gates[names[3]];contexts=gates[names[4]]
 assert component['cases']==1228 and component['binary_bytes']==2180 and component['code_address']==0x164018 and joint['cases']==2084 and joint['max_private_depth']==630
 assert len(negative['controls'])==4 and all(x['rejected']for x in negative['controls'])and startup['cases']==96 and startup['payload_bytes']==23260
 assert contexts['status']=='terminal_final_three_roots_and_context_canaries_pass'and contexts['completed']==8672 and len(contexts['negative_controls'])==5
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);sites=set()
 for lo,hi in [(0x137e0,0x138bc),(0x13902,0x13ae0)]:
  ins=list(md.disasm(baseline[lo:hi],lo));assert ins[-1].address+ins[-1].size==hi;sites.update(x.address for x in ins)
 assert sites==set(component['original_sites'])and len(sites)==184
 pair=[]
 for kind in ['candidate','control']:
  p=v/f'native-sprite-create-{kind}-current.json';s=read(p);assert s['status']=='terminal_native_sprite_create_route_pending_review'and s['exit_code']==0 and s['returned_outdoors']and s['live_monitor_pass']and s['sprite_create_monitor_pass'],(kind,s.get('status'),s.get('live_monitor_pass'))
  o=s['observations'];assert o['ad_entries']==o['ad_returns']==13 and o['ad_actor']==12 and o['ad_sprite']==1 and o['ai_entries']==o['ai_returns']==12 and o['sc_entries']==o['sc_returns']==1
  assert o['ad_context_checks']==13 and o['ai_context_checks']==16 and o['sc_context_checks']==(o['sc_helper_entries']if kind=='candidate'else 0)
  assert o['ai_native_entries']==12 and o['ai_old_steps']==0
  assert o['sc_native_entries']==(1 if kind=='candidate'else 0)and(o['sc_old_steps']==0 if kind=='candidate'else o['sc_old_steps']>0)
  assert o['sc_position_calls']==o['sc_allocate_calls']==o['sc_decode_calls']==1
  for key in ['errors','copy_errors','acquire_monitor_errors','acquire_pending','acquire_user_stack_outside','geometry_errors','geometry_pending','geometry_stack_outside','select_errors','select_pending','select_stack_outside','scan_errors','scan_pending','scan_stack_outside','door_errors','door_pending','door_stack_outside','interior_errors','interior_pending','interior_stack_outside','leaf_pending','heap_floor_errors','ad_errors','ad_pending','ad_context_collisions','ad_context_SP_inside','ad_stack_outside','ai_errors','ai_pending','ai_context_corruptions','ai_stack_outside','sc_errors','sc_pending','sc_context_corruptions','sc_stack_outside']:assert o[key]==0,(kind,key,o[key])
  assert o['sc_helper_entries']==o['sc_helper_returns']and o['heap_base']==0x164d80 and o['heap_inits']>0
  folder=Path(s['directory'])/'candidate';report=read(folder/'report.json');assert sha(folder/'report.json')==s['report_sha256']and read(folder/'gameplay-observation.json')==o
  assert report['C_CPU_backend']['stats']['errors']==0 and report['frames'][-1]['player_mode_word']==1 and report['frames'][-1]['floor_word']==0 and report['frames'][-1]['navigation']['outdoor_hold']>=120
  assert [x['frame']for x in report['frames']]==list(range(1,len(report['frames'])+1));pair.append((s,report,folder))
 delta=pair[1][0]['control_delta'];assert delta['restored_entries']==['137e0']and delta['declared_bytes']==8
 assert pair[0][1]['disc_sha256']==build['derived_disc_sha256']and pair[1][1]['disc_sha256']==delta['control_sha256']
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];diff={k:sum(a[k]!=b[k]for a,b in zip(pair[0][1]['frames'],pair[1][1]['frames']))for k in fields};frames=[len(x[1]['frames'])for x in pair];pcm=[x[2]/'frontend-PCM.s16le'for x in pair];PCM_equal=sha(pcm[0])==sha(pcm[1]);PCM_bytes=[p.stat().st_size for p in pcm]
 out=v/'sprite-create-integration-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(path,h=None):
  p=Path(path).resolve();actual=sha(p);assert h is None or h==actual,p
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target);p=target
  deps[str(p)]=actual
 for obj in [build,*gates.values(),*[x[0]for x in pair]]:
  for p,h in obj.get('source_sha256',{}).items():bind(p,h)
 for p in [Path(__file__),bp,*[v/n for n in names],v/'native-sprite-create-candidate-current.json',v/'native-sprite-create-control-current.json']:bind(p)
 for _,_,folder in pair:
  for name in ['report.json','frontend-PCM.s16le','gameplay-observation.json']:bind(folder/name)
 co=pair[0][0]['observations'];ctrl=pair[1][0]['observations'];report=out/'review.txt'
 text=f'''BIWN: native sprite creator 137E0 integrated into experimental disc

The coordinator's readable C routine and original-facing ABI compile to 2,180 bytes at 0x164018. The resident payload is 23,260 bytes in the unchanged 24,512-byte reservation, with 1,252 bytes free. Heap floor 0x164D80 and initial capacity 373,376 are unchanged. The parent's first 21,080 resident bytes remain identical. The original disc is unchanged. The new clone changes {build['delta_CDI_changed_bytes']} actual bytes in declared new-code/entry regions.

The sprite component passes 1,228 original-versus-C cases at the final address, covering all 184 decoded original instruction sites (inline callback table excluded). The three reconstructed actor/sprite roots together pass 2,084 dispatcher-rooted cases, maximum private depth 630 bytes. Both lanes retain common parent compiled position helpers; four other leaf services are prescribed. Native CPU replay checks full returned registers, SR and register banks, actual helper-entry CPU/SR/SP/arguments, public 2MB RAM and ordered public accesses. Selected changing handle rereads are included, not arbitrary concurrency or modified jump tables.

Four seeded missing-body, wrong-callback, wrong-helper-X and original-body-delegation defects are rejected. All 96 complete-payload startup cases pass. Read-only context monitors pass 8,672 root executions: 2,084 dispatcher, 1,024 initializer and 1,228 sprite cases, original and C each. Five decoded-CPU/mirror-only corruption controls reject. Root/callee/packed arguments and actual helper SP are checked; the decoder's leftover fourth stack argument must retain the allocator request. Actual fixture/native RAM is unchanged by the monitor. This is finite component coverage, not live resource decoding or a general task-stack bound.

Fresh gameplay candidate {frames[0]} frames; same-layout control {frames[1]} frames. Both return outdoors and hold 120 frames. Only the eight-byte 137E0 entry redirect is restored in the control. Both retain native 13AE0/134DC, the new unused code, enlarged reservation and previous functions. Candidate executes one native sprite call and zero original sprite-body instructions; control executes {ctrl['sc_old_steps']} original-body instructions. Each calls real 105DA position, 152A2 allocation and E2B8 decode once. Candidate checks {co['sc_context_checks']} saved sprite contexts, plus 13 parent and 16 initializer contexts. All context, ABI, task-boundary and inherited geometry/resource/cache/heap/door/selector monitors pass. Observed dispatcher nested depth {co['ad_max_depth']} / minimum headroom {co['ad_min_headroom']}; sprite depth {co['sc_max_depth']} / minimum headroom {co['sc_min_headroom']}. These are observed paths, not universal bounds.

Fresh aligned-prefix frame differences: {json.dumps(diff)}. PCM equality {PCM_equal}; sizes {PCM_bytes}. Functional/ABI completion does not imply timing/media/state equivalence. Older scanner/initializer discrepancies remain unresolved even if a field happens to match in this new pair. Live sprite pool exhaustion, animated callback variants/double-object case and other IDs remain component-only. Inherited actor selectors still need their explicitly reported success/failure scope. Retained native emulator CPU/GPU/DSP/IRQ/platform services execute both routes. No new strict C-processor or physical-console proof applies to this disc.

No local model wrote this new routine; source/ABI/fixtures/integration/review are coordinator work. Prior accepted local functions retain their separate attribution. Local status Reader and failed profile trial are separately logged; no new weights or default-profile changes. The interactive preview is unchanged. Full readable game/same-console rebuild, timing/media, broader resources/callbacks/stack paths, native Chat usability, Advertising reliability and complete migration/future256GB preparation remain unfinished.
'''
 report.write_text(text);bind(report)
 record=dict(status='terminal_native_sprite_create_two_routes_reviewed',directory=str(out),report=str(report),build=str(bp),build_sha256=sha(bp),resident_bytes=23260,reservation_bytes=24512,heap_floor='0x164d80',reservation_free=1252,initial_heap_capacity=373376,native_sprite_bytes=2180,component_cases=1228,component_sites=184,triple_cases=2084,context_root_executions=8672,startup_cases=96,candidate_frames=frames[0],control_frames=frames[1],compared_prefix_frames=min(frames),same_layout_differences=diff,PCM_equal=PCM_equal,PCM_bytes=PCM_bytes,live_monitor_pass=True,sprite_live_calls=1,real_sprite_helper_calls=co['sc_helper_entries'],max_nested_private_depth=co['ad_max_depth'],min_task_headroom=co['ad_min_headroom'],candidate_observations=co,control_observations=ctrl,new_training=False,default_promoted=False,native_Chat_verified=False,new_logical_functions=0,whole_game_complete=False,dependencies_sha256=deps,pointer_snapshots=aliases)
 save(out/'protocol.json',record);save(v/'sprite-create-integration-reviewed-current.json',record);print(json.dumps({k:record[k]for k in ['status','resident_bytes','candidate_frames','control_frames','PCM_equal','max_nested_private_depth','min_task_headroom']}))
if __name__=='__main__':main()
