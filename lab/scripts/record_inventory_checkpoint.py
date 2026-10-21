"""Record checked UI components, observed updates and exact-string tool repair."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    import sys;sys.path.insert(0,str(ROOT));import lab
    now=datetime.now(timezone.utc).isoformat();backup=read(ROOT/'verification/inventory-selection-checkpoint-backup.json')['directory']
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    checks=read(ROOT/'verification/biwn-inventory-select-checks.json');runtime=read(ROOT/'verification/biwn-inventory-runtime-review.json');local=read(ROOT/'verification/biwn-inventory-local-review.json')
    assert (checks['digit_decoder_CPU_cases'],checks['selection_block_CPU_cases'],checks['host_guard_cases'])==(4096,2581,14)
    assert runtime['all_observed_selection_copy_writes_covered']==8 and local['status']=='coordinator_reviewed_partial_facts_contract_rejected'
    attempts=[]
    for name in ['20261013T041341.857470Z','20261013T041900.272871Z','20261013T042052.919341Z']:
        out=ROOT/'verification/easy-inventory-fixture'/name;protocol=read(out/'protocol.json');assert protocol['status']=='completed_pending_coordinator_review'
        calls=[c['toolCallRequest']for e in protocol['events']for c in e['content']if c['type']=='toolCallRequest']
        tooltexts=[c['content']for e in protocol['events']for c in e['content']if c['type']=='toolCallResult']
        answer='\n'.join(c['text']for e in protocol['events']if e['role']=='assistant'for c in e['content']if c['type']=='text'and c['text'])
        assert len(calls)==len(tooltexts)==1
        if name!='20261013T042052.919341Z':
            assert isinstance(calls[0]['arguments']['bytes_hex'],(float,int))and tooltexts[0].startswith('Failed to parse arguments')
            verdict='failed_type_coercion_no_fixture_execution'
            note='Tool rejected numeric bytes before execution. Final message is unexecuted raw tool-call text, not an answer. Exact intermediate generation/parser boundary not captured; numeric coercion mechanism inferred from received arguments.'
            tool=None
        else:
            tool=json.loads(tooltexts[0]);assert tool['status']=='bounded_fixture_completed'and tool['final_registers']['D0']=='0x12340000'
            assert calls[0]['arguments']['bytes_hex'].startswith('hex:')and '0x12340000'in answer and len(answer.split())<60
            assert tool['executed_instructions'][0]['assembly'].startswith('btst.l')and tool['decoder']['display_normalizations']
            verdict='bounded_one_tool_call_answer_pass';note='Correct fullD0and CLR.W upperword explanation. Literalhex:marker preserves exact bytes; normalizedBTSTmetadata visible. One localSDK case, not nativeUI/generalautonomy proof.'
        row={'directory':str(out),'status':verdict,'note':note,'calls':calls,'tool_result':tool,'answer':answer,'words':len(answer.split()),'SDK_reported_seconds':protocol['SDK_reported_seconds'],'exact_prompts_and_responses':str(out/'prompts-and-responses.txt')}
        save(out/'coordinator-review.json',row);attempts.append(row)
    ease={'recorded_at':now,'status':'literal_hex_marker_repair_bounded_API_pass_native_refresh_unverified','attempts':attempts,
          'scope':'Same ordinary user question across three freshSDKruns. Bare and0xguidance attempts arrived numeric and failed. Literalhex:format completed one tool call in10.18seconds; user did not have to add marker. APImax2round guard, no nativeChat message.'}
    save(ROOT/'verification/easy-inventory-fixture-review.json',ease)
    validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==14
    validation.update(portable_C_component_count=16,latest_aggregate_update=now,
                      component_count_scope='Fourteen earlier components plus full digit helper1B718 and selection basic block1A1F0..1A254. The block is not a complete original function; actual1B786renderer remains excluded.',
                      nextstage_inventory_selection_C=checks)
    save(session/'boot-slice-validation.json',validation)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/summarize_biwn_checks.py')],check=True)
    game=('Sixteen isolated portable C components checked. New digit helper and inventory-selection basic block match4096decoder CPU cases,2581selection CPU/scripted-bus cases and14host guards. CLR.W zero-digit path retains D0upper16; bit priority and source rereads preserved. Basic block falls through1A254, not an original whole-functionRTS. Actual1B786rendering, fullCCR/controllerhardware and complete-game integration remain unverified. Latest approximateGhidra export remains18306instructions/206entry candidates.')
    observed=('Read-only9000frame input replay exactly matches all prior frames, DSP/command data, CPUcatalog and captures. All8observed active slot updates match checked C read-address/order shapes with statically inferred widths, write values/order and postframe outcomes. Original watch reads contain placeholderzero, not actualreadvalues; source snapshots are not instruction-time capture. C redrawcall is modeled; original-game emulator observation is not a reconstructed build. Local reviewer copied analyst’s false49D56read claim; both contracts rejected.')
    frontend=('Bounded fixture helper now accepts literalhex:strings without numeric recovery; float inputs remain rejected.160existingCPUcases/9guards and4prefixcompatibility/10invalidinput checks pass. One same-question localSDK test with revisedGameAssistant prompt/tool description returns correctD0=12340000in10.18seconds after two retained coercion failures. BTSTregister presentation corrected from manual reference with raw decoder text preserved. Updated configuration installed below; adoption in resident nativeChat remains unverified while locked.')
    next_work='Reconstruct original1B786drawing/data dependencies and broaden game integration. Verify revised fixture format/preset in nativeChat when UI accessible. Continue advertising semantic/source evaluation before further training/default promotion. Full goal active and incomplete.'
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['modelKey']=='local/advertising-qwen38'and models[0]['status']=='idle'
    evidence=['verification/biwn-inventory-select-checks.json','verification/biwn-inventory-runtime-review.json','verification/biwn-inventory-local-review.json','verification/easy-inventory-fixture-review.json','verification/cpu-fixture-hex-prefix-checks.json','verification/btst-register-display-checks.json']
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path)
        if name=='setup-status.json':value.update(updated_at_utc=now,game_work=game+' '+observed,frontend=frontend,pending=next_work)
        elif name=='current-runtime-state.json':value.update(recorded_at=now,models=models,model_state_refreshed_at=now,decomp_progress=game+' '+observed,
                    local_inference_jobs='All known jobs terminal: input component checks, two local role drafts and three ordinary-question API attempts completed; no background training/inference claimed.',
                    emulator_jobs='Inventory observer9000frame replay completed normally, baseline data/captures identical; original core/CDI/BIOS preserved.',visible_chat=frontend,
                    MCP_updated_evidence='Sixteen components and observed input/slot update consistency; new exact-string marker and BTSTnormalization sources refreshed. Live nativeChat adoption unverified.')
        elif name=='everyday-inference.json':value.update(updated_at=now,model=models,model_state_refreshed_at=now,frontend=frontend,latest_API_ease_review=str(ROOT/evidence[3]),latest_game_selection_review=str(ROOT/evidence[1]))
        else:
            value.update(recorded_at_utc=now,previous_goal_turn_classification=value['this_goal_turn_classification'],this_goal_turn_classification='progress: two inputUI Ccomponents checked6677CPUcases/14guards, identical9000frame replay and8writegroups, rejected correlated localcontracts, exact-string fixture APIrepair after retained failures',next_safe_work=next_work)
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['state']=game+' '+observed;item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Configure LM frontend'in item['requirement']:item['state']=frontend;item['evidence']=list(dict.fromkeys(item['evidence']+evidence[3:]))
                elif 'Multiagent game'in item['requirement']:item['state']+=' Latest inventory analyst/reviewer copy includes false49D56read; coordinator rejected contracts and uses checked C.';item['evidence']=list(dict.fromkeys(item['evidence']+[evidence[2]]))
            value['post_review_evidence'].update({Path(e).name:str(ROOT/e)for e in evidence})
        save(path,value)
    config=read(ROOT/'config.json');config['chat_frontend']['game']['status']=game+' '+observed+' '+frontend;save(ROOT/'config.json',config)
    intake=read(ROOT/'corpus/game/project-intake.json');intake.update(latest_checked_at=now,latest_checked_status=game+' '+observed,latest_inventory_CPU_check=str(ROOT/evidence[0]),latest_inventory_runtime_review=str(ROOT/evidence[1]));save(ROOT/'corpus/game/project-intake.json',intake)
    path=ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt';path.write_text(path.read_text()+'\nINPUT / INVENTORY SELECTION — '+now+'\nbiwn_inventory_select.c/.h add the full1B718digit helper and1A1F0..1A254selection basic block.4096decoderCPUcases and2581selection/scriptedbus cases plus14host guards pass. Preserve CLR.W upperword behavior, exact bit priority and rereads. Actual1B786redraw remains abstracted and the block has fallthrough, notRTS. Eight runtime active write groups/read-address shapes match under snapshot inputs; watchreadvalues are placeholders. Reproduce: .venv/bin/python scripts/check_biwn_inventory_select.py. Total16isolated checkedCcomponents.\n')
    for name in ['START HERE.txt','CURRENT DECOMPILATION.txt']:
        path=ROOT/name;text=path.read_text().replace('14 isolated portable C components','16 isolated portable C components').replace('components (14)','components (16)')
        if name=='CURRENT DECOMPILATION.txt':text+='\nLATEST INPUT / SELECTION CHECK — '+now+'\n'+game+'\n'+observed+'\n'
        else:text+='\nLatest input/selection update: two new checked components and eight observed slot updates. Ordinary SDK fixture question passed with one tool call after an exact-string format repair. Revised preset is installed; live native Chat refresh is not yet visually verified while locked.\n'
        path.write_text(text)
    path=ROOT/'POST REVIEW.txt';path.write_text(path.read_text()+'\nINPUT SELECTION / RUNTIME CONSISTENCY / TOOL STRING CHECKPOINT — '+now+'\n'+game+'\n'+observed+'\n'+frontend+'\nWHO DID WHAT: Codex translated original digit helper and UIblock, compiled/tested6677CPUcases and14host guards, added a read-only observer and verified9000frame baseline identity. Codex compared8active bus shapes/writegroups, corrected a missing1A21Cwidth lookup in the first review script, and rejected both local contracts. Actual local analyst→reviewer repeated an incorrect49D56read claim and errorsnone. Codex checked NXPmanual BTSTsize and corrected presentation without changing bytes. Two ordinary localSDK attempts failed schema type coercion and did not execute; a literalhex:marker preserved exact bytes and the third attempt passed. No Codex subagents, no independent verification, no weight/core changes.\nCPUfixtures: '+checks['directory']+'\nRuntime trace and compared groups: '+runtime['directory']+'\nExact local prompts/responses: '+str(Path(local['directory'])/'prompts-and-responses.txt')+'\nAll three ordinary-question prompts/results: '+str(ROOT/evidence[3])+'\nReview-script failed lookup iteration: '+str(ROOT/'verification/inventory-runtime-review-iterations/notes.json')+'\nPrimary BTSTreference: https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf#page=165\n'+next_work+'\nAll known jobs terminal at this checkpoint; usual27B idle. NativeChat/CLI/API distinctions and unresolved adoption retained.\n')
    install=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_frontend_config.py')],capture_output=True,text=True,check=True)
    (ROOT/'verification/inventory-frontend-install.txt').write_text(install.stdout+'\n'+install.stderr)
    assert (ROOT/'presets/Game Assistant.preset.json').read_bytes()==(Path.home()/'.lmstudio/config-presets/Game Assistant.preset.json').read_bytes()
    save(ROOT/'verification/inventory-selection-checkpoint.json',{'recorded_at':now,'backup':backup,'models':models,'CPU_components':16,'full_goal_status':'active incomplete','known_compute_jobs':'terminal','evidence':evidence,'frontend_config_installed':True,'live_native_Chat_adoption':'unverified while locked','next_work':next_work})
    print(json.dumps({'recorded_at':now,'CPU_components':16,'CPU_cases':6677,'runtime_groups':8,'SDK_fixture':'third attempt passed10.18seconds','preset_installed':True,'native_adoption':'unverified','model_status':models[0]['status']}))


if __name__=='__main__':main()
