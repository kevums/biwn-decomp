"""Review actual main-menuS local Reader delivery, preserving coverage omissions."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=ROOT/'verification/current-biwn-status-v12-reader-current.json';s=read(p);assert s['status']=='terminal_local_current_status_v12_pending_semantic_review'and s['rounds']==2 and len(s['tool_calls'])==1 and s['word_count']==144
 evidence=s['tool_calls'][0];assert evidence['experimental_build']['resident_bytes']==19460 and evidence['gameplay_comparison']['minimum_observed_context_clearance']==70
 assert len(evidence['processor_tests'])==5 and all(t['final_verdict_available']and not t['applies_to_latest_published_disc']for t in evidence['processor_tests'])
 answer=s['answer'];assert all(x in answer for x in ['19,460','856','96','12 actor routes','1 sprite route','zero full-pool','no new code predictions','14 actor successes','1 sprite skipped failure','Video, audio, and navigation do not match','older identified discs','134DC'])
 out=ROOT/'verification/gap320-status-delivery'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);report=ROOT/'reports/current-biwn-gap320-status-delivery.txt';assert not report.exists()
 omissions=['Retained native emulator processors not explicitly stated.','Full-pool/unreached-selector paths are not explicitly labeled component-only, though exact zero/live counts and remaining path work are stated.','Separate134DC1024case/1620byte proof and70byte clearance are omitted.','Advertising reliability and actual future-hardware/migration qualification omitted from the short answer.','Default preview remains unchanged but the Reader does not explicitly say so.']
 report.write_text('LOCAL STATUS — ACTUAL START LOCAL AI → S\n\n144words,19.19seconds,2localpredictionrounds,1actualconfiguredMCPcall,0Editorcalls.\n\n'+answer+'\n\nCoordinator review: core build/count/attribution/media/job-applicability claims match supplied evidence. This is a useful brief answer with coverage omissions, not a complete technical or full-goal audit.\n\nOmissions:\n'+'\n'.join('- '+x for x in omissions)+'\n\nCurrentChatwindow interaction remains unverified. This was a localSDK/stdioMCPinteraction, not independent multiagent review or new training. Published experimentaldisc19460is distinct from the unchanged interactive preview.\n')
 files=[Path(__file__),Path(s['directory'])/'protocol.json',Path(s['directory'])/'prompts-and-responses.txt',Path(s['directory'])/'answer.txt',ROOT/'runs/main-menu-gap320-status.log',report]
 record=dict(status='terminal_current_gap320_status_core_correct_with_coverage_omissions',directory=str(out),report=str(report),Reader_run=str(s['directory']),transcript=str(Path(s['directory'])/'prompts-and-responses.txt'),actual_predictions=2,actual_configured_MCP_calls=1,Editor_used=False,seconds=s['seconds'],words=144,core_claims_correct=True,omissions=omissions,native_Chat_verified=False,new_training=False,source_sha256={str(f):sha(f)for f in files})
 (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(ROOT/'verification/current-gap320-status-delivery-current.json').write_bytes((out/'protocol.json').read_bytes());print(json.dumps({k:record[k]for k in ['status','seconds','words','actual_predictions','actual_configured_MCP_calls']}))

if __name__=='__main__':main()
