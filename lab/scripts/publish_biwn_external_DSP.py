"""Publish the checked DSP extension without claiming its pending full combined route."""
import json
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    pp=ROOT/'verification/source-CPU-entry-gameplay-publication-current.json';parent=read(pp);assert 'external_DSP_repair'not in parent['current_status']
    window=read(ROOT/'verification/external-DSP-live-window-current.json');assert window['status']=='terminal_external_DSP_live_window_equal'and window['external_instructions']==460 and window['PCM_prefix_byte_equal']
    candidate=read(window['candidate']);cp=Path(candidate['directory'])/'candidate.json'
    gate=read(ROOT/'verification/external-DSP-native-check-current.json');guards=read(ROOT/'verification/external-DSP-guards-current.json');export=read(ROOT/'verification/external-DSP-source-export-current.json')
    assert gate['status']=='terminal_external_DSP_native_pass'and gate['cases']==5580 and gate['failed_cases']==0
    assert gate['candidate_sha256']==sha(cp)and guards['status']=='terminal_external_DSP_guards_pass'
    deps=dict(parent['status_dependencies_sha256']);aliases={str(ROOT/'verification/external-DSP-experimental-candidate-current.json'):str(cp)}
    def add(p,expected=None):
        p=Path(aliases.get(str(p),str(p))).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);assert str(p)not in deps or deps[str(p)]==h,str(p);deps[str(p)]=h
    frozen=Path(parent['directory'])/'publication.json';assert sha(frozen)==sha(pp);add(frozen)
    for proof in [gate,guards,window]:
        directory=Path(proof['directory'])
        for p in directory.rglob('*'):
            if p.is_file():add(p)
        for p,h in proof['source_sha256'].items():add(p,h)
    for p,h in candidate['source_sha256'].items():add(p,h)
    for p,h in export['source_sha256'].items():add(p,h)
    for name in ['external-DSP-Code-Author-current.json','external-DSP-Code-Author-revision-current.json','external-DSP-local-C-review-current.json']:
        data=read(ROOT/'verification'/name)
        if data.get('directory'):
            for p in Path(data['directory']).rglob('*'):
                if p.is_file():add(p)
        else:
            outpath=Path(candidate['directory'])/name;save(outpath,data);add(outpath)
    # Retain the actual negative gate for the original model source too.
    rejected=ROOT/'verification/external-DSP-native-check/20261019T002523.653324Z'
    for p in rejected.rglob('*'):
        if p.is_file():add(p)
    add(Path(__file__))
    for p,h in deps.items():assert sha(p)==h,p
    now=datetime.now(timezone.utc);out=ROOT/'verification/external-DSP-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    repair=dict(status='terminal_external_DSP_component_and_live_window_verified',candidate=str(cp),compiled_external_instruction_identities=460,
        atomic_native_cases=5580,captured_cases=460,controlled_register_variants=5120,atomic_failures=0,rejection_guards=10,
        fresh_route_frames=15920,source_DSP_window=[15845,15920],source_DSP_owned_frames=75,source_DSP_external_instructions=460,
        all_eight_recorded_fields_equal=True,PCM_prefix_byte_equal=True,nonzero_captured_audio_samples=window['nonzero_audio_samples'],
        Original_DSP_instructions_during_owned_window=0,scope=window['scope'],proof=str(Path(window['directory'])/'protocol.json'),proof_sha256=sha(Path(window['directory'])/'protocol.json'),full_combined_route_verified=False,
        code_authorship=candidate['code_authorship'],source_export=export['directory'])
    summary=(
        'The repaired-disc initial-entry C CPU/GPU/DSP/IRQ candidate retains its separate 1,600-frame gameplay pass with zero original CPU opcode execution from the HLE-prepared entry. '
        'The external DSP gap is now repaired at the component and transition-window level: 5,580 native atomic comparisons and ten rejection guards pass. In a fresh 15,920-frame route, source DSP owns frames 15,845–15,919, executes all 460 formerly uncovered external instructions, and uses zero original DSP fallback during that window. All eight recorded state/video/input fields and captured PCM prefix bytes match the reused native control, including nonzero audio. CPU/GPU/IRQ remain original providers in this separate DSP-only window test. '
        'The old full combined route still failed at frame 15,849; a new full combined route has not passed yet. The earlier 24,975-frame CPU-only pass retains native bootstrap/GPU/DSP/IRQ and cannot establish the newer candidate. '
        'Local Code Author supplied ADDC unchanged; both local MTOI drafts were rejected, and Codex corrected MTOI. No whole-game source rebuild, standalone console boot, general speedup, physical audio or new weights are proved. Firmware HLE, device/IRQ line+ACK/vector, host commit/prefetch/cost/clock and blitter/objectprocessor services remain.')
    current=dict(parent['current_status']);current.update(recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,external_DSP_repair=repair,external_DSP_code_authorship=candidate['code_authorship'])
    current['unresolved_runtime_failure']=dict(parent['current_status']['latest_combined_route_failure'],specific_external_gap_fixed_in_component_and_DSP_only_window=True,full_combined_route_retest_pending=True)
    current['long_route_scope']='Previous combined route failed at15849. External gap now passes component and75frame DSP-only window; new full combined route not yet passed. Earlier24975CPU-only and1600initial-entry scopes remain separate.'
    report=ROOT/'reports/BIWN-external-DSP-repair.txt';current['report']=str(report)
    report.write_text('BIWN — EXTERNAL DSP REPAIR\n'+now.isoformat()+'\n\n'+summary+'\n\nComponent source/export: '+export['directory']+'\nNative check: '+str(Path(gate['directory'])/'protocol.json')+'\nFresh transition test: '+str(Path(window['directory'])/'protocol.json')+'\n\nExact original local prompt/response: '+str(Path(read(ROOT/'verification/external-DSP-Code-Author-current.json')['directory'])/'prompts-and-responses.txt')+'\nGuided revision: '+str(Path(read(ROOT/'verification/external-DSP-Code-Author-revision-current.json')['directory'])/'prompts-and-responses.txt')+'\nNo standalone same-console or whole-game completion claim.\n')
    pub=dict(parent,directory=str(out),recorded_at=now.isoformat(),parent_publication=str(frozen),current_status=current,report=str(report),status_dependencies_sha256=deps,status_dependency_aliases=aliases,evidence_files_verified=len(deps),integrity_mismatches=[])
    save(out/'publication.json',pub);save(pp,pub);save(ROOT/'verification/external-DSP-publication-current.json',pub)
    print(json.dumps(dict(status=repair['status'],bound_files=len(deps),nonzero_audio_samples=window['nonzero_audio_samples'])),flush=True)

if __name__=='__main__':main()
