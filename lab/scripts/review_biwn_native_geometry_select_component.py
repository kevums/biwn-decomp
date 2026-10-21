"""Bind the complete native selector, exact local failures and final-address build."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';names=['native-geometry-select-current.json','native-geometry-select-disc-build-current.json','local-native-geometry-select-author-current.json','local-native-geometry-select-repair-current.json'];component,build,author,repair=[read(v/n)for n in names]
    assert component['status']=='terminal_native_geometry_select_CPU_RAM_ordered_pass' and component['source_accepted']
    assert component['native_cases']==896 and component['changing_coordinate_cases']==256 and component['original_instruction_coverage']==[46,46]
    assert component['binary_bytes']==324 and component['max_private_stack_bytes']==112
    assert build['status']=='terminal_native_geometry_select_disc_built_entry_verified_pending_gameplay'
    assert build['linked_component_bytes']==17408 and build['appended_bytes']==324 and build['component_bytes']==20480
    assert build['linked_native_cases']==896 and build['linked_changing_coordinate_cases']==256 and build['entry_cases']==96
    assert not author['raw_kernel_gate_pass'] and not repair['raw_repair_gate_pass']
    assert author['gate_exit_code']==repair['gate_exit_code']==1
    assert Path(component['source']).name=='geometry-select-coordinator.c'
    assert component['source_sha256']==sha(component['source'])
    first=Path(author['directory']);second=Path(repair['directory']);first_prediction=read(first/'author.json');second_prediction=read(second/'author-repair.json')
    assert first_prediction['usage']['completion_tokens']==2599
    assert 'output_budget_near_limit'in first_prediction['quality_flags']
    assert 'Invalid memory read'in(second/'gate.log').read_text()
    now=datetime.now(timezone.utc);out=v/'native-geometry-select-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        path=Path(path).resolve();assert path.is_relative_to(ROOT);digest=sha(path);assert expected is None or digest==expected,str(path);target=path
        if path.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name);shutil.copy2(path,target);aliases[str(path)]=str(target)
        deps[str(target)]=digest
    for name in names:bind(v/name)
    for proof,key in [(component,'dependencies_sha256'),(build,'source_sha256')]:
        for path,digest in proof[key].items():bind(path,digest)
    for folder in [first,second,Path(component['directory']),Path(build['directory'])]:
        for path in folder.rglob('*'):
            if path.is_file() and path.suffix not in ['.cdi']:bind(path)
    # Bind derived stage/disc by their build identities without duplicating binaries.
    bind(build['derived_stage'],build['derived_stage_sha256']);bind(build['derived_disc'],build['derived_disc_sha256'])
    for path in [Path(__file__),ROOT/'scripts/native_geometry_select_observer.inc.c',ROOT/'scripts/run_biwn_native_geometry_select_route.py']:bind(path)
    transcript=ROOT/'reports/native-geometry-select-prompts-and-responses.txt'
    transcript.write_text('FIRST AUTHOR AND SAME-WEIGHT REVIEWER — BOTH REJECTED/UNRELIABLE\n'+(first/'prompts-and-responses.txt').read_text()+'\n\nONE BOUNDED REPAIR AND SAME-WEIGHT REVIEWER — REPAIR REJECTED\n'+(second/'prompts-and-responses.txt').read_text())
    bind(transcript)
    report=ROOT/'reports/native-geometry-select.txt'
    report.write_text('BIWN — COMPLETE NATIVE INDEXED GEOMETRY SELECTOR, ORIGINAL1039C\n'+now.isoformat()+'\n\n'
        'The complete indexed geometry selector now has a readable freestanding C implementation compiled to324native68000bytes with its register ABI wrapper. It preserves signed16 count/index behavior, negative indices admitted by the original, WORD shift truncation/sign extension, original volatile read/write widths/order, partial-register outputs and final X/CCR. This is a native port of a previously recovered host routine, not an additional discovered logical function.\n\n'
        'The accepted C is coordinator-written. The local27B Author first produced a2,599token response that exhausted its budget in comments and stopped mid-function; it did not compile. A single repair compiled but still used the wrong table dereference and failed on an invalid memory read. Both raw local candidates are rejected. Same-weight Reviewer responses were also truncated and included false statements about signed BGE, CLR flags, word-register writes and shift X; these are recorded model failures, not independent verification. The repair received explicit coordinator assembly corrections. No unchanged local output was accepted and no weights changed.\n\n'
        'The separate coordinator C/ABI passed896stable and256controlled changing-read comparisons against the original CPU, including full D/A/PC/SR/USP/SSP and public RAM plus exact ordered accesses. All46original instruction locations were exercised. The independent stable output contract also passed896untouched-original cases before generation. Maximum private stack use was112bytes. The original register-save area,8KBprivate scratch and code/entry windows are excluded from RAM identity. Controlled fixtures do not prove arbitrary aliases, faults, IRQ schedules or physical timing.\n\n'
        'The final linked selector passed the same896+256cases at its actual address plus96startup-loader cases. The experimental derived disc contains17,408resident bytes in the unchanged20,480byte reservation, retaining the prior17,084bytes exactly. Only the declared absolute kernel-call relocation changed the standalone code. Heap floor/reservation and original disc remain unchanged. The build is pending fresh gameplay comparison with a same-layout disc restoring only the original1039Centry. No full-game rebuild, physical console, cycle equivalence or preview promotion is established.\n\n'
        'The earlier cache-disc C-processor result and running boundary-disc C-processor job apply only to their identified discs; neither proves this new selector build.\n\nExact prompts and raw responses:\n'+str(transcript)+'\n')
    bind(report)
    result=dict(status='terminal_native_geometry_select_component_and_final_address_reviewed_pending_gameplay',recorded_at=now.isoformat(),directory=str(out),report=str(report),prompts_and_responses=str(transcript),source=component['source'],source_sha256=component['source_sha256'],authorship='Coordinator C/ABI/checks after two rejected local Author candidates',actual_local_predictions=4,raw_local_candidates_passed=0,raw_local_candidates_attempted=2,independent_model_review=False,new_native_port_count=1,new_logical_function_count=0,component_stable_cases=896,component_changing_cases=256,original_instruction_coverage=[46,46],linked_stable_cases=896,linked_changing_cases=256,startup_cases=96,native_bytes=324,resident_bytes=17408,reserved_bytes=20480,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False)
    save(out/'protocol.json',result);save(v/'native-geometry-select-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','resident_bytes','actual_local_predictions','report']}),flush=True)
if __name__=='__main__':main()
