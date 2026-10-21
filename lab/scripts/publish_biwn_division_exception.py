"""Publish an exception component without implying fresh-game installation."""
import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(path):return json.loads(Path(path).read_text())

def main():
    baseline=ROOT/'verification/CPU-division-native-check/20261018T233842.613794Z/protocol.json'
    old=read(baseline);assert old['cases']==old['failed_cases']==11264
    paths={name:ROOT/'verification'/(name+'-current.json') for name in ['CPU-division-provider-build','CPU-division-native-check','CPU-division-owner-check','CPU-divzero-host-guards','divzero-Code-Author','divzero-Code-Author-compact','divzero-local-C-review']}
    proof={name:read(p) for name,p in paths.items()}
    gate=proof['CPU-division-native-check'];owner=proof['CPU-division-owner-check'];guards=proof['CPU-divzero-host-guards'];author=proof['divzero-Code-Author-compact'];build=proof['CPU-division-provider-build']
    assert gate['status']=='terminal_division_CPU_native_pass' and gate['cases']==34944 and gate['failed_cases']==0
    assert owner['status']=='terminal_strict_C_division_exception_RTE_pass' and owner['roundtrips']==11264 and owner['C_rejections']==owner['C_original_opcode_fallback']==0
    assert guards['cases']==22 and guards['status']=='terminal_local_divzero_host_guards_pass'
    old_author=proof['divzero-Code-Author'];old_response=read(Path(old_author['directory'])/'response.json')
    assert old_response['stats']['stopReason']=='maxPredictedTokensReached' and old_author['status']=='terminal_divzero_author_failed'
    source=Path(author['source']);assert sha(source)==author['source_text_sha256']
    now=datetime.now(timezone.utc);out=ROOT/'verification/CPU-division-exception-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    parentp=ROOT/'verification/native-formatter-C-processors-publication-current.json';parent=read(parentp)
    deps=dict(parent['status_dependencies_sha256'])
    def add(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT),str(p);h=sha(p)
        assert expected is None or h==expected,str(p)
        if str(p)in deps:assert deps[str(p)]==h,str(p)
        deps[str(p)]=h
    # Bind the immutable parent publication rather than its advancing pointer.
    parent_snapshot=Path(parent['directory'])/'publication.json';assert sha(parent_snapshot)==sha(parentp);add(parent_snapshot)
    add(baseline)
    for p,h in old['source_sha256'].items():add(p,h)
    for p in Path(old['directory']).iterdir():
        if p.is_file():add(p)
    for name,p in paths.items():
        d=proof[name]
        # Current pointers are frozen as bytes alongside immutable protocols.
        # These component pointers remain unchanged by later gameplay runs.
        add(p)
        sources=d.get('source_sha256',{})
        if isinstance(sources,dict):
            for p,h in sources.items():add(p,h)
        elif isinstance(sources,str):add(d['source'],sources)
        if d.get('directory'):
            for p in Path(d['directory']).iterdir():
                if p.is_file():add(p)
    directory=Path(build['directory']);native=read(directory/'native-CPU-candidate.json')
    add(directory/'native-CPU-candidate.json');add(Path(native['directory'])/'fast_CPU_bridge.c');add(Path(native['library']))
    export=ROOT/'projects/black-ice-white-noise/restoration/experimental/division-exceptions-C'
    assert (export/'biwn_divzero_entry.c').read_bytes()==source.read_bytes()
    save(export/'provenance.json',dict(local_source=str(source),source_sha256=sha(source),author_protocol=str(Path(author['directory'])/'protocol.json'),publication=str(out/'publication.json'),new_training=False,source_unedited=True))
    for p in export.rglob('*'):
        if p.is_file():add(p)
    for name in ['biwn_scheduler.h','biwn_world_update.h','biwn_input_dispatch_cpu.h']:
        add(ROOT/'projects/black-ice-white-noise/restoration'/name)
    add(Path(__file__))
    for p,h in deps.items():assert sha(p)==h,p
    current=dict(status='terminal_division_exception_component_and_local_C_verified',recorded_at=now.isoformat(),
        problem='The prior C CPU provider rejects zero divisors and its cost model returns-1 instead of entering native vector5.',
        baseline_zero_cases_rejected=11264,fixed_instruction_entries=28,variable_divisor_entries=22,
        native_CPU_RAM_cost_cases=34944,zero_divisor_cases=11264,native_mismatches=0,
        strict_C_owner_exception_RTE_roundtrips=11264,instruction_boundaries=22528,original_opcode_fallback=0,rejections=0,host_guards=22,
        local_Code_Author=dict(model_identifier=author['model_identifier'],source=str(export/'biwn_divzero_entry.c'),source_sha256=sha(source),
            seconds=author['seconds'],exact_prompts_and_response=str(Path(author['directory'])/'prompts-and-responses.txt'),
            source_unedited=True,explicit_coordinator_contract=True,independent_review=False,same_weights_as_other_roles=True,
            first_reply=dict(seconds=old_response['seconds'],accepted=False,reason='Invalid JSON at output limit; task repeated in assumptions, no complete C produced.')),
        coordinator_contribution='Fixed28-address DIVU/DIVS provider, normal/overflow math, unsigned INT_MIN magnitude cost repair, zero-divisor pinned instruction charge, wrapper/bridge, fixtures, review and packaging.',
        source_export=str(export),native_CPU_candidate=str(directory/'native-CPU-candidate.json'),
        source_and_cost_candidate_scope='Isolated host C provider. Existing live preview/default runtime and currently running merchant test retain their prior backend.',
        fresh_gameplay_with_division_candidate_verified=False,whole_game_complete=False,physical_console_verified=False,
        original_game_function_recovery_claimed=False,new_training=False,default_promoted=False,
        scope='28 fixed addresses, controlled valid-RAM operands/stack/vector; allCCR,bothCPU modes,allIPL on zero cases. Native CPU/2MBRAM/pinned emulator instruction charge and strict owner exception/RTE. No arbitrary faults/aliasing,asyncIRQ or physical timing proof.')
    report=ROOT/'reports/BIWN-division-exceptions-and-local-Code-Author.txt';current['report']=str(report)
    report.write_text(f'''BIWN DIVISION EXCEPTIONS AND LOCAL CODE AUTHOR
{now.isoformat()}

The experimental host C CPU now has a separately checked division provider. The old provider rejects all11,264zero-divisor fixtures; the new candidate matches native execution in34,944division fixtures, including11,264zero cases, with full CPU state, all2MBRAM and the pinned emulator instruction charge equal. It covers28fixed DIVU/DIVS addresses,22with variable divisors. Immediate divisors retain their original instruction values.

The strict CPU-owner bridge also passes11,264actual divide-by-zero / DE06 RTE roundtrips at22,528instruction boundaries with0originalCPUopcodefallback/rejections. The exception stack and restored CPU/RAM/cost match the original CPU at both boundaries. All32CCRvalues,bothCPU modes and all8interrupt masks are exercised. These are controlled fixtures, not asynchronous IRQ, arbitrary fault or physical68000timing proof. The pinned emulator's exception charge is preserved even where it is not a hardware timing claim.

LOCAL MODEL
The same27B6bit local Code Author produced the exception-entry function in{author['seconds']:.2f}seconds after a compact prompt with an explicit coordinator contract. Its C text was accepted without edits after source review, the native/owner gates and22host guards. It clearsV before saving SR, switches user/supervisor stack correctly, pushes resumePC then oldSR, reads vector5after stacking, and requests a prefetch flush. Host-error cases retain earlier bus writes but leave the callerCPUobject unchanged.

The first request took{old_response['seconds']:.2f}seconds and failed at the output limit with invalidJSON. It repeated task metadata instead of delivering complete code; it was not compiled or accepted. The successful prompt removes that metadata and requests one source field. This is a guided workflow result, not new weight training, independent review or newly recovered original-game source.
First prompt/response: {old_author['directory']}
Compact prompt/response: {author['directory']}

The coordinator wrote the28-address normal/overflow division wrapper, repaired zero-divisor and INT_MIN cost edges, compiled the bridge and ran/reviewed the native comparisons. Compiler/emulator processes are tools.

Reusable unedited helper, header, Makefile and provenance:
{export}

This component has NOT been installed in the existing preview or the active combined-processor merchant/return test. Its fresh-gameplay integration is a separate next step. The long test keeps its original pinned candidate so its result cannot silently change mid-run. Original disc and accepted defaults are unchanged.

Full game/source/platform restoration, more scenes and exception/IRQ behavior, authenticated console boot, physical audio, representative model training gains and future hardware testing remain unfinished.
''')
    add(report)
    publication=dict(status=current['status'],directory=str(out),recorded_at=now.isoformat(),current_status=current,
        status_dependencies_sha256=deps,integrity_mismatches=0,report=str(report),new_training=False,default_promoted=False,goal_complete=False)
    save(out/'publication.json',publication);save(ROOT/'verification/CPU-division-exception-publication-current.json',publication)
    print(json.dumps(dict(status=current['status'],files=len(deps),integrity_mismatches=0,local_C_seconds=author['seconds'],report=str(report))),flush=True)

if __name__=='__main__':main()
