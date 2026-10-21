"""Review the corrected artifact-type response against its actual v30 snapshot."""
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
    qp=V/'queued-copied-Reader38-v1-current.json';q=read(qp)
    assert q['status']=='terminal_one_copied_Reader_attempt_pending_review'and q['new_predictions']==1
    src=Path(q['Reader_directory']);state=read(src/'protocol.json');evidence=read(src/'evidence.json');response=(src/'response.txt').read_text()
    assert state['new_predictions']==1 and state['words']==127 and state['word_limit_pass']and state['seconds']==11.02
    assert evidence['experimental_candidate']['candidate_frames']==25001 and evidence['measured_heap_while_outer_active']==dict(candidate=560,control=560)
    assert evidence['latest_source_artifact_kind']=='source_component_prototype'and evidence['pending_native_candidate']is None
    assert 'not a disc image'in response and all(x in response for x in ['5304','8481','168','560','zero of four'])
    assert 'coordinator'not in response.lower()
    out=V/'copied-Reader38-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    subprocess.run(['/bin/cp','-cR',str(src),str(out/'raw')],check=True,capture_output=True)
    for path in src.rglob('*'):
        if path.is_file():assert sha(path)==sha(out/'raw'/path.relative_to(src))
    (out/'prompts-and-responses.txt').write_text('ACTUAL COPIED READER38 — supplied-snapshot facts and artifact type pass; current reply not verified\n\nOne prompt/evidence correction fixes the previously invented pending image. Generation11.02seconds,127words. Correct for its captured v30 snapshot, before compact-image publication. It omits the requested explicit code-authorship distinction; not a complete approved briefing, no held-out or trained-quality result.\n\n'+(src/'prompts-and-responses.txt').read_text())
    facts=dict(status='terminal_copied_Reader38_snapshot_facts_and_artifact_type_pass_authorship_omitted',directory=str(out),source_directory=str(src),actual_predictions=1,new_predictions=0,
        model_identifier=state['model_identifier'],generation_seconds=11.02,seconds=11.02,words=127,max_words=150,word_limit_pass=True,
        supplied_snapshot_factual_claims_approved=True,artifact_type_pass=True,code_authorship_statement_present=False,complete_requested_briefing_approved=False,
        current_compact_image_reply_verified=False,latest_source_changed_since_prediction=True,provided_candidate_profile='v30',provided_sampled_heap_bytes=560,
        source_evidence_sha256=state['source_evidence_proof_sha256'],new_training=False,optimizer_updates=0,trained_adapter_used=False,native_Chat_verified=False,
        scope='One development prompt correction, same copied model and supplied numeric facts. The reply is correct for its v30 evidence and no longer invents a pending image, but omits requested authorship and predates compact-image facts. This is not model-weight training or a general/held-out quality result. Generation time excludes the earlier queue wait; total launcher latency was not instrumented.')
    save(out/'facts.json',facts);facts['dependencies_sha256']={str(p):sha(p)for p in [Path(__file__),qp,*out.rglob('*')]if p.is_file()}
    atomic(V/'copied-Reader38-reviewed-v1-current.json',facts);print(facts['status'],out,flush=True)

if __name__=='__main__':main()
