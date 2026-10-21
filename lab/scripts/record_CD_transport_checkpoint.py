"""Archive transfer progress and ordinary local scope explanation."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');transport=read(ROOT/'verification/CD-transport-components-checkpoint.json');local=Path(read(ROOT/'verification/easy-CD-transport-scope-pointer.json')['directory']);a=read(local/'protocol.json');i=a['results'][0]
    assert cp['CDROM_timing_extension_compared']and transport['linked_cases']==4 and not transport['actual_transport_linked_into_game']and cp['main_game_CD_transport_file_backed']
    assert a['status']=='completed_pending_coordinator_review'and not i['quality_flags']and i['words']<160 and all(s['stats']['stopReason']=='eosFound'for s in i['prediction_stats'])
    assert i['answer'].startswith('No.')and 'file-backed' in i['answer']and 'cannot play' in i['answer']and '129118' in i['answer']
    now=datetime.now(timezone.utc);out=ROOT/'verification/CD-transport-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[Path(__file__),ROOT/'scripts/publish_CD_transport_components.py',ROOT/'scripts/check_CD_transport_mcp.py',ROOT/'scripts/test_CD_transport_scope.py',ROOT/'chat_tools.py',ROOT/'verification/CD-transport-components-checkpoint.json',ROOT/'verification/CD-transport-MCP-check.json',ROOT/'verification/CDI-normalization-offset-check.json',ROOT/'verification/startup-loading-movie-world-checkpoint.json',local/'protocol.json',local/'prompts-and-responses.txt'];manifest=[]
    for n,p in enumerate(files):
        target=out/f'{n:02d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    semantic=['Correctly distinguishes separate actual BIOS/GPU stream proof from still-file-backed connected game loading, reports all48/64component comparisons and four linked transfer sizes, and rejects full boot/playability.','Uses an internal boolean name and omits source32byteblock overshoot,SR2700/host API frames/ownedGPU MMIO shadow and some fixture details. Full declared-provider and buffer scope remains in source checkpoint.','Earlier controller comparisons saved baseline CDROM serialization without its9byte timing/IRQ extension. Fresh mode,TOC,transport,GPUISR and main-chain reruns include it; main187frame/12worldcycle outcomes still match.']
    report=dict(status='CD_transport_components_and_linkage_verified_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=transport['audit'],main_chain_audit=cp['audit'],interface=a['interface'],model=a['model'],words=i['words'],seconds=i['seconds'],semantic_review=semantic,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,manifest=manifest)
    save(out/'review.json',report);save(ROOT/'verification/CD-transport-local-review.json',report)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+transport['implementation_authorship']+'\nTranslated78CPU and94GPU fixed instructions.48CPU/64controlledIRQ comparisons; linked4CPU->controller->GPU FIFO->status/stop streams, including129118byte actualstartup asset. C-owned state persists; logical GPU synchronized to MMIO shadow, pipeline tail remains supplied. Full main-chain and component comparisons repeated with baseline+9byte CDROM timing extension. Current game path still uses file-disc transport; no independent physical normalization/timing claim.\n\nLOCAL GAME ASSISTANT EXACT PROMPTS / TOOLS / RESPONSE\n'+(local/'prompts-and-responses.txt').read_text()+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(semantic)+'\n')
    history=out/'prior-daily-pages';history.mkdir()
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,history/name)
    ad=read(ROOT/'verification/TOC-and-advertising-methods-review.json');ad_dir=Path(ad['directory'])
    start=f'''LOCAL AI — START HERE
Updated {now.isoformat()}

1. Double-click Game Model.command or Advertising Model.command. Both load the shared27B/6bit everyday model and open LM Studio.
2. In Chat, select Game Assistant or Advertising Assistant and enable local-ai-lab in Integrations.
3. Ask normally: Where are we with Black Ice White Noise, and can I play it yet?
Picture: Show the current interior drawing.
Advertising: Compare measured involvement in Olsen’s survey with a hypothetical randomized advertising experiment.

CURRENT GAME RESULT
Actual BIOS CPU read/status/stop code and GPU CD handler passed48/64component comparisons, all78/94instructions. Four linked transfers matched original/C, including one129118byte startup asset, without a payload-copy/progress script. The connected game still uses file-backed loading; actual transport adoption, full firmware boot/globaltiming/remaining scenes/tasks are unfinished. The game is not playable yet.
Latest local GameAssistant answer:115words/{i['seconds']:.2f}seconds; core scope accepted.

CURRENT ADVERTISING RESULT
Method-page excerpts and coordinator design notes improve retrieval; latest classroom draft still needs source/causal qualifications. Source-checked activity:
{ad_dir/'coordinator-corrected-classroom-activity.txt'}

These are LMStudio SDK/tool tests. Current visible native Chat remains unverified. Trained pilots are retained; no new weights/defaults changed. Game Team is a separate experimental coding workflow.

EXACT WHO / PROMPTS / RESPONSES / REVIEW
{out/'who-prompts-and-responses.txt'}
{out/'review.json'}
SOURCE STATUS
{ROOT/'CURRENT DECOMPILATION.txt'}
LOCAL INFERENCE STATUS
{ROOT/'CURRENT LOCAL INFERENCE.txt'}
PRIOR DAILY PAGE HISTORY
{history}
'''
    (ROOT/'START HERE.txt').write_text(start)
    inference=f'''CURRENT LOCAL INFERENCE
Updated {now.isoformat()}

Shared everydaymodel local/advertising-qwen38,27B/6bit,advertising-scholar,32,768context/oneworker/60minuteTTL. No new weights, presets or model defaults.

GAME ASSISTANT
Latest115word answer completed in{i['seconds']:.2f}s, one lookup. Correctly says component/API transport is verified separately and the connected game remains file-backed/unplayable. Internal boolean wording and incomplete fixture inventory remain rough edges. This is SDK inference, not verified native Chat.

EXACT COORDINATOR / GAME MODEL PROMPTS / RESPONSES / REVIEW
{out/'who-prompts-and-responses.txt'}
{out/'review.json'}

ADVERTISING
Original methods excerpts plus explicit coordinator design notes are configured. Last199word draft31.43s improved page/design grounding but still needs source, baseline-timing and causal qualifications. Same-model reviewer remained correlated and missed some errors. Corrected activity and exact earlier roles:
{ad_dir/'coordinator-corrected-classroom-activity.txt'}
{ad_dir/'who-prompts-and-responses.txt'}

Experimental trained advertising/game pilots remain loadable and unpromoted. Diagnostic feedback is training-only candidate data from a reused question, not independent heldout evidence. Future256GB profile remains unbenchmarked.

PRIOR HISTORY
{history/'CURRENT LOCAL INFERENCE.txt'}
'''
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(source_audit=transport['audit'],local_audit=str(out),last_turn_classification='progress',local_roles_this_turn='Coordinator authors CPU/GPU transport and validates against original instructions; GameAssistant explains four linked API transfers versus unchanged file-backed main-game path. Same27B model viaSDK; exact audit preserved.')
    n['next_source_work'][0]='Adopt actual BIOS303C/3042/304E plus GPUCDIRQ1 into source scheduledstartup/asset loading. Separate4stream API proof and first129118byte asset hash match; resolve actual caller/VBI progress,buffer/end semantics,padding,retained GPU shadow/event scheduling. Then transport/movie/firmware relocation/stage-load/fullboot/global timing. Do not promote separateAPI proof as game adoption.';save(p,n)
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        src=ROOT/name;target=out/('current-'+name);shutil.copy2(src,target);report['manifest'].append(dict(source=str(src),snapshot=str(target),sha256=sha(src)))
    for f in report['manifest']:assert sha(Path(f['snapshot']))==f['sha256']
    assert (ROOT/'chat_tools.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/chat_tools.py').read_bytes()and len((ROOT/'START HERE.txt').read_text().splitlines())<45
    save(out/'review.json',report);save(ROOT/'verification/CD-transport-local-review.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),words=i['words'],seconds=i['seconds'])))
if __name__=='__main__':main()
