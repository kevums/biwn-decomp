"""Reconcile completed checks and failures without promoting a failed model."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text())
def write(path,value): path.write_text(json.dumps(value,indent=2)+'\n')

def main():
    now=datetime.now(timezone.utc).isoformat()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    backup=ROOT/'config-backups'/stamp/'post-review-checkpoint';backup.mkdir(parents=True)
    names=['setup-status.json','requirements-audit.json','current-runtime-state.json',
           'everyday-inference.json','cpu-remediation-dataset.json']
    for name in names:shutil.copy2(ROOT/'verification'/name,backup/name)
    shutil.copy2(ROOT/'config.json',backup/'config.json')
    shutil.copy2(ROOT/'START HERE.txt',backup/'START HERE.txt')
    checks={name:str(ROOT/'verification'/name) for name in [
        'cpu-remediation-response-review.json','easy-local-tools-review.json',
        'cpu-fixture-tool-checks.json','chat-tools-fixture-mcp-check.json',
        'biwn-copy-checks.json','biwn-local-polling-team.json',
        'advertising-latest-team-review.json','word-limit-regression.json']}
    for path in checks.values():assert Path(path).exists()
    assert read(Path(checks['cpu-remediation-response-review.json']))['status']=='generated_answer_review_completed_candidate_rejected_as_default'
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio'))
    training=('Actual128-step game QLoRA completed; validation selected step96. Combined heldout teacher-forced loss3.946base to1.887adapter/hybrid. '
              'Generated comparison44responses rejected hybrid as default: all16CMP/BMI answers reportedD0=2, eight incorrect, with unsupported verification claims. '
              'Weights retained for diagnosis. No improved trained default promoted. Future dataset generator removes unsupplied execution claims; frozen training/evaluation records unchanged.')
    decomp=('Seven isolated portable C components checked, including CPU forward-byte copy and a device-command planner. New1024bytecopy fixtures,1024command traces and7host guards passed; device behavior unverified. '
            'Separate Ghidra listing18225instructions,206entry candidates/approximateCexports. Volatile shared-memory annotation restores the E0A6 polling/return representation with instruction bytes and function entries unchanged. '
            'New900frame BIOS/HLE processor snapshots each reproduce prior sampled PCs; BIOS first running lowGPU-PC at439, CPUwait begins620. '
            'HLE2184helper bytes match static relocation atframes177–205 with explicit36byte main-GPU overlap and4byte completion exclusions. HLEaudio still silent. Whole rebuilt game remains incomplete.')
    frontend=('Two saved native32k Chat assistants retain the existing27B model. Four MCP tools pass fresh stdio registration; bounded CPU fixture tool passes160CPUcases+9guards. '
              'Three ordinary-question API tests passed with one tool step+final answer in10–12seconds; earlier duplicate/hallucination failures retained. '
              'Updated preset/MCP activation remains untested in nativeUI. User authorizes local API while locked; full prompts/responses saved separately, not native Chat history.')
    advertising=('Actual local researcher→educator→reviewer source-backed lesson run completed. Final247words violated179maximum and rubric awarded incorrect performance. '
                 'Bounded repair145words swapped experiment labels and was rejected. Coordinator-corrected142word example saved separately. '
                 'Compact word-limit parser fixed and11checks passed. Supervised drafting only; no advertising weight adapter trained.')
    setup=read(ROOT/'verification/setup-status.json')
    setup.update(updated_at_utc=now,training=training,game_work=decomp,frontend=frontend,
                 advertising_workflow=advertising,quality='Generated prose remains unreliable; deterministic scoped checks and coordinator/source review required.',
                 pending='Full goal active and incomplete: whole-game reconstruction, improved trained default, advertising adaptation and native activation of new tool remain outstanding.')
    write(ROOT/'verification/setup-status.json',setup)
    dataset=read(ROOT/'verification/cpu-remediation-dataset.json')
    dataset.update(status='trained_scored_packaged_generated_candidate_rejected_as_default',
                   response_review=checks['cpu-remediation-response-review.json'],
                   future_generator_correction='Offline CPU execution provenance removed from assistant targets when not supplied in inference prompt. Existing frozen dataset and weights unchanged.')
    write(ROOT/'verification/cpu-remediation-dataset.json',dataset)
    audit=read(ROOT/'verification/requirements-audit.json')
    audit.update(recorded_at_utc=now,goal_status='active incomplete; API progress explicitly authorized while locked',
                 this_goal_turn_classification='progress: generated-answer rejection, bounded CPU tool/API tests, volatile decompiler annotation, processor snapshots and advertising failure/correction review')
    for item in audit['requirements']:
        requirement=item['requirement']
        if requirement=='Configure LM frontend on this Mac': item['state']=frontend
        elif requirement=='Train/adapt from prior game workflows': item['state']=training
        elif requirement=='Black Ice White Noise Atari Jaguar CD decompilation test':item['state']=decomp
        elif requirement.startswith('Advertising research/education'):item['state']=advertising
        elif requirement.startswith('Multiagent game'):item['state']='Actual local separate-context analyst/restorer/reviewer polling review recorded. Reviewer correctly identifies volatile propagation; two unsupported function/decode proposals rejected. Same-model roles remain correlated and require deterministic/source checks.'
    audit['post_review_evidence']=checks
    audit['next_safe_work']='Trace GPU flags/register banks and PC/control/interrupt ordering within assisted BIOSframes438–439. Continue original-instruction reconstruction and scoped CPU comparisons. Rework training data/evaluation before another adapter. Activate/test four tools in nativeChat when UI available.'
    write(ROOT/'verification/requirements-audit.json',audit)
    state=read(ROOT/'verification/current-runtime-state.json')
    state.update(recorded_at=now,models=models,decomp_progress=decomp,visible_chat=frontend,
                 local_inference_jobs='All logged comparison/role/repair/tool jobs terminal; current loaded model state recorded above.',
                 ghidra_jobs='All logged jobs terminal; seven isolated components only, approximate exports remain unverified.',
                 emulator_jobs='New processor-state BIOS/HLE900frames each terminal. Core/CDI/BIOS unchanged. HLEaudio failure retained.',
                 MCP_updated_evidence='Seven components, volatile annotation and processor snapshot summary supplied. New tool native activation/UI test pending.',
                 post_review=str(ROOT/'POST REVIEW.txt'))
    write(ROOT/'verification/current-runtime-state.json',state)
    everyday=read(ROOT/'verification/everyday-inference.json')
    everyday.update(updated_at=now,model=models,frontend=frontend,full_goal_status='active incomplete',
                    trained_candidate_status='Rejected as default after generated-answer comparison',
                    latest_API_ease_review=checks['easy-local-tools-review.json'],
                    latest_advertising_review=checks['advertising-latest-team-review.json'])
    write(ROOT/'verification/everyday-inference.json',everyday)
    config=read(ROOT/'config.json')
    config['chat_frontend']['game']['status']='Existing native32k supervised Chat retained; hybrid rejected after generated evaluation. New four-tool runtime installed, native activation/UI check pending. Seven isolated C components checked; whole game incomplete.'
    config['chat_frontend']['advertising']['status']='Existing native32k supervised Chat retained. Latest source-backed three-role run and bounded repair both need coordinator corrections; no advertising adapter trained.'
    config['models']['advertising']['status']='Ready for supervised drafting with source/variable/outcome/rubric/word-limit review; base weights unchanged.'
    write(ROOT/'config.json',config)
    repair=Path(read(ROOT/'verification/advertising-reviewer-repair-current.json')['directory'])
    review_lines=[
        'LOCAL AI LAB — POST REVIEW', 'Recorded '+now,
        'The full goal remains active and incomplete. Original DEV references and CDI are preserved.',
        'Current work uses the internal CDI copy; SHiN TiTAN can be ejected/disconnected.',
        '', 'WHO DID WHAT',
        'Codex coordinator: selected evidence/ranges, wrote and ran extraction/validation harnesses, reviewed model outputs, preserved failed attempts, applied the volatile annotation and prepared the corrected teaching example.',
        'Actual local model roles: separate fresh contexts on the same27B weights. Polling review: analyst→restorer→reviewer. Advertising: researcher→educator→reviewer plus one rejected reviewer repair. These are not independent models or human reviewers. No Codex subagents used.',
        'Deterministic tools: Ghidra approximate C; Capstone/MAME decoders; Unicorn isolated68000 execution; clang portableC fixtures; pinned VirtualJaguar original-game observations. Scope limits remain attached to each report.',
        '', 'RESULTS', training, decomp, frontend, advertising,
        '', 'EXACT LOCAL PROMPTS AND RESPONSES',
        str(ROOT/'verification/cpu-remediation-responses/20261012T223503.669686Z/prompts-and-responses.txt'),
        str(ROOT/'runs/20261012T223918.271453Z-game-polling-review/prompts-and-responses.txt'),
        str(ROOT/'verification/easy-local-tools/20261012T224608.859756Z/prompts-and-responses.txt'),
        str(ROOT/'runs/20261012T224641.967331Z-advertising/prompts-and-responses.txt'),
        str(repair/'prompts-and-responses.txt'),
        'Each accompanying protocol/request/role JSON preserves model, settings, original evidence, dependency drafts, output and timing. API requests do not appear automatically in native Chat history.',
        '', 'REVIEWED TEACHING EXAMPLE (COORDINATOR CORRECTION, NOT LOCAL-MODEL OUTPUT)',
        str(repair/'coordinator-corrected-lesson.txt'),
        '', 'CHECKS AND LIMITS', *checks.values(),
        str(session/'shared-volatile-summary.json'),str(session/'emulator-runtime/processor-state-review.json'),
        '', 'NEXT',audit['next_safe_work']]
    (ROOT/'POST REVIEW.txt').write_text('\n'.join(review_lines)+'\n')
    (ROOT/'START HERE.txt').write_text('''LOCAL AI — DAILY USE

1. Open LM Studio.
2. Choose Game Assistant — BIWN or Advertising Assistant — Research & Teaching from Chats.
3. Reload the last used model if needed, then ask normally.

Try: Where are we with Black Ice White Noise?
Try: Using Lee & Koo (2016), was involvement measured or manipulated?

Both saved chats use the existing local27B model at32k context, one worker. Earlier native Chat tests completed; generated code/statistics/causal wording still need review. Expand tool calls to inspect evidence.

The game has seven isolated portable C components checked. The complete reconstructed game is unfinished. The trained hybrid candidate failed generated accuracy checks and is NOT the default. The advertising workflow supports supervised source-backed drafting; no advertising weight adapter is trained.

New bounded CPU-fixture tool:160CPUcases+9guards passed; three ordinary-question localAPI tests passed in10–12seconds with a one-tool-step guard. Four tools register in a fresh MCP process. Updated preset/tool activation still requires a nativeUI check; the API guard has not been proved in nativeChat.

While locked, work continues through LM Studio's localhost API as requested. Those calls do not appear automatically in Chat history. Full agent prompts/responses, roles, corrections and failures are collected in POST REVIEW.txt and the linked records.

The preserved CDI working copy is on the Mac's internal drive. Eject SHiN TiTAN in Finder before unplugging; current work does not need it.
''')
    event={'time':now,'actor':'Codex coordinator; actual local LMStudio roles; deterministic tools; no Codex subagents',
           'action':'Reconcile generated model rejection, bounded CPU API checks, shared-memory annotation, processor snapshots and advertising repair failures',
           'post_review':str(ROOT/'POST REVIEW.txt'),'evidence':checks,'full_goal':'active incomplete'}
    with (session/'activity.jsonl').open('a') as stream:stream.write(json.dumps(event)+'\n')
    with (session/'workflow.txt').open('a') as stream:stream.write('\n'+now+'\n'+training+'\n'+decomp+'\n'+advertising+'\nPost review: '+str(ROOT/'POST REVIEW.txt')+'\n')
    print(json.dumps({'status':'checkpoint_saved_goal_incomplete','backup':str(backup),'post_review':str(ROOT/'POST REVIEW.txt'),'models':models},indent=2))

if __name__=='__main__':main()
