"""Record the checked C inventory render and preserve failed ease-test attempts."""
from datetime import datetime, timezone
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text())
def save(p, value): p.write_text(json.dumps(value, indent=2) + '\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    checks = read(ROOT/'verification/biwn-inventory-frame-checks.json')
    assert (checks['fast_cases'], checks['accurate_cases'], checks['actual_capture_poison_checks']) == (300, 30, 8)
    rows = []
    for p in sorted((ROOT/'verification/easy-inventory-render').glob('*/protocol.json')):
        d = read(p)
        assert d['status'] == 'completed_pending_coordinator_review'
        call = d['MCP_calls'][0]
        answer = '\n'.join(b['text'] for e in d['events'] if e['role']=='assistant' for b in e['content'] if b['type']=='text').strip()
        if p.parent.name in ['20261013T062028.045423Z', '20261013T062616.815011Z']:
            verdict = 'partial: image generated; caption ambiguously implies ten visible rows'
        elif p.parent.name == '20261013T063155.058090Z':
            verdict = 'failed: SDK adapter silently defaulted requested slot10 to slot1; retained, repaired and retested'
        else:
            assert answer == call['metadata']['verified_caption']
            expected = 10 if 'slot10 ' in d['user'] else 1
            assert call['metadata']['starting_slot'] == expected
            assert call['metadata']['selected_slot'] == expected
            assert call['metadata']['visible_slot_labels'] == [(expected-1+i)%10+1 for i in range(5)]
            assert call['PNG_image_block_received'] and not call['SDK_model_received_image_pixels']
            verdict = 'passed: requested parameters, PNG transport and exact scoped caption'
        audit = {'directory':str(p.parent), 'question':d['user'], 'seconds':d['SDK_reported_seconds'],
                 'tool_calls':len(d['MCP_calls']), 'actual_arguments':call['arguments'], 'answer':answer, 'verdict':verdict}
        save(p.parent/'coordinator-review.json', audit)
        rows.append(audit)
    assert len(rows) == 6
    ease = {'recorded_at':now, 'status':'reviewed_with_failures_and_repaired_retests_retained', 'runs':rows,
            'scope':'Local model tool choice and caption; fresh installed MCP returns PNG. SDK forwards metadata only, not pixels. Native Chat display/adoption remains unverified while locked.',
            'repairs':['Caption now copied from bounded renderer verified_caption, explicitly five visible rows.',
                       'SDK adapter now uses camelCase parameters to match SDK request keys, explicitly maps them to MCP snake_case, and asserts requested values were delivered. Native MCP tool itself passed slots1/10 before this adapter repair.'],
            'weight_training_this_checkpoint':False}
    save(ROOT/'verification/easy-inventory-render-review.json', ease)
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    validation = read(session/'boot-slice-validation.json')
    assert validation['portable_C_component_count'] == 22
    game = ('22 checked C components (21 CPU, one GPU). The integrated C inventory, text and sprite routines now render the internal96x180 inventory panel using the pinned emulator blitter. '
            '300 fast and30 accurate cases match original CPU/GPU execution; eight poisoned C renders exactly regenerate the saved original-game panel. Five of ten inventory rows are visible. '
            'No original CPU/GPU instructions or whole game frames execute in the rebuilt render. Hardware blitter emulation and synchronous mailbox acknowledgement remain dependencies. Full game/viewport, audio and physical hardware validation remain unfinished.')
    frontend = ('Five scoped MCP tools installed, including render_inventory_preview with visible slots1..10, optional money and PNG output. Plain local-model requests tested; exact prompts/responses retained. '
                'Native LM Studio Chat adoption/display unverified while locked. API exchanges do not automatically appear in Chat history.')
    pending = ('Broaden reconstructed game scene/UI integration and investigate game audio; continue source-grounded local-model evaluation and verify native Chat display when accessible. '
               'Advertising Source Pilot v1 remains loadable/experimental; everyday base remains default. Full goal active incomplete.')
    validation.update(latest_aggregate_update=now, component_count_scope=game, inventory_panel_reconstruction=checks)
    save(session/'boot-slice-validation.json', validation)
    subprocess.run([str(ROOT/'.venv/bin/python'), str(ROOT/'scripts/summarize_biwn_checks.py')], check=True)
    models = json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'], cwd=Path.home()/'.lmstudio', text=True))
    assert len(models)==1 and models[0]['status']=='idle'
    evidence = ['verification/biwn-inventory-frame-checks.json','verification/inventory-preview-MCP-check.json',
                'verification/easy-inventory-render-review.json','artifacts/reconstructed-inventory/provenance.json']
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        p=ROOT/'verification'/name; x=read(p)
        if name=='setup-status.json': x.update(updated_at_utc=now, game_work=game, frontend=frontend, pending=pending)
        elif name=='current-runtime-state.json':
            x.update(recorded_at=now, models=models, model_state_refreshed_at=now, decomp_progress=game, visible_chat=frontend,
                     local_inference_jobs='All six local render requests terminal; usual27B idle. No background training or inference claimed.',
                     emulator_jobs='330 original-vs-C panel cases and eight capture checks terminal. Pinned core unchanged.', MCP_updated_evidence=frontend,
                     latest_API_ease_review=str(ROOT/evidence[2]))
        elif name=='everyday-inference.json':
            x.update(updated_at=now, model=models, model_state_refreshed_at=now, frontend=frontend,
                     latest_API_ease_review=str(ROOT/evidence[2]), latest_inventory_frame_review=str(ROOT/evidence[0]))
        else:
            x.update(recorded_at_utc=now, previous_goal_turn_classification=x['this_goal_turn_classification'],
                     this_goal_turn_classification='progress: connected C sprite decoder, rendered internal inventory with emulated blitter;330 comparisons/eight poisoned capture checks; installed bounded PNG tool, repaired and retested normal requests', next_safe_work=pending)
            for item in x['requirements']:
                if 'decompilation test' in item['requirement']: item['state']=game; item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Configure LM frontend' in item['requirement']: item['state']=frontend; item['evidence']=list(dict.fromkeys(item['evidence']+evidence[1:3]))
            x['post_review_evidence'].update({Path(e).name:str(ROOT/e) for e in evidence})
        save(p,x)
    config=read(ROOT/'config.json'); config['chat_frontend']['game']['status']=game+' '+frontend; save(ROOT/'config.json',config)
    intake=read(ROOT/'corpus/game/project-intake.json'); intake.update(latest_checked_at=now,latest_checked_status=game,latest_inventory_frame_check=str(ROOT/evidence[0]));save(ROOT/'corpus/game/project-intake.json',intake)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+game+'\n\nREBUILT PANEL\n'+str(ROOT/'artifacts/reconstructed-inventory/inventory-panel-slot-1.png')+'\nComparison details and limits:\n'+str(ROOT/evidence[0])+'\n\nCPU EXPORT\n18,306 decoded CPU instructions and206 entry candidates. Automatic C remains approximate. Integration is not another original component.\n\n'+pending+'\n')
    (ROOT/'START HERE.txt').write_text('LOCAL AI — DAILY USE\n\n1. Open LM Studio.\n2. Select Game Assistant — Quick Start or Advertising Assistant — Research & Teaching.\n3. Load the last used model if necessary and type normally. Expand tool calls to inspect evidence.\n\nBoth everyday chats use the local Advertising Qwen38 model, thinking off,32,768 context and one worker.\n\nTRY\nShow the rebuilt Black Ice White Noise inventory panel starting at slot1 with $200.\nShow the rebuilt inventory starting at slot10 with $350.\nHow far have we got with Black Ice White Noise?\nUsing Lee & Koo(2016), was involvement measured or manipulated?\nMake a lesson on the involvement scale with an objective, hypothetical example, student question and independently scored answer key.\n\nCURRENT RESULTS\n'+game+'\n\nAdvertising Source Pilot v1 is trained, loadable and experimental. Everyday base remains default; both need source/teaching review. See TRY ADVERTISING PILOT.txt.\n\n'+frontend+'\n\nAGENTS AND AUDIT\nPOST REVIEW.txt links exact prompts, responses, errors and coordinator corrections. Sequential roles using one model are not independent verification. Current render requests need one local tool call, not multiple roles. Current corrected tests took about5.4seconds(custom slot); see audit for all successes and failures.\n\nThe verified CDI copy is internal. Current checks do not require the external game drive; eject it before unplugging.\n')
    p=ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt'; p.write_text(p.read_text()+'\nCONNECTED INVENTORY PANEL — '+now+'\n'+game+'\nReproduce comparisons: .venv/bin/python scripts/check_biwn_inventory_frame.py\nNative device bridge: scripts/biwn_inventory_device_bridge.c. Pinned emulator source unchanged. Preview: inventory_renderer.py, CLI internal slots0..9; MCP visible slots1..10.\n')
    p=ROOT/'POST REVIEW.txt'; p.write_text(p.read_text()+'\nREBUILT INVENTORY PANEL AND EASY LOCAL RENDER — '+now+'\n'+game+'\nWHO DID WHAT: Codex wrote the native device bridge linking previously checked gameC and the existing pinned emulator blitter; compared original CPU/GPU execution against nativeC across330cases; eight poison checks regenerated the exact saved original-game internalbuffer. Formatter scratch10bytes/private stack excluded; mailbox scheduling synchronous; colors use pinned emulatorCRYtables, not physical calibration. No emulatorcore edits, fullgame frames, new weighttraining or cloudsubagents.\nCodex built a bounded pinned-assets renderer and installed the fifth MCPtool returning PNGplusmetadata; two valid transport cases and12bad-input guards passed. The local27B model selected the renderer and wrote captions. Six exact attempts retained: firsttwo captions ambiguously said ten-slotpanel/layout; third fixed caption. Firstcustom-slot request exposed SDKadapter lost startingSlot and defaulted1; repaired adapter with explicit camelCase-to-MCPmapping plus assertions; customslot and default reruns passed. NativeMCPslotmapping had already passed direct checks. SDKmodel receivedmetadata only, no pixels. NativeChatdisplay remains unverified whilelocked; no fabricated Chat history.\nAll prompts and responses are in each listed run directory:\n'+str(ROOT/evidence[2])+'\nTransport/guards:\n'+str(ROOT/evidence[1])+'\nPixel comparison:\n'+str(ROOT/evidence[0])+'\n'+pending+'\n')
    install=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True,capture_output=True,text=True)
    (ROOT/'verification/inventory-frame-runtime-install.txt').write_text(install.stdout+'\n'+install.stderr)
    save(ROOT/'verification/inventory-frame-checkpoint.json', {'recorded_at':now,'backup':read(ROOT/'verification/inventory-frame-checkpoint-backup.json')['directory'],
         'portable_components':22,'CPU_components':21,'GPU_components':1,'original_vs_C_panel_cases':330,'capture_poison_checks':8,
         'MCP_tools':5,'local_render_attempts':6,'models':models,'full_goal_status':'active incomplete','known_compute_jobs':'terminal',
         'evidence':evidence,'fresh_evidence_snapshot_installed':True,'native_Chat_adoption':'unverified while locked','next_work':pending})
    print(json.dumps({'components':22,'panel_cases':330,'capture_checks':8,'render_attempts':6,'installed':True}))

if __name__=='__main__': main()
