"""Verify actual configured MCP serves current hybrid status and primary source sections."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
from run_biwn_native_fast_gameplay_route import sha,save

def main():
 out=ROOT/'verification/hybrid-section-current-MCP'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 with ReferenceBridge()as bridge:
  status=bridge.call('project_evidence',dict(topic='status'));references=bridge.call('search_references',dict(domain='advertising',query='Schreiner2026 Study2A design procedure AI aversion measurement',max_chunks=4));connection=bridge.metadata
 assert status['experimental_build']['resident_bytes']==30036 and status['gameplay_comparison']['PCM_byte_equal']and status['gameplay_comparison']['all_field_difference_counts']['video_sha256']==1404
 assert status['hybrid_integration']['live_returns']==4 and not status['hybrid_integration']['raw_local_output_adopted']and not status['whole_game_complete']and not status['physical_console_verified']
 assert status['selector_outcomes']['sprite']['skipped_failures']==status['selector_outcomes']['sprite']['non_skipped_failures']==1
 assert {9,20}<={row['pdf_page']for row in references['source_section_evidence']}and len(connection['tools'])==18
 save(out/'status.json',status);save(out/'references.json',references);state=dict(status='terminal_actual_MCP_hybrid_and_source_sections_verified',directory=str(out),connection=connection,response=status,source_section_pages=[r['pdf_page']for r in references['source_section_evidence']],new_predictions=0,native_Chat_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),out/'status.json',out/'references.json',Path(status['proof'])]});save(out/'protocol.json',state);save(ROOT/'verification/hybrid-section-current-MCP-current.json',state);print(json.dumps(dict(status=state['status'],resident_bytes=30036,tool_count=18,PCM_equal=True,section_pages=state['source_section_pages'])))
if __name__=='__main__':main()
