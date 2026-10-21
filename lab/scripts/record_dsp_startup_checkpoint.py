"""Refresh current checkpoint after original DSP-startup CPU comparisons."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads(path.read_text())
def save(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc).isoformat()
    backup=read(ROOT/'verification/dsp-startup-checkpoint-backup.json')['directory']
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    checks=read(ROOT/'verification/biwn-dsp-startup-checks.json')
    reviewed=read(ROOT/'verification/biwn-dsp-startup-review.json')
    local=read(ROOT/'verification/biwn-dsp-startup-local-review.json')
    assert (checks['completed_CPU_cases'],checks['host_guard_cases'])==(96,19)
    assert reviewed['status']=='coordinator_reviewed_initial_stream_loop_and_CPU_startup'
    for role in local['roles']:
        obj=json.loads(role['text'])
        assert obj['copy_count_actual']==1156 and obj['zero_length_copy_count']==65536
        assert obj['mailbox_clear_condition']=='exactly zero'
        assert role['word_count']<180
    local.update(recorded_at=now,status='coordinator_reviewed_bounded_facts_pass_with_wording_omission',
                 decisions=['Both typed objects preserve supplied copy counts, exactzero mailbox condition, observed minus8 loop, scope and next test.',
                            'Reviewer identifies missing explicit warning that counter0 does not mean stopped timer; corrected observation below. It otherwise repeats analyst wording. Same weights and coordinator-supplied facts; no independent verification.',
                            'No local role wrote or executed the C comparison. Codex coordinator translated and checked original CPU instructions separately.'],
                 corrected_stream_observation='In sampled original-game emulator PC windows, control7fffff01 branches by-minus8 to3BD04 and reloads counter0. The sequencer executes; counter0 is not evidence of a stopped timer. No no-sound-assets or hardware-accuracy conclusion.',
                 source_review=str(ROOT/'verification/biwn-dsp-startup-review.json'),CPU_checks=str(ROOT/'verification/biwn-dsp-startup-checks.json'))
    save(ROOT/'verification/biwn-dsp-startup-local-review.json',local)
    save(Path(local['directory'])/'coordinator-review.json',local)
    validation=read(session/'boot-slice-validation.json')
    assert validation['portable_C_component_count']==10
    validation.update(portable_C_component_count=14,latest_aggregate_update=now,
                      component_count_scope='Ten earlier isolated components plus four original CPU DSP-startup/mailbox routines. No standalone DSP or whole-game equivalence.',
                      nextstage_DSP_startup_CPU_C=checks)
    save(session/'boot-slice-validation.json',validation)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/summarize_biwn_checks.py')],check=True)
    game=('Fourteen isolated portable C components checked. New original CPU entriesE942/E96C/E9EC/EA08 match96 scripted-bus/68000fixtures and19host guards: ordered16/32bit writes, all table/payload reads, exactzero mailbox polling, completedD1/A0/A1, other register preservation and private-stack return. Actual DSP payload4624bytes/1156longwords; zero/short lengths preserve the original65536-copy behavior, and signed/16bitwrap counts were checked. No DSP scheduling, CCR, hardware or complete-game validation. Original candidate and core unchanged.')
    audio=('The initial160byte stream at3BCE0 matches the original file and all279 postframe samples in the assisted-BIOS command baseline;40GPU writes populated it at483. DSP command2 selects pointer3BD04. Sampled DSP handler PCs in both game runs follow control7FFFFF01 through F1B9A2: minus8 returns to3BD04 and reloads counter0. The sequencer executes; counter0 is not proof of a stopped timer. The observed initial loop does not request a voice in those handler windows, consistent with zero game audio. No conclusion that sound assets are absent; alternate streams/actions and full reconstruction remain outstanding.')
    next_work='Locate alternate stream updates/selection and sound-triggering game paths; continue checked original event/voice reconstruction. Broaden source-grounded advertising evaluation before promoting another trained model. Full goal active and incomplete.'
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
    assert len(models)==1 and models[0]['modelKey']=='local/advertising-qwen38' and models[0]['status']=='idle'
    evidence=['verification/biwn-dsp-startup-checks.json','verification/biwn-dsp-startup-review.json','verification/biwn-dsp-startup-local-review.json']
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path)
        if name=='setup-status.json': value.update(updated_at_utc=now,game_work=game+' '+audio,pending=next_work)
        elif name=='current-runtime-state.json':
            value.update(recorded_at=now,model_state_refreshed_at=now,models=models,decomp_progress=game+' '+audio,
                         local_inference_jobs='All known jobs terminal:96CPU comparisons/19host guards and two local DSP-startup review roles completed. No background training/inference job claimed.',
                         ghidra_jobs='All logged jobs terminal;14isolated portable components checked. Approximate Ghidra export remains unverified as a full build.',
                         MCP_updated_evidence='Fourteen components; new CPU startup contract and initial audio stream loop observations refreshed.')
        elif name=='everyday-inference.json':
            value.update(updated_at=now,model=models,model_state_refreshed_at=now,latest_game_startup_review=str(ROOT/evidence[1]),latest_local_game_roles=str(ROOT/evidence[2]))
        else:
            value.update(recorded_at_utc=now,previous_goal_turn_classification=value['this_goal_turn_classification'],
                         this_goal_turn_classification='progress: four original CPU DSP-startup routines translated and checked96fixtures/19guards; initial stream loop traced and reviewed by two actual local roles',next_safe_work=next_work)
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:item['state']=game+' '+audio;item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Multiagent game' in item['requirement']:item['state']+=' Latest typed DSP-startup analyst/reviewer preserve bounded facts; reviewer flagged omitted counter0 warning, corrected by coordinator. Same-model correlated review remains supervised.';item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
            value['post_review_evidence'].update({Path(e).name:str(ROOT/e)for e in evidence})
        save(path,value)
    config=read(ROOT/'config.json');config['chat_frontend']['game']['status']=game+' '+audio+' Native Game Assistant — Quick Start remains configured32k/oneworker with all four tools.';save(ROOT/'config.json',config)
    intake=read(ROOT/'corpus/game/project-intake.json');intake.update(latest_checked_at=now,latest_checked_status=game+' '+audio,latest_DSP_startup_CPU_check=checks,latest_audio_sequence_review=str(ROOT/evidence[1]));save(ROOT/'corpus/game/project-intake.json',intake)
    path=ROOT/'START HERE.txt';text=path.read_text().replace('Ten isolated portable C components checked','Fourteen isolated portable C components checked');path.write_text(text+'\nLATEST DSP STARTUP / STREAM CHECK — '+now+'\n'+game+'\n'+audio+'\n')
    path=ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt';path.write_text(path.read_text()+'\nDSP STARTUP CPU PROTOCOLS — '+now+'\nbiwn_dsp_startup.c/.h translate four original CPU routines E942/E96C/E9EC/EA08. Reproduce: .venv/bin/python scripts/check_biwn_dsp_startup.py.96CPUfixtures and19host guards pass. Payload1156longwords, exactzero mailbox completion, widths/order and completedD1/A0/A1 checked. ASR/SUBQ/DBRA behavior preserved, including65536copies for zero length. Host read budgets/errors are added guards; no original timeout or D0 return inferred. These are CPU protocols, not standalone DSP implementations. Total14checked isolated components.\n')
    path=ROOT/'POST REVIEW.txt';path.write_text(path.read_text()+'\nDSP STARTUP / INITIAL STREAM CHECKPOINT — '+now+'\n'+game+'\n'+audio+'\nWHO DID WHAT: Codex coordinator located original CPU routines and literal references, translated four routines, compiled portableC and executed96original-CPU/scripted-bus comparisons plus19host guards. Coordinator matched stream population and sampled DSP code/PC paths, derived exact-minus8 control-loop arithmetic and corrected the counter0 wording. Actual local analyst→reviewer returned bounded typed summaries using separate contexts on the same27B model. Reviewer identified an omitted stopped-timer warning, but otherwise repeated analyst. No Codex subagents, no independent verification, no new training or core change.\nExact local prompts/responses: '+str(Path(local['directory'])/'prompts-and-responses.txt')+'\nCPU fixtures/guards: '+checks['directory']+'\nDSP original-byte decodes and sampled handler paths: '+reviewed['directory']+'\nCoordinator role review: '+str(ROOT/evidence[2])+'\n'+next_work+'\nAll known jobs terminal at this checkpoint; everyday27B restored idle. Native Chat history unchanged during locked API review; latest evidence becomes available through project_evidence.\n')
    save(ROOT/'verification/dsp-startup-checkpoint.json',{'recorded_at':now,'backup':backup,'models':models,'CPU_components':14,'checks':checks,'local_roles':str(ROOT/evidence[2]),'full_goal_status':'active incomplete','known_compute_jobs':'terminal','next_work':next_work})
    print(json.dumps({'recorded_at':now,'CPU_components':14,'CPU_cases':96,'host_guards':19,'local_roles':'bounded facts reviewed; wording corrected','model_status':models[0]['status']}))


if __name__=='__main__':main()
