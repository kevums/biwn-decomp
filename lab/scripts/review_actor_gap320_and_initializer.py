"""Review measured capture clearance and next original-ABI source component."""
import hashlib,json,shutil,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);out=V/'actor-gap320-and-initializer-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or h==actual,p
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target);p=target
  deps[str(p)]=actual
 buildp=V/'native-actor-dispatch-gap320-disc-build-current.json';build=read(buildp);component=read(build['component_gate']);monitor=read(V/'native-actor-dispatch-gap320-monitor-current.json');initp=V/'native-actor-initialize-current.json';init=read(initp);jointp=V/'native-actor-dispatch-initialize-joint-current.json';joint=read(jointp);negp=V/'native-actor-initialize-negatives-current.json';neg=read(negp)
 assert component['cases']==856 and component['binary_bytes']==572 and component['max_private_depth']==392 and build['entry_cases']==96 and build['private_gap']==320
 assert monitor['original_cases']==monitor['compiled_cases']==856 and len(monitor['negative_controls'])==3
 assert init['status']=='terminal_original_ABI_actor_initialize_pass'and init['cases']==1024 and init['binary_bytes']==1620 and init['max_private_depth']==564
 assert joint['status']=='terminal_original_ABI_joint_actor_group_pass'and joint['cases']==856 and joint['joint_bytes']==2192 and joint['max_private_depth']==600
 expected={int(x,16)for x in re.findall(r'case 0x([a-f0-9]+)u:',(ROOT/'projects/black-ice-white-noise/restoration/biwn_actor_factory_cpu.c').read_text())if 0x134dc<=int(x,16)<0x137e0};assert expected==set(init['original_sites'])and len(expected)==148
 assert len(neg['controls'])==3
 pair=[];old_pair=[]
 for kind in ['candidate','control']:
  p=V/f'native-actor-dispatch-gap320-{kind}-current.json';s=read(p);assert s['status']=='terminal_native_actor_dispatch_route_pending_review'and s['returned_outdoors']and s['live_monitor_pass']
  o=s['observations'];assert o['ad_entries']==o['ad_returns']==o['ad_child_entries']==o['ad_child_returns']==13 and o['ad_actor']==12 and o['ad_sprite']==1 and o['ad_full']==0
  assert o['ad_max_child_depth']==194 and o['ad_min_context_clearance']==70 and o['ad_context_collisions']==o['ad_errors']==o['ad_pending']==o['ad_stack_outside']==0
  assert o['ad_max_depth']==(392 if kind=='candidate'else 194)and o['ad_min_headroom']==(390 if kind=='candidate'else 606)
  folder=Path(s['directory'])/'candidate';r=read(folder/'report.json');assert sha(folder/'report.json')==s['report_sha256']and read(folder/'gameplay-observation.json')==o
  previous=read(V/f'native-actor-dispatch-{kind}-current.json');old=read(Path(previous['directory'])/'candidate/report.json');old_pair.append((previous,old))
  assert len(r['frames'])==len(old['frames'])==(24983 if kind=='candidate'else 24996)
  assert [f['frame']for f in r['frames']]==list(range(1,len(r['frames'])+1))
  unchanged=['video_sha256','navigation','locomotion_state','held_buttons','full_GPU_state_sha256','full_DSP_state_sha256'];assert all(a[k]==b[k]for a,b in zip(r['frames'],old['frames'])for k in unchanged)
  assert sha(folder/'frontend-PCM.s16le')==sha(Path(previous['directory'])/'candidate/frontend-PCM.s16le')
  pair.append((s,r,folder));bind(p)
  for name in ['report.json','frontend-PCM.s16le','gameplay-observation.json']:bind(folder/name);bind(Path(previous['directory'])/'candidate'/name)
  for path,digest in s['source_sha256'].items():bind(path,digest)
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];diff={k:sum(a[k]!=b[k]for a,b in zip(pair[0][1]['frames'],pair[1][1]['frames']))for k in fields};assert diff['video_sha256']==17515
 oldbuild=read(V/'native-actor-dispatch-disc-build-current.json');oldcode=Path(read(oldbuild['component_gate'])['binary']).read_bytes();code=Path(component['binary']).read_bytes();changes=[dict(offset=i,before=a,after=b)for i,(a,b)in enumerate(zip(oldcode,code))if a!=b];assert len(oldcode)==len(code)==572 and len(changes)==6
 for p in [Path(__file__),buildp,Path(build['component_gate']),V/'native-actor-dispatch-gap320-monitor-current.json',V/'native-actor-dispatch-gap320-negatives-current.json',initp,jointp,negp]:bind(p)
 for data in [build,component,monitor,init,joint,neg,read(V/'native-actor-dispatch-gap320-negatives-current.json')]:
  for p,h in data.get('source_sha256',{}).items():bind(p,h)
 report=ROOT/'reports/native-actor-dispatch-gap320-and-initializer.txt';assert not report.exists()
 report.write_text('''BIWN — WIDER DISPATCHER CAPTURE GAP AND NEXT ACTOR SOURCE INTERFACE

The572byte13AE0dispatcher now reserves320private gap bytes. Its saved72byte
context is rootSP-336throughrootSP-264. The C algorithm is unchanged except
for the header include name; five LEA displacement operands differ in six
binary bytes.856full original-ABI cases/all38sites pass at prototype/final
addresses; two binary/source defects are rejected;96startup cases pass.
Resident size19460, unchanged20480reserve and heap163DC0,1020bytes free.

The read-only monitor now directly measures real descendant SP versus the
context boundary. It is qualified on856original+856compiled cases and three
negatives: wrong rootD0, wrong childX, and a childSPoverlap caught specifically
by the context guard. Both fresh real gameplay runs return outdoors: candidate
24983frames/control24996. Each dispatches13calls(12actor/1sprite), zero fullpool
returns. Full child/root ABI, args, task-stack and context checks pass, no errors
or pending calls. Candidate reaches392private bytes with390minimum task-stack
bytes of headroom. Actual original descendants reach194bytes belowrootSP,
leaving70observed context bytes clear. Control has194depth/606headroom; its
clearance value is hypothetical because it has no C context. These finite paths
do not bound every future descendant or interrupt/device/concurrent change.

Compared with the previous256gap route, both320gap variants preserve every
recorded video/GPU/DSP/navigation/locomotion/button frame and full captured PCM.
Candidate CPUdiffers at1frame, control0; publicRAMhashes differ24810/24823frames
because changed code/private stack data remain in full snapshots. No exact
whole-machine equality is claimed. Against its fresh original-dispatcher-entry
control, the320gap candidate still differs in17515video frames; PCMlength/hash,
CPU/RAM/GPU/DSP/navigation/input state differ. This widening resolves the
observed6byte context clearance, not those inherited timing/media differences.
The same eight-field fresh-pair differences are retained in the protocol.

NEXT SOURCE COMPONENT:134DC
A complete high-level C actor initializer plus original-facing adapter now
passes1024fullCPU/SR/bank/public2MBRAM/ordered-bus/real10520child cases, all148
original instruction sites, including all15callback dispatches, invalid/finished
cases, raw signed slot arithmetic and partial-word/full-register behavior.
Geometry102C4and taskDF6C remain prescribed leaf services in this component
proof. Native helpers receive their original argumentSPand full entry CPU/SR.
The inline13620jump table remains a real ordered guestWORDread. Source-private
compiler constants/frames are excluded. Unknown modified table targets trap;
arbitrary faults/targets/concurrency are not established.

Initializer1620bytes/private564; shim gap448. Joint native13AE0+134DCexecutes
both C bodies in856additional cases and matches complete original group CPU,
helper-entry state/publicRAM/ordered accesses. Their nested frames coexist at
maximum600private bytes. The joint prototype uses separate test addresses,
not a disc insertion. No-body, wrong helperX and forbidden original134E0body
delegation defects are rejected. This is target compilation/interface recovery
of an already-recovered algorithm, not a new logical-function count.

1620initializer bytes exceed current1020free by600before alignment. No heap or
reservation expansion is adopted. Full-loader/heap/resource/task/gameplay checks
and context-canary monitoring for nested native frames are required before
insertion. A descendant native frame may legitimately skip over its parent's
saved context; the current SP-only collision rule is scoped to original children
and must be replaced by an appropriate interval/canary check for that integration.

All source/interface/layout/verification work this turn is coordinator work;
no new local predictions or weight updates occurred. Earlier local dispatcher
drafts failed; accepted parent functions retain their separate attribution.
The separate3384byte source-owned five-member group is still not disc-integrated.
Published/default18888preview is unchanged at this review. Full readable game,
remaining sprite factory/interfaces, timing/media, LM Studio nativeChat usability,
Advertising reliability and complete workbench migration remain unfinished.
''');bind(report)
 record=dict(status='terminal_gap320_live_and_initializer_components_reviewed',directory=str(out),report=str(report),build=str(buildp),build_sha256=sha(buildp),resident_bytes=19460,private_gap=320,native_bytes=572,component_cases=856,startup_cases=96,candidate_frames=24983,control_frames=24996,live_dispatches=13,actor_routes=12,sprite_routes=1,full_pool_live=0,max_private_depth=392,min_task_headroom=390,max_actual_descendant_depth=194,min_observed_context_clearance=70,context_collisions=0,live_monitor_pass=True,gap256_variant_media_and_navigation_preserved=True,gap256_variant_CPU_different_frames=[1,0],gap256_variant_RAM_different_frames=[24810,24823],binary_delta_bytes=changes,same_layout_differences=diff,PCM_equal=False,candidate_observations=pair[0][0]['observations'],control_observations=pair[1][0]['observations'],initializer=dict(cases=1024,sites=148,bytes=1620,private_depth=564,joint_cases=856,joint_private_depth=600,disc_integrated=False,additional_bytes_needed_before_alignment=600),new_predictions=0,new_training=False,new_logical_functions=0,default_promoted=False,native_Chat_verified=False,whole_game_complete=False,dependencies_sha256=deps,pointer_snapshots=aliases)
 (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(V/'actor-gap320-and-initializer-reviewed-current.json').write_bytes((out/'protocol.json').read_bytes());print(json.dumps({k:record[k]for k in ['status','candidate_frames','control_frames','min_observed_context_clearance','initializer','report']}))

if __name__=='__main__':main()
