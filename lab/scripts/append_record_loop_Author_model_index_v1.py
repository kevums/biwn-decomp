"""Append one saved local Author;do not inspect or replay other workflows."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
    job=read(V/'local-record-loop-advance-v1-current.json');source=Path(job['directory'])/'prompts-and-responses.txt'
    assert job['new_predictions']==1
    results=[];stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    for root in [ROOT,P/'workbench']:
        pointer=root/'verification/current-model-work-index-v4-current.json';old=read(pointer);before=Path(old['report']);snapshot=Path(old['source_list_snapshot'])
        assert sha(before)==old['report_sha256']and sha(snapshot)==old['source_list_sha256']
        current=source if root==ROOT else root/source.relative_to(ROOT);assert sha(current)==sha(source)
        if any(x.get('path')==str(current)and x.get('sha256')==sha(current)for x in old['files']):continue
        config=root/'config/current-model-work-sources.json';sources=read(config)
        entry=['local-record-loop-advance-v1-current.json','BIWN loop-tail Author: one16.92second prediction,strict compile failed;not adopted;Repair not generated']
        if entry not in sources:sources.append(entry);save(config,sources)
        out=root/'reports/model-work-index'/stamp;out.mkdir(parents=True);report=out/'prompts-and-responses.txt'
        report.write_bytes(before.read_bytes()+b'\n\n'+('BIWN RECORD LOOP AUTHOR — one actual prediction;strict compile failed;zero new training\nThis is a saved Terminal/API transcript,not a native LM Studio Chat session. Repair prompt prepared butzero Repair generations while the shared slot was busy. Coordinator passing source is separate.\nExact source: '+str(current)+'\n\n').encode()+current.read_bytes())
        save(out/'source-list.json',sources);item=dict(kind='saved_role_transcript',path=str(current),sha256=sha(current),protocol=str(root/'verification/local-record-loop-advance-v1-current.json'),protocol_status=job['status'],compile_review=str(root/'verification/local-record-loop-compile-v1-current.json'),actual_generations_in_this_transcript=1,model_generation_replayed=False)
        files=old['files']+[item];new=dict(old,recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),report=str(report),report_sha256=sha(report),source_list_snapshot=str(out/'source-list.json'),source_list_sha256=sha(out/'source-list.json'),saved_prompt_or_transcript_records=len(files),files=files,new_inference=False,native_Chat=False,previous_index_preserved=True)
        save(out/'manifest.json',new);save(pointer,new);results.append(dict(root=str(root),before=old['saved_prompt_or_transcript_records'],after=len(files),report=str(report)))
    save(V/'record-loop-Autor-model-index-append-v1-current.json',dict(status='terminal_one_actual_Author_appended_without_other_job_reread_or_prediction_replay',results=results,new_predictions=0,new_training=False))
    print('Appended one actual failed Author transcript to Root/copied frozen indices.',flush=True)

if __name__=='__main__':main()
