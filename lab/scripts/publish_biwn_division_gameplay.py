"""Join exact fresh-gameplay evidence to the separately checked division component."""
import json
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(path):return json.loads(Path(path).read_text())

def main():
    parentp=ROOT/'verification/CPU-division-exception-publication-current.json';parent=read(parentp)
    gp=ROOT/'verification/CPU-division-fresh-gameplay-current.json';game=read(gp);directory=Path(game['directory'])
    assert game['status']=='terminal_fresh_division_gameplay_equal' and game['frames']==1600 and game['reference_reused']
    assert not any(game['comparisons'].values()) and game['audio_PCM_equal']
    counts=game['division_provider_counts'];assert counts==dict(total=7462,unsigned_steps=7443,signed_steps=19,zero_exceptions=0,normal_returns=7462,errors=0)
    assert not game['ordinary_gameplay_zero_exception_verified'] and game['checkpoint_restores']==game['host_guest_RAM_writes']==0
    deps=dict(parent['status_dependencies_sha256'])
    def add(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT),str(p);h=sha(p);assert expected is None or expected==h,str(p)
        if str(p)in deps:assert deps[str(p)]==h,str(p)
        deps[str(p)]=h
    parent_snapshot=Path(parent['directory'])/'publication.json';assert sha(parent_snapshot)==sha(parentp);add(parent_snapshot)
    add(directory/'protocol.json')
    for p,h in game['source_sha256'].items():add(p,h)
    for p in directory.rglob('*'):
        if p.is_file():add(p)
    reference=Path(game['reference'])
    for name in ['report.json','frontend-PCM.s16le','RAM-final.bin']:add(reference/name)
    native=read(directory/'native-CPU-candidate.json');assert sha(directory/'C/report.json')==game['report_sha256']
    add(Path(__file__))
    for p,h in deps.items():assert sha(p)==h,p
    now=datetime.now(timezone.utc);out=ROOT/'verification/CPU-division-gameplay-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    current=dict(parent['current_status']);current.update(status='terminal_division_component_and_fresh_gameplay_verified',recorded_at=now.isoformat(),
        fresh_gameplay_with_division_candidate_verified=True,native_CPU_candidate=str(directory/'native-CPU-candidate.json'),
        fresh_gameplay=dict(frames=1600,all_recorded_fields_equal=True,compared_fields=list(game['comparisons']),PCM_byte_identical=True,PCM_nonzero_samples=0,
            division_provider_counts=counts,ordinary_gameplay_zero_exception_verified=False,reference_reused=True,
            reference_scope=game['reference_scope'],reference=str(reference),fresh_C_run=str(directory/'C'),
            source_CPU_original_opcode_fallback_after4000=0,source_GPU_original_fallback=0,source_DSP_original_fallback=0,
            retained_providers=['original CPU bootstrap before4000','HLE','blitter/object processor','devices','IRQ lines/ACK/vector resolution','host state commit/prefetch','emulator cycle/clock services']),
        source_and_cost_candidate_scope='The candidate passes a fresh 1600-frame normal gameplay comparison with an immutable same-core/disc/input native control. It is not installed in the existing preview or the active long merchant test.',
        local_model_gameplay_authorship_scope='The unedited local model function handles zero exceptions. This ordinary gameplay run observes zero such exceptions; its7462normal division calls use coordinator wrapper logic. Model exception code is verified by the separate native and strict-owner fault fixtures.',
        long_merchant_route_with_division_candidate_verified=False,default_promoted=False,new_training=False,goal_complete=False)
    report=ROOT/'reports/BIWN-division-fresh-gameplay.txt';current['report']=str(report)
    report.write_text(f'''BIWN DIVISION BACKEND — FRESH GAMEPLAY CHECK
{now.isoformat()}

A new fresh 1,600-frame C CPU/GPU/DSP/interrupt run matches the immutable native control on every recorded full CPU, all 2 MB RAM, GPU/DSP state, video, navigation, locomotion and held-button field. Captured PCM is byte-identical and silent. The native control was reused from the exact earlier fresh run with matching core, disc and input bytes; it was not rerun for this experiment. No checkpoint was restored and no live guest RAM was patched.

The new division provider executes 7,462 normal division instructions: 7,443 unsigned and 19 signed, with zero errors. No zero-divisor exception occurs in this ordinary gameplay run. These are execution counts, not new recovered functions or a completion percentage.

The local model's unedited 17.85-second C function handles zero-exception entry. It is validated by the earlier 34,944 native CPU/RAM/cost fixtures and 11,264 strict-owner fault/RTE roundtrips, plus 22 host guards. It was not naturally invoked in this normal gameplay sample. The coordinator wrote the normal/overflow division wrapper, cost fixes, observation counter and fresh-gameplay driver.

The C CPU has zero original opcode fallback after mainstage4000; the 2,837,350 earlier bootstrap callbacks remain native. GPU/DSP and source interrupt providers have no original instruction fallback or rejection in the tested C run. Firmware HLE, devices, blitter/object processor, IRQ lines/ACK/vector resolution, host state commit/prefetch and emulator clock/cost services remain supplied. This is not a standalone console rebuild, a physical timing/audio test or complete game recovery.

The existing preview and the separately running long merchant comparison keep their previous candidates. No new weights or default promotion occurred. The new division candidate still needs broader scene/route and fault/IRQ testing before wider use.

Fresh C run and exact command:
{directory/'protocol.json'}
Native control:
{reference/'report.json'}
Local Author prompt/response:
{parent['current_status']['local_Code_Author']['exact_prompts_and_response']}
Reusable helper:
{parent['current_status']['source_export']}
''')
    add(report)
    publication=dict(status=current['status'],recorded_at=now.isoformat(),directory=str(out),current_status=current,report=str(report),status_dependencies_sha256=deps,integrity_mismatches=0,new_training=False,default_promoted=False,goal_complete=False)
    save(out/'publication.json',publication);save(ROOT/'verification/CPU-division-gameplay-publication-current.json',publication)
    print(json.dumps(dict(status=current['status'],evidence_files=len(deps),integrity_mismatches=0,normal_division_calls=counts['total'],natural_zero_exceptions=0,report=str(report))),flush=True)

if __name__=='__main__':main()
