"""Freeze the exact18270byte disc's C instruction and complete-function gates."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';bp=v/'doorway-C-bank-build-current.json';ap=v/'doorway-CPU-instructions-current.json';build,atomic=read(bp),read(ap)
    assert atomic['status']=='terminal_doorway_CPU_instructions_native_and_cost_pass' and atomic['failed_cases']==0 and atomic['cases']==atomic['entries']*384
    function_paths=[v/('doorway-C-function-'+name+'-current.json')for name in ['select','scan','doorway']];functions=[read(p)for p in function_paths]
    for d,name,stable,changing in zip(functions,['select','scan','doorway'],[1280,1377,2025],[512,768,768]):
        assert d['status']=='terminal_complete_geometry_'+name+'_C_provider_CPU_RAM_ordered_pass' and d['stable_cases']==stable and d['changing_coordinate_cases']==changing and not d['right_lane_original_opcode_execution']
        assert d['CPU_candidate']==atomic['CPU_candidate']==build['CPU_candidate']
    candidate=read(build['CPU_candidate']);bridgep=Path(build['directory'])/'native-CPU-candidate.json';bridge=read(bridgep);assert bridge['CPU_library']==candidate['library'] and bridge['private_CPU_state']
    now=datetime.now(timezone.utc);out=v/'doorway-C-runtime-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [bp,ap,*function_paths]:bind(p)
    for d in [build,atomic,*functions]:
        for p,h in d['source_sha256'].items():bind(p,h)
    for p in [bridgep,Path(bridge['library']),Path(bridge['directory'])/'fast_CPU_bridge.c',Path(__file__)]:bind(p)
    for d,files in [(atomic,['entries.json','cases.json'])]+[(d,['stable-fixtures.json','changing-fixtures.json','stable-results.json','changing-results.json'])for d in functions]:
        for name in files:bind(Path(d['directory'])/name)
    report=ROOT/'reports/native-doorway-C-provider.txt';report.write_text('BIWN — EXACT18270BYTE DOORWAY DISC C INSTRUCTION PROVIDER\n'+now.isoformat()+'\n\n'
      f"The extension regenerated/added {atomic['entries']} static instruction locations for the458byte local-model doorway component, redirects and startup. All {atomic['cases']} one-instruction cases passed fullD/A/PC/SR/USP/SSP/2MBRAM and pinned emulator cycle checks, using32CCR/two stack modes/IPL0and7/three controlled operand profiles. Locations are not recovered game-function counts.\n\n"
      'The same provider also passed the complete indexed selector1280stable+512changing, scanner1377stable+768changing and doorway2025stable+768changing function comparisons against original native CPU execution. Right lanes execute generated C instruction steps and RAM callbacks, with no original CPU opcode execution. Full register/bank/publicRAM and logical ordered-width/value checks include24bitbus/tagged pointers, signed counts, sentinel and invalid directions, byte sign extension, source-ordered actor/record overlaps, and the scanner32768entry miss. The declared private8KBstack/code/entry exclusions remain.\n\n'
      'The active-bank normalization wrapper and exact-core private-state/cost bridge are compiled. Component gates do not establish live C CPU/GPU/DSP/IRQ equality; that is a separate exact-disc job. No physical timing, arbitrary faults/IRQ interleavings, whole-game source rebuild or default preview promotion is established. The selected doorway kernel is unedited repaired local output; instruction translation, bridge and these verifiers are coordinator work. No new model prediction or training occurred in this provider step.\n')
    bind(report);result=dict(status='terminal_doorway_C_provider_components_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),CPU_candidate=build['CPU_candidate'],native_CPU_candidate=str(bridgep),instruction_locations=atomic['entries'],atomic_cases=atomic['cases'],function_cases={name:dict(stable=d['stable_cases'],changing=d['changing_coordinate_cases'],C_instruction_addresses=len(d['C_instruction_addresses_exercised']))for name,d in zip(['select','scan','doorway'],functions)},dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,default_promoted=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'doorway-C-runtime-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','atomic_cases','report']}))
if __name__=='__main__':main()
