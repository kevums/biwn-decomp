"""Archive exact local roles and candid coordinator evaluation, without cleanup."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
    primary=Path(read(ROOT/'verification/easy-timer-startup-scope-pointer.json')['directory'])
    reviewer=Path(read(ROOT/'verification/local-timer-startup-reviewer-pointer.json')['directory'])
    a=read(primary/'protocol.json');b=read(reviewer/'protocol.json');item=a['results'][0]
    assert a['status']==b['status']=='completed_pending_coordinator_review'
    assert all(s['stats']['stopReason']=='eosFound'for s in item['prediction_stats']+b['prediction_stats'])
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json')
    assert cp['source_system_clock_IRQ2_handler']and not cp['source_system_clock_direct_RAM_increment']and not cp['source_boot_verified']
    assert all(x in item['answer']for x in ['externally delivered','128 cases','112/142','cannot yet be booted and played'])
    assert all(x in b['response']for x in ['task quiescence','synchronous blitter/GPU completion','DSP music execution'])
    corrected=b['response'].split('Corrected answer:',1)[1].strip()
    now=datetime.now(timezone.utc);out=ROOT/'verification/timer-local-workflow-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    primary_findings=['Correctly distinguishes verified source clock-handler effects from supplied timer IRQ delivery and unverified physical period/global scheduling.',
        'Correctly reports standalone timer/helper coverage, continuous bounded chain and unverified full boot/playability.',
        'Does not clearly state that the source clock handler also runs in the connected chain; in-isolation wording is incomplete.',
        'Omits principal RAM/setup, task quiescence, file-CD/BIOS and synchronous GPU/blitter/movie timing providers; DSP music execution limit is not explicit.']
    reviewer_findings=['Identifies principal provider omissions and adds most to its corrected answer.',
        'Incorrectly says the primary explicitly excluded DSP music execution: primary did not; reviewer adds it only in correction.',
        'Incorrectly reports that primary omitted physical scanout: primary explicitly names it.',
        'Retains incomplete in-isolation framing; connected source timer handler is also verified.',
        f'Exceeds total220-word instruction with{b["words"]}words; corrected answer{len(corrected.split())}words meets160-word instruction.']
    files=[primary/'protocol.json',primary/'prompts-and-responses.txt',reviewer/'protocol.json',reviewer/'prompts-and-responses.txt',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/startup-loading-movie-world-MCP-check.json',ROOT/'scripts/test_timer_startup_scope.py',ROOT/'scripts/review_timer_startup_local_answer.py',ROOT/'chat_tools.py',Path(__file__)]
    manifest=[]
    for i,p in enumerate(files):
        dest=out/f'{i:02d}-{p.name}';shutil.copy2(p,dest);assert sha(p)==sha(dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(p)))
    review=dict(status='core_timer_scope_correct_with_provider_omissions_reviewer_partial_repair_failed_length_and_meta_accuracy',directory=str(out),recorded_at=now.isoformat(),model=a['model'],interface=a['interface'],roles=[dict(role=item['role'],seconds=item['seconds'],words=item['words'],findings=primary_findings),dict(role=b['role'],seconds=b['seconds'],words=b['words'],corrected_words=len(corrected.split()),findings=reviewer_findings)],same_weights=True,sequential_one_worker=True,independent_model_verification=False,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,source_code_authorship=cp['implementation_authorship'],source_code_verification_audit=cp['audit'],manifest=manifest)
    save(out/'review.json',review);save(ROOT/'verification/timer-local-workflow-review.json',review)
    transcript='COORDINATOR\n'+cp['implementation_authorship']+'\n\nPRIMARY EXACT SYSTEM/USER PROMPTS, TOOL MESSAGES, RESPONSE\n'+(primary/'prompts-and-responses.txt').read_text()+'\n\nREVIEWER EXACT SYSTEM/USER PROMPTS, TOOL MESSAGES, RESPONSE\n'+(reviewer/'prompts-and-responses.txt').read_text()
    (out/'who-prompts-and-responses.txt').write_text(transcript)
    note='LATEST LOCAL TIMER WORKFLOW\n'+now.isoformat()+'\n\n'+f'Everyday27B6bit/32K/one-worker. Primary{item["seconds"]:.2f}s/{item["words"]}words: core timer/boot/playability distinction correct; principal providers omitted. Reviewer{b["seconds"]:.2f}s/{b["words"]}words: adds providers but fails requested total length and two claims about primary wording. Exact outputs retained. Backend SDK, native Chat unverified; no new training/default changes or general reliability claim.\n\n'+cp['checked_answer']+'\n\nWHO / EXACT PROMPTS / RESPONSES\n'+str(out/'who-prompts-and-responses.txt')+'\n\nREVIEW\n'+str(out/'review.json')+'\n\n'
    p=ROOT/'CURRENT LOCAL INFERENCE.txt';p.write_text(note+p.read_text())
    p=ROOT/'START HERE.txt';p.write_text('Latest: source GPU timer IRQ2 handler replaces direct system-startup clock increments in two bounded Native/C chains.13externally delivered events,26startup handoffs,187movie frames,125audio enqueues,12world/NPC/renderer cycles. Standalone128timer cases/all33instructions; early CPU helpers56cases/112of142generatedinstructions. InitialRAM/setup, physicaltimer/globaltime, laterworld/movieclocks, input/task/CD/BIOS/GPUcompletion providers remain. Full4000boot/DSPmusic/physicalscanout/playability/nativeChat unverified.\nLocal inference primary21.09s, reviewer26.94s; reviewer partial repair with length/meta-accuracy failures recorded.\nAudit: '+str(out)+'\n\n'+p.read_text())
    print(json.dumps(dict(status=review['status'],directory=str(out),primary_seconds=item['seconds'],reviewer_seconds=b['seconds'],corrected_words=len(corrected.split()))))
if __name__=='__main__':main()
