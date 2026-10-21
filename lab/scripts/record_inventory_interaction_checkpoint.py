"""Record checked input-to-image integration without changing component count."""
from datetime import datetime,timezone
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    now=datetime.now(timezone.utc).isoformat()
    checks=read(ROOT/'verification/biwn-inventory-interaction-checks.json')
    roles=read(ROOT/'verification/biwn-inventory-interaction-local-review.json')
    transport=read(ROOT/'verification/inventory-interaction-MCP-check.json')
    assert checks['steps']==600 and checks['redraw_steps']==520 and checks['additional_original_components']==0
    assert roles['status']=='coordinator_reviewed_correlated_priority_error_rejected'
    assert len(transport['render_cases'])==5 and len(transport['invalid_input_cases'])==8
    ease=[]
    for name in ['20261013T064500.062495Z','20261013T064638.454840Z']:
        p=ROOT/'verification/easy-inventory-render'/name/'protocol.json';d=read(p)
        assert d['status']=='completed_pending_coordinator_review' and len(d['MCP_calls'])==1
        call=d['MCP_calls'][0];metadata=call['metadata']
        answer='\n'.join(b['text']for e in d['events']if e['role']=='assistant'for b in e['content']if b['type']=='text').strip()
        assert answer==metadata['verified_caption']
        if name=='20261013T064500.062495Z':assert call['arguments']['actions']==['cycle','cycle'] and metadata['starting_slot']==1
        else:assert call['arguments']['actions']==['0'] and metadata['starting_slot']==10 and metadata['visible_slot_labels'][0]==0
        assert call['PNG_image_block_received'] and not call['SDK_model_received_image_pixels']
        audit={'directory':str(p.parent),'question':d['user'],'tool_calls':1,'arguments':call['arguments'],'transitions':metadata['transitions'],'seconds':d['SDK_reported_seconds'],'answer':answer,'verdict':'passed requested actions and resulting PNG/caption'}
        save(p.parent/'coordinator-review.json',audit);ease.append(audit)
    review={'recorded_at':now,'status':'two_action_requests_passed','runs':ease,
            'scope':'Local SDK model selected tool and caption; fresh installed MCP executed C and returned PNG. Model received metadata only. Native Chat display remains unverified while locked.'}
    save(ROOT/'verification/easy-inventory-interaction-review.json',review)
    s=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    validation=read(s/'boot-slice-validation.json');assert validation['portable_C_component_count']==22
    validation.update(latest_aggregate_update=now,connected_inventory_selection_render=checks)
    save(s/'boot-slice-validation.json',validation)
    game=('22 checked C components (21 CPU, one GPU). Reconstructed selection, digit decoding, inventory/text drawing and sprite decoding now work together:600 input steps in60 sequences match original CPU/GPU execution, including520 redraws. '
          'External CPU bus traces,2MB RAM except10 formatter scratchbytes, blitter registers and panel bytes agree; fast/accurate engines agree. Earlier330 rendering cases/eight poisoned capture checks remain valid. '
          'Internal96x180 panel only, five of ten rows. Game display digits1..9 then0 correspond to positions1..10. Inputs are supplied game-memory words; physical polling, whole main loop, viewport/audio/game reconstruction and hardware validation remain unfinished. Existing emulator blitter and synchronous mailbox model remain dependencies.')
    frontend=('Installed Game Assistant preset and bounded renderer support an optional ordered action list (max20):cycle, digit strings0..9,none. Each call begins from the supplied starting position; it does not persist chat state. '
              'Two plain local requests applied cycle wrap and digit0 correctly in one tool call each; full prompts and responses saved. Native Chat visual adoption remains unverified while locked; API exchanges do not appear automatically in Chat history.')
    pending=('Reconstruct more of the game main-loop/scene behavior and investigate audio; continue source-grounded model quality work. Verify native Chat tool/image adoption when accessible. '
             'Advertising Source Pilot v1 remains loadable/experimental, everyday base default. Future256GB hardware unbenchmarked. Full goal active incomplete.')
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['status']=='idle'
    evidence=['verification/biwn-inventory-interaction-checks.json','verification/biwn-inventory-interaction-local-review.json','verification/inventory-interaction-MCP-check.json','verification/easy-inventory-interaction-review.json']
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        p=ROOT/'verification'/name;v=read(p)
        if name=='setup-status.json':v.update(updated_at_utc=now,game_work=game,frontend=frontend,pending=pending)
        elif name=='current-runtime-state.json':v.update(recorded_at=now,models=models,model_state_refreshed_at=now,decomp_progress=game,visible_chat=frontend,MCP_updated_evidence=frontend,
             local_inference_jobs='Two local roles and two action requests terminal; correlated priority error rejected. Usual27B idle; no background training/inference claimed.',emulator_jobs='600 final input-to-image steps terminal; earlier580-run and58-step preflight retained. Pinned emulator core unchanged.',latest_API_ease_review=str(ROOT/evidence[3]))
        elif name=='everyday-inference.json':v.update(updated_at=now,model=models,model_state_refreshed_at=now,frontend=frontend,latest_local_game_roles=str(ROOT/evidence[1]),latest_API_ease_review=str(ROOT/evidence[3]))
        else:
            v.update(recorded_at_utc=now,previous_goal_turn_classification=v['this_goal_turn_classification'],this_goal_turn_classification='progress: C selection linked to actual C renderer;600 original-vs-C input steps;bounded action tool installed and two plain requests passed;correlated role priority error rejected',next_safe_work=pending)
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=game;item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Configure LM frontend'in item['requirement']:item['state']=frontend;item['evidence']=list(dict.fromkeys(item['evidence']+evidence[2:]))
                elif 'Multiagent game'in item['requirement']:item['state']+=' Latest local Analyst/Reviewer both got cycle-plus-digit priority wrong; coordinator rejected that contract using exact original-code case.';item['evidence']=list(dict.fromkeys(item['evidence']+[evidence[1]]))
            v['post_review_evidence'].update({Path(e).name:str(ROOT/e)for e in evidence})
        save(p,v)
    config=read(ROOT/'config.json');config['chat_frontend']['game']['status']=game+' '+frontend;save(ROOT/'config.json',config)
    intake=read(ROOT/'corpus/game/project-intake.json');intake.update(latest_checked_at=now,latest_checked_status=game,latest_inventory_interaction_check=str(ROOT/evidence[0]));save(ROOT/'corpus/game/project-intake.json',intake)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+game+'\n\nINTERACTION CHECKS\n'+str(ROOT/evidence[0])+'\n\nBASE PANEL\n'+str(ROOT/'artifacts/reconstructed-inventory/inventory-panel-slot-1.png')+'\n\nCPU EXPORT\n18,306 decoded CPU instructions and206 entry candidates in latest drawing-volatile export; automatic C remains approximate. Selection block1A1F0..1A254 is not the entire1A188 main-loop function. Connecting existing components does not add an original component.\n\n'+pending+'\n')
    p=ROOT/'START HERE.txt';text=p.read_text();start=text.index('CURRENT RESULTS\n');end=text.index('\nAdvertising Source Pilot',start)
    text=text[:start]+'CURRENT RESULTS\n'+game+'\n'+text[end:]
    text=text.replace('TRY\n','TRY\nStart the rebuilt inventory at position9, advance twice and show the resulting panel.\nStart at position3 with $350, select digit0 and show the resulting panel.\n')
    text=text.replace('Positions','Positions')
    text+='\nINPUT ACTIONS — '+now+'\n'+frontend+'\nCorrected cycle request:8.7seconds; digit0 request:'+str(round(ease[1]['seconds'],1))+'seconds. Single measurements, not a benchmark distribution.\n'
    p.write_text(text)
    p=ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt';p.write_text(p.read_text()+'\nCONNECTED SELECTION / DRAWING — '+now+'\n'+game+'\nReproduce: .venv/bin/python scripts/check_biwn_inventory_interaction.py. Separate library tools/libbiwn-inventory-interaction.dylib preserves the earlier pinned render library. Source scripts/biwn_inventory_interaction_bridge.c links existing selectionC to actual C drawing.\n')
    p=ROOT/'POST REVIEW.txt';p.write_text(p.read_text()+'\nINPUT-TO-IMAGE INTEGRATION — '+now+'\n'+game+'\nWHO DID WHAT: Codex connected previously checked selectionC to the native C inventory pipeline in a separate bridge/library, preserving the old pinned library. Original oracle executes selection block, real digit helper, complete original drawing/text/sprite CPU routines and original GPU overlay; no redraw stub. Codex checked58-step preflight,580-step run, then added20 exact cycle-plus-digit1 priority steps after local review revealed an error. Final600-step/60sequence run passes, including520redraws; earlier runs retained.\nLocal27BAnalyst6.44seconds and Reviewer5.11seconds both said simultaneous cycle+digit1 frominternal4 yields1. Actual original/C result is5, demonstrated in finalfastsequence14/input0x80200. Both contracts rejected; other four answers match scoped evidence. Same weights and reviewer sees prior draft, not independent verification. No model code accepted or weighttraining this turn.\nExact role prompts/responses:\n'+str(Path(roles['directory'])/'prompts-and-responses.txt')+'\nCoordinator review:\n'+str(ROOT/evidence[1])+'\nCodex added max20action support to bounded preview tool; five valid PNGcases and eight new invalidaction guards pass without invalid cache creation. Corrected position/display terminology: game screen uses0forlastposition, not10. Each call starts from supplied position and fixed inventory. Both ordinary local-model action requests used one tool call and copied scoped verified_caption. SDK model received metadata, not imagepixels; native MCP returns PNG. Native Chat accessibility checked and Mac remained locked; no unlock requested per user instruction.\nRequest transcripts and audits:\n'+str(ROOT/evidence[3])+'\n'+frontend+'\n'+pending+'\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
    save(ROOT/'verification/inventory-interaction-checkpoint.json',{'recorded_at':now,'backup':read(ROOT/'verification/inventory-interaction-checkpoint-backup.json')['directory'],'components':22,'steps':600,'sequences':60,'redraw_steps':520,'known_compute_jobs':'terminal','models':models,'full_goal_status':'active incomplete','evidence':evidence,'native_Chat_adoption':'unverified while locked','next_work':pending})
    print(json.dumps({'steps':600,'components':22,'action_requests':2,'installed':True}))

if __name__=='__main__':main()
