"""Repeatable read-only evidence/source audit; writes only its own receipt."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import native_format_evidence
def sha(p):
 with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def main():
 pp=ROOT/'verification/native-number-publication-current.json';pub=read(pp)
 fp=ROOT/'verification/native-number-operator-followup-current.json';follow=read(fp)
 assert follow['status']=='terminal_native_number_operator_followup_integrity_and_scoped_review_pass'
 assert follow['publication_sha256']==sha(pp)
 tables=[pub['status_dependencies_sha256'],pub['dependencies_sha256'],follow['dependencies_sha256']]
 for table in tables:
  for p,h in table.items():assert sha(p)==h,p
 assert sha(follow['runtime_frontend'])==follow['runtime_frontend_sha256']==sha(ROOT/'native_format_evidence.py')
 current=native_format_evidence.load(ROOT);assert current.pop('proof_sha256')==sha(pp)and current==pub['current_status']
 reader=read(Path(follow['reader_directory'])/'protocol.json');observed=dict(reader['calls'][0]['result'])
 assert observed.pop('proof_sha256')==sha(pp)and observed==current
 assert not reader['answer_review_flags']and reader['answer']==follow['answer']and len(reader['calls'])==1
 review=read(follow['semantic_review']);assert review['answer_sha256']==hashlib.sha256(reader['answer'].encode()).hexdigest()
 if 'Editor'in reader:
  editor=reader['Editor'];assert editor['same_weights_as_Reader']and not editor['independent_review']and not editor['flags']
  assert all(len(v)<=180 for v in editor['structured_fields'].values())
  assert reader['answer']==' '.join(editor['structured_fields'][k].strip()for k in ['build','checks','gameplay','limits'])
  assert reader['Reader_draft_flags']==['word_limit_exceeded']
 allpaths=set().union(*(set(t)for t in tables))
 result=dict(status='terminal_native_number_game_core_and_operator_integrity_verified',publication=str(pp),publication_sha256=sha(pp),game_core_files=len(pub['status_dependencies_sha256']),all_checked_files=len(allpaths),integrity_mismatches=0,local_workflow_seconds=reader['seconds'],local_workflow_words=len(reader['answer'].split()),actual_MCP_calls=1,roles=follow['roles'],same_weights=True,independent_review=False,initial_Reader_word_limit_pass=False,structured_Editor_final_pass=True,coordinator_semantic_review_scope='One guided current-status output; broad reliability not established.',new_tests_or_model_restarts=False,source_or_publication_mutations=False,new_training=False,default_promoted=False,goal_complete=False)
 (ROOT/'verification/native-number-operator-final-verification-current.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
