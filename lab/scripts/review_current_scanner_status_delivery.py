"""Review exact menu outputs and fresh installed MCP without claiming native Chat."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';latestp=v/'current-biwn-status-v10-reader-current.json';latest=read(latestp);earlierp=v/'current-biwn-status-v9-reader-current.json';earlier=read(earlierp);rejectedp=v/'current-scanner-status-v8-rejected-current.json';rejected=read(rejectedp);mcpp=v/'current-scanner-MCP-v5-current.json';mcp=read(mcpp)
    assert latest['status']=='terminal_local_current_status_v10_pending_semantic_review' and len(latest['tool_calls'])==1 and latest['rounds']==2 and not latest['automatic_format_flags'] and not latest.get('Editor')
    facts=latest['tool_calls'][0];assert facts['experimental_build']['resident_bytes']==17812 and facts['gameplay_comparison']['live_success_returns']==11 and facts['gameplay_comparison']['live_failure_returns']==4742
    assert facts['scanner_disc_C_processor_test']['status']=='running_verified' and facts['scanner_disc_C_processor_test']['applies_to_latest_published_disc']
    assert len(facts['processor_tests'])==3 and all(not x['applies_to_latest_published_disc']for x in facts['processor_tests'][:2])
    assert latest['word_count']==123 and earlier['word_count']==129 and earlier.get('Editor')
    now=datetime.now(timezone.utc);out=v/'current-scanner-status-delivery'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [latestp,earlierp,rejectedp,mcpp]:bind(p)
    combined=[]
    for p in [v/'current-biwn-status-v8-reader-current.json',earlierp,latestp]:
        d=read(p);folder=Path(d['directory'])
        for f in folder.rglob('*'):
            if f.is_file():bind(f)
        combined.append(('SOURCE: '+str(folder)+'\n').encode()+(folder/'prompts-and-responses.txt').read_bytes())
    for label,name in [('current-command','BIWN Current Status.command'),('main-menu','Start Local AI.command'),('bootstrap','Bootstrap.command'),('source-list','config/current-model-work-sources.json')]:
        p=ROOT/name;q=snap/(label+'-'+p.name);shutil.copy2(p,q);bind(q)
    for name in ['current_biwn_evidence_v5.py','chat_tools_current_v5.py','scripts/ask_biwn_current_status_v10.py','scripts/install_frontend_current_v5.py','biwn_status_brevity_v5.py']:bind(ROOT/name)
    for f in Path(mcp['directory']).iterdir():
        if f.is_file():bind(f)
    for folder in sorted((ROOT/'runs').glob('main-menu-scanner-status*')):
        for f in folder.iterdir():
            if f.is_file():bind(f)
    transcript=out/'prompts-and-responses.txt';transcript.write_bytes(b'\n\n'.join(combined));bind(transcript)
    report=ROOT/'reports/current-biwn-scanner-status.txt';report.write_text('LOCAL STATUS OUTPUT TEST — COMPLETE102C4 SCANNER\n'+now.isoformat()+'\n\n'
      'Start Local AI -> S now executes Reader v10 through the actual configured local MCP stdio server v5. A fresh menu execution called the evidence tool once and produced123words in15.87seconds, two prediction rounds, no brevity Editor. It states17812resident bytes,1377stable+768changing+96startup,24996/24978frame native routes,4753calls/11success/4742failure returns, retained processors, video/audio/CPU disagreement, coordinator authorship after rejected local drafts, the current scanner C job running, older cache/boundary jobs terminal/equal, and unfinished readable game/console work. The last recorded frame is an observation only.\n\n'
      'Coordinator source review accepts these facts at the recorded observation time. Minor presentation limit: the model included two differing-frame counts despite the requested concise style; it did not establish a general reliability or independent-review result. The current status fetch verifies114frozen evidence files and separately checks the actual handles/disc applicability of all three named jobs. A fresh installed stdio call returned all18tools. Native LM Studio Chat display remains unverified.\n\n'
      'Earlier v8 output is rejected and preserved: it falsely claimed failure paths were unreached despite4742live failure returns. V9 required explicit return counts; its first draft was too long and the same-weight brevity Editor produced129words in34.82seconds total (Reader18.02s, Editor16.80s). That earlier valid answer predates the new C job. V10 removes the stale two-job tool description and requires every listed job phase/applicability; it is the current menu target. No weights were changed.\n\n'
      'All raw prompts/tool responses/Reader and Editor messages:\n'+str(transcript)+'\nLatest exact raw answer:\n'+str(Path(latest['directory'])/'answer.txt')+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_current_scanner_status_v10_delivery_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),latest_reader=latest['directory'],word_count=123,seconds=latest['seconds'],actual_evidence_calls=1,Reader_prediction_rounds=2,Editor_calls=0,semantic_review_complete=True,semantic_review_notes=['Core facts correct at observation time; two differing-frame counts remain despite style instruction','Earlier v8 wrong failure-path statement rejected; no raw response edited','Same base weights in sequential contexts; no independent model review'],raw_answer=str(Path(latest['directory'])/'answer.txt'),transcript=str(transcript),dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,whole_goal_complete=False)
    save(out/'protocol.json',result);save(v/'current-scanner-status-delivery-current.json',result);print(json.dumps({k:result[k]for k in ['status','word_count','seconds','report']}))
if __name__=='__main__':main()
