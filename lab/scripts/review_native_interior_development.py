"""Bind the actual local development history and final linked component evidence."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from check_biwn_native_button_digit import ROOT, sha, save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';now=datetime.now(timezone.utc)
    out=v/'native-interior-development-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();dependencies={}
    def bind(path,expected=None,snapshot=False):
        p=Path(path).resolve();h=sha(p);assert expected is None or h==expected,str(p)
        target=p
        if snapshot or p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target)
        dependencies[str(target)]=h
        return target
    def pointer(name):
        p=v/name;bind(p);return read(p)
    author=pointer('local-native-interior-select-author-current.json')
    repair=pointer('local-native-interior-select-repair-current.json')
    selection=pointer('native-interior-select-selected-current.json')
    build=pointer('native-interior-select-disc-build-current.json')
    negative=pointer('native-interior-gate-negative-controls-current.json')
    assert not author['raw_kernel_gate_pass'] and repair['raw_repair_gate_pass']
    assert author['reviewer_issues']==repair['reviewer_issues']==0
    assert selection['raw_candidates_attempted']==2 and selection['raw_candidates_passed']==1
    assert not selection['accepted_local_body_edited'] and selection['actual_model_predictions']==4
    assert build['status']=='terminal_native_interior_select_disc_built_entry_verified_pending_gameplay'
    assert build['linked_component_bytes']==18888 and build['semantic_code_bytes']==616
    assert build['appended_bytes']==618 and build['entry_cases']==96
    assert build['component_bytes']==20480 and build['heap_start']==0x163dc0
    assert build['parent_resident_prefix_byte_identical'] and build['game_frames']==0
    parent=read(build['parent_build']);bind(build['parent_build'],build['parent_build_sha256'])
    assert Path(build['linked_component']).read_bytes()[:parent['linked_component_bytes']]==Path(parent['linked_component']).read_bytes()
    assert build['resident_address']+build['linked_component_bytes']<=build['heap_start']
    final=read(build['component_gate']);bind(build['component_gate'],build['component_gate_sha256'])
    assert final['stable_cases']==1958 and final['changing_cases']==768 and final['source_accepted']
    assert final['code_address']==build['interior_select_start']==0x163520
    assert final['original_instruction_coverage']=={'0':[60,60],'1':[39,39]}
    assert final['max_private_stack_bytes']==100
    for p,h in final['dependencies_sha256'].items():bind(p,h)
    assert len(final['before_execution_sha256'])>=9
    assert sha(selection['source'])==selection['source_sha256']==final['source_sha256']
    assert Path(selection['source']).read_bytes()==Path(repair['candidate']).read_bytes()
    assert len(negative['controls'])==2 and all(c['rejected_for_expected_defect']for c in negative['controls'])
    for row in negative['controls']:
        bind(row['source'],row['source_sha256']);bind(row['diagnostic'],row['diagnostic_sha256']);bind(row['proof'])
    for p,h in negative['source_sha256'].items():bind(p,h)
    for p,h in build['source_sha256'].items():bind(p,h)
    for name in ['derived_disc','derived_stage','linked_component','component']:
        bind(build[name],build.get(name+'_sha256'))
    bind(build['patch_manifest'],build['patch_manifest_sha256'])
    bind(Path(build['directory'])/'entry-cases.json')
    assert len(read(Path(build['directory'])/'entry-cases.json'))==96
    seconds=0;records=[];parts=[]
    for role,state,author_file in [('Initial Author/Reviewer',author,'author.json'),('One repair/Reviewer',repair,'author-repair.json')]:
        folder=Path(state['directory']);bind(folder/'protocol.json');bind(folder/'runner-as-run.py')
        for name in ['frozen-request.json','response.txt',author_file,'reviewer.json','reviewer-request.json','prompts-and-responses.txt','gate.log']:
            bind(folder/name)
        first=read(folder/author_file);second=read(folder/'reviewer.json')
        seconds+=first['seconds']+second['seconds']
        records.extend([dict(role=role+' author',request=str(folder/'frozen-request.json'),response=str(folder/'response.txt'),seconds=first['seconds']),
                        dict(role=role+' reviewer',request=str(folder/'reviewer-request.json'),response=str(folder/'reviewer.json'),seconds=second['seconds'])])
        parts.append((folder/'prompts-and-responses.txt').read_text())
        gp=Path(state['gate_proof']);bind(gp)
        gate=read(gp)
        for p,h in gate.get('dependencies_sha256',{}).items():bind(p,h)
    transcript=out/'prompts-and-responses.txt';transcript.write_text('\n\n'.join(parts)+'\n');bind(transcript)
    index=out/'prediction-index.json';save(index,records);bind(index)
    for p in [Path(__file__),ROOT/'scripts/author_biwn_native_interior_select_v2.py',
              ROOT/'scripts/repair_biwn_native_interior_select_v2.py',ROOT/'scripts/run_native_interior_select_model_trial.py']:
        bind(p)
    bind(ROOT/'Game Code Worker.command',snapshot=True)
    report=ROOT/'reports/native-interior-select-development.txt'
    report.write_text('BIWN — LOCAL-MODEL INTERIOR ACTOR/SPRITE SELECTORS\n'+now.isoformat()+'\n\n'
      'Complete already-recovered original10520..105D8 and105DA..10650 routines now have a shared native C component from '
      'the local27B base Author after one coordinator-guided repair. The repaired body is unchanged; only its complete '
      'outer Markdown fence was removed. The model used volatile scalar-width helpers rather than the requested struct '
      'fields. This prompt-compliance limitation is retained; native ABI and ordered-access semantics passed.\n\n'
      'The initial Author response began with an unclosed Markdown fence and failed compilation before semantic tests. '
      'Coordinator inspection also found uninitialized X state, reversed signed lower comparisons and missing full/partial '
      'D0 updates. These findings were supplied to the single repair; no coordinator implementation or fixture values '
      'were supplied. Both same-weight Reviewers returned no issues. Reviewer agreement is not independent evidence. '
      f'Four actual predictions took {seconds:.2f} seconds combined, excluding all tests/coordinator/build work.\n\n'
      'The repaired616byte component/private100byte stack passed1958stable+768changing-read fixtures, all99 original '
      'instruction sites (60actor/39sprite), full native D/A/PC/SR/USP/SSP and public2MBRAM, logical read/write width/value '
      'order and separate native/tracer publicRAM checks. Fixtures include signed16 bounds/counts,32768-entry scans, '
      'pointer tags, actor/record overlaps, both CPU stack modes/all32CCR, and changing header/record/origin reads. '
      'Private8KBstack, entry patches and isolated code are declared exclusions. Two deliberate defects were rejected '
      'for the intended reasons: wrong skipped-path X and an eliminated repeated record read.\n\n'
      'Final address163520 repeated1958+768cases using the parent installation. Exactly one absolute kernel-call '
      'relocation changes standalone bytes. The derived disc contains18888resident bytes, with618appended including '
      'two NOP alignment bytes, in the unchanged20480reserve/heapfloor163DC0;1592bytes remain. The previous18270byte '
      'prefix is byte-identical. The startup loader passed96cases, copying the complete payload, clearing staging, '
      'preserving CPU state and resuming400A. The derivedCDI has533changed bytes, all within declared append/entry '
      'patch ranges. This development receipt does not claim new logical-function recovery or model training gains.\n\n'
      'GAMEPLAY REMAINS UNTESTED ON THIS18888BYTE DISC. The latest published live build remains the18270doorway '
      'disc. The17812scanner C-processor route is terminal/equal24996frames/fullPCM on that exact disc; the separate '
      '18270doorway C-processor route is observed independently. Neither proves18888disc gameplay or physical console '
      'boot. Older scanner original-entry video/audio/timing differences remain unresolved. No default preview changes.\n\n'
      'Start Local AI → I: exact saved prompts/responses. Start Local AI →9→5: reusable interior-selector trial with '
      'one repair maximum, no automatic source adoption. The new wrapper has target/shell checks; its helpers were '
      'executed directly above, and the new wrapper itself has not had an additional full inference run. The initial '
      'prompt budget is raised to3000 for future runs. Saved roles are files, not verified LM Studio native Chat streaming.\n\n'
      'Disc: '+build['derived_disc']+'\nTranscript: '+str(transcript)+'\nComponent: '+str(Path(build['component_gate']))+'\n')
    bind(report)
    result=dict(status='terminal_local_native_interior_component_and_disc_reviewed_pending_gameplay',recorded_at=now.isoformat(),
                directory=str(out),report=str(report),transcript=str(transcript),prediction_index=str(index),
                actual_model_predictions=4,model_prediction_seconds=round(seconds,2),raw_candidates_attempted=2,
                raw_candidates_passed=1,accepted_local_body_edited=False,format_normalization=repair['format_normalization'],
                prompt_compliance_limit=selection['prompt_compliance_limit'],component_bytes=616,private_stack_bytes=100,
                stable_cases=1958,changing_cases=768,original_instruction_coverage=[99,99],resident_bytes=18888,
                reservation_bytes=20480,reservation_free_bytes=1592,entry_cases=96,derived_disc=build['derived_disc'],
                derived_disc_sha256=build['derived_disc_sha256'],build=str(Path(build['directory'])/'protocol.json'),
                dependencies_sha256=dependencies,game_frames=0,new_training=False,default_promoted=False,
                native_Chat_verified=False,physical_console_verified=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'native-interior-development-reviewed-current.json',result)
    print(json.dumps({k:result[k]for k in ['status','actual_model_predictions','resident_bytes','report']}))


if __name__=='__main__':main()
