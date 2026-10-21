"""Freeze local native10430authorship, component/build gates and exact messages."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';ap=v/'local-native-doorway-author-current.json';rp=v/'local-native-doorway-repair-current.json';a,b=read(ap),read(rp)
    assert not a['raw_kernel_gate_pass'] and b['raw_repair_gate_pass'];assert a['reviewer_schema_valid'] and a['reviewer_issues']==0
    gp=Path(b['gate_proof']);g=read(gp);assert g['source_accepted'] and g['native_cases']==2025 and g['changing_coordinate_cases']==768 and g['original_instruction_coverage']==[75,75]
    sp=v/'native-doorway-selected-current.json';selected=read(sp);assert selected['source_sha256']==b['candidate_sha256']==g['source_sha256']==sha(selected['source']) and selected['raw_local_candidates_passed']==1
    bp=v/'native-doorway-disc-build-current.json';build=read(bp);assert build['status']=='terminal_native_doorway_disc_built_entry_verified_pending_gameplay' and build['linked_component_bytes']==18270 and build['linked_native_cases']==2025 and build['linked_changing_coordinate_cases']==768 and build['entry_cases']==96
    mp=v/'native-doorway-monitor-current.json';monitor=read(mp);assert monitor['status']=='terminal_doorway_live_oracle_stable_fixtures_pass' and monitor['original_cases']==monitor['compiled_cases']==2025
    now=datetime.now(timezone.utc);out=v/'native-doorway-development-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [ap,rp,gp,sp,bp,mp]:bind(p)
    for d in [selected,g]:
        for p,h in d['dependencies_sha256'].items():bind(p,h)
    for p,h in monitor['source_sha256'].items():bind(p,h)
    for p,h in build['source_sha256'].items():bind(p,h)
    for name in ['derived_disc','derived_stage','component','linked_component','patch_manifest']:bind(build[name],build.get(name+'_sha256'))
    for name in ['final-address-cases.json','final-address-changing-cases.json','entry-cases.json','doorway-disassembly.txt','relocations.txt','body-relocations.txt']:bind(Path(build['directory'])/name)
    predictions=[];transcripts=[]
    for d,author_name,role in [(a,'author.json','Author'),(b,'author-repair.json','one repair Author')]:
        folder=Path(d['directory'])
        for p in folder.iterdir():
            if p.is_file():bind(p)
        transcripts.append(('SOURCE: '+str(folder/'prompts-and-responses.txt')+'\n').encode()+(folder/'prompts-and-responses.txt').read_bytes())
        for name,label in [(author_name,role),('reviewer.json','Reviewer')]:
            p=folder/name;x=read(p);request=x.get('request',{})
            predictions.append(dict(role=label,model=request.get('model','advertising-scholar'),response=str(p),response_sha256=sha(p),seconds=x['seconds'],same_weight_review=label=='Reviewer',independent_review=False))
    assert len(predictions)==4
    transcript=ROOT/'reports/native-doorway-prompts-and-responses.txt';transcript.write_bytes(b'\n\n'.join(transcripts));bind(transcript)
    index=ROOT/'reports/native-doorway-prediction-index.json';save(index,dict(count=4,predictions=predictions,combined_seconds=sum(x['seconds']for x in predictions),source='Actual sequential LM Studio local calls; coordinator work/load/build/test time excluded',new_training=False,native_Chat_verified=False));bind(index)
    for name in ['Game Code Worker.command','config/current-model-work-sources.json']:
        p=ROOT/name;target=snap/p.name;shutil.copy2(p,target);bind(target)
    for name in ['scripts/run_native_doorway_model_trial.py','scripts/author_biwn_native_doorway.py','scripts/repair_biwn_native_doorway_once.py']:bind(ROOT/name)
    report=ROOT/'reports/native-doorway-development.txt';report.write_text('BIWN — LOCAL-MODEL NATIVE DOORWAY10430 PORT\n'+now.isoformat()+'\n\n'
      'The selected native kernel is the local27B Author\'s complete C after one coordinator-guided repair. The repaired body was copied byte-identically into doorway-kernel.c; only the outer Markdown fence was stripped before compilation. No manual body edits or cleanup were applied. A duplicate stdint include remains despite the no-extra-include prompt, so this behavioral pass is not perfect prompt-format adherence. The coordinator supplied the recovered full contract, typed field layout, native register ABI, original-opcode verifier, integration and a separate withheld golden reference. The earlier local portable body was supplied as narrower-contract reference.\n\n'
      'The first draft compiled but failed ordered-read case0: it treated the table slot as the header and omitted its LONG pointer load. The same-weight Reviewer returned an empty issue array despite this real error. One repair received the actual mismatch and a source explanation of1044E. It then passed2025stable+768changing-read full CPU/SR/USP/SSP/publicRAM and logical ordered-access cases, including signed index/count, sentinel/carry, valid/invalid directions, byte sign extension, tagged pointers and nine actor/record overlaps. All75original instruction sites were reached. Native and traced publicRAM were independently compared on both sides, using width-correct external changes. The second same-weight Reviewer returned no issues; it is not independent verification.\n\n'
      f"Four actual local predictions took {sum(x['seconds']for x in predictions):.2f} seconds combined, including Author{a['author_seconds']:.2f}s and repair{b['author_seconds']:.2f}s. The daily local27Bbase used32Kcontext/oneworker, temperature0 and reasoningoff. This is a supported seen-assembly development task; no new weights, training gain, model ranking or independent benchmark is established.\n\n"
      'The repaired component is458bytes/private stack80bytes. Its final-linked2025+768cases and96startup cases pass in an18270byte resident, preserving the preceding17812byte scanner prefix,20480byte reservation and heap floor. Original CDI is unchanged. The read-only live monitor was qualified on2025original and2025compiled stable fixtures, with shadow writes preserving record/actor overlap. Fresh native candidate/original-entry gameplay runs are separate and not accepted by this component receipt. The earlier17812byte scanner C-processor test remains separately scoped. No default preview promotion, physical console boot, arbitrary fault/IRQ/timing or full-game source rebuild claim.\n\n'
      'Start Local AI ->9 ->4 exposes a repeatable Author/Reviewer/verifier trial with one repair maximum and no automatic source adoption. The Author/repair steps above were run individually; the new wrapper has check-only target/dispatch validation, not another fresh full-model run. Native Chat display remains unverified. Exact prompts and responses:\n'+str(transcript)+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_native_doorway_local_repair_development_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),transcript=str(transcript),prediction_index=str(index),raw_candidates_attempted=2,raw_candidates_passed=1,local_prediction_count=4,kernel_attribution=selected['kernel_attribution'],accepted_local_body_edited=False,format_normalization=selected['format_limit'],stable_cases=2025,changing_cases=768,original_instruction_coverage=[75,75],native_bytes=458,private_stack_bytes=80,resident_bytes=18270,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'native-doorway-development-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','raw_candidates_passed','local_prediction_count','report']}))
if __name__=='__main__':main()
