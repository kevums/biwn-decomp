"""Use the actual installed MCP: new direction task plus retained source retrieval."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 out=ROOT/'verification/configured-actor-direction-frontend'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 with ReferenceBridge()as bridge:
  task=bridge.call('get_game_function_task',{'routine':'actor_direction'});save(out/'actual-direction-task.json',task);assert task['routine']=='actor_direction'and task['original_ABI_component_cases']==2560 and not task['gold_C_supplied']
  source=bridge.call('search_references',dict(domain='advertising',query='Schreiner2026 Study2A AI aversion measurement timing',max_chunks=4));save(out/'actual-advertising-source-response.json',source);assert{9,20}<={x['pdf_page']for x in source['source_section_evidence']}
  status=bridge.call('project_evidence',{'topic':'status'});save(out/'actual-status-response.json',status);assert status['experimental_build']['resident_bytes']==30036;connection=bridge.metadata
 save(out/'connection.json',connection);assert len(connection['tools'])==18
 state=dict(status='terminal_actual_configured_direction_task_source_retrieval_and_status_pass',directory=str(out),tool_count=18,new_predictions=0,new_training=False,native_Chat_verified=False);save(out/'protocol.json',state);save(ROOT/'verification/configured-actor-direction-frontend-current.json',state);print(json.dumps(state))
if __name__=='__main__':main()
