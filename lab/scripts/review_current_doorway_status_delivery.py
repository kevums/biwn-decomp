"""Review actual menuS output and the four-job configured MCP response."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';p=v/'current-biwn-status-v11-reader-current.json';d=read(p);assert d['status']=='terminal_local_current_status_v11_pending_semantic_review' and d['rounds']==2 and len(d['tool_calls'])==1 and not d.get('Editor') and not d['automatic_format_flags']
    facts=d['tool_calls'][0];assert facts['experimental_build']['resident_bytes']==18270 and facts['local_authorship']['raw_repair_pass'] and facts['local_authorship']['accepted_unchanged_local_output']
    assert len(facts['processor_tests'])==4 and len(d['MCP_connection']['tools'])==18
    assert all(not x['applies_to_latest_published_disc']for x in facts['processor_tests'][:3]) and facts['processor_tests'][3]['applies_to_latest_published_disc']
    assert all(x['status']=='running_verified'for x in facts['processor_tests'][2:]) and all(x['final_verdict_available']for x in facts['processor_tests'][:2])
    assert facts['gameplay_comparison']['live_success_returns']==1 and facts['gameplay_comparison']['live_failure_returns']==0 and facts['gameplay_comparison']['video_equal'] and facts['gameplay_comparison']['PCM_byte_equal']
    assert d['word_count']==140
    now=datetime.now(timezone.utc);out=v/'current-doorway-status-delivery'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path):
        q=Path(path).resolve();assert q.is_relative_to(ROOT);h=sha(q);target=q
        if q.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(q).encode()).hexdigest()[:12]+'-'+q.name);shutil.copy2(q,target);aliases[str(q)]=str(target)
        deps[str(target)]=h
    bind(p);folder=Path(d['directory'])
    for q in folder.rglob('*'):
        if q.is_file():bind(q)
    menu=sorted((ROOT/'runs').glob('main-menu-doorway-status-v11-*'))[-1]
    assert read(menu/'driver.json')['exit_code']==0
    for q in menu.iterdir():
        if q.is_file():bind(q)
    for name in ['current_biwn_evidence_v6.py','chat_tools_current_v6.py','scripts/ask_biwn_current_status_v11.py','scripts/install_frontend_current_v6.py','biwn_status_brevity_v5.py']:bind(ROOT/name)
    for label,name in [('main-menu','Start Local AI.command'),('current-command','BIWN Current Status.command'),('code-worker','Game Code Worker.command'),('bootstrap','Bootstrap.command'),('source-list','config/current-model-work-sources.json')]:
        source=ROOT/name;target=snap/(label+'-'+source.name);shutil.copy2(source,target);bind(target)
    for name in ['current_biwn_evidence_v2.py','current_biwn_evidence_v4.py','current_biwn_evidence_v5.py','current_biwn_evidence_v6.py','chat_tools_current_v6.py']:assert (ROOT/name).read_bytes()==(Path.home()/'.lmstudio/local-ai-lab'/name).read_bytes(),name
    transcript=out/'prompts-and-responses.txt';transcript.write_bytes((folder/'prompts-and-responses.txt').read_bytes());bind(transcript)
    report=ROOT/'reports/current-biwn-doorway-status.txt';report.write_text('LOCAL STATUS OUTPUT TEST — ACCEPTED LOCAL NATIVE DOORWAY\n'+now.isoformat()+'\n\n'
      'The actual Start Local AI -> S menu ran Reader v11 through the configured MCPv6 stdio entrypoint. It called the current-status tool once, used two local prediction rounds/noEditor, and produced140words in18.85seconds. The tool response verified203frozen evidence files and returned all18tools plus four individually identified processor jobs. Two older cache/boundary tests are terminal/equal, scanner17812anddoorway18270jobs were confirmed live by actual handles, and only the doorway test applies to the current published disc. The two latest-frame values are progress observations, not final verdicts.\n\n'
      'Coordinator source review finds the core facts correct at that observation time: accepted local repaired C with coordinator support,18270resident bytes,24996native frames, one success/zero failure returns, video/PCM/navigation matching the identified control, CPU/RAM differences, each named job phase, inherited timing/state limits and unfinished readable game/console/nativeChat work. No model training, independent review or physical readiness is asserted.\n\n'
      'Coverage omissions remain: the brief model reply does not state2025+768component/96startup counts or explicitly say failure paths remain component-only; it gives the correct1success/0failure return counts. It mentions inherited timing/state limits but omits the parent scanner\'s video/audio drift. The full verified evidence and the native-doorway-live report retain these limits. This is a factually correct core summary with incomplete coverage of the requested scope, not a general model-reliability or training-gain certification. Raw answer is unchanged.\n\n'
      'Exact model prompt, tool result and response:\n'+str(transcript)+'\nRaw answer:\n'+str(folder/'answer.txt')+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_current_doorway_status_v11_reviewed_with_coverage_omissions',recorded_at=now.isoformat(),directory=str(out),report=str(report),reader=str(folder),word_count=140,seconds=d['seconds'],actual_evidence_calls=1,Reader_prediction_rounds=2,Editor_calls=0,factual_core_correct=True,full_requested_coverage=False,semantic_review_complete=True,omissions=['component/startupcounts','explicitfailurepathscomponentonlywording','inheritedparentvideoaudiodrift'],transcript=str(transcript),raw_answer=str(folder/'answer.txt'),dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,whole_goal_complete=False)
    save(out/'protocol.json',result);save(v/'current-doorway-status-delivery-current.json',result);print(json.dumps({k:result[k]for k in ['status','word_count','seconds','report']}))
if __name__=='__main__':main()
