"""Append this one completed BIWN transcript without re-reading unrelated jobs."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
 name='copied-Reader37-reviewed-v1-current.json'
 for root in [ROOT,P/'workbench']:
  pointer=root/'verification/current-model-work-index-v4-current.json';old=read(pointer)
  # Existing moved-package metadata retains historical original absolute paths.
  def local(value):
   p=Path(value)
   if root!=ROOT and p.is_relative_to(ROOT):return root/p.relative_to(ROOT)
   return p
  pub=root/'verification'/name;review=read(pub);folder=local(review['directory']);transcript=folder/'prompts-and-responses.txt'
  if any(Path(row.get('protocol','')).name==name for row in old['files']):print('Already indexed',root);continue
  prior=local(old['report']);assert sha(prior)==old['report_sha256']
  out=root/'reports/model-work-index'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
  report=out/'prompts-and-responses.txt';report.write_text(prior.read_text()+'\n'+'='*72+'\nBIWN copied Reader37 — exact prompts and raw response\nReview: numeric and word-limit checks pass; invents a pending image for an unbuilt prototype. No training gain.\n\n'+transcript.read_text()+'\n')
  source=root/'config/current-model-work-sources.json';(out/'source-list.json').write_bytes(source.read_bytes())
  row=dict(kind='saved_role_transcript',path=str(transcript),sha256=sha(transcript),protocol=str(pub),protocol_status=review['status'],model_generation_replayed=False)
  index=dict(old,recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),report=str(report),report_sha256=sha(report),source_list_snapshot=str(out/'source-list.json'),source_list_sha256=sha(source),saved_prompt_or_transcript_records=old['saved_prompt_or_transcript_records']+1,files=[*old['files'],row],new_inference=False,native_Chat=False)
  save(out/'manifest.json',index);atomic(pointer,index);print(root,index['saved_prompt_or_transcript_records'],flush=True)
if __name__=='__main__':main()
