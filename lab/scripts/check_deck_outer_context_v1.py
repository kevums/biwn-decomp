"""Check current native backend context routes; performs zero predictions."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=ROOT/'verification/deck-outer-context'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);rows=[]
 requests=[dict(domain='game',query='What does the recovered Deck outer task at 11E6C do?'),dict(domain='game',query='How do I run in the BIWN preview?'),dict(domain='advertising',query='Copyedit this paragraph: We study consumer responses to AI disclosure.')]
 for i,request in enumerate(requests):
  p=subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/native_chat_team_context.py')],input=json.dumps(request)+'\n',capture_output=True,text=True,timeout=45)
  (out/(str(i)+'-stderr.txt')).write_text(p.stderr);assert p.returncode==0,p.stderr
  response=json.loads(p.stdout);assert response['status']=='ready',response
  (out/(str(i)+'-request.json')).write_text(json.dumps(request,indent=2)+'\n');(out/(str(i)+'-response.json')).write_text(json.dumps(response,indent=2)+'\n')
  if i==0:
   f=response['evidence'];assert len(f['complete_hosted_callers'])==5 and f['new_outer_task_component']['original_CPU_cases']==1280 and f['connected_pipeline']['outer_task_resumes']==18 and f['whole_game_complete']is False
  elif i==1:
   assert response['topic']=='controls'
   assert any(row.get('preview_keys')=='Hold keyboard C + Up'for row in response['evidence']['actions'])
  else:assert response['workflow']=='copyediting'and response['advertising_anchor_gate']is None
  rows.append(dict(request=request,status=response['status'],topic=response['topic'],workflow=response['workflow'],roles=[x[0]for x in response['roles']]))
 paths=[Path(__file__),ROOT/'scripts/native_chat_team_context.py',ROOT/'deck_source_context_v3.py']
 report=dict(status='terminal_current_Deck_outer_and_other_backend_routes_checked',directory=str(out),routes=rows,actual_predictions=0,native_Chat_verified=False,source_sha256={str(p):sha(p)for p in paths},scope='Actual installed-backend context provider withits realinference lock andcurrent savedproofs. Context routing only;noChatmodelselection/render/generation claim.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/Deck-outer-context-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
