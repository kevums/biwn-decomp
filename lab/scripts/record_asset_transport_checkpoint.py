"""Archive asset-adoption proof, source scope and real ordinary local outputs."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');proof=read(ROOT/'verification/asset-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json');raw=Path(proof['directory'])
    assert cp['actual_asset_transport_linked_into_game']and not cp['game_asset_transport_file_backed']and cp['movie_transport_file_backed']and cp['source_VBI_progress']and not cp['asset_file_payload_memcpy']and not cp['asset_scripted_progress']and not cp['source_boot_verified']
    assert cp['asset_controller_ticks_total']==101447 and cp['asset_GPU_IRQs_total']==34681 and cp['asset_VBI_events_total']==18 and proof['cases']==2
    for case in range(2):
        a=read(raw/f'case-{case}-native.json');b=read(raw/f'case-{case}-C.json');assert a==b
        assert (raw/f'case-{case}-native-final-RAM.bin').read_bytes()==(raw/f'case-{case}-C-final-RAM.bin').read_bytes()
        assert sha(raw/f'case-{case}-native-movie.wav')==sha(raw/f'case-{case}-C-movie.wav')
        s=b['summary'];assert len(s['asset_disc_requests'])==len(s['asset_disc_completions'])==18
        assert all(x['transport']=='actual_BIOS_CPU_BUTCH_GPU_FIFO_sourceVBI'for x in s['asset_disc_requests'])
        assert max(x['source_write_end_inclusive']for x in s['asset_disc_completions'])==0x1e601f
    first=ROOT/'verification/easy-asset-transport-scope/20261014T225543.209359Z';last=Path(read(ROOT/'verification/easy-asset-transport-scope-pointer.json')['directory']);runs=[read(p/'protocol.json')for p in [first,last]];assert runs[0]['questions']==runs[1]['questions']
    for a in runs:
        i=a['results'][0];assert a['status']=='completed_pending_coordinator_review'and not i['quality_flags']and i['words']<160 and all(s['stats']['stopReason']=='eosFound'for s in i['prediction_stats'])
    item=runs[-1]['results'][0];assert item['answer'].startswith('Yes.')and '18 transfers' in item['answer']and 'Movie streaming remains file-backed' in item['answer']and 'does not prove full boot or playability' in item['answer']
    now=datetime.now(timezone.utc);out=ROOT/'verification/asset-transport-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    findings=['Latest ordinary answer correctly reports18asset transfers/1,108,650bytes, actual BIOS/GPU data movement,18sourceVBI progress events and remaining movie file backend; rejects full boot/playability.','Concise answer omits common initial controller buffers,CPU/device seed/GPU MMIO shadow/pipeline tail, controlled input/taskquiescence and the explicit handoff-based controller/VBI schedule. Those remain supplied in the full checkpoint.','First startup attempt hit forbidden old payload callback; corrected routing. Next comparison matched payload/finalRAM/tasks but initial inactive controller buffers differed because Reset retains them; identical pre-execution controller fixture now supplied to both, with no later restoration.','Reference driver no longer patches asset BIOS entry opcodes. First frontend check caught stale duplicate component metadata; publisher now updates both records. First local answer was correct despite inconsistent evidence; replay after fresh MCP pass is authoritative for current tool scope.','These two single-question outputs include warm/cache effects; they are SDK inference, not native Chat verification or broad reliability measurements.']
    files=[Path(__file__),ROOT/'scripts/prepare_asset_transport_evidence.py',ROOT/'scripts/biwn_asset_transport_runtime.py',ROOT/'scripts/check_biwn_asset_transport_scheduled_startup.py',ROOT/'scripts/check_biwn_continuous_loading_movie_world.py',ROOT/'scripts/check_biwn_VBI_event.py',ROOT/'scripts/check_asset_transport_mcp.py',ROOT/'scripts/test_asset_transport_scope.py',ROOT/'verification/VBI-event-checks.json',ROOT/'verification/asset-transport-MCP-check.json',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'chat_tools.py',raw/'initial-controller-state.bin',raw/'initial-controller-timing.bin'];manifest=[]
    for n,p in enumerate(files):
        target=out/f'{n:02d}-{p.name}';shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    for label,p in [('stale-duplicate',first),('corrected',last)]:
        for name in ['protocol.json','prompts-and-responses.txt']:
            target=out/f'{label}-{name}';shutil.copy2(p/name,target);manifest.append(dict(source=str(p/name),snapshot=str(target),sha256=sha(target)))
    report=dict(status='connected_asset_transport_verified_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],source_report=proof['directory'],interface=runs[-1]['interface'],model=runs[-1]['model'],words=item['words'],seconds=item['seconds'],first_output=dict(words=runs[0]['results'][0]['words'],seconds=runs[0]['results'][0]['seconds']),semantic_review=findings,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,implementation_authorship=cp['implementation_authorship'],manifest=manifest)
    save(out/'review.json',report);save(ROOT/'verification/asset-transport-local-review.json',report)
    text='COORDINATOR\n'+cp['implementation_authorship']+'\n32sourceVBI user/supervisor IRQ-frame/actual304E/RTE comparisons. Connected18asset transfers now use actual firmware CPU/GPU instructions,34,681GPU IRQs,101,447explicit controller ticks and18sourceVBI events. Saved full native/C states/privateRAM/WAVbytes match in2profiles. Identical initial controller buffers/timing are supplied once per fixture. Movie transport and globaltiming/input/boot remain incomplete.\n\nFIRST LOCAL EXACT PROMPTS / RESPONSE (STALE DUPLICATE EVIDENCE)\n'+(first/'prompts-and-responses.txt').read_text()+'\n\nCORRECTED LOCAL EXACT PROMPTS / RESPONSE\n'+(last/'prompts-and-responses.txt').read_text()+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(findings)+'\n';(out/'who-prompts-and-responses.txt').write_text(text)
    history=out/'prior-daily-pages';history.mkdir()
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,history/name)
    ad=Path(read(ROOT/'verification/TOC-and-advertising-methods-review.json')['directory'])
    start=f'''LOCAL AI — START HERE
Updated {now.isoformat()}

1. Double-click Game Model.command or Advertising Model.command. Both load the shared27B/6bit everyday model and open LM Studio.
2. In Chat, select Game Assistant or Advertising Assistant and enable local-ai-lab in Integrations.
3. Ask normally: Where are we with Black Ice White Noise, and can I play it yet?
Picture: Show the current interior drawing.
Advertising: Compare measured involvement in Olsen’s survey with a hypothetical randomized advertising experiment.

CURRENT GAME RESULT
Asset loading is now connected to actual BIOS/controller/GPU transport:18transfers/1,108,650bytes with sourceVBI progress reporting. Two original/C profiles match startup,187movieframes and12worldcycles. Movie streaming still uses file-backed transport; complete firmware boot/globaltiming/remaining tasks/scenes/playability remain unfinished.
Latest local GameAssistant answer:{item['words']}words/{item['seconds']:.2f}seconds, core scope accepted.

CURRENT ADVERTISING RESULT
Method excerpts and coordinator design notes improve retrieval; latest classroom draft still needs source/causal qualifications. Corrected activity:
{ad/'coordinator-corrected-classroom-activity.txt'}

These are LMStudio SDK/tool tests. Current visible native Chat remains unverified. Trained pilots are retained; no new weights/defaults changed. Game Team is a separate experimental coding workflow.

EXACT WHO / PROMPTS / RESPONSES / REVIEW
{out/'who-prompts-and-responses.txt'}
{out/'review.json'}
SOURCE STATUS
{ROOT/'CURRENT DECOMPILATION.txt'}
LOCAL INFERENCE STATUS
{ROOT/'CURRENT LOCAL INFERENCE.txt'}
PRIOR HISTORY
{history}
''';(ROOT/'START HERE.txt').write_text(start)
    inference=f'''CURRENT LOCAL INFERENCE
Updated {now.isoformat()}

Shared everydaymodel local/advertising-qwen38,27B/6bit,advertising-scholar,32,768context/oneworker/60minuteTTL. No new weights/presets/defaults.

GAME ASSISTANT
Latest{item['words']}word answer/{item['seconds']:.2f}s with one evidence lookup. Correct asset-versus-movie scope and incomplete boot/playability. First{runs[0]['results'][0]['words']}word answer/{runs[0]['results'][0]['seconds']:.2f}s used a stale duplicate metadata field; first answer was correct, but the tool evidence was corrected and fresh MCP check passed before replay. Cache effects possible; SDK, not nativeChat.

EXACT WHO / SYSTEM / USER PROMPTS / TOOL RESULTS / RESPONSES
{out/'who-prompts-and-responses.txt'}
REVIEW
{out/'review.json'}

ADVERTISING
Original method-page excerpts and explicit coordinator design notes are configured. Last199word draft31.43s improved design grounding but still needs source,baseline-timing and causal qualifications. Same-model reviewer missed some errors. Corrected activity and exact earlier roles:
{ad/'coordinator-corrected-classroom-activity.txt'}
{ad/'who-prompts-and-responses.txt'}

Experimental trained pilots remain loadable and unpromoted. Diagnostic feedback from a reused question is training-only candidate data, not independent heldout evidence. Future256GB profile remains unbenchmarked.

PRIOR HISTORY
{history/'CURRENT LOCAL INFERENCE.txt'}
''';(ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(source_audit=cp['audit'],local_audit=str(out),last_turn_classification='progress',local_roles_this_turn='Coordinator connects actual BIOS/GPU asset transport and VBI progress; GameAssistant explains adoption before/after duplicate-metadata correction. Exact prompts/tool/results preserved; no new weight training.')
    n['next_source_work'][0]='18assets now use actual BIOS303C/3042/304E/GPU IRQ1 and sourceVBI progress in2matched startup/movie/world profiles. Replace remaining movie transport/BIOS adapters,connect firmware relocation/stage-load/fullboot and globaldevice scheduling. Shared initial controller buffers/GPU shadow/pipeline tail and handoff-driven controller/VBI events remain supplied; general buffer/padding/other calls still need work.';save(p,n)
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        p=ROOT/name;target=out/('current-'+name);shutil.copy2(p,target);report['manifest'].append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in report['manifest'])
    assert (ROOT/'chat_tools.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/chat_tools.py').read_bytes()
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    save(out/'review.json',report);save(ROOT/'verification/asset-transport-local-review.json',report);print(json.dumps(dict(status=report['status'],directory=str(out),words=item['words'],seconds=item['seconds'])))
if __name__=='__main__':main()
