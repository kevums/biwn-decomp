"""Independent exact18888disc C/native report audit; distinct report path."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 p=V/'interior-C-processors-route-current.json';job=read(p);assert job['status']=='terminal_interior_C_processors_route_equal'and job['exit_code']==0 and job['tested_resident_bytes']==18888
 a=Path(job['reference']);b=Path(job['directory'])/'C';left=read(a/'report.json');right=read(b/'report.json')
 assert left['disc_sha256']==right['disc_sha256']=='f5f378de20e37bd4bca471efbece7bab4d525c68bfb228bd48a7f99dede92128'
 assert len(left['frames'])==len(right['frames'])==24996
 ids=[x['frame']for x in left['frames']];assert ids==[x['frame']for x in right['frames']]and len(set(ids))==24996 and all(y==x+1 for x,y in zip(ids,ids[1:]))
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
 differences={k:sum(x[k]!=y[k]for x,y in zip(left['frames'],right['frames']))for k in fields};assert not any(differences.values())
 assert (a/'frontend-PCM.s16le').stat().st_size==(b/'frontend-PCM.s16le').stat().st_size==79987200 and sha(a/'frontend-PCM.s16le')==sha(b/'frontend-PCM.s16le')
 obs=read(b/'gameplay-observation.json');assert obs==read(a/'gameplay-observation.json'),'Full observer equality failed'
 cpu=right['C_CPU_backend'];assert cpu['mode']=='C'and cpu['entry_gate']==dict(armed=True,bootstrap_native_callbacks=0,source_from_initial_entry=True,original_before_owner_install=0)
 counts=cpu['counts'];stats=cpu['stats'];assert counts['Original']==counts['Rejected']==stats['errors']==0 and counts['Owned']==stats['calls']==stats['steps']+stats['HLE']
 back=right['C_processor_backends'];gpu,dsp,irq=[back[k]for k in ['GPU','DSP','IRQ']]
 for count in [gpu['counts'],dsp['core_counts'],irq['core'],irq['selection']]:assert count['Owned']>0 and count['Original']==count['Rejected']==0
 assert gpu['stats']['errors']==gpu['stats']['uncovered']==0 and gpu['errors']==[]
 assert dsp['errors']==dsp['uncovered']==irq['source']['errors']==0
 assert obs['scan_entries']==4753 and obs['scan_successes']==11 and obs['scan_failures']==4742 and obs['door_successes']==1
 assert obs['interior_kind_entries']==[14,1]and obs['interior_kind_successes']==[14,0]and obs['interior_kind_failures']==[0,1]and obs['interior_skips']==1
 for k in ['errors','copy_errors','acquire_monitor_errors','acquire_pending','acquire_user_stack_outside','geometry_errors','geometry_pending','geometry_stack_outside','select_errors','select_pending','select_stack_outside','scan_errors','scan_pending','scan_stack_outside','door_errors','door_pending','door_stack_outside','interior_errors','interior_pending','interior_stack_outside']:assert obs[k]==0,k
 last=right['frames'][-1];assert last['player_mode_word']==1 and last['floor_word']==0 and last['navigation']['outdoor_hold']>=120
 for path,digest in job['source_sha256'].items():assert sha(path)==digest,path
 out=V/'interior-C-processors-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 report=ROOT/'reports/native-interior-C-processors.txt';assert not report.exists()
 report.write_text('''BIWN — EXACT18888BYTE DISC, C PROCESSORS VERSUS RETAINED NATIVE PROCESSORS

24996aligned unique consecutive frame IDs match. All eight recorded fields
match on every frame: fullCPU, publicRAMhash, GPUstatehash, DSPstatehash,
video hash, navigation, locomotion and held buttons. Full captured PCM matches
byte-hash and length79987200bytes. Both routes return outdoors with120holdframes.
The full read-only observer JSON objects also match, not selected counters only.

Strict C CPU starts from HLE-prepared initial entry, with zero bootstrap native
callbacks, native fallback, rejected ownership or reported CPU errors. Recorded
CPU calls436659999 include435925472source steps and734527HLE services. GPU,
DSP and IRQ selection/entry likewise show owned execution and zero recorded
original/rejected/uncovered/error counts where applicable. These are runtime
processor-validation counts, not recovered readable game-function counts.

Actual scanner4753calls:11successes/4742failures; doorway1success. Interior
selectors:14actor successes and1sprite skipped failure. All related monitor,
pending and task-stack error counters are zero. Actor failures, sprite successes
and sprite non-skipped misses remain component-only in this route.

Only this identified18888byte modified disc is compared against itself under
two processor implementations. This does not resolve compiled-helper versus
original-entry timing/state/video differences, inherited original-scanner media
disagreement, or validate the later actor-dispatch experimental build. CPU cost,
HLE/platform/device services, IRQ line/ACK/vector/commit/prefetch, blitter and
object processor remain retained. Finite route/oracle facts are not full-game
or physical-console proof. No new local predictions, training or nativeChat test.
''')
 paths=[Path(__file__),p,a/'report.json',b/'report.json',a/'frontend-PCM.s16le',b/'frontend-PCM.s16le',a/'gameplay-observation.json',b/'gameplay-observation.json',report,V/'interior-C-runtime-reviewed-current.json']
 hashes={str(path):sha(path)for path in paths};hashes.update(job['source_sha256'])
 record=dict(status='terminal_interior_C_processors_independently_reviewed_equal',directory=str(out),report=str(report),tested_resident_bytes=18888,disc_sha256=right['disc_sha256'],frames=24996,frame_ID_alignment=True,differences=differences,PCM_bytes=79987200,PCM_equal=True,full_observer_equal=True,returned_outdoors=True,CPU_counts=counts,GPU_counts=gpu['counts'],DSP_counts=dsp['core_counts'],IRQ_counts=irq['core'],IRQ_selection_counts=irq['selection'],source_sha256=hashes,applies_to_actor_dispatch_build=False,new_predictions=0,whole_game_complete=False)
 (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(V/'interior-C-processors-reviewed-current.json').write_bytes((out/'protocol.json').read_bytes());print(json.dumps({k:record[k]for k in ['status','frames','PCM_equal','full_observer_equal','report']}))

if __name__=='__main__':main()
