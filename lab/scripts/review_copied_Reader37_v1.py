"""Review one real copied Reader response, retaining its artifact-type error."""
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
    qp=V/'queued-copied-Reader37-v1-current.json';queue=read(qp)
    assert queue['status']=='terminal_one_copied_Reader_attempt_pending_review'and queue['new_predictions']==1
    src=Path(queue['Reader_directory']);protocol=read(src/'protocol.json')
    assert protocol['new_predictions']==1 and protocol['words']==140 and protocol['word_limit_pass']
    response=(src/'response.txt').read_text();evidence=read(src/'evidence.json')
    assert all(x in response for x in ['5304','8481','168','560','zero of four'])
    assert evidence['pending_native_candidate'] is None
    assert evidence['latest_source_development']['profile']=='deck-outer-v31-inplace-v1'
    assert evidence['latest_source_development']['disc_integrated'] is False
    assert 'v31 pending image'in response
    out=V/'copied-Reader37-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    copied=out/'raw';subprocess.run(['/bin/cp','-cR',str(src),str(copied)],check=True,capture_output=True)
    for p in src.rglob('*'):
        if p.is_file():assert sha(p)==sha(copied/p.relative_to(src))
    (out/'prompts-and-responses.txt').write_text('ACTUAL COPIED READER37 — factual answer not fully approved\n\nNumeric facts and140-word format pass. It calls an unbuilt component prototype a pending image; no v31disc existed in its supplied evidence. No model training gain or Native Chat rendering claim.\n\n'+(src/'prompts-and-responses.txt').read_text())
    facts=dict(status='terminal_copied_Reader37_numeric_and_format_pass_artifact_type_error',directory=str(out),source_directory=str(src),model_identifier=protocol['model_identifier'],actual_predictions=1,new_predictions=0,recovered_completed_predictions=1,seconds=protocol['seconds'],words=140,word_limit_pass=True,numeric_facts_reviewed=True,factual_reply_approved=False,
        failure='Calls unintegrated v31 source component a pending image, although pending_native_candidate is null and no v31disc was built.',
        prompt_limitation='System asks for a distinction from any newer pending image; the next version makes artifact type explicit and forbids calling a source prototype an image.',new_training=False,optimizer_updates=0,native_Chat_verified=False,
        source_evidence_sha256=protocol['source_evidence_proof_sha256'],reply_is_current_after_new_source_changes=False)
    save(out/'facts.json',facts)
    dependencies={str(p):sha(p)for p in [Path(__file__),qp,*out.rglob('*')]if p.is_file()}
    facts['dependencies_sha256']=dependencies;atomic(V/'copied-Reader37-reviewed-v1-current.json',facts)
    print(facts['status'],out,flush=True)

if __name__=='__main__':main()
