"""Append three existing local trials to frozen indices without new inference."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha
from publish_geometry_records_progress_v1 import clone


def main():
    trials=[]
    for version in [41,42,43]:
        name=f'copied-Reader{version}-'+('reviewed'if version==43 else'rejected')+'-v1-current.json'
        rp=V/name;r=read(rp);d=Path(r['directory'])/'actual-run';source=d/'prompts-and-responses.txt'
        assert source.is_file() and r['actual_predictions']==1
        assert read(d/'protocol.json')['new_predictions']==1
        for path in [rp,*[p for p in Path(r['directory']).rglob('*')if p.is_file()]]:
            clone(path,P/'workbench'/path.relative_to(ROOT))
        trials.append((version,rp,r,source))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');results=[]
    for root in [ROOT,P/'workbench']:
        pointer=root/'verification/current-model-work-index-v4-current.json';old=read(pointer)
        before=Path(old['report']);snapshot=Path(old['source_list_snapshot'])
        assert sha(before)==old['report_sha256'] and sha(snapshot)==old['source_list_sha256']
        files=list(old['files']);content=before.read_bytes();config=root/'config/current-model-work-sources.json';sources=read(config)
        appended=0
        for version,rp,r,source in trials:
            current=root/source.relative_to(ROOT);receipt=root/rp.relative_to(ROOT)
            assert sha(current)==sha(source)
            if any(x.get('path')==str(current)and x.get('sha256')==sha(current)for x in files):continue
            approved=version==43
            title=f'BIWN COPIED READER{version} — '+('supplied facts/units/causal scope/format approved'if approved else'rejected;raw response retained')
            note=(title+'\nOne actual saved local prediction,not a native LM Studio Chat session;zero training updates. '
                  'The inherited raw transcript header may say READER40;the executable and protocol identify the actual version. '
                  f'Generation{r["seconds"]}seconds;warm CLI firsttext{r["CLI_start_to_first_text_seconds"]}seconds,complete{r["CLI_start_to_completion_seconds"]}seconds;{r["words"]}words. '
                  'Approval is one supplied-snapshot result,not heldout quality or useful training gain.\nExact source: '+str(current)+'\nReview: '+str(receipt)+'\n\n')
            content+=b'\n\n'+note.encode()+current.read_bytes()
            files.append(dict(kind='saved_role_transcript',path=str(current),sha256=sha(current),review=str(receipt),
                              protocol_status=r['status'],actual_generations_in_this_transcript=1,
                              complete_requested_briefing_approved=approved,model_generation_replayed=False))
            entry=[rp.name,title]
            if entry not in sources:sources.append(entry)
            appended+=1
        if not appended:continue
        out=root/'reports/model-work-index'/stamp;out.mkdir(parents=True)
        report=out/'prompts-and-responses.txt';report.write_bytes(content);save(config,sources);save(out/'source-list.json',sources)
        new=dict(old,recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),report=str(report),
                 report_sha256=sha(report),source_list_snapshot=str(out/'source-list.json'),source_list_sha256=sha(out/'source-list.json'),
                 saved_prompt_or_transcript_records=len(files),files=files,new_inference=False,native_Chat=False,previous_index_preserved=True)
        save(out/'manifest.json',new);save(pointer,new)
        results.append(dict(root=str(root),appended=appended,saved_prompt_records=len(files),report=str(report)))
    save(V/'Reader41-43-model-index-append-v1-current.json',dict(status='terminal_three_saved_trials_appended_without_prediction_replay_or_other_job_reread',results=results,new_predictions=0,new_training=False))
    print(results,flush=True)


if __name__=='__main__':main()
