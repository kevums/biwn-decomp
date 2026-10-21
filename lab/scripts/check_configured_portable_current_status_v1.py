"""Read current portable acceptance through the actual installed reference MCP."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 out=V/'configured-portable-current-status'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 publication=read(V/'current-biwn-latest-publication-current.json')
 failures=[p for p,h in publication['dependencies_sha256'].items()if not Path(p).is_file()or sha(p)!=h]
 save(out/'publication-integrity.json',dict(files=len(publication['dependencies_sha256']),failures=failures));assert not failures,failures
 config=Path.home()/'.lmstudio/mcp.json';before=sha(config)
 with ReferenceBridge()as bridge:
  status=bridge.call('project_evidence',{'topic':'status'});save(out/'actual-status.json',status)
  assert status['experimental_build']['resident_bytes']==32980
  migration=status['migration_progress'];assert migration['actual_predictions']==12 and migration['actual_training_updates']==1
  assert migration['live_daily_model_restored']and not migration['full_portable_workflow_complete']
  assert status['portable_model_output_progress']['Advertising_source_errors_and_Reviewer_falsepasses_retained']
  task=bridge.call('get_game_function_task',{'routine':'gpu_mailbox'});save(out/'actual-gpu-task.json',task);assert task['arena_component_cases']==2512 and not task['gold_C_supplied']
  source=bridge.call('search_references',dict(domain='advertising',query='Schreiner2026 Study2A AI aversion measurement timing',max_chunks=4));save(out/'actual-source.json',source);assert{9,20}<={x['pdf_page']for x in source['source_section_evidence']}
  connection=bridge.metadata
 save(out/'connection.json',connection);assert len(connection['tools'])==18 and sha(config)==before
 state=dict(status='terminal_actual_configured_portable_current_status_sources_and_bound_integrity_pass',directory=str(out),bound_files=len(publication['dependencies_sha256']),tool_count=18,actual_predictions=12,actual_unpromoted_training_updates=1,new_predictions=0,new_training=False,native_Chat_verified=False,live_MCP_unchanged=True,publication_directory=publication['directory'],source_sha256={str(Path(__file__)):sha(__file__)})
 save(out/'protocol.json',state);save(V/'configured-portable-current-status-current.json',state);print(json.dumps(state))
if __name__=='__main__':main()
