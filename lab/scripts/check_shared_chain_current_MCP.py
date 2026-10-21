"""Fresh configured MCP read checks publication matches reviewed shared-chain proof."""
import json
from pathlib import Path
from datetime import datetime,timezone
from reference_mcp_bridge import ReferenceBridge,ROOT
from run_biwn_native_fast_gameplay_route import sha,save

def main():
 out=ROOT/'verification/shared-chain-current-MCP-read'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 with ReferenceBridge()as bridge:
  result=bridge.call('project_evidence',{'topic':'status'});connection=bridge.metadata
 assert result['status']=='terminal_native_geometry_status_v2_published'and result['experimental_build']['resident_bytes']==28448
 assert result['gameplay_comparison']['candidate_frames']==29808 and result['gameplay_comparison']['control_frames']==29804
 assert result['next_component_development']['prototype_cases']==6144 and not result['next_component_development']['disc_integrated']
 assert result['selector_outcomes']['actor']['successes']==14 and result['selector_outcomes']['sprite']['skipped_failures']==1
 assert not result['whole_game_complete']and not result['native_Chat_verified']and not result['physical_console_verified']
 save(out/'response.json',result);state=dict(status='terminal_actual_MCP_shared_chain_gameplay_publication_verified',directory=str(out),connection=connection,response=result,new_prediction=False,native_Chat_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),out/'response.json',Path(result['proof'])]})
 save(out/'protocol.json',state);save(ROOT/'verification/shared-chain-current-MCP-read-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=28448,tools=len(connection['tools']))))
if __name__=='__main__':main()
