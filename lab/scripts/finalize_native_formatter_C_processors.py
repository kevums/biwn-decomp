"""Close this integration turn against actual evidence and process state."""
import hashlib,json,shlex,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import native_format_evidence

def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')

def main():
    active=read(ROOT/'verification/native-formatter-C-operator-active.json')
    out=Path(active['directory'])
    pp=ROOT/'verification/native-formatter-C-processors-publication-current.json'
    publication=read(pp)
    current=native_format_evidence.load(ROOT)
    assert current.pop('proof_sha256')==sha(pp) and current==publication['current_status']
    mp=ROOT/'verification/native-formatter-C-processors-MCP-current.json';mcp=read(mp)
    assert mcp['publication_sha256']==sha(pp) and mcp['current_status']==current and mcp['actual_MCP_calls']==3
    ap=ROOT/'verification/advertising-seminar-evaluation-publication-current.json';advertising=read(ap)
    for p,h in advertising['dependencies_sha256'].items():assert sha(p)==h,p
    assert advertising['new_training'] is False
    controls_reader=read(ROOT/'verification/BIWN-controls-Reader-reviewed-current.json')
    assert controls_reader['final_channel_words']==36 and controls_reader['raw_reply_accepted_as_display'] is False
    rd=Path(controls_reader['protocol']).parent
    assert sha(rd/'protocol.json')==controls_reader['protocol_sha256']
    rejected=read(ROOT/'verification/native-formatter-C-status-reader-reviewed-current.json')
    assert rejected['Reader_accepted'] is False and rejected['Editor_accepted'] is False and rejected['fallback_verified']
    bad_run=Path(rejected['protocol']).parent
    assert sha(bad_run/'protocol.json')==rejected['protocol_sha256']
    rt=Path('/Users/kevin/.lmstudio/local-ai-lab')
    for name in ['native_format_evidence.py','chat_tools.py']:
        assert (ROOT/name).read_bytes()==(rt/name).read_bytes()
    ps=subprocess.check_output(['ps','-axo','pid,ppid,etime,command'],text=True)
    live=[]
    for line in ps.splitlines()[1:]:
        parts=line.strip().split(None,3)
        if len(parts)!=4:continue
        try:args=shlex.split(parts[3])
        except ValueError:continue
        scripts=[Path(arg).name for arg in args if arg.endswith('.py')]
        relevant=['run_biwn_interactive.py','run_native_formatter_C_processors.py','ask_biwn_controls.py','ask_biwn_current_status.py']
        if any(name in scripts for name in relevant):live.append(dict(pid=int(parts[0]),ppid=int(parts[1]),elapsed=parts[2],scripts=scripts,command=parts[3]))
    assert all(row['scripts']==['run_biwn_interactive.py'] for row in live),live
    model=subprocess.check_output(['/Users/kevin/.lmstudio/bin/lms','ps'],text=True)
    assert 'advertising-scholar' in model and 'IDLE' in model
    (out/'processes.txt').write_text(ps)
    (out/'model-state.txt').write_text(model)
    now=datetime.now(timezone.utc)
    path=ROOT/'CURRENT DECOMPILATION.txt';text=path.read_text()
    start=text.index('A new combined C CPU/GPU/DSP/IRQ test is being checked separately:')
    stop=text.index('The older native-formatter',start)
    text=text[:start]+f'''The combined C CPU/GPU/DSP/IRQ providers pass two separate fresh 1,600-frame comparisons, one with the original movement prefix and one holding Up+C. All recorded full CPU/RAM/GPU/DSP/video/navigation fields and captured PCM match. The run-input pair records running state8 for1,000frames in each lane. GPU/DSP and IRQ providers have zero original fallback/rejection; CPU ownership begins at4000. These short runs have silent PCM and use the DSP music profile only. Retained platform services and the earlier CPU-only long route remain separately scoped.
{publication['report']}

'''+text[stop:]
    path.write_text(text)
    path=ROOT/'CURRENT LOCAL INFERENCE.txt';text=path.read_text()
    text=text.replace('Latest Code Author:',f'''Latest control-help Reader:6.43seconds,one actual configuredMCPcall. Its36word final-channel answer gives C+Up correctly. The raw reply repeated itself across a model formatting delimiter and failed the raw word cap; raw text is preserved, and delimiter extraction makes no semantic edits. This is a qualified frontend/workflow result, not broad model reliability.
{rd/'prompts-and-responses.txt'}
{rd/'coordinator-review.json'}

Latest Code Author:''')
    path.write_text(text)
    path=ROOT/'WATCH LOCAL AGENTS.txt';text=path.read_text().replace('Currently testing combined C CPU/GPU/DSP/IRQ providers from fresh disc entry.','Combined C CPU/GPU/DSP/IRQ providers now pass two separate fresh1,600frame comparisons, including the run shortcut.')
    text+=f'''\nControls Reader: same27Bweights; requested the controls table through configured MCP and answered the run question in6.43seconds. Raw reply duplicated text around a model delimiter. The36word final channel was accepted with that formatting qualification; no prose was rewritten.
{rd/'prompts-and-responses.txt'}
{rd/'coordinator-review.json'}
''';path.write_text(text)
    report=ROOT/'reports/local-inference-combined-processors-handoff.txt'
    report.write_text(f'''LOCAL AI LAB — COMBINED PROCESSORS AND LOCAL OUTPUT TEST
{now.isoformat()}

RUN IN THE PREVIEW
Hold keyboard C + Up to run forward. P starts/resumes/pauses. Shift is unmapped. C remains contextual in menus. Original input/dispatcher fixtures and a new fresh gameplay pair verify the mapping; direct native-keyboard and physical-controller testing remain unverified. The current preview process was left in place. Next launches display the shortcut in their control label.
{ROOT/'BIWN Controls.txt'}

GAME PROGRESS
Two separate fresh1,600frame comparisons now run the repaired14,690byte disc with C CPU/GPU/DSP/IRQ selection+entry providers together. Every recorded CPU,all2MBRAM,GPU/DSPstate,video,navigation and capturedPCM result matches native execution of the same repaired disc. The new Up+C pair records1,000running-state frames in both lanes. Both runs use the DSP music profile and silentPCM; media/audio listening remain separate. Original bootstrap and platform services remain. This does not extend the previous24,975frame CPU-only merchant/return proof to combined processors, erase earlier formatter/control differences, or demonstrate a whole-game rebuild/speedup/physical-console boot.
{publication['report']}

LOCAL OUTPUT TEST
The control-help Reader used the existing27B6bit32K model and one real configuredMCPlookup. It took{controls_reader['seconds']:.2f}seconds. The final-channel36word answer gives C+Up correctly. The raw reply was73words with repeated prose separated by a model formatting delimiter; it failed the original raw word cap and remains unchanged on disk. The explicit delimiter parser returns the final channel without semantic edits. This is a qualified usability result, not a raw-format pass or general model-quality result.
Exact prompt/tool/response: {rd/'prompts-and-responses.txt'}
Reviewed displayed answer: {rd/'rendered-answer.txt'}

The larger status Reader+Editor took{rejected['seconds']:.2f}seconds but both omitted required CPU/runtime scope. They were rejected, and the launcher uses a labelled verified-evidence fallback. The updated frontend saves the displayed status separately from raw model text.
{bad_run/'coordinator-review.json'}

Earlier guided local wait-C authorship remains8192nativecases plus7guards; first draft failed832/1024. This turn's processor integration and run-control fixtures were coordinator work, not additional local-model source recovery. Compiler/emulator processes are tools. Three final installedMCPlookups verify the latest status, controls and authorship views; those lookups do not generate model text.

ADVERTISING
Research Desk and Teaching Demo remain available on the existing local model. Their prior full-source teaching evaluation and coordinator-corrected example are unchanged. No new training, independent verification or adapter promotion occurred.
{ROOT/'reports/advertising-full-source-seminar-evaluation.txt'}

The daily model is loaded and idle. Native Chat generation was not verified in this round. The complete game/source/platform, physical boot/audio, representative training improvements and future256GBhardware test remain unfinished; the full goal stays active.
''')
    dependencies={}
    for p in [Path(__file__),pp,ap,mp,ROOT/'verification/biwn-controls-current.json',
        ROOT/'verification/BIWN-controls-Reader-reviewed-current.json',ROOT/'verification/native-formatter-C-status-reader-reviewed-current.json',
        ROOT/'native_format_evidence.py',ROOT/'chat_tools.py',ROOT/'biwn_status_editor.py',
        ROOT/'scripts/ask_biwn_current_status.py',ROOT/'scripts/ask_biwn_controls.py',
        ROOT/'Ask BIWN Candidate Status.command',ROOT/'Advertising Research Desk.command',ROOT/'Advertising Teaching Demo.command',
        ROOT/'CURRENT DECOMPILATION.txt',ROOT/'CURRENT LOCAL INFERENCE.txt',ROOT/'WATCH LOCAL AGENTS.txt',ROOT/'BIWN Controls.txt',
        report,out/'processes.txt',out/'model-state.txt']:
        dependencies[str(p)]=sha(p)
    for folder in [rd,bad_run]:
        for p in folder.rglob('*'):
            if p.is_file():dependencies[str(p)]=sha(p)
    for p in (out/'before').iterdir():dependencies[str(p)]=sha(p)
    checked=set(publication['status_dependencies_sha256'])|set(advertising['dependencies_sha256'])|set(dependencies)
    result=dict(status='terminal_combined_C_processors_controls_and_local_workflow_handoff_verified',
        recorded_at=now.isoformat(),directory=str(out),game_publication=str(pp),game_publication_sha256=sha(pp),
        advertising_publication=str(ap),advertising_publication_sha256=sha(ap),game_evidence_files=len(publication['status_dependencies_sha256']),
        all_checked_files=len(checked),integrity_mismatches=0,
        combined_processors_frames_per_pair=1600,separate_combined_pairs=2,sprint_state_frames_per_lane=1000,
        local_controls_Reader_seconds=controls_reader['seconds'],local_controls_final_channel_words=36,
        local_controls_raw_format_pass=False,explicit_channel_parser_used=True,semantic_output_edits=False,
        local_status_Reader_and_Editor_accepted=False,labelled_verified_status_fallback=True,
        installed_MCP_current_views_verified=True,native_Chat_verified=False,new_training=False,
        default_promoted=False,goal_complete=False,model_idle=True,live_processes=live,
        dependencies_sha256=dependencies,report=str(report))
    save(out/'verification.json',result)
    save(ROOT/'verification/native-formatter-C-operator-current.json',result)
    save(ROOT/'verification/native-formatter-C-operator-active.json',result)
    ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=read(ledger_path)
    ledger.update(status='active_combined_C_processors_and_run_control_verified_goal_incomplete',
        recorded_at=now.isoformat(),previous_goal_turn_classification='progress: fresh C CPU-only formatter runtime and guided local wait-C native checks published.',
        current_goal_turn_classification='progress',this_turn_classification='progress',
        current_goal_turn_progress='Combined C CPU/GPU/DSP/IRQ providers pass two separate fresh1600frame comparisons with0recordedstate/video/PCM differences; newUp+C game input records1000run-state frames in both lanes. Original control fixtures, currentMCP and qualified6.43second controlReader final-channel output verified.',
        current_goal_turn_evidence=str(pp),latest_operator_handoff=str(ROOT/'verification/native-formatter-C-operator-current.json'),
        latest_finite_jobs_running=False,live_processes=live,model_backend_observation=model.strip(),
        native_Chat_verified_this_turn=False,goal_complete=False,new_training=False,
        next_actions=['Exercise the new combined providers on the merchant/return and other scene routes; current combined proof is only separate1600frame tests.',
            'Recover more readable original-game functions and verify exception/IRQ behavior; instruction counters are not decompilation coverage.',
            'Improve representative local-model workflows and training gains while keeping validation/frozen advertising material outside training/index.',
            'Continue nativeChat usability, authenticated console boot, physical audio and future hardware verification.'])
    save(ledger_path,ledger)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a') as f:
        f.write(json.dumps(dict(recorded_at=now.isoformat(),coordinator='Combined C processor integration, original run-control fixtures, native/C fresh comparisons, visible control label and output-format handling',
            local_Controls_Reader='One configuredMCP lookup,6.43seconds; final36word channel accepted with explicit format qualification; raw73word duplicate preserved',
            local_status_Reader_Editor='Both rejected for omitted runtime scope; verified evidence fallback retained',new_training=False,native_Chat_verified=False,publication=str(pp),operator=str(ROOT/'verification/native-formatter-C-operator-current.json')))+'\n')
    print(json.dumps({k:result[k] for k in ['status','all_checked_files','integrity_mismatches','sprint_state_frames_per_lane','local_controls_Reader_seconds','local_controls_raw_format_pass','new_training','goal_complete','report']},indent=2))


if __name__=='__main__':main()
