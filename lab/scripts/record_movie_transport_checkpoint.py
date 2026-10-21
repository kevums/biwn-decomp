"""Record bounded movie transport proof and exact local inference provenance."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json')
    proof=read(ROOT/'verification/movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json')
    raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass' and proof['cases']==2
    assert cp['actual_movie_transport_linked_into_game'] and not cp['movie_file_payload_memcpy'] and not cp['movie_scripted_progress']
    assert cp['movie_GPU_IRQs']==81045 and cp['movie_VBI_events']==452 and not cp['source_boot_verified']
    assert not cp['main_game_CD_transport_file_backed'] and cp['nominal_movie_transfer_pacing_supplied']
    for case in range(2):
        assert read(raw/f'case-{case}-native.json')==read(raw/f'case-{case}-C.json')
        assert (raw/f'case-{case}-native-final-RAM.bin').read_bytes()==(raw/f'case-{case}-C-final-RAM.bin').read_bytes()
        assert sha(raw/f'case-{case}-native-movie.wav')==sha(raw/f'case-{case}-C-movie.wav')
    first=ROOT/'verification/easy-movie-transport-scope/20261014T231523.282163Z'
    latest=Path(read(ROOT/'verification/easy-movie-transport-scope-pointer.json')['directory'])
    runs=[read(p/'protocol.json') for p in [first,latest]]
    assert runs[0]['questions']==runs[1]['questions']
    for run in runs:
        item=run['results'][0]
        assert run['status']=='completed_pending_coordinator_review' and not item['quality_flags'] and item['words']<160
        assert all(x['stats']['stopReason']=='eosFound' for x in item['prediction_stats'])
    item=runs[-1]['results'][0]
    now=datetime.now(timezone.utc)
    out=ROOT/'verification/movie-transport-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    findings=[
        'Both ordinary local answers correctly identify actual BIOS/controller/GPU data transport and sourceVBI progress, nominal pacing/clocks and incomplete boot/playability. Counts agree with saved source comparisons.',
        'First evidence still contained historical file-backed wording in nested component limitations/status and checked_boot_scope. Coordinator corrected those fields; fresh MCP check and same-question replay passed. First answer was correct despite inconsistent supporting fields.',
        'This is a repeated SDK question with warm/cache effects, not native Chat usability, heldout accuracy, general reliability or independent model verification. No new weights/defaults/presets.',
        'Initial full prototype inherited pending movie metadata across initial fixtures and failed C pacing. Clearing pending only at fixture reset fixed it. Two later runs exposed GPU_FLAGS cached N/C/Z differences; matching the real F02100 read side effect fixed full-state comparison without masking bytes.',
        'Two fresh original/C profiles match startup,18asset transfers/1,108,650bytes,187movie frames,125audio enqueues and12world cycles, complete CPU/privateRAM/logicalGPU-DSP/controller baseline+9byte extension/peripherals/events and WAV bytes. Movie10seek/fills use232,163controller ticks/81,045GPU IRQs/452VBIs; assets use101,447ticks/34,681IRQs/18VBIs.',
        'Nominal588byte target-fill pacing and explicit clocks remain supplied, as do initial stage/resident firmware/device seeds/shared controller buffers/GPU shadow/pipeline tail, controlled input/task quiescence/synchronous blitter and movie-exit/main-reload BIOS3000 adapters. Other movies/tasks/scenes, full boot/global physical timing and playability remain unverified.',
        'CUA returned LM Studio window and AX state this turn, but picker/focus interactions produced no visible changes. No prompt was sent or history injected. Lock status is unknown; native Chat verification remains pending.'
    ]
    files=[Path(__file__),ROOT/'scripts/biwn_movie_transport_runtime.py',ROOT/'scripts/biwn_asset_transport_runtime.py',ROOT/'scripts/check_biwn_movie_transport_scheduled_startup.py',ROOT/'scripts/check_biwn_continuous_loading_movie_world.py',ROOT/'scripts/prepare_movie_transport_evidence.py',ROOT/'scripts/check_movie_transport_mcp.py',ROOT/'scripts/test_movie_transport_scope.py',ROOT/'chat_tools.py',ROOT/'verification/movie-transport-MCP-check.json',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json']
    manifest=[]
    for n,p in enumerate(files):
        dest=out/f'{n:02d}-{p.name}';shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    for label,p in [('initial',first),('corrected-evidence',latest)]:
        for name in ['protocol.json','prompts-and-responses.txt']:
            dest=out/f'{label}-{name}';shutil.copy2(p/name,dest);manifest.append(dict(source=str(p/name),snapshot=str(dest),sha256=sha(dest)))
    report=dict(status='connected_asset_movie_transport_verified_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],source_report=str(raw),interface=runs[-1]['interface'],model=runs[-1]['model'],words=item['words'],seconds=item['seconds'],first_output={k:runs[0]['results'][0][k]for k in ['words','seconds']},semantic_review=findings,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,implementation_authorship=cp['implementation_authorship'],manifest=manifest)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+cp['implementation_authorship']+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(findings)+'\n\nINITIAL LOCAL EXACT PROMPTS / TOOL RESULTS / RESPONSE\n'+(first/'prompts-and-responses.txt').read_text()+'\n\nCORRECTED-EVIDENCE LOCAL EXACT PROMPTS / TOOL RESULTS / RESPONSE\n'+(latest/'prompts-and-responses.txt').read_text())
    history=out/'prior-daily-pages';history.mkdir()
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,history/name)
    ad=Path(read(ROOT/'verification/TOC-and-advertising-methods-review.json')['directory'])
    (ROOT/'START HERE.txt').write_text(f'''LOCAL AI — START HERE
Updated {now.isoformat()}

1. Double-click Game Model.command or Advertising Model.command. Both load the shared 27B/6bit everyday model and open LM Studio.
2. In Chat, select Game Assistant or Advertising Assistant and enable local-ai-lab in Integrations.
3. Ask: Where are we with Black Ice White Noise, and can I play it yet?
Picture: Show the current interior drawing.
Advertising: Compare measured involvement in Olsen’s survey with a hypothetical randomized advertising experiment.

CURRENT GAME RESULT
Asset and movie bytes now use actual BIOS/controller/GPU transport with source VBI progress. Two original/C profiles match startup, 18 asset transfers, 187 movie frames and 12 world cycles. Nominal pacing/clocks, remaining firmware adapters, full boot and playability are unfinished.
Latest local Game Assistant answer: {item['words']} words/{item['seconds']:.2f} seconds; core scope accepted.

CURRENT ADVERTISING RESULT
Method excerpts and coordinator design notes improve retrieval; latest classroom draft still needs source/causal qualifications. Corrected activity:
{ad/'coordinator-corrected-classroom-activity.txt'}

These are LM Studio SDK/tool tests. Current visible native Chat remains unverified. Trained pilots are retained; no new weights/defaults changed. Game Team is a separate experimental coding workflow.

EXACT WHO / PROMPTS / RESPONSES / REVIEW
{out/'who-prompts-and-responses.txt'}
{out/'review.json'}
SOURCE STATUS
{ROOT/'CURRENT DECOMPILATION.txt'}
LOCAL INFERENCE STATUS
{ROOT/'CURRENT LOCAL INFERENCE.txt'}
PRIOR HISTORY
{history}
''')
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(f'''CURRENT LOCAL INFERENCE
Updated {now.isoformat()}

Everyday model: local/advertising-qwen38, 27B/6bit, advertising-scholar, 32,768 context, one worker, 60-minute TTL. No new weights/presets/defaults.

GAME ASSISTANT
Latest {item['words']}-word answer/{item['seconds']:.2f}s with one evidence lookup. Correct asset/movie BIOS-controller-GPU transport and remaining clocks/firmware/playability scope. First {runs[0]['results'][0]['words']}-word answer/{runs[0]['results'][0]['seconds']:.2f}s was correct despite stale supporting evidence; metadata corrected, fresh MCP passed, then replayed. Same question and warm/cache effects: SDK, not native Chat or broad reliability evidence.

EXACT WHO / SYSTEM / USER / TOOL RESULTS / RESPONSES
{out/'who-prompts-and-responses.txt'}
REVIEW
{out/'review.json'}

ADVERTISING
Original method excerpts and explicit coordinator design notes are configured. Last 199-word draft/31.43s improved grounding but still needs source, baseline timing and causal qualifications. Same-model reviewer missed errors. Corrected activity:
{ad/'coordinator-corrected-classroom-activity.txt'}
{ad/'who-prompts-and-responses.txt'}

Trained pilots remain loadable and unpromoted. Reused-question diagnostic feedback is training-only candidate data. Future 256GB profile remains unbenchmarked.
Native Chat window was readable this turn; controls did not respond, and no new prompt was sent. Lock status unknown. UI usability still pending.

PRIOR HISTORY
{history/'CURRENT LOCAL INFERENCE.txt'}
''')
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p)
    n.update(source_audit=cp['audit'],local_audit=str(out),last_turn_classification='progress',local_roles_this_turn='Coordinator implemented actual movie BIOS/controller/GPU transport and reviewed source evidence. Local Game Assistant answered same question before/after evidence correction; exact prompts/results saved. No new training.')
    n['next_source_work'][0]='18 assets and10 movie seek/fills now use actual BIOS303C/3042/304E/controller/GPU IRQ1/sourceVBI in two matched profiles. Replace remaining movie-exit/main-reload BIOS3000 adapters, connect firmware relocation/stage-load/full boot and global scheduling; general buffer/end semantics and other calls remain unverified.';save(p,n)
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        dest=out/('current-'+name);shutil.copy2(ROOT/name,dest);manifest.append(dict(source=str(ROOT/name),snapshot=str(dest),sha256=sha(dest)))
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in manifest)
    assert (ROOT/'chat_tools.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/chat_tools.py').read_bytes()
    save(out/'review.json',report);save(ROOT/'verification/movie-transport-local-review.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),words=item['words'],seconds=item['seconds'])))
if __name__=='__main__':main()
