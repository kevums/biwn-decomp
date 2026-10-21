"""Bind live clock/movement evidence, original/recovered-C replays and Author rejection."""
import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import binary_tools


def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-format-movement-analysis'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    parent_path=ROOT/'verification/native-format-movement-diagnostic-current.json';parent=read(parent_path)
    assert parent['status']=='terminal_fresh_movement_diagnostic_prefixes_repeat_with_identical_buttons'
    replay_path=ROOT/'verification/native-format-movement-clock-replay-current.json';replay=read(replay_path)
    assert replay['status']=='terminal_original_dispatch_clock_counterfactual_matches_observed_movement'
    assert len(replay['cases'])==4 and all(r['full_recovered_C_CPU_and_2MB_RAM_equal']for r in replay['cases'])
    deps={}
    def bind(path):path=Path(path).resolve();deps[str(path)]=sha(path)
    for proof in [parent,replay]:
        for path,digest in proof['source_sha256'].items():assert sha(path)==digest,path;bind(path)
    bind(__file__);bind(parent_path);bind(replay_path)
    lanes={};all_rows={};all_records={}
    for lane in ['base','optimized']:
        folder=Path(parent['directory'])/lane;report=read(folder/'report.json');records_path=folder/'gameplay-events.bin.movement.jsonl'
        assert sha(folder/'report.json')==parent['results'][lane]['report_sha256'] and sha(records_path)==parent['results'][lane]['diagnostic_sha256']
        records=[json.loads(x)for x in records_path.read_text().splitlines()];all_rows[lane]=report['frames'];all_records[lane]=records
        bind(folder/'report.json');bind(records_path);bind(folder/'gameplay-observation.json')
        for path,digest in parent['results'][lane]['snapshots_sha256'].items():assert sha(path)==digest;bind(path)
        selected={}
        for seq in [6811,6812,6813,6814,6815]:
            selected[str(seq)]={}
            for pc in [0x1a188,0x1a26c,0x1a2c2,0x1a542]:
                r=next(x for x in records if x['world_sequence']==seq and x['pc']==pc)
                ram=Path(r['RAM']).read_bytes()
                selected[str(seq)][hex(pc)]={k:r[k]for k in ['frame','sequence','world_sequence','pc','clock','previous_clock','delta_clock','player','heading','speed','pad_49ba4','pad_49bac','gpu_packet','deltas']}
                selected[str(seq)][hex(pc)]['movement_fraction']=int.from_bytes(ram[0x49cc8:0x49ccc],'big')
        order=[{k:r[k]for k in ['sequence','pc','clock','world_sequence','task','exception_return_pc']}for r in records if r['frame']==9920]
        lanes[lane]=dict(executed_frames=10050,prior_selected_frame_differences=parent['results'][lane]['prior_prefix_selected_frame_differences'],
                         navigation_and_buttons_repeat_exactly=parent['results'][lane]['navigation_and_buttons_repeat_exactly'],
                         selected_world_updates=selected,frame9920_event_order=order)
    first=next(a['frame']for a,b in zip(all_rows['base'],all_rows['optimized'])if(a['raw_player_X'],a['raw_player_Z'])!=(b['raw_player_X'],b['raw_player_Z']))
    assert first==9920
    assert all((a.get('navigation')or{}).get('buttons')==(b.get('navigation')or{}).get('buttons')for a,b in zip(all_rows['base'],all_rows['optimized']))
    base=lanes['base']['selected_world_updates'];opt=lanes['optimized']['selected_world_updates']
    assert base['6812']['0x1a188']['player']==opt['6812']['0x1a188']['player']
    assert base['6812']['0x1a188']['movement_fraction']==opt['6812']['0x1a188']['movement_fraction']==44514
    assert base['6812']['0x1a26c']['delta_clock']==5 and opt['6812']['0x1a26c']['delta_clock']==4
    assert base['6812']['0x1a26c']['speed']==1 and opt['6812']['0x1a26c']['speed']==0
    assert base['6812']['0x1a26c']['movement_fraction']==5192 and opt['6812']['0x1a26c']['movement_fraction']==65485
    assert base['6813']['0x1a26c']['delta_clock']==4 and opt['6813']['0x1a26c']['delta_clock']==5
    assert base['6813']['0x1a26c']['movement_fraction']==opt['6813']['0x1a26c']['movement_fraction']==26163
    for k in ['player','heading','speed','movement_fraction']:
        assert base['6814']['0x1a542'][k]==opt['6814']['0x1a542'][k],k
    # Native event order establishes which side of the first tick the update
    # samples. This is stronger than attributing all differences to CPU speed.
    for lane in ['base','optimized']:
        events=lanes[lane]['frame9920_event_order']
        irq=next(r['sequence']for r in events if r['pc']==0xe7d4)
        world=next(r['sequence']for r in events if r['pc']==0x1a188)
        assert(irq<world)if lane=='base'else(world<irq)
    author_path=ROOT/'verification/native-string-reference-optimizer-current.json';author=read(author_path)
    assert author['status']=='terminal_local_Author_candidate_unverified' and author['passing_C_reference_supplied']
    gate=read(Path(author['directory'])/'preflight/native-format-string-active.json');assert gate['status']=='terminal_failed'
    mismatch=read(Path(gate['directory'])/'mismatch.json');assert mismatch['case']==0
    assert mismatch['original_CPU'][8]==0x1b1a0 and mismatch['compiled_CPU'][8]==0
    author_review=dict(status='rejected_reference_supplied_optimization_Author',
        source=str(author['source']),source_sha256=author['source_sha256'],passing_reference_supplied=True,
        input_tokens=author['input_tokens'],seconds=author['seconds'],AST_valid=True,
        first_failing_case=0,semantic_register='A0',expected='0x1B1A0',actual='0x00000000',
        source_diagnosis='Inverted the original BNE/goto fallback when restructuring: it assigns fallback for a nonzero source, and leaves NULL unchanged.',
        coordinator_edited_model_code=False,full_gate_run=False,promoted=False,new_training=False,
        evaluation_scope='One guided source-editing development task. Not a held-out recovery benchmark or evidence of efficient code.')
    save(out/'local-Optimization-Author-review.json',author_review)
    for folder in [Path(author['directory']),Path(gate['directory']),Path(replay['directory'])]:
        for path in folder.rglob('*'):
            if path.is_file():bind(path)
    bind(author_path)
    evaluation=ROOT/'evaluation/native-format-optimization';evaluation.mkdir(exist_ok=True)
    save(evaluation/'reference-editing-development-failure.json',dict(review=author_review,
        exact_prompt=author['directory']+'/prompts-and-responses.txt',
        reference_CFG='if (nonzero source) goto continuation; source=fallback; continuation:',
        equivalent_structured_condition='if (source is zero) source=fallback;',
        training_not_run=True,holdout_note='Development feedback. Exclude exact routine/task if later used for training.'))
    bind(evaluation/'reference-editing-development-failure.json')
    ram_path=ROOT/'render-assets/biwn-inventory-baseline.bin';ram=ram_path.read_bytes();bind(ram_path)
    ranges=[(0x1a1b2,0x1a1e0),(0x19a02,0x19a16),(0x19d42,0x19d78)]
    facts=[dict(start=hex(a),stop=hex(b),instructions=[{k:v for k,v in r.items()if k in ['address','size','bytes','assembly']}for r in binary_tools.m68k_instructions(ram[a:b],a)[0]])for a,b in ranges]
    save(out/'original-clock-quantizer-facts.json',facts);bind(out/'original-clock-quantizer-facts.json');bind(out/'local-Optimization-Author-review.json')
    report=ROOT/'reports/native-format-movement-clock-diagnosis.txt'
    report.write_text(
        'BIWN FIRST POSITION DIFFERENCE — CLOCK / MOVEMENT DIAGNOSIS\n'+now.isoformat()+'\n\n'
        'The first position difference is a clock-sampling/fractional-movement threshold shift. At world update6812 in frame9920, '
        'base samples clock47775after the first observed IRQ entry; optimized samples47774before that entry. '
        'Both start with the same player coordinates/fractions,heading226,heldpad0x100000 and movement accumulator44514. '
        'The previous movement clock is47770, so the measured elapsed values are5versus4.\n\n'
        'The original input routine computes the forward movement fraction using elapsed ticks: '
        'floor(((3*dt*8)&65535)*65536/300), adds the saved fraction, outputs the high16bits as movement, and retains low16bits. '
        'dt5 gives1unit/fraction5192; dt4 gives0units/fraction65485. '
        'The GPU receives these different movement arguments and returns the corresponding zero/nonzero deltas. '
        'The next update reverses the tick amounts4versus5; both fractions become26163 and the integer position catches up. '
        'By update6814 all recorded player components,heading,speed and accumulator match again. '
        'This does not establish all later movement/timing equivalence or identify the full earlier scheduling shift.\n\n'
        'FRESH LIVE EVIDENCE\n'
        'Two new HLEstarts,10050frames each,with identical recorded buttons through the entire prefix. '
        'Every recorded playerX/Z,mode,floor,scene,video hash,cumulative audio-count frame and navigation decision repeats the corresponding prior build prefix exactly. '
        'Read-only instruction observer records clock/movement/controller/GPUworkRAM/IRQentry and captures RAM around9915..9923. '
        'No guest RAM,CPU,disc,controller-policy,waypoint or arrival-tolerance change. The full original engine and platform providers remain.\n\n'
        'CONTROLLED SOURCE REPLAY\n'
        'Four offline original191F4..19F2Ainput-routine runs: each captured buildRAM with explicit elapsed ticks4and5. '
        'Original signed division executes on the retained CPU; no helper-result stub. Both captured build memories give exactly the same result for the same supplied ticks. '
        'The unchanged recovered hostC input routine plus real recoveredC signed division matches all16D/A registers,PC,SR,USP,SSP and all2MBRAM in all four fixtures. '
        'These are isolated explicit-input fixtures with IRQ disabled; no physical timing,live C substitution,fault behavior,ordered-native-access trace or whole-game proof.\n\n'
        'LOCAL OPTIMIZATION AUTHOR OUTPUT TEST\n'
        'Daily Qwen3_5 27B6bit received the complete passing string-helper C plus ABI/ISAheaders. '
        '3925inputtokens,'+str(round(author['seconds'],2))+'seconds. This tested source editing with a reference, not recovery from scratch. '
        'Its source passed AST validation but failed the first original-CPU case: NULLsource should leaveA0=0x1B1A0,but outputA0=0. '
        'It reversed the fallback branch when restructuring the supplied goto. No coordinator patch,full gate,efficiency claim or promotion. '
        'Exact prompt/output: '+author['directory']+'/prompts-and-responses.txt\n\n'
        'Next source/tool work: isolate the earlier task/IRQ phase shift and improve safe compiler lowering/optimization; preserve rejection data and validate representative training on separate tasks. '
        'Advertising research/education training,full game recovery/platform replacement,physical console/audio and future256GBhardware remain incomplete.\n')
    bind(report)
    result=dict(status='terminal_clock_quantization_explains_first_position_difference_with_limits',recorded_at=now.isoformat(),directory=str(out),report=str(report),
        first_position_difference_frame=9920,common_buttons_verified_through_frame=10050,world_update=6812,
        elapsed_ticks={'base':5,'optimized':4},initial_movement_fraction=44514,
        observed_movement={'base':dict(amount=1,fraction=5192),'optimized':dict(amount=0,fraction=65485)},
        sampled_clock={'base':47775,'optimized':47774},previous_clock=47770,
        base_IRQ_entry_precedes_world_update=True,optimized_world_update_precedes_IRQ_entry=True,
        next_update_elapsed_ticks={'base':4,'optimized':5},next_update_common_fraction=26163,
        rejoined_recorded_player_components_at_world_update=6814,lanes=lanes,
        offline_original_and_recovered_C_cases=4,full_CPU_and_2MB_RAM_equal=True,helper_results_stubbed=False,
        upstream_task_phase_cause_isolated=False,live_source_C_substitution=False,whole_game_speedup_demonstrated=False,
        local_Optimization_Author=author_review,new_training=False,default_promoted=False,native_Chat_verified=False,
        whole_game_complete=False,goal_complete=False,dependencies_sha256=deps)
    save(out/'report.json',result);save(ROOT/'verification/native-format-movement-analysis-current.json',result)
    print(json.dumps({k:result[k]for k in ['status','report','first_position_difference_frame','offline_original_and_recovered_C_cases','goal_complete']}))


if __name__=='__main__':main()
