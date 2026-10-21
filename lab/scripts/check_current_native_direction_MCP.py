"""Read current consistent direction/layout/scope facts from installed v11 MCP."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 out=ROOT/'verification/current-native-direction-MCP'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 with ReferenceBridge()as bridge:response=bridge.call('project_evidence',{'topic':'status'});connection=bridge.metadata
 save(out/'actual-response.json',response);save(out/'connection.json',connection);assert response['experimental_build']['resident_bytes']==30834 and response['layout_verification']['reservation_bytes']==31104 and response['layout_verification']['heap_floor']=='0x166740'and response['layout_verification']['staging_address']=='0xf6800'
 assert response['gameplay_comparison']['direction_completed_returns']==12474 and response['gameplay_comparison']['control_original_direction_completed_returns']==14255 and response['gameplay_comparison']['all_pending_zero']and not response['gameplay_comparison']['PCM_byte_equal']and response['gameplay_comparison']['PCM_common_prefix_equal']
 assert not response['whole_game_complete']and not response['physical_console_verified']and not response['native_Chat_verified']and response['frontend_progress']['entrypoint'].endswith('chat_tools_current_v11.py')
 assert response['migration_progress']['canonical_publication_snapshot_resident_bytes']==30036 and not response['migration_progress']['new_actor_direction_frontend_copied_to_cold_package']
 state=dict(status='terminal_actual_current_native_direction_MCP_status_pass',directory=str(out),resident_bytes=30834,tool_count=len(connection['tools']),response=str(out/'actual-response.json'),new_predictions=0,new_training=False,native_Chat_verified=False);save(out/'protocol.json',state);save(ROOT/'verification/current-native-direction-MCP-current.json',state);print(json.dumps(state))
if __name__=='__main__':main()
