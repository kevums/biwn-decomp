"""Publish resident-copy progress, bounded proof and exact local-role audits."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');proof=read(ROOT/'verification/ROM-install-movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json');raw=Path(proof['directory'])
    assert read(raw/'status.json')['status']=='terminal_pass' and proof['cases']==2
    assert cp['resident_install_bytes']==2540 and cp['actual_ROM_resident_install_before_seeded_game_entry'] and not cp['resident_RAM_payload_host_copy']
    assert cp['initial_game_stage_hostloaded'] and not cp['complete_firmware_to_game_CPU_continuation'] and not cp['source_boot_verified']
    for case in range(2):
        assert read(raw/f'case-{case}-native.json')==read(raw/f'case-{case}-C.json')
        assert (raw/f'case-{case}-native-final-RAM.bin').read_bytes()==(raw/f'case-{case}-C-final-RAM.bin').read_bytes()
        assert sha(raw/f'case-{case}-native-movie.wav')==sha(raw/f'case-{case}-C-movie.wav')
    install=read(ROOT/'verification/bios-resident-install-CPU-checks.json');marker=read(ROOT/'verification/bios-marker-setup-CPU-checks.json')
    assert install['cases']==32 and install['source_instruction_coverage']==[6,6] and marker['cases']==24 and marker['source_instruction_coverage']==[22,22]
    first=ROOT/'verification/easy-ROM-install-scope/20261014T233728.174335Z';last=Path(read(ROOT/'verification/easy-ROM-install-scope-pointer.json')['directory']);runs=[read(p/'protocol.json')for p in [first,last]]
    assert runs[0]['questions']==runs[1]['questions']
    for run in runs:
        item=run['results'][0];assert run['status']=='completed_pending_coordinator_review' and not item['quality_flags'] and item['words']<140
        assert all(s['stats']['stopReason']=='eosFound'for s in item['prediction_stats'])
    item=runs[-1]['results'][0];assert 'Full startup tests require workspace scripts' in item['answer'] and 'not booting entirely' in item['answer']
    now=datetime.now(timezone.utc);out=ROOT/'verification/ROM-install-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    findings=[
        'Previous goal turn was progress: connected asset/movie transport and separate actual E00A caller proofs, evidence corrections and exact local responses were recorded. This turn replaces resident RAM payload initialization with actual ROM80203E..802054 copy before independently seeded game entry.',
        'Thirty-two original/C standalone fixtures cover all6selectedROM copy instructions, both CPU stack banks and SR/CCR/X variations. FullCPU/private2MBRAM/peripherals/controller baseline+9byte extension match. Source copies635longs/2540bytes from8084A6..808E92 to3000..39EC; it overshoots nominal source end808E90 by2bytes and leaves outside RAM untouched.',
        'Two fresh original/C profiles with actual resident install before separately seeded game4000 entry still match startup,18asset transfers/1,108,650bytes,187movieframes,125audioenqueues and12world cycles, complete CPU/privateRAM/logicalGPU-DSP/controller/peripherals/events/WAV bytes. UserROM and game stage remain supplied; complete firmware-to-game CPU continuation is explicitly unimplemented.',
        'Separate BIOS3060 marker-handler setup now matches24original/C user/supervisor/threeGPU-base fixtures, all22selectedCPUinstructions. It installs84longs/336bytes and sets3072=FF. MarkerGPU execution/patch modes/synchronization/first-stage delivery and natural game180000 boot remain unverified.',
        'First81word/17.11second local answer correctly rejected full disc boot, but said the assistant could verify bounded startup without distinguishing saved-report lookup from test execution. Coordinator added explicit supported-actions/tool-execution fields. Latest77word/11.98second same-question replay correctly explains supplied inputs and separate workspace tests, and lists report explanation, previews, reference search and small CPU fixtures.',
        'Both outputs are SDK/tool inference with the same27B weights and repeated question; warm/cache effects possible. Native Chat was not tested this turn. These timings are not heldout/general reliability or independent model verification.',
        'During new marker-setup generator creation, a copied output filename temporarily overwrote the original BIOS3000 generation metadata. The first marker test failed before execution because its own metadata file was missing. Coordinator corrected the filename, regenerated both mappings, confirmed original3000 C/H hashes match its earlier verified proof, then passed24marker cases. The connected test had already loaded its rows before the temporary metadata overwrite.',
        'Coordinator authored ROM/marker CPU translations, initialization linkage, source tests and evidence changes. Local GameAssistant explained evidence. Accepted local-model body counts remain171 and component counts139; no new weights/defaults/presets changed. Full firmware, stage boot, clocks, remaining game paths/playability and native Chat remain unfinished.'
    ]
    src=ROOT/'projects/black-ice-white-noise/restoration'
    files=[Path(__file__),ROOT/'scripts/generate_biwn_bios_resident_install_cpu.py',ROOT/'scripts/check_biwn_bios_resident_install_cpu.py',ROOT/'scripts/biwn_bios_resident_install_runtime.py',ROOT/'scripts/check_biwn_ROM_install_scheduled_startup.py',ROOT/'scripts/generate_biwn_bios_marker_setup_cpu.py',ROOT/'scripts/check_biwn_bios_marker_setup_cpu.py',ROOT/'scripts/prepare_ROM_install_evidence.py',ROOT/'scripts/check_ROM_install_mcp.py',ROOT/'scripts/test_ROM_install_scope.py',ROOT/'chat_tools.py',ROOT/'verification/ROM-install-MCP-check.json',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/bios-resident-install-CPU-checks.json',ROOT/'verification/bios-marker-setup-CPU-checks.json',ROOT/'verification/ROM-install-movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json',ROOT/'verification/ROM-install-run-console.txt']
    for n in ['biwn_bios_resident_install_cpu','biwn_bios_marker_setup_cpu']:
        files.extend(src/(n+suffix)for suffix in ['.c','.h'])
    manifest=[]
    for n,p in enumerate(files):
        dest=out/f'{n:02d}-{p.name}';shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest)))
    for label,p in [('first',first),('explicit-tool-scope',last)]:
        for name in ['protocol.json','prompts-and-responses.txt']:
            dest=out/f'{label}-{name}';shutil.copy2(p/name,dest);manifest.append(dict(source=str(p/name),snapshot=str(dest),sha256=sha(dest)))
    report=dict(status='actual_ROM_resident_install_verified_before_seeded_game_entry_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],source_report=str(raw),interface=runs[-1]['interface'],model=runs[-1]['model'],words=item['words'],seconds=item['seconds'],first_output={k:runs[0]['results'][0][k]for k in ['words','seconds']},semantic_review=findings,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,implementation_authorship=cp['implementation_authorship'],manifest=manifest)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+cp['implementation_authorship']+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(findings)+'\n\nFIRST LOCAL EXACT SYSTEM / USER / TOOL RESULTS / RESPONSE\n'+(first/'prompts-and-responses.txt').read_text()+'\n\nEXPLICIT-TOOL-SCOPE LOCAL EXACT SYSTEM / USER / TOOL RESULTS / RESPONSE\n'+(last/'prompts-and-responses.txt').read_text())
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
The BIOS now installs its resident RAM code using its original ROM routine. Two original/C profiles still match startup, real asset/movie transport, 187 movie frames and 12 world cycles. The game stage is still preloaded; complete disc boot, timing and playability remain unfinished.
Latest local answer: {item['words']} words/{item['seconds']:.2f} seconds, core scope accepted. Chat explains saved evidence, renders checked previews, searches references and verifies small CPU fixtures. Full startup comparisons use workspace scripts.

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
Latest {item['words']}-word answer/{item['seconds']:.2f}s with one evidence lookup. Correct real resident install and supplied stage/game-entry/full-boot boundary. Correct supported tool actions and separate workspace tests. First81-word answer/17.11s left tool capabilities vague; explicit scope fields added before replay. Same question/warm-cache effects: SDK, not native Chat or broad reliability evidence.

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
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(source_audit=cp['audit'],local_audit=str(out),last_turn_classification='progress',local_roles_this_turn='Coordinator translated/linked actual ROM resident install and separately verified BIOS3060 marker setup. Local GameAssistant explained source/host boundary and tool capabilities before/after explicit scope correction. No new training/default changes.')
    n['next_source_work'][0]='Implement game180000 prefix, actualBIOS3060 marker GPU handler/303C patch mode and marker-synchronized first-stage transfer into4000, replacing hostloaded stage. Actual ROM80203E installs resident RAM before separately seeded game4000 in two matched profiles, but complete firmware-to-game CPU continuation is still missing. Separate3060 setup24cases/all22instructions does not prove marker synchronization.';save(p,n)
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        dest=out/('current-'+name);shutil.copy2(ROOT/name,dest);manifest.append(dict(source=str(ROOT/name),snapshot=str(dest),sha256=sha(dest)))
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in manifest)
    assert (ROOT/'chat_tools.py').read_bytes()==(Path.home()/'.lmstudio/local-ai-lab/chat_tools.py').read_bytes()
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    save(out/'review.json',report);save(ROOT/'verification/ROM-install-local-review.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),words=item['words'],seconds=item['seconds'])))
if __name__=='__main__':main()
