"""Publish movement mechanism and the rejected local source-editing trial."""
import hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge


def read(path):return json.loads(Path(path).read_text())
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-format-movement-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    analysis_path=ROOT/'verification/native-format-movement-analysis-current.json';analysis=read(analysis_path)
    assert analysis['status']=='terminal_clock_quantization_explains_first_position_difference_with_limits'
    with ReferenceBridge()as bridge:
        status=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
    current=status['movement_clock_diagnosis']
    assert current['elapsed_ticks']=={'base':5,'optimized':4}
    assert current['full_CPU_and_2MB_RAM_equal']and current['offline_original_and_recovered_C_cases']==4
    assert current['local_Optimization_Author']['status']=='rejected_reference_supplied_optimization_Author'
    save(out/'configured-MCP-status.json',dict(connection=metadata,result=status,model_inference_invoked=False,native_Chat_verified=False))
    previous_path=ROOT/'verification/native-format-exit-publication-current.json';previous=read(previous_path)
    changed=[p for p,h in previous['dependencies_sha256'].items()if sha(p)!=h]
    expected={str(ROOT/'native_format_evidence.py'),str(Path.home()/'.lmstudio/local-ai-lab/native_format_evidence.py')}
    assert set(changed)==expected,changed
    save(out/'previous-workflow-revision.json',dict(previous_publication=str(previous_path),sha256=sha(previous_path),
         intentional_module_changes=changed,reason='Append bound movement-clock analysis; existing game source/tests and prior model outputs unchanged. Previous frozen source snapshots remain available.'))
    report=ROOT/'reports/native-format-movement-clock-and-local-output.txt'
    author=analysis['local_Optimization_Author'];raw_author=read(ROOT/'verification/native-string-reference-optimizer-current.json')
    report.write_text(
        'BIWN MOVEMENT CLOCK / LOCAL OUTPUT TEST\n'+now.isoformat()+'\n\n'
        'The first position difference atframe9920 is immediately explained by when the world task samples the clock. '
        'Base samples after the first clockIRQentry at47775; optimized samples before it at47774. '
        'Both start update6812with identical player coordinates/fractions,heading226,heldpad0x100000 and saved movement fraction44514. '
        'Elapsed ticks are5versus4. Original fractional movement logic therefore produces1unit/fraction5192versus0units/fraction65485. '
        'The next update reverses elapsed ticks4versus5 and the fractional state rejoins at26163; recorded player components match again by update6814.\n\n'
        'Two new fresh10050frame prefixes reproduce every recorded selected game/video/audio-count field and navigation decision of their respective prior builds, '
        'and use identical recorded buttons throughout. No live guest RAM,CPU,disc or controller-policy change. '
        'This isolates the immediate quantization mechanism, not the full earlier task/IRQ phase shift or all later gameplay differences.\n\n'
        'The original full input-routine path was replayed in four explicit offline captured-RAM fixtures with elapsed ticks4and5. '
        'Original native CPU and unchanged recovered hostC input routine plus real recoveredC division match all D/A registers,PC,SR,USP,SSP and all2MBRAM. '
        'No helper-result stubs. CPUentry/elapsed ticks are supplied and IRQ is disabled in this isolated test. '
        'No native console/liveC substitution,whole-game timing,ordered-native-access,fault or physical-console proof.\n\n'
        'LOCAL MODEL\n'
        'One local Optimization Author call to the daily Qwen3_5 27B6bit model. Complete passing C reference supplied; source editing,not recovery from scratch. '
        +str(author['input_tokens'])+'inputtokens,'+str(round(author['seconds'],2))+'seconds. '
        'AST accepted,first CPUcase rejected: expectedA0=0x1B1A0,actual0,after reversing the NULLfallback branch. '
        'Raw model source was not edited or promoted. No full CPU gate/efficiency claim,new training or independent Reviewer. '
        'Exact prompt/output: '+raw_author['directory']+'/prompts-and-responses.txt\n\n'
        'WHO DID WHAT\n'
        'Codex coordinator derived the read-only clock/GPU/IRQobserver, ran two fresh prefix processes, compared repeatability, '
        'replayed original and recoveredC input logic, checked original instruction facts and rejected the model source. '
        'The observer/compiler/CPUcomparison are deterministic tools,not extra LLMagents. '
        'A diagnostic disassembly excerpt initially ended mid-instruction; the analysis failed explicitly, the excerpt boundary was corrected, '
        'and that metadata analysis reran. Gameplay traces were not restarted for this.\n\n'
        'LOCAL FRONTEND\n'
        'Configured local-ai-lab MCP project_evidence(topic=status) now includes movement_clock_diagnosis and the Author rejection. '
        'Fresh configured stdio verified; source and installed modules match. Existing Ask BIWN Candidate Status.command uses that tool. '
        'No additional Reader generation or native Chat-window generation was tested this continuation. Previous successful Reader demonstrations remain historical scoped results.\n\n'
        'Detailed trace/source analysis: '+analysis['report']+'\n'
        'Next: investigate the upstream task/IRQphase shift and improve efficient source lowering/compilation. '
        'Preserve model failures as development feedback; validate separate representative tasks before training promotion. '
        'Full recovery/platform replacement,physical console/audio,advertising training/reliability and future256GBhardware remain open.\n')
    head=('CURRENT MOVEMENT CLOCK / OUTPUT TEST — '+now.isoformat()+'\n\n'
          'Frame9920movement difference follows5vs4elapsed ticks sampled on opposite sides of a clockIRQ. '
          'Four explicit offline original/recoveredC input-routine fixtures match fullCPU/2MBRAM. '
          'Upstream phase shift remains unresolved. Local source-editing Author rejected atcase0; no new weights/default promotion. '
          'Configured statusMCP includes current diagnosis; no new Reader/nativeChatgeneration this turn.\nReport: '+str(report)+'\n\nEARLIER RECORDS\n\n')
    for name in ['CURRENT LOCAL INFERENCE.txt','CURRENT DECOMPILATION.txt']:
        path=ROOT/name;path.write_text(head+path.read_text())
    watch=ROOT/'WATCH LOCAL AGENTS.txt';watch.write_text('LATEST CLOCK / SOURCE-EDITING OUTPUT TEST\n'+str(report)+'\n'
         'One local Optimization Author received passing C but failed the first CPUcase. Exact prompt/output is linked in the report. '
         'The current statusMCP also includes the native clock-quantization finding; no new nativeChatmessage or weighttraining was verified.\n\n'+watch.read_text())
    deps={};snapshots={}
    def bind(path,snapshot=False):
        path=Path(path).resolve();deps[str(path)]=sha(path)
        if snapshot:
            target=out/'snapshots'/(hashlib.sha256(str(path).encode()).hexdigest()[:16]+'-'+path.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target);snapshots[str(path)]=str(target)
    for path,digest in analysis['dependencies_sha256'].items():assert sha(path)==digest,path;bind(path)
    old_build=ROOT/'verification/native-optimized-format-publication-current.json'
    for path,digest in read(old_build)['dependencies_sha256'].items():assert sha(path)==digest,path;bind(path)
    for name in ['scripts/publish_format_movement_diagnosis.py','scripts/author_format_string_from_reference.py','native_format_evidence.py','chat_tools.py',
                 'scripts/ask_biwn_current_status.py','Ask BIWN Candidate Status.command','CURRENT LOCAL INFERENCE.txt','CURRENT DECOMPILATION.txt',
                 'WATCH LOCAL AGENTS.txt','verification/native-format-movement-analysis-current.json','verification/native-string-reference-optimizer-current.json']:
        bind(ROOT/name,True)
    for name in ['native_format_evidence.py','chat_tools.py']:
        p=Path.home()/'.lmstudio/local-ai-lab'/name;assert sha(ROOT/name)==sha(p);bind(p,True)
    bind(Path.home()/'.lmstudio/mcp.json',True);bind(old_build,True);bind(report,True)
    failed=ROOT/'verification/native-format-movement-analysis/20261018T170216.028591Z'
    for path in failed.iterdir():
        if path.is_file():bind(path,True)
    for name in ['configured-MCP-status.json','previous-workflow-revision.json']:bind(out/name,True)
    proof=dict(status='terminal_movement_clock_native_C_and_local_Author_review_published',recorded_at=now.isoformat(),directory=str(out),report=str(report),
        live_prefix_frames_per_lane=10050,first_position_difference_frame=9920,offline_original_recovered_C_cases=4,
        current_MCP_verified=True,native_Chat_verified=False,local_LLM_calls=1,local_Author_raw_source_accepted=False,
        passing_C_reference_supplied=True,new_training=False,default_promoted=False,upstream_task_phase_cause_isolated=False,
        whole_game_complete=False,goal_complete=False,dependencies_sha256=deps,snapshots=snapshots)
    save(out/'report.json',proof);save(ROOT/'verification/native-format-movement-publication-current.json',proof)
    ledger=ROOT/'verification/goal-continuation-current.json';goal=read(ledger);save(out/'goal-before.json',goal)
    goal.update(status='active_first_position_clock_mechanism_and_recovered_C_verified_full_goal_incomplete',recorded_at=now.isoformat(),
        previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
        current_goal_turn_progress='Fresh identical-button prefixes identify clock quantization at first position difference; original/recoveredC fullCPU/2MBRAM match four explicit fixtures. Reference-supplied local Optimization Author rejected; configured statusMCP updated.',
        current_goal_turn_evidence=str(ROOT/'verification/native-format-movement-publication-current.json'),latest_movement_clock_proof=str(analysis_path),
        latest_local_optimization_Author_review=author,latest_finite_jobs_running=False,
        latest_finite_job_status='Both fresh prefixes,original/Cfixtures and localAuthor generation/preflight terminal; no pending CPU/model job.',
        new_training=False,native_Chat_this_continuation=False,whole_game_complete=False,goal_complete=False,
        next_actions=['Isolate earlier task/IRQ phase shift; immediate frame9920clock quantization and laterNPCencounter are traced.',
                      'Improve safe native compiler lowering/optimization while preserving full CPU/RAM/access contracts; continue remaining source/platform recovery.',
                      'Use reference-editing branch inversion as development feedback; require representative separate validation before training promotion.',
                      'Continue advertising research/education training and reliability; physical console/audio and future256GBhardware remain unverified.'])
    save(ledger,goal)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:
        stream.write(json.dumps(dict(time=now.isoformat(),action='movement_clock_and_local_reference_editing_review',
            coordinator='read-only native prefixes,clock counterfactuals,existing recoveredC comparison,source/MCP evidence review',
            local_roles=['Optimization Author'],local_LLM_calls=1,source_reference_supplied=True,raw_source_accepted=False,
            training_updates=0,native_Chat_verified=False,proof=str(ROOT/'verification/native-format-movement-publication-current.json')))+'\n')
    print(json.dumps({k:proof[k]for k in ['status','report','offline_original_recovered_C_cases','local_LLM_calls','goal_complete']}))


if __name__=='__main__':main()
