"""Preserve two actual copied Reader trials without promoting their quality."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
def main():
 out=V/'input-copied-readers-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[];transcript=[]
 for version in [34,35]:
  job=read(P/f'workbench/verification/Deck-status-live-v{version}-current.json');assert job['new_predictions']==1 and job['status']=='terminal_streamed_local_briefing_pending_source_review'
  raw=Path(job['directory']);response=read(raw/'response.json');request=read(raw/'request.json');assert request['model']=='portable-ailab-4f5658686590-daily'
  subprocess.run(['/bin/cp','-cR',str(raw),str(out/f'Reader{version}')],check=True,capture_output=True);transcript.append(f'READER{version}\n'+(raw/'prompts-and-responses.txt').read_text());rows.append(dict(version=version,seconds=response['seconds'],answer=job['answer'],recorded_format_pass=job['format_pass'],quality_approved=False,review='Ambiguous case0failure attribution to prototype versus older baseline'if version==34 else'Older baseline/prototype attribution clarified. Required27..34percent improvement omitted;training section adds ambiguous no-new-predictions assertion. Literal14format check rejects valid wordFourteen;do not mistake this validator limitation for numerical misinformation.'))
 save(out/'reviews.json',rows);(out/'prompts-and-responses.txt').write_text('\n\n'.join(transcript))
 facts=dict(status='terminal_two_copied_input_Readers_reviewed_unpromoted',directory=str(out),actual_predictions=2,seconds=[x['seconds']for x in rows],current_source_entry='0x11b4c',current_source_reply_verified=False,latest_source_changed_since_last_prediction=False,baseline_attribution_improved=True,broader_quality_approved=False,run_speed_measured=False,new_training=False,trained_adapter_used=False,native_Chat_display_verified=False,raw_responses_retained=True,scope='Actual ordinary copied portable launcher with package-owned base model,SDK and actual referenceMCP. Two adaptive prompt-development trials;no holdout,training gain or accepted complete current-status briefing. All whole-game/preview promotion booleans false. Exact prompts/responses visible in Terminal and saved.')
 report=ROOT/'reports/Input Prototype Copied Reader Review.txt';facts['report']=str(report);save(out/'facts.json',facts);report.write_text('Copied BIWN Reader — two actual output tests\n\n'
  'Reader34completed in13.69seconds andReader35in15.68seconds through ordinary portable_biwn.py reader. Reader34ambiguously attached the old case0bus failure to the new prototype. One prompt clarification madeReader35separate older v20failure from13passing new bus cases. It omitted the requested27..34percent improvement and added an unqualified no-new-model-predictions assertion in its training section. Neither response is approved as a complete scoped briefing. Both correctly deny whole-game rebuild and preview promotion.\n\n'
  'The simple format validator requires literal14and marksReader35false for writingFourteen. That is an overly strict validator,not a wrong video count. Broader outputquality remains unproven;these adaptive trials are not a benchmark or training gain. No weights/adapter changed. Native LMStudioChat rendering was not tested;Terminal exact prompts/responses were streamed and preserved.\n\n'+str(out/'prompts-and-responses.txt')+'\n')
 manifest=V/'native-Deck-current-status-v1-current.json';w=read(manifest)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);save(out/'before-packet.json',packet);packet['previous_copied_Reader_progress']=packet['current_copied_Reader_progress'];packet['current_copied_Reader_progress']=facts;save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py')
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report);pub=V/'input-copied-readers-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),transcript=str(out/'prompts-and-responses.txt'),new_predictions=2,new_training=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(manifest,w)
 index=ROOT/'config/current-model-work-sources.json';items=read(index);items=[x for x in items if x[0]!=pub.name];items.append([pub.name,'BIWN actual copied Reader34/35 prompts and unpromoted output reviews']);atomic(index,items)
 for p,h in w['dependencies_sha256'].items():
  source=Path(p);assert source.is_relative_to(ROOT);dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(source),str(dest)],check=True,capture_output=True)
 shutil.copy2(manifest,P/'workbench/verification'/manifest.name);shutil.copy2(index,P/'workbench/config'/index.name);print(facts['status'],facts['seconds'],flush=True)
if __name__=='__main__':main()
