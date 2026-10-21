"""Record actual scanner model outputs and the selected coordinator implementation."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    now=datetime.now(timezone.utc);v=ROOT/'verification';out=v/'native-geometry-scan-development-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    names=['local-native-geometry-scan-author-current.json','local-native-geometry-scan-repair-current.json','local-native-geometry-scan-q3-current.json'];rows=[];transcripts=[];runs=[]
    for name in names:
        p=v/name;d=json.loads(p.read_text());bind(p);folder=Path(d['directory']);runs.append(d)
        assert d['gate_exit_code']==1 and d['native_cases']==d['changing_cases']==0
        assert not d.get('raw_kernel_gate_pass',d.get('raw_repair_gate_pass',True))
        bind(d['candidate'],d['candidate_sha256']);gp=Path(d['gate_proof']);g=json.loads(gp.read_text());assert g['status']=='terminal_failed';bind(gp)
        for fname in ['ordered-mismatch.json','mismatch.json']:
            if (gp.parent/fname).exists():bind(gp.parent/fname)
        for f in folder.iterdir():
            if f.is_file():bind(f)
        transcripts.append(('SOURCE: '+str(folder/'prompts-and-responses.txt')+'\n').encode()+(folder/'prompts-and-responses.txt').read_bytes())
        for fname,role in [('author.json','Author'),('author-repair.json','Author repair'),('reviewer.json','Reviewer')]:
            f=folder/fname
            if not f.exists():continue
            dcall=json.loads(f.read_text());request=dcall.get('request')
            if request is None:request=json.loads((folder/'reviewer-request.json').read_text())
            rows.append(dict(role=role,model=request.get('model','advertising-scholar'),seconds=dcall['seconds'],response=str(f),response_sha256=sha(f),request_source=str(f if 'request'in dcall else folder/'reviewer-request.json'),endpoint=dcall.get('endpoint','local LM Studio SDK'),independent_review=False if role=='Reviewer'else None))
    assert len(rows)==5
    # The fresh coder run reuses the exact original task, without repair examples.
    original=json.loads((Path(runs[0]['directory'])/'frozen-request.json').read_text());fresh=json.loads((Path(runs[2]['directory'])/'frozen-request.json').read_text())
    for key in ['system','user','max_output_tokens']:assert original[key]==fresh[key],key
    assert runs[2]['daily_model_restored'] and not runs[2]['resource_guard_bypassed']
    selectionp=v/'native-geometry-scan-selected-current.json';selection=json.loads(selectionp.read_text());bind(selectionp)
    assert selection['status']=='terminal_scanner_kernel_component_reviewed' and selection['raw_local_candidates_attempted']==3 and selection['raw_local_candidates_passed']==0
    for p,h in selection['dependencies_sha256'].items():bind(p,h)
    componentp=Path(selection['component_proof']);component=json.loads(componentp.read_text());assert component['source_accepted'] and component['native_cases']==1377 and component['changing_coordinate_cases']==768 and component['original_instruction_coverage']==[69,69]
    for p,h in component['dependencies_sha256'].items():bind(p,h)
    buildp=v/'native-geometry-scan-disc-build-current.json';build=json.loads(buildp.read_text());bind(buildp)
    assert build['status']=='terminal_native_geometry_scan_disc_built_entry_verified_pending_gameplay' and build['linked_component_bytes']==17812 and build['linked_native_cases']==1377 and build['linked_changing_coordinate_cases']==768
    bind(build['derived_disc'],build['derived_disc_sha256']);bind(build['derived_stage'],build['derived_stage_sha256']);bind(build['linked_component'])
    for p,h in build.get('dependencies_sha256',{}).items():bind(p,h)
    transcript=ROOT/'reports/native-geometry-scan-prompts-and-responses.txt';transcript.write_bytes(b'\n\n'.join(transcripts));bind(transcript)
    index=ROOT/'reports/native-geometry-scan-prediction-index.json';save(index,dict(predictions=rows,count=len(rows),combined_seconds=sum(x['seconds']for x in rows),source='Local LM Studio responses; coordinator test/build/observer work excluded',new_training=False,native_Chat_verified=False));bind(index)
    report=ROOT/'reports/native-geometry-scan-development.txt';report.write_text('BIWN — COMPLETE102C4 NATIVE SCANNER AND LOCAL OUTPUT TEST\n'+now.isoformat()+'\n\n'
      'The complete reverse scan is now compiled as a428byte native68000 component, linked with two bytes of alignment after the preceding17382byte resident to produce17812resident bytes in the existing20480byte reservation. The original sector/table indirection, count-1 signed WORD boundary, reverse first-match order,32768entry complete miss, partial registers, X/carry retention, tagged pointers and repeated volatile read widths/order are preserved by the selected coordinator implementation.\n\n'
      'All three raw local candidates were rejected. The first27B Author failed ordered access case0; its one guided repair failed fullCPU/RAM case0. The separate-context same-weight first Reviewer raised unreliable issues; the schema-constrained second Reviewer returned {} despite a real failing candidate. Schema validity is not semantic correctness. One fresh Qwen3CoderNext GGUF Q3_K_XL response to the exact original task also failed ordered access case0. No raw local scanner C was accepted. No second repair or coding-model Reviewer was run.\n\n'
      f"Five actual local predictions took {sum(x['seconds']for x in rows):.2f} seconds combined: Author35.56s, Reviewer35.62s, repair37.16s, constrained Reviewer8.86s, fresh coder10.84s. This excludes model loading, compilation, testing and coordinator work. The coder fit32Kcontext/oneworker under the normal resource guard after temporarily unloading the idle daily base, which was restored. This single development task does not establish model ranking, independent review or training gain.\n\n"
      'The coordinator C/layout/bounds helper/ABI and linked addresses passed1377stable+768changing-read fixtures with all69original instruction sites reached, and96startup fixtures. No new logical recovered function is counted merely for this native adaptation. Stable-only live monitor qualification and fresh native gameplay are separate evidence. Preceding-disc C-processor comparisons do not verify this scanner disc. Physical console boot, complete readable whole-game source rebuild, native LM Studio Chat display and default preview promotion remain unverified. No weights changed.\n\nExact prompts and responses:\n'+str(transcript)+'\nPrediction index:\n'+str(index)+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_native_geometry_scan_development_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),transcript=str(transcript),prediction_index=str(index),new_local_predictions=5,raw_local_candidates_attempted=3,raw_local_candidates_passed=0,selected_kernel_attribution=selection['kernel_attribution'],stable_cases=1377,changing_cases=768,original_instruction_coverage=[69,69],native_bytes=428,resident_bytes=17812,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'native-geometry-scan-development-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','new_local_predictions','raw_local_candidates_passed','report']}))
if __name__=='__main__':main()
