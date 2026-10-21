"""Archive source mode proof and before/after ordinary local inference outputs."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json')
    assert cp['actual_BIOS3006_mode_wait_linked'] and not cp['BIOS3006_adapter'] and cp['BUTCH_full_state_compared'] and not cp['source_boot_verified']
    assert cp['BIOS_mode_proof']['source_instruction_coverage']==[31,31] and cp['BIOS_mode_proof']['cases']==24 and cp['verified_profiles']==2
    first=ROOT/'verification/easy-bios-mode-scope/20261014T215149.284382Z'
    last=Path(read(ROOT/'verification/easy-bios-mode-scope-pointer.json')['directory'])
    runs=[read(p/'protocol.json')for p in [first,last]]
    assert runs[0]['questions']==runs[1]['questions'] and runs[0]['model']==runs[1]['model']
    for a in runs:
        i=a['results'][0]
        assert a['status']=='completed_pending_coordinator_review' and not i['quality_flags'] and i['words']<160
        assert all(s['stats']['stopReason']=='eosFound'for s in i['prediction_stats'])
        assert 'not a complete BIOS' in i['answer'] and 'playable game' in i['answer'] and 'stub' in i['answer']
        assert len([c for e in i['events']for c in e['content']if c['type']=='toolCallRequest'])==1
    now=datetime.now(timezone.utc);out=ROOT/'verification/bios-mode-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    review=['Both outputs correctly explain actual BIOS3006 execution, queued-reply retry, eight source-poll ticks, four-tick model delay and incomplete boot/playability. The compact answer explicitly distinguishes supplied polling from physical/global timing.',
            'First output includes24cases/all31instructions/four modes; compact output omits these counts. Both summarize providers without listing initial game-stage/CPU-device seed or task-quiescence detail. Full inventory remains in checkpoint; no broad completeness/reliability claim.',
            'Same prompt, same model and same settings. Boot tool now returns checked facts and full-report paths rather than nested raw proofs. Two single observations include warm/cache effects and do not isolate a causal speedup or measure native Chat latency.']
    measures=[]
    for p,a in zip([first,last],runs):
        i=a['results'][0]
        calls=[c['content']for e in i['events']for c in e['content']if c['type']=='toolCallResult']
        measures.append(dict(directory=str(p),seconds=i['seconds'],words=i['words'],tool_result_UTF8_bytes=sum(len(c.encode())for c in calls),round_stats=[{k:q['stats'].get(k)for k in ['stopReason','promptTokensCount','predictedTokensCount','timeToFirstTokenSec','tokensPerSecond']}for q in i['prediction_stats']]))
    files=[Path(__file__),ROOT/'chat_tools.py',ROOT/'scripts/prepare_bios_mode_evidence.py',ROOT/'scripts/test_bios_mode_scope.py',ROOT/'scripts/check_bios_setup_mcp.py',ROOT/'scripts/check_biwn_bios_mode_cpu.py',ROOT/'scripts/generate_biwn_bios_mode_cpu.py',ROOT/'scripts/biwn_bios_mode_runtime.py',ROOT/'scripts/check_biwn_bios_mode_music_cold_entry_scheduled_startup.py',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/bios-mode-CPU-checks.json',ROOT/'verification/bios-setup-MCP-check.json',ROOT/'projects/black-ice-white-noise/restoration/biwn_bios_mode_cpu.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_bios_mode_cpu.h']
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    for label,p in [('before',first),('compact',last)]:
        for name in ['protocol.json','prompts-and-responses.txt']:
            target=out/f'{label}-{name}';shutil.copy2(p/name,target);manifest.append(dict(source=str(p/name),snapshot=str(target),sha256=sha(target)))
    report=dict(status='actual_BIOS3006_linkage_verified_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],interface=runs[1]['interface'],model=runs[1]['model'],observations=measures,semantic_review=review,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,authorship=cp['implementation_authorship'],manifest=manifest)
    save(out/'review.json',report);save(ROOT/'verification/bios-mode-local-review.json',report)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+cp['implementation_authorship']+'\n31source instructions matched24 standalone original/C cases. Two full connected profiles and full controller-state snapshots match. Boot lookup compacted for daily inference; full proofs retained.\n\nLOCAL GAME ASSISTANT — FIRST EXACT RUN\n'+(first/'prompts-and-responses.txt').read_text()+'\n\nLOCAL GAME ASSISTANT — COMPACT LOOKUP EXACT RUN\n'+(last/'prompts-and-responses.txt').read_text()+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(review)+'\n')
    # Preserve prior long daily-use pages, then give the user one current front page.
    history=out/'prior-daily-pages';history.mkdir()
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        shutil.copy2(ROOT/name,history/name)
    latest=measures[-1]
    start=f'''LOCAL AI — START HERE
Updated {now.isoformat()}

1. Double-click Game Model.command or Advertising Model.command in this folder. Both daily launchers load the shared Advertising Qwen38 6bit model and open LM Studio.
2. In LM Studio Chat, choose the Game Assistant or Advertising Assistant preset. Existing chats are Game Assistant — Quick Start and Advertising Assistant — Research & Teaching; a new Chat can use the same presets.
3. Check that local-ai-lab is enabled in Integrations, then ask normally.

Game example: Where are we with Black Ice White Noise, and can I play it yet?
Picture example: Show the current interior drawing.
Advertising example: What can Olsen2001 tell me about involvement and repurchase? Explain how to teach it without claiming the survey proves an ad caused a purchase.

CURRENT RESULT
BIOS3006 now executes actual disc-mode/wait/retry/status code.24 standalone cases cover31/31instructions; two original/C comparisons match startup,187movieframes and12world cycles. Disc/controller timing, TOC/transport, remaining game paths and full firmware boot still need work. The game is not playable yet.

Latest ordinary local answer: {latest['words']} words in {latest['seconds']:.2f} seconds. This was an LM Studio SDK/tool test. Current visible native Chat operation remains unverified. Earlier larger evidence response took {measures[0]['seconds']:.2f} seconds; these are two individual observations with possible cache effects.

Advertising Assistant is configured with saved research. Trained pilot models are retained for experiments; source citation and teaching-design errors have been found, so research outputs still require source review. Game Team.command is a separate experimental coding workflow, not the daily Chat launcher.

EXACT WHO / PROMPTS / RESPONSES
{out/'who-prompts-and-responses.txt'}

SOURCE STATUS
{ROOT/'CURRENT DECOMPILATION.txt'}

LOCAL INFERENCE / ADVERTISING STATUS
{ROOT/'CURRENT LOCAL INFERENCE.txt'}

PRIOR DAILY PAGE HISTORY
{history}
'''
    (ROOT/'START HERE.txt').write_text(start)
    inference=f'''CURRENT LOCAL INFERENCE
Updated {now.isoformat()}

Everyday model: local/advertising-qwen38 (27B,6bit), identifier advertising-scholar,32,768-token context, one worker,60-minute idle TTL. Shared by Game Assistant and Advertising Assistant. No weights, preset or model defaults changed in this checkpoint.

GAME ASSISTANT TEST
Same ordinary question before/after compact boot evidence: {measures[0]['words']} words/{measures[0]['seconds']:.2f}s, then {latest['words']} words/{latest['seconds']:.2f}s. Both made one evidence lookup and completed naturally. Core scope accepted; concise output omits some counts and fixture details. Tool response sizes: {measures[0]['tool_result_UTF8_bytes']} then {latest['tool_result_UTF8_bytes']} UTF-8 bytes. Warm/cache effects may contribute. This is SDK inference, not a fresh native Chat test or broad benchmark.

LATEST EXACT ANSWER
{runs[-1]['results'][0]['answer']}

WHO DID WHAT
Coordinator translated/integrated BIOS3006, checked original/C execution and compacted evidence lookup. Local Game Assistant explained saved evidence twice on the same model. No independent model code review or new weight training. Current native Chat test remains pending; work continues while UI is inaccessible.

ADVERTISING
Saved research retrieval and sequential researcher/educator/reviewer workflow are configured. Latest classroom task required source-page and study-design corrections; do not promote that first draft as verified. Corrected activity:
{ROOT/'verification/easy-advertising-lesson-review/20261014T201641.431986Z/corrected-classroom-activity.txt'}
Experimental advertising/game trained pilots remain retained and unpromoted. Future256GB model/worker profile remains unbenchmarked.

EXACT PROMPTS, TOOL CALLS, RESPONSES, TIMING AND REVIEW
{out/'who-prompts-and-responses.txt'}
{out/'review.json'}

PRIOR HISTORY
{history/'CURRENT LOCAL INFERENCE.txt'}
'''
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(inference);(out/'readable-results.txt').write_text(start)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p)
    n.update(last_turn_classification='progress',source_audit=cp['audit'],local_audit=str(out),local_roles_this_turn='Coordinator authors/translates/tests source; GameAssistant explains the same question twice with full then compact installed boot evidence. Same27B6bit32k one-worker model viaSDK; exact prompts/tool/results retained.')
    n['next_source_work'][0]='Actual residentBIOS3000/3048/3006 execute from hostloadedROM bytes. Implement actual305A TOC and remaining transport/GPU CDISR, firmware relocation/stage-load/boot; source-poll controller ticks remain supplied until global timing is verified.'
    save(p,n)
    print(json.dumps(dict(status=report['status'],directory=str(out),observations=measures)))
if __name__=='__main__':main()
