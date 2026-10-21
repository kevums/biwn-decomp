"""Preserve the failed long route alongside the successful initial-entry gameplay proof."""
import json,struct
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())

def main():
    pp=ROOT/'verification/source-CPU-entry-gameplay-publication-current.json';parent=read(pp)
    assert 'latest_combined_route_failure' not in parent['current_status'], 'Already published; do not repeat unchanged work'
    directory=ROOT/'verification/native-formatter-C-processors/20261018T233557.255349Z'
    run=read(directory/'protocol.json');DSP=read(directory/'C/DSP-owner-report.json')
    assert run['exit_codes']=={'reference':0,'C':1} and DSP['uncovered']==DSP['core_counts']['Original']==460
    reference=read(directory/'reference/report.json');by={f['frame']:f for f in reference['frames']}
    samples=[]
    for line in (directory/'C.log').read_text().splitlines():
        try:d=json.loads(line)
        except ValueError:continue
        if isinstance(d,dict) and 'CPU_full' in d and 'frame' in d:samples.append(d)
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
    mismatches=[dict(frame=s['frame'],fields=[k for k in fields if s[k]!=by[s['frame']][k]])for s in samples if any(s[k]!=by[s['frame']][k]for k in fields)]
    snapshot=directory/'C/DSP-first-uncovered-state.bin';raw=snapshot.read_bytes();pc=struct.unpack_from('=I',raw,8192)[0]
    now=datetime.now(timezone.utc);out=ROOT/'verification/combined-merchant-DSP-gap'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    failure=dict(status='terminal_combined_merchant_DSP_uncovered',directory=str(out),failed_run=str(directory/'protocol.json'),
        failure_frame=15849,reported_outer_driver_failure='Missing C/report.json after the source processor guard aborted; the original child error is preserved in C/status.json and C.log.',
        DSP=DSP,first_uncovered_PC=hex(pc),first_uncovered_control=hex(struct.unpack_from('=8I',raw,8204)[6]),
        cause='DSP byte-fenced router owns only known local-RAM music/media identities; saved first uncovered PC is outside that range. Whether this matches native execution or follows a C semantic divergence requires the separate fresh native observer.',
        reference_completed_frames=len(reference['frames']),C_last_logged_frame=samples[-1]['frame'],logged_samples_checked=len(samples),sampled_mismatches=mismatches,
        full_frame_and_PCM_comparison_passed=False,strict_no_fallback_passed=False,original_DSP_fallbacks_in_failed_frame=460,
        no_new_C_rerun_started=True,new_training=False,preview_or_default_promoted=False)
    save(out/'failure-analysis.json',failure)
    deps=dict(parent['status_dependencies_sha256'])
    def add(p):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert str(p)not in deps or deps[str(p)]==h,str(p);deps[str(p)]=h
    frozen=Path(parent['directory'])/'publication.json';assert sha(frozen)==sha(pp);add(frozen)
    for p in [directory/'protocol.json',directory/'runner-as-run.py',directory/'probe.py',directory/'C.log',directory/'C/status.json',directory/'C/DSP-owner-report.json',directory/'C/CPU-IRQ-owner-report.json',snapshot,directory/'reference/report.json',directory/'reference/frontend-PCM.s16le',directory/'C/frontend-PCM.s16le',out/'failure-analysis.json',Path(__file__)]:add(p)
    for p,h in deps.items():assert sha(p)==h,p
    current=dict(parent['current_status'])
    summary=('The repaired-disc initial-entry C CPU/GPU/DSP/IRQ candidate passes1600freshgameplayframes, including1000scripted run-stateframes. OriginalCPUopcodeexecution is0 before installation and throughout that HLE-prepared window; every recorded fullCPU/RAM/GPU/DSP/video/navigation/control field and silentPCM matches the reused native control. '
        'A separate older combined-provider merchant route FAILED at frame15849: the DSP router encountered outside-catalogue execution at savedPC0 and allowed460originalDSPinterpreterfallbacks before the frame guard stopped it. Its265logged samples through15841 match; there is no completed full-frame/PCM pass for that route. Native reference completed24975frames. Native read-only diagnosis is separate; the root cause remains unresolved. '
        'The earlier24975frame sourceCPU-only route retains nativebootstrap/GPU/DSP/IRQ; it does not prove the failed combined route or new initial-entry candidate. '
        'FirmwareHLE,device/IRQline+ACK/vector resolution,hostcommit/prefetch/cost/clock and blitter/objectprocessor services remain supplied. Full game decompilation,standalone console rebuild,authenticatedboot and physicalaudio remain unverified. No new model weights or preview/default promotion.')
    current.update(recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,
        latest_combined_route_failure=failure,unresolved_runtime_failure=failure,
        long_route_scope='Combined merchant route terminal_failed at15849, distinct from passing1600initial-entry and earlier24975CPU-only comparison.')
    report=ROOT/'reports/BIWN-combined-merchant-DSP-gap.txt';report.write_text('BIWN — COMBINED MERCHANT DSP GAP\n'+now.isoformat()+'\n\n'+summary+'\n\nFailure analysis: '+str(out/'failure-analysis.json')+'\nEarlier passing initial-entry gameplay: '+str(frozen)+'\n')
    current['report']=str(report)
    pub=dict(parent,status=parent['status'],recorded_at=now.isoformat(),directory=str(out),report=str(report),parent_publication=str(frozen),current_status=current,
        status_dependencies_sha256=deps,evidence_files_verified=len(deps),integrity_mismatches=[])
    save(out/'publication.json',pub);save(pp,pub);save(ROOT/'verification/combined-merchant-DSP-gap-current.json',failure)
    save(ROOT/'verification/combined-merchant-live-observation-current.json',dict(status='terminal_failed_not_live',failure_analysis=str(out/'failure-analysis.json'),failure_frame=15849,parent_pid=6055,C_child_pid=6057,exec_session=48774,processes_terminal=True))
    print(json.dumps(dict(status=failure['status'],samples=len(samples),mismatches=len(mismatches),bound_files=len(deps))),flush=True)

if __name__=='__main__':main()
