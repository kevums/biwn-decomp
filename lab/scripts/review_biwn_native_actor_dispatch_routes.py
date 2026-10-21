"""Review source, local trial and fresh same-layout actor-dispatch native pair."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 bp=V/'native-actor-dispatch-disc-build-current.json';build=read(bp);component=read(build['component_gate']);selected=read(V/'native-actor-dispatch-selected-current.json');model=read(V/'local-native-actor-dispatch-current.json');monitor=read(V/'native-actor-dispatch-monitor-current.json');negative=read(V/'native-actor-dispatch-negatives-current.json');pair=[];paths=[bp,Path(__file__),Path(build['component_gate']),V/'native-actor-dispatch-selected-current.json',V/'local-native-actor-dispatch-current.json',V/'native-actor-dispatch-monitor-current.json',V/'native-actor-dispatch-negatives-current.json',V/'local-actor-dispatch-diagnostic-current.json',V/'actor-dispatch-repair-example-current.json']
 assert build['linked_component_bytes']==19460 and build['semantic_code_bytes']==572 and build['entry_cases']==96 and component['cases']==856 and len(component['original_sites'])==38
 assert monitor['original_cases']==monitor['compiled_cases']==856 and len(monitor['negative_controls'])==2 and len(negative['controls'])==2
 assert model['actual_predictions']==2 and not model['raw_candidate_gate_pass']and not selected['raw_local_accepted']
 for kind in ['candidate','control']:
  p=V/f'native-actor-dispatch-{kind}-current.json';s=read(p);assert s['status']=='terminal_native_actor_dispatch_route_pending_review'and s['exit_code']==0 and s['returned_outdoors']and s['live_monitor_pass']and s['actor_dispatch_monitor_pass']
  folder=Path(s['directory'])/'candidate';report=read(folder/'report.json');o=read(folder/'gameplay-observation.json');assert o==s['observations']
  assert o['ad_entries']==o['ad_returns']==o['ad_child_entries']==o['ad_child_returns']==13 and o['ad_actor']==12 and o['ad_sprite']==1 and o['ad_full']==0
  assert o['ad_errors']==o['ad_pending']==o['ad_stack_outside']==0
  assert (o['ad_native_entries'],o['ad_old_steps'])==((13,0)if kind=='candidate'else(0,425))
  assert o['interior_kind_entries']==[14,1]and o['interior_kind_successes']==[14,0]and o['interior_kind_failures']==[0,1]
  assert report['C_CPU_backend']['stats']['errors']==0
  assert report['frames'][-1]['navigation']['outdoor_hold']>=120 and report['frames'][-1]['floor_word']==0 and report['frames'][-1]['player_mode_word']==1
  assert sha(folder/'report.json')==s['report_sha256']
  paths += [p,folder/'report.json',folder/'gameplay-observation.json',folder/'frontend-PCM.s16le',Path(s['directory'])/'protocol.json']
  pair.append((s,report,o,folder))
 left,right=[x[1]['frames']for x in pair];assert len(left)==24983 and len(right)==24996
 assert [x['frame']for x in left]==list(range(1,24984))and [x['frame']for x in right]==list(range(1,24997))
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];differences={k:sum(a[k]!=b[k]for a,b in zip(left,right))for k in fields}
 pcm=[x[3]/'frontend-PCM.s16le'for x in pair];pcm_equal=sha(pcm[0])==sha(pcm[1]);assert not pcm_equal and [p.stat().st_size for p in pcm]==[79945600,79987200]
 delta=pair[1][0]['control_delta'];assert delta['restored_entries']==['13ae0']and delta['declared_bytes']==8
 assert pair[0][1]['disc_sha256']==build['derived_disc_sha256']and pair[1][1]['disc_sha256']==delta['control_sha256']
 out=V/'native-actor-dispatch-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(p,digest=None):
  p=Path(p).resolve();h=sha(p);assert digest is None or h==digest,p
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target);p=target
  deps[str(p)]=h
 for obj in [build,component,monitor,negative,*[x[0]for x in pair],read(V/'actor-dispatch-repair-example-current.json')]:
  for p,h in obj.get('source_sha256',{}).items():bind(p,h)
 for p in paths:bind(p)
 run=Path(model['directory']);paths2=[run/'frozen-request.json',run/'author.json',run/'reviewer-request.json',run/'reviewer.json',run/'response.txt',run/'prompts-and-responses.txt',Path(model['candidate'])]
 for p in paths2:bind(p)
 report=ROOT/'reports/native-actor-dispatch-development-and-live.txt';assert not report.exists()
 report.write_text('''BIWN — ORIGINAL-ABI13AE0DISPATCHER, EXPERIMENTAL19460BYTE DISC

Coordinator native C dispatcher plus original-facing adapter:572bytes,856full
CPU/SR/bank/public2MBRAM/ordered-bus cases, all38original dispatcher instruction
sites. Actual original134DC/137E0children execute; four leaf services remain
prescribed in the component fixtures. Child-entry fullD/A/SR/bank/SP and packed
argument bytes match. Root saves/restoresD2-D5 and preserves actual child outputs.
No-body and wrong child-X seeded defects are rejected; the X control specifically
passes the Unicorn bus/register comparison but fails retained-native childSR.

Final address163788passes all856cases with preceding compiled parent functions
installed;96stage-loader/startup cases pass. The18888byte parent prefix,20480
reserve and heapfloor163DC0are unchanged. New resident size19460,1020spare.
Only13AE0entry and appended code are patched; original disc remains untouched.
The separate3384byte whole actor-group C-ABI component is not inserted here.

A read-only stable-entry oracle was qualified on856original+856compiled cases,
with corrupted returnD0 and childX callback negatives and watched-boundary RAM
immutability checks. It predicts root dispatch/child-entry state, then captures
actual child outputs to predict root return. It does not reimplement children.
The fixture task-ID adapter changes association only; actual gameplay readsC0920.

FRESH GAMEPLAY — REAL CHILDREN AND EXTERNAL HELPERS
Compiled candidate24983frames; control24996. Both return outdoors and hold120
frames. Control restores only the8bytes of original13AE0entry, retaining all
prior compiled functions, identical resident layout and unused new code.
Both dispatch13calls:12actor routes,1sprite route,0exhausted pools. Every child
entry/return and root return matches its read-only ABI contract; no pending,
monitor or task-stack-outside errors. Candidate executes13native entries and
zero original dispatcher body steps; control executes425original body steps.
Candidate max private depth328bytes/minimum454task-stack bytes of headroom;
control194/606. Full-pool live coverage remains component-only.

The256byte private-gap adapter places its72byte context between rootSP-272and
rootSP-200. The control's observed194byte descendant depth leaves only6bytes
of clearance to that context boundary in these observed paths. This is a
layout-derived estimate, not a general bound on descendant stack use. Broader
helper paths and a larger private-gap variant need evaluation before default
promotion. No stack collision is reported in the actual13compiled calls.

Fresh aligned prefix24983frames differs in21146CPU,24972RAMhash,24518GPU,
9112DSP,17515video,19197navigation,234locomotion and347held-button records.
Captured PCM differs in hash and length79945600versus79987200bytes. Functional
route completion and ABI agreement do not establish timing/media/full-state
equivalence. Historical comparisons printed by the runner are distinct from
this fresh pair. Prior interior selectors again cover14actor successes and1
sprite skipped failure; other paths remain component-only. The old scanner's
media/state limits remain. Retained native emulator processors/platform services
execute both routes. No new strict-C processor test applies to this19460disc.

LOCAL MODEL / TRAINING
Two actual local27Bpredictions: Author62.01seconds, same-weight Reviewer8.38.
Raw candidate fails Werror on an unused variable; Reviewer identifies that
compiler defect. A separate diagnostic removes exactly that declaration, then
fails native childSR(expected4,actual0). Additional source findings include
incorrectXmask0200, incorrectNZexpression2fornonzero, full32bitD1comparison and
highWORDloss on exhaustion. Neither raw nor diagnostic code is accepted; no
local body is adopted. A setup-only missing-sampling failure made0predictions
and remains archived. The selected body, header, adapter, fixtures, monitor,
layout and integration are coordinator work. Prior accepted local functions
retain their separate attribution. No new logical-function recovery is counted.
One verified development SFT repair example is prepared, with exposure labels;
no optimizer step/new weight occurred. Exact prompts/responses: StartLocalAI→I.

STATUS
Experimental19460disc is built and live-tested but not selected as the published
or default preview build. Published18888disc's separate strict-C processor test
now independently matches24996frames/eightfields/fullPCM/fullobserver; that is
not a19460verdict. Current nativeChat inspection timed out again; local SDK works.
Full readable game/original-console reconstruction, broader paths/timing/media,
LM Studio Chat usability, Advertising reliability and full migration remain open.
''')
 bind(report)
 record=dict(status='terminal_native_actor_dispatch_component_and_two_routes_reviewed',directory=str(out),report=str(report),build=str(bp),build_sha256=sha(bp),resident_bytes=19460,native_bytes=572,component_cases=856,original_sites=38,startup_cases=96,monitor_fixture_cases=1712,actor_routed_calls=12,sprite_routed_calls=1,full_pool_live_calls=0,candidate_frames=len(left),control_frames=len(right),compared_prefix_frames=len(left),same_layout_differences=differences,PCM_equal=False,PCM_bytes=[p.stat().st_size for p in pcm],live_monitor_pass=True,candidate_observations=pair[0][2],control_observations=pair[1][2],observed_candidate_depth=328,minimum_candidate_task_headroom=454,private_gap=256,context_boundary_below_root=200,control_descendant_depth=194,estimated_observed_clearance_to_context=6,default_promoted=False,published_as_latest=False,raw_local_output_accepted=False,actual_local_predictions=2,new_training=False,new_logical_functions=0,native_Chat_verified=False,dependencies_sha256=deps,pointer_snapshots=aliases,whole_game_complete=False)
 (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(V/'native-actor-dispatch-reviewed-current.json').write_bytes((out/'protocol.json').read_bytes());print(json.dumps({k:record[k]for k in ['status','resident_bytes','candidate_frames','control_frames','live_monitor_pass','PCM_equal','report']}))

if __name__=='__main__':main()
