"""Freeze exact-disc C instruction, cost and complete function checks."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';paths=[v/'geometry-scan-C-bank-build-current.json',v/'geometry-scan-CPU-instructions-current.json',v/'geometry-scan-C-function-select-current.json',v/'geometry-scan-C-function-scan-current.json'];build,atomic,select,scan=[read(p)for p in paths]
    assert atomic['status']=='terminal_geometry_scan_CPU_instructions_native_and_cost_pass' and atomic['failed_cases']==0 and atomic['cases']==atomic['entries']*384
    assert select['status']=='terminal_complete_geometry_select_C_provider_CPU_RAM_ordered_pass' and select['stable_cases']==1280 and select['changing_coordinate_cases']==512
    assert scan['status']=='terminal_complete_geometry_scan_C_provider_CPU_RAM_ordered_pass' and scan['stable_cases']==1377 and scan['changing_coordinate_cases']==768
    assert atomic['CPU_candidate']==select['CPU_candidate']==scan['CPU_candidate']==build['CPU_candidate']
    candidate=read(build['CPU_candidate']);bridgep=Path(build['directory'])/'native-CPU-candidate.json';bridge=read(bridgep);assert bridge['CPU_library']==candidate['library'] and bridge['private_CPU_state']
    correctionp=v/'native-geometry-scan-word-correction-current.json';correction=read(correctionp);assert correction['status']=='terminal_linked_scanner_word_injection_corrected_pass'
    now=datetime.now(timezone.utc);out=v/'geometry-scan-C-runtime-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in paths+[correctionp]:bind(p)
    for d in [build,atomic,select,scan]:
        for p,h in d['source_sha256'].items():bind(p,h)
    for p,h in correction['dependencies_sha256'].items():bind(p,h)
    for p in [bridgep,Path(bridge['library']),Path(bridge['directory'])/'fast_CPU_bridge.c',Path(__file__)]:bind(p)
    for d,files in [(atomic,['entries.json','cases.json']),(select,['stable-fixtures.json','changing-fixtures.json','stable-results.json','changing-results.json']),(scan,['stable-fixtures.json','changing-fixtures.json','stable-results.json','changing-results.json'])]:
        for name in files:bind(Path(d['directory'])/name)
    report=ROOT/'reports/native-geometry-scan-C-provider.txt';report.write_text('BIWN — C INSTRUCTION PROVIDER FOR EXACT17812BYTE SCANNER DISC\n'+now.isoformat()+'\n\n'
      f"The fixed C instruction provider regenerated/added {atomic['entries']} static instruction locations for the indexed selector, complete reverse scanner, redirects and startup. All {atomic['cases']} one-instruction cases pass full native CPU/SR/USP/SSP/2MBRAM and pinned emulator cycle checks, using32CCR/two stack modes/IPL0and7/three operand profiles. Static instruction locations are not recovered game-function counts.\n\n"
      f"Complete1039Cindexed selector:1280stable+512changing-read cases passed through C steps and RAM callbacks, exercising {len(select['C_instruction_addresses_exercised'])} C instruction locations. Complete102C4reverse scanner:1377stable+768changing-read cases passed, exercising {len(scan['C_instruction_addresses_exercised'])} locations. Right lanes use no original CPU opcode execution. Full register/bank/publicRAM and ordered width/value checks include tagged pointers through24bitbus, reverse search and32768entry miss. Source-register save/private8KBstack/code/entry exclusions remain.\n\n"
      'The first scanner function run is retained as rejected: its C/native final CPU andRAM matched, while ordered WORD-read values did not. The tracer injected four bytes for a declared two-byte change. A versioned tracer now writes the exact declared width; standalone/final-linked checks additionally compare native publicRAM against traced publicRAM on each side. The corrected full scanner C-function suite passed. Game C and all disc bytes are unchanged.\n\n'
      'The bank-coherent wrapper preserves activeUSP/SSP=A7 after accepted instructions. A strict private-state/cost bridge has been compiled for the exact core. Live C CPU/GPU/DSP/IRQ comparison remains a separate job; these gates do not establish physical timing, arbitrary faults/IRQ interleavings, whole-game readable source, physical console boot or default preview promotion. All new provider, bridge and verifier work here is coordinator work; no new model predictions or weights.\n')
    bind(report);result=dict(status='terminal_geometry_scan_C_provider_components_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),CPU_candidate=build['CPU_candidate'],native_CPU_candidate=str(bridgep),instruction_locations=atomic['entries'],atomic_cases=atomic['cases'],select_stable_cases=1280,select_changing_cases=512,scan_stable_cases=1377,scan_changing_cases=768,dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,default_promoted=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'geometry-scan-C-runtime-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','atomic_cases','report']}))
if __name__=='__main__':main()
