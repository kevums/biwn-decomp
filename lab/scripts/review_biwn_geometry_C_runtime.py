"""Freeze the boundary-disc C-provider checks; gameplay remains a separate job."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';bp=v/'geometry-C-bank-build-current.json';ap=v/'geometry-CPU-instructions-current.json';fp=v/'geometry-C-function-current.json'
    build,atomic,function=[read(p) for p in [bp,ap,fp]]
    assert atomic['status']=='terminal_geometry_CPU_instructions_native_and_cost_pass'
    assert atomic['entries']==118 and atomic['cases']==45312 and atomic['failed_cases']==0
    assert function['status']=='terminal_complete_boundary_C_provider_CPU_RAM_ordered_pass'
    assert function['stable_cases']==1376 and function['changing_coordinate_cases']==256
    assert function['max_private_stack_bytes']==48 and not function['right_lane_original_opcode_execution']
    assert atomic['CPU_candidate']==function['CPU_candidate']==build['CPU_candidate']
    candidate=read(build['CPU_candidate']);new_sites={row['address'] for row in candidate['new_cases']}
    assert set(function['C_instruction_addresses_exercised'])<=new_sites
    bridge_path=Path(build['directory'])/'native-CPU-candidate.json';bridge=read(bridge_path)
    assert bridge['CPU_library']==candidate['library'] and bridge['private_CPU_state']
    first_failure=v/'geometry-CPU-instructions/20261019T042221.018295Z'
    mismatch=read(first_failure/'first-mismatches.json')[0]
    assert mismatch['pc']=='0xf8004' and not mismatch['CPU_equal'] and mismatch['RAM_equal'] and mismatch['C_cost']==mismatch['native_cost']
    assert mismatch['actual']['usp']!=mismatch['expected']['usp']
    now=datetime.now(timezone.utc);out=v/'geometry-C-runtime-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir()
    deps={};aliases={}
    def bind(p,expected=None):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);digest=sha(p);assert expected is None or expected==digest,str(p)
        target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=digest
    for p in [bp,ap,fp]:bind(p)
    for proof in [build,atomic,function]:
        for p,h in proof['source_sha256'].items():bind(p,h)
    for p in [bridge_path,Path(bridge['library']),Path(build['directory'])/'bank-coherent-CPU.c',first_failure/'first-mismatches.json',first_failure/'protocol.json',Path(__file__)]:bind(p)
    for directory,names in [(Path(atomic['directory']),['entries.json','cases.json','runner-as-run.py']),
                            (Path(function['directory']),['stable-fixtures.json','stable-results.json','changing-results.json','runner-as-run.py'])]:
        for name in names:bind(directory/name)
    report=ROOT/'reports/native-geometry-C-provider.txt'
    report.write_text('BIWN — C PROCESSOR SUPPORT FOR THE LATEST BOUNDARY DISC\n'+now.isoformat()+'\n\n'
        'The fixed C instruction provider now covers the latest 17,084-byte native boundary disc. The extension regenerated or added 118 instruction locations, including startup and redirects; this is not 118 recovered game functions. The signed SLE.B condition result and the four-register MOVEM reuse/add explicit C semantics.\n\n'
        'All 45,312 one-instruction cases passed against the retained native CPU: full registers, SR, both stack banks, 2MB RAM and pinned emulator cycle charges. The cases use all 32 CCR combinations, two stack modes, interrupt masks 0/7 and three controlled register variants. They do not establish arbitrary aliases, faults, IRQ interleavings or physical timing.\n\n'
        'The complete original boundary routine was also compared with the final linked component executed solely through the C instruction provider and RAM callbacks. All 1,376 stable and 256 changing-coordinate cases passed full CPU/public-RAM and ordered-access checks. They exercised 72 C instruction locations across the complete routine, including paths not reached in the gameplay route. Private stack use was 48 bytes. The declared private scratch/code/entry exclusions remain.\n\n'
        'A failed atomic check is retained: direct stack-pointer assignment left the serialized active USP field stale. Registers, RAM and cycle charge matched, but USP did not. The new outer provider normalizes only the active USP/SSP field to A7 after an accepted instruction; the inactive bank and other state remain intact. Both the complete atomic suite and whole-function suite were rerun successfully after this fix. Expected state was not weakened.\n\n'
        'A full C CPU/GPU/DSP/IRQ comparison has now been launched on this exact boundary disc against its fresh native route. That job is separate from the older 16,872-byte cache-disc comparison, which remains on its original provider. Neither running job has a final verdict in this component receipt. Platform HLE, devices, IRQ lines/ACK/vector handling, host state commit/prefetch/clock/cost and blitter/objectprocessor services remain.\n\n'
        'All new instruction emission, bank repair, compiler wiring and checks in this receipt are coordinator work. No new original-game function recovery, local-model game-code authorship, weight training, preview promotion, full source rebuild or physical-console readiness is claimed. The native boundary game code and original disc were not changed by this host-provider work.\n')
    bind(report)
    result=dict(status='terminal_geometry_C_provider_atomic_and_complete_function_reviewed',recorded_at=now.isoformat(),directory=str(out),
                report=str(report),CPU_candidate=build['CPU_candidate'],native_CPU_candidate=str(bridge_path),
                instruction_locations=118,atomic_cases=45312,whole_function_stable_cases=1376,whole_function_changing_cases=256,
                whole_function_C_instruction_locations=len(function['C_instruction_addresses_exercised']),
                fixed_serialized_active_stack_bank=True,original_opcode_execution_on_component_right_lane=False,
                dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,new_original_game_functions=0,
                game_frames_verified_in_this_receipt=0,native_Chat_verified=False,default_promoted=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'geometry-C-runtime-reviewed-current.json',result)
    print(json.dumps({k:result[k] for k in ['status','atomic_cases','whole_function_stable_cases','whole_function_changing_cases','report']}),flush=True)


if __name__=='__main__':main()
