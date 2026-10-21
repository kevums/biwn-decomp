"""Audit natural stage-loader continuation and ordinary local model outputs."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');proof=read(ROOT/'verification/game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json');raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass' and proof['cases']==2 and not cp['initial_game_stage_hostloaded']
    assert cp['natural_CPU_jump_to4000'] and not cp['CPU_replaced_at4000'] and cp['initial60000byte_boot_stub_supplied'] and not cp['source_boot_verified']
    for case in range(2):
        a=read(raw/f'case-{case}-native.json');b=read(raw/f'case-{case}-C.json');assert a==b
        assert (raw/f'case-{case}-native-final-RAM.bin').read_bytes()==(raw/f'case-{case}-C-final-RAM.bin').read_bytes()
        assert sha(raw/f'case-{case}-native-movie.wav')==sha(raw/f'case-{case}-C-movie.wav')
        w=b['summary']['startup']['source_music_word_events'];assert len(w)==13 and sum(2 in e['IRQs']for e in w)==4
    first=ROOT/'verification/easy-game-firstboot-scope/20261015T002511.159726Z';last=Path(read(ROOT/'verification/easy-game-firstboot-scope-pointer.json')['directory']);runs=[read(p/'protocol.json')for p in [first,last]]
    assert runs[0]['questions']==runs[1]['questions']
    for run in runs:
        item=run['results'][0];assert run['status']=='completed_pending_coordinator_review' and not item['quality_flags'] and item['words']<140
        assert all(s['stats']['stopReason']=='eosFound'for s in item['prediction_stats'])
    item=runs[-1]['results'][0];assert 'no longer preloaded' in item['answer'] and 'Full firmware boot and a playable game remain unverified' in item['answer']
    now=datetime.now(timezone.utc);out=ROOT/'verification/game-firstboot-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    findings=[
        'Previous goal turn was progress: actual ROM resident copy linked before seeded game4000 and separate3060 setup verified. This turn implements the missing game180000 loader/marker GPU/boot GPU and removes large-stage host loading and CPU replacement at4000.',
        'MarkerGPU64controlledIRQ cases cover129of144instructions; actual CPU303C/304E/3042-linked STUB16-long transfers cover135of144, union144of144. SourceD2=0patch pairs match3060 defaults. OtherD2/encryption modes are not verified. Linked4096byte and1032192byte original/C payloads match; fullstage SHA52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453.',
        'First linked stream stopped at equality. Coordinator corrected it to the source caller condition progress strictlypast100000; rerun matches fullstate/payload and finalprogress100020. Source32bytegranularity produces padding beyond nominal end. General padding/other callers remain unverified.',
        'Boot GPU native initialization probe found244executedaddresses; generated287startup/RLE/poll/shutdown blocks. Original/C two-profile initialization/redraw/shutdown comparison covers285of287selectedinstructions; two halted-loop instructions and other compressed inputs/paths remain unverified. ControlledVCOUNT0/4 and explicit flag event are supplied.',
        'Actual game180000 CPU prefix has82selectedinstructions,71reached on the currentregion/nonborrowMSF path. Two separate original/C loader profiles select actualTOCtrack2/minus6frames, request023217/STUB/D2=0/4000..100000, executeGPU initialization/markerIRQs/shutdown and naturally JMP4000 with fullCPU/RAM/hardware/orderedtrace-state/count equality.',
        'The same natural4000 CPU state now continues into sourceGPU/music initialization, sourceDD40 scheduledstartup,18assets/187movieframes/125audioenqueues and12worldcycles without4000CPU replacement or intermediate owned-processor reset/RAM restore during game180000 onward. Two fresh complete original/C profiles match CPU/privateRAM/logicalGPU-DSP/controller baseline+9byte extension/peripherals/events/WAV bytes, including13silent startup words/4timer2 events.',
        'New stage transfer95569controller ticks/33436GPU IRQs. Assets101261ticks/34681IRQs; movie232162ticks/81045IRQs. Transfer totals428992ticks/149162IRQs and470VBIs. Controller counts differ from the earlier hostloaded-stage fixture because the real stage read leaves a different controller/head state; the distance-dependent model is not physical/global timing proof. Mode/TOC polls/sourceGPUtimer events are separate.',
        'Failed attempts preserved: missing XOR emitter support; unused CPU template declarations rejected by Werror; missing entry_rows before constructor; copied source-entry return used an undefinedsha; then matching finalRAM/WAV still had earlierDAC/JERRY carryover and timing-counter classification differences. Initial pre-execution DAC(version9)/JERRY state is now canonicalized/shared before ROM copy, restored only at each initial fixture. C firmware305A hook is cleared on return like native3904.',
        'Next complete original/C run matched bothprofiles but its startupmusic gate failed: overriding source_entry ahead of MusicEngineMixin bypassed mixer initialization. Coordinator moved natural-entry preparation into an optional hook inside EntryBootMixin, preserving the existing mixer wrapper; the final complete rerun passes its13word/4timer2 gate. Checks were not removed or masked.',
        'Initial60000byte BIOS-loaded game stub/userBIOSROM/CPU-GPU-DSP-device seed/GPU R31 and host-invoked firmware3048/3006/305A API prelude remain supplied. Native CPU fixture resets occur in initial ROM/API setup, not during sourcegame180000-to4000/startup/movie/world. FixedVCOUNT4/controller pollticks/synchronousGPU work/nominalmovie pacing/SSI-VBI/system/later clocks/controlledposes/input/taskquiescence remain providers. Complete preceding/authenticated firmware/headerload/boot,globalphysicaltiming,otherregions/MSFbranches/inputs/movies/tasks/scenes/musicpaths/scanout/playability are unfinished.',
        'First local108word/21.15second SDK answer accurately explains stage delivery/inheritedCPU and supplied inputs/actions, but uses technical terms. Coordinator added a clearly labeled plain-language evidence summary. Latest96word/10.25second same-question replay preserves correct facts and fullboot/playability limits with clearer wording. Addresses/BIOS labels remain slightly technical. Exact responses are unchanged; no nativeChat verification or broad/heldout/general reliability claim.',
        'Coordinator authored all new source translations/integration/repairs/tests. Local GameAssistant explained saved evidence, not code-generation or test execution. Accepted local-model body171/component139counts unchanged; no new weights/defaults/presets or independent neural verifier. Advertising setup and prior source/causal qualifications remain unchanged.'
    ]
    scripts=['generate_biwn_GPU_CD_marker_ISR.py','check_biwn_GPU_CD_marker_ISR.py','check_biwn_CD_marker_stream_linked.py','probe_biwn_game_firstboot_GPU.py','generate_biwn_game_firstboot_GPU.py','check_biwn_game_firstboot_GPU.py','generate_biwn_game_firstboot_cpu.py','biwn_game_firstboot_runtime.py','check_biwn_game_firstboot_to_stage.py','check_biwn_game_firstboot_scheduled_startup.py','check_biwn_source_entry_boot.py','biwn_bios_resident_install_runtime.py','prepare_game_firstboot_evidence.py','check_game_firstboot_mcp.py','test_game_firstboot_scope.py']
    files=[Path(__file__),ROOT/'chat_tools.py',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/game-firstboot-MCP-check.json']+[ROOT/'scripts'/n for n in scripts]
    files.extend(ROOT/'verification'/n for n in ['GPU-CD-marker-ISR-checks.json','CD-marker-stream-linked-checks.json','game-firstboot-GPU-checks.json','game-firstboot-to-stage-checks.json','game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json'])
    files.extend(raw/n for n in ['initial-DAC-state.bin','initial-JERRY-state.bin'])
    files.extend(sorted(ROOT.glob('verification/game-firstboot*console*.txt')))
    failures=[]
    for category in ['BIWN-game-firstboot-to-stage','BIWN-game-firstboot-movie-transport-music-cold-entry-timer-startup-loading-movie-world']:
        for p in sorted((ROOT/'verification'/category).glob('*/status.json')):
            status=read(p)
            if status['status']!='terminal_pass':failures.append(dict(directory=str(p.parent),status=status));files.append(p)
    manifest=[]
    for n,p in enumerate(files):
        dest=out/f'{n:02d}-{p.name}';shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    for label,p in [('first',first),('plain-evidence',last)]:
        for name in ['protocol.json','prompts-and-responses.txt']:
            dest=out/f'{label}-{name}';shutil.copy2(p/name,dest);manifest.append(dict(source=str(p/name),snapshot=str(dest),sha256=sha(dest)))
    report=dict(status='natural_game180000_stage_load_startup_movie_world_verified_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],source_report=str(raw),interface=runs[-1]['interface'],model=runs[-1]['model'],words=item['words'],seconds=item['seconds'],first_output={k:runs[0]['results'][0][k]for k in ['words','seconds']},semantic_review=findings,failed_attempts=failures,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,implementation_authorship=cp['implementation_authorship'],manifest=manifest)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+cp['implementation_authorship']+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(findings)+'\n\nFIRST LOCAL EXACT SYSTEM / USER / TOOL RESULTS / RESPONSE\n'+(first/'prompts-and-responses.txt').read_text()+'\n\nPLAIN-EVIDENCE LOCAL EXACT SYSTEM / USER / TOOL RESULTS / RESPONSE\n'+(last/'prompts-and-responses.txt').read_text())
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
The game’s own loader now brings the large stage in from disc and continues directly into startup. Two original/C profiles match real stage/asset/movie transport, startup music, 187 movie frames and 12 world cycles. The initial small boot stub/firmware setup and some timing/input remain supplied; full boot and playability are unfinished.
Latest local answer: {item['words']} words/{item['seconds']:.2f} seconds, core scope accepted. Chat explains saved evidence, shows checked previews, searches references and verifies small CPU fixtures. Full startup comparisons use workspace scripts.

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
Latest {item['words']}-word answer/{item['seconds']:.2f}s with one evidence lookup. Correct actual stage delivery/natural entry and supplied smallstub/firmware/device/timing/input/fullboot/playability boundary. Correct supported tool actions; full comparisons require workspace scripts. First108-word answer/21.15s was accurate but technical. Plain coordinator evidence summary added before replay. Reused question/warm-cache effects: SDK, not native Chat or broad reliability evidence.

EXACT WHO / SYSTEM / USER / TOOL RESULTS / RESPONSES
{out/'who-prompts-and-responses.txt'}
REVIEW
{out/'review.json'}

ADVERTISING
Original method excerpts and explicit coordinator design notes are configured. Last199-word draft/31.43s improved grounding but still needs source, baseline timing and causal qualifications. Same-model reviewer missed errors. Corrected activity:
{ad/'coordinator-corrected-classroom-activity.txt'}
{ad/'who-prompts-and-responses.txt'}

Trained pilots remain loadable and unpromoted. Reused-question diagnostic feedback is training-only candidate data. Future256GB profile remains unbenchmarked. Native Chat interaction remains unverified; no UI attempt this turn.

PRIOR HISTORY
{history/'CURRENT LOCAL INFERENCE.txt'}
''')
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(source_audit=cp['audit'],local_audit=str(out),last_turn_classification='progress',local_roles_this_turn='Coordinator implemented actual game180000 marker-stage loader and natural4000 continuation, restored mixer wrapper and initialserial fixture invariants. Local GameAssistant explained facts/actions before/after plain-evidence summary. Exact outputs retained; no new training/defaults.')
    n['next_source_work'][0]='Replace supplied60000byte BIOS-loaded stub and host-invoked3048/3006/305A firmwareTOC prelude with preceding/authenticated ROM boot/header-load/dispatch and naturalCPU continuation. Actual game180000 now delivers1032192byte4000stage and continues into startup/movie/world in two matched profiles; no4000CPU replacement. Extend region/MSF/markerD2/buffer/bootGPU/othercaller variants and globaldevice schedule.';save(p,n)
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        dest=out/('current-'+name);shutil.copy2(ROOT/name,dest);manifest.append(dict(source=str(ROOT/name),snapshot=str(dest),sha256=sha(dest)))
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in manifest)
    assert (ROOT/'chat_tools.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/chat_tools.py').read_bytes()
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    save(out/'review.json',report);save(ROOT/'verification/game-firstboot-local-review.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),words=item['words'],seconds=item['seconds'])))
if __name__=='__main__':main()
