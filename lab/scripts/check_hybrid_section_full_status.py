"""Check the final four-part status through the actual configured MCP entry."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
from run_biwn_native_fast_gameplay_route import sha,save

def main():
 out=ROOT/'verification/hybrid-section-full-status'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 with ReferenceBridge()as bridge:response=bridge.call('project_evidence',{'topic':'status'});connection=bridge.metadata
 assert response['experimental_build']['resident_bytes']==30036 and response['advertising_workflow_progress']['actual_local_predictions']==4 and response['advertising_workflow_progress']['trained_Reviewer_false_pass']
 assert response['frontend_progress']['tool_count']==18 and Path(response['frontend_progress']['entrypoint']).name=='chat_tools_current_v10.py'
 assert response['gameplay_comparison']['PCM_byte_equal']and not response['gameplay_comparison']['video_equal']and not response['whole_game_complete']
 save(out/'response.json',response);state=dict(status='terminal_actual_MCP_full_scope_hybrid_and_advertising_status_verified',directory=str(out),response=response,connection=connection,new_prediction=False,native_Chat_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),out/'response.json',Path(response['proof'])]});save(out/'protocol.json',state);save(ROOT/'verification/hybrid-section-full-status-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=30036,advertising_predictions=4,tool_count=18)))
if __name__=='__main__':main()
