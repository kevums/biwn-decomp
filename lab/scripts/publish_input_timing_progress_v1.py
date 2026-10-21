"""Publish measured clock/remainder behavior; preserve game acceptance scopes."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    rp=V/'input-timing-connected-v1-current.json';r=read(rp)
    assert r['connected_original_dispatch_and_division_cases']==425 and r['captured_walking_cases']==194
    for path,digest in r['source_sha256'].items():assert sha(path)==digest,path
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,digest in w['dependencies_sha256'].items():assert sha(path)==digest,path
    out=V/'input-timing-progress-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p)
    assert p['latest_native_candidate']['native_record_returns']==4777
    assert not p['pending_native_candidate']['default_promoted'] and not p['pending_native_candidate']['final_matrix_video_comparison_pass']
    facts={k:v for k,v in r.items()if k!='source_sha256'};facts['review']=str(rp)
    ap=V/'local-input-timing-analyst-v1-current.json';analyst=read(ap)
    assert analyst['status']=='terminal_shared_slot_busy_zero_predictions' and analyst['new_predictions']==0
    report=ROOT/'reports/BIWN Input Clock and Remainder Diagnosis.txt'
    lines=['BIWN — input clock and remainder diagnosis','',
        'Previous goal turn:Progress. Twelve saved-state renderer/movement lanes and627actual C integration transitions established stationary image equality and a22/23movement-step discrepancy. This turn adds read-only input boundaries and connected dispatcher/division verification;it does not rerun fresh game routes or build a new disc.','',
        'CURRENT BASELINE',
        'v34 remains the reviewed game image. v37 remains unpromoted after its fresh matrix-route final-video comparison failed22858pixels. The installed Desktop outdoor checkpoint preview is unchanged. The earlier fresh-route cause is still unresolved.','',
        'NEW CONTROLLED EVIDENCE',
        'Four180-frame exact-snapshot motion lanes now capture original191F4input entry,1A26Creturn and1A2C2world-integration boundaries. Ordinary Up input is heldframes1..60,then released61..180. Native versus original scene code is the sole ten-byte entry intervention. No player,camera,timer or input normalization. All previously recorded CPU/RAM/GPU/DSP/video rows reproduce exactly,so the new observer does not change those executions.','',
        'Origin / scene code | walking calls | admitted clock ticks | movement steps | fraction discarded onrelease',]
    for origin in ['candidate','control']:
        for lane in ['native','original']:
            row=r['lane_summary'][origin][lane]
            lines.append(f"{origin} / {lane} | {row['walking_calls']} | {row['walking_clock_ticks']} | {row['movement_steps']} | {row['remainder_discarded_at_release']}")
    lines += ['',
        'Every release is observed atframe61 and resets speed/remainder tozero. Candidate-origin native admits287movement ticks and ends with22whole steps plus62908/65536fraction;original admits290ticks and ends with23steps plus13087/65536fraction. Native last processes held Up atframe59;original atframe60. This explains the one-step difference in this controlled trial.','',
        'Both control-origin lanes admit293ticks and produce23steps. Their final input remainders differ by14least-significant fraction units(28829/28815),because integer division truncates on each separate call. World update consumes whole movement counts,so both end at the same expanded pose in this second origin.','',
        'SOURCE CHECK',
        'Recovered biwn_input_dispatch.c and biwn_signed_division.c are linked together.425connected fixtures execute original191F4and originalE588instructions as the comparison;no RTS stub supplies division. C matches original D0,all ordered global reads/writes/helper arguments,and nonprivate RAM in every case.194fixtures use the captured walking dt/remainder and match observed speed/remainder exactly;231additional cases cover forward,backward and run branches with wide time/carry boundaries. Other preamble globals are neutral fixture values,so this is not full captured-runtime register/RAM equivalence. Existing source is unchanged;no newly recovered unique routine is claimed.','',
        'AGENT / MODEL ACTIVITY',
        'The coordinator authored the observer,ran the original-CPU/C comparisons and reviewed the evidence. A local Trace Analyst prompt was saved but generated zero responses because the shared inference lease was unavailable. No model was loaded,unloaded or interrupted;no new predictions or optimizer updates. The lock observation does not identify a live job or count as a verified wait. Reader43remains the installed supplied-facts status default. Exact prepared prompt: '+str(Path(analyst['directory'])/'prompt.json'),'',
        'LIMITS / NEXT WORK',
        'The controlled scene-code intervention changes update timing and which fixed-point threshold is crossed before input release. Wrong walking arithmetic is not observed in these cases. This does not establish the specific earlier fresh-route mismatch cause or waive that failed video gate. Whole-game source-only same-console rebuilding,complete CPU/GPU/DSP/HLEcoverage,audio/IRQ/arbitrary reentry,wider fidelity,useful untouched-task training gain,copied-weight native Chat usability and future256GBhardware measurements remain unfinished.','',
        'Continue full-game CPU/GPU/DSP/IRQ source integration and fidelity. Use this measured quantization behavior when interpreting pose-divergent frame comparisons. Do not change controller endpoints or normalize state merely to force image equality. Retry the prepared local analyst only after observing actual shared-slot availability;do not replay these terminal fourlanes/425cases for receipts.','',
        'Detailed evidence: '+str(rp),'Prior equal-state evidence: '+str(V/'record-loop-equal-state-reviewed-v3-current.json'),'',]
    report.write_text('\n'.join(lines))
    facts['report']=str(report);p['current_input_timing_progress']=facts
    p['current_copied_Reader_progress']['new_input_timing_facts_not_in_saved_briefing']=True
    p['prepared_local_input_timing_analyst']=dict(status=analyst['status'],directory=analyst['directory'],new_predictions=0,new_training=False,
        scope='Prompt prepared;inference lease unavailable. No live owner is inferred and no model is loaded or interrupted.')
    p['checked_current_summary']+=' New read-only input trace preserves every earlier frame;controlled walking accumulates287/290ticks and22/23whole steps,versus293/293ticks and23/23steps from the other origin.425connected original-dispatch/division cases pass,including194captured walking speed/remainder cases. Earlier fresh matrix gate remains failed.'
    p['checked_answer']=p['checked_current_summary'];p['recorded_at']=datetime.now(timezone.utc).isoformat()
    save(out/'current-status-packet.json',p)
    deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),**r['source_sha256'],str(report):sha(report),str(ap):sha(ap)}
    for source in [ROOT/'scripts/run_local_input_timing_analyst_v1.py',*[x for x in Path(analyst['directory']).iterdir()if x.is_file()]]:
        deps[str(source)]=sha(source)
    deps.update({str(x):sha(x)for x in out.iterdir()if x.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    save(V/'input-timing-progress-delivered-v1-current.json',dict(status='terminal_input_clock_diagnosis_published_v34_retained_v37_unpromoted',
         directory=str(out),report=str(report),new_predictions=0,new_training=False,new_fresh_routes=0,gameplay_promoted=False))
    print('Input clock/remainder diagnosis delivered;425connected/194captured pass. No fresh gate waived.',flush=True)


if __name__=='__main__':main()
