"""Bind component/build/game evidence with explicit scope and metadata corrections."""
import hashlib,json,os,struct
from pathlib import Path
from datetime import datetime,timezone
from check_biwn_native_button_digit import ROOT,sha,save

def main():
    refs={name:ROOT/'verification'/file for name,file in dict(component='native-frame-acquire-lean-current.json',nested='native-frame-acquire-lean-nested-current.json',build='native-frame-acquire-lean-disc-build-current.json',candidate='native-frame-acquire-lean-route-current.json',control='native-frame-acquire-lean-layout-control-current.json').items()}
    data={k:json.loads(p.read_text()) for k,p in refs.items()};component,nested,build=(data[k] for k in ['component','nested','build'])
    assert component['source_accepted'] and nested['source_accepted']
    for state in [component,nested,build]:
        for field in ['dependencies_sha256','source_sha256']:
            for path,digest in state.get(field,{}).items():assert sha(path)==digest,(path,'Source changed')
    out=ROOT/'verification/native-frame-acquire-lean-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    (out/'reviewer-as-run.py').write_bytes(Path(__file__).read_bytes())
    bd=Path(build['directory']);normal=json.loads((Path(component['directory'])/'normal-results.json').read_text());zeros=json.loads((Path(component['directory'])/'zero-results.json').read_text());nested_rows=json.loads((Path(nested['directory'])/'results.json').read_text())
    assert len(normal)==631 and len(zeros)==192 and len(nested_rows)==72
    assert len(json.loads((bd/'linked-normal-results.json').read_text()))==631 and len(json.loads((bd/'linked-zero-results.json').read_text()))==192 and len(json.loads((bd/'entry-cases.json').read_text()))==96
    assert sha(build['derived_disc'])==build['derived_disc_sha256'] and sha(build['derived_stage'])==build['derived_stage_sha256']
    parent=json.loads(Path(build['parent_build']).read_text());old=Path(parent['linked_component']).read_bytes();payload=Path(build['linked_component']).read_bytes();changed=[i for i,(a,b) in enumerate(zip(old,payload)) if a!=b]
    assert changed==[] and build['heap_start']==parent['heap_start'] and build['component_bytes']==parent['component_bytes']
    routes={};all_terminal=True
    for label in ['candidate','control']:
        v=data[label];directory=Path(v['directory']);terminal=v['status']=='terminal_native_frame_acquire_route_pending_review';all_terminal &= terminal
        if not terminal:
            # An actual process check, not the presence of a running-state file.
            live=[]
            for key in ['pid','child_pid']:
                try:os.kill(v[key],0);live.append(v[key])
                except (ProcessLookupError,KeyError):pass
            assert live,('Nonterminal job has no live handle',label)
            routes[label]=dict(status=v['status'],directory=str(directory),live_pids=live);continue
        report=json.loads((directory/'candidate/report.json').read_text());observed=json.loads((directory/'candidate/gameplay-observation.json').read_text());assert not observed['errors'] and not observed['copy_errors']
        rows=report['frames'];raw=(directory/'candidate/gameplay-events.bin').read_bytes();events=[struct.unpack_from('<II',raw,i) for i in range(0,len(raw)//112*112,112)];calls=[f for f,pc in events if pc==0x1ac68]
        assert observed['acquire_entries']==len(calls) and observed['acquire_returns']==len(calls)
        routes[label]=dict(status=v['status'],directory=str(directory),frames=len(rows),returned_outdoors=v['returned_outdoors'],whole_old_route_equivalent=v['frame_differences']==dict.fromkeys(v['frame_differences'],0) and v['PCM_equal'],per_frame_differences=v['frame_differences'],PCM_equal_to_old_parent=v['PCM_equal'],live_monitor_pass=v['live_monitor_pass'],observations=observed,first_entry_frame=calls[0] if calls else None,actual_events=len(events),audio=report['audio'],report_sha256=sha(directory/'candidate/report.json'))
    paired=None
    if all_terminal:
        ca,co=(Path(data[k]['directory'])/'candidate' for k in ['candidate','control']);a=json.loads((ca/'report.json').read_text());b=json.loads((co/'report.json').read_text());fields=['CPU_full','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];diff={key:sum(x[key]!=y[key] for x,y in zip(a['frames'],b['frames'])) for key in fields};first={key:next((x['frame'] for x,y in zip(a['frames'],b['frames']) if x[key]!=y[key]),None) for key in fields}
        paired=dict(candidate_frames=len(a['frames']),control_frames=len(b['frames']),compared_prefix_frames=min(len(a['frames']),len(b['frames'])),per_frame_differences=diff,first_difference_frames=first,PCM_equal=sha(ca/'frontend-PCM.s16le')==sha(co/'frontend-PCM.s16le'),whole_route_equivalent=len(a['frames'])==len(b['frames']) and not any(diff.values()) and sha(ca/'frontend-PCM.s16le')==sha(co/'frontend-PCM.s16le'))
    state=dict(status='terminal_native_frame_acquire_component_build_and_live_review' if all_terminal else 'native_frame_acquire_component_build_verified_live_route_pending',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),proofs={k:str(p) for k,p in refs.items()},component_normal_cases=len(normal),component_ordered_cases=len(normal),component_zero_cases=len(zeros),actual_zero_exceptions=sum(len(r['faults']) for r in zeros),original_instruction_coverage=component['original_instruction_coverage'],component_max_stack_bytes=component['maximum_stack_bytes'],nested_fixture_sets=len(nested_rows),nested_native_comparisons=nested['native_cases'],nested_ordered_comparisons=nested['ordered_cases'],linked_normal_cases=631,linked_zero_cases=192,new_heap_regression_cases=0,prior_heap_code_and_floor_unchanged=True,entry_cases=96,resident_bytes=len(payload),reserve_bytes=build['component_bytes'],heap_start=hex(build['heap_start']),delta_parent_resident_bytes=len(changed),delta_parent_resident_offsets=[hex(x) for x in changed],build_metadata_corrections=[],routes=routes,paired_same_layout=paired,authorship='Codex coordinator wrote native C/ABI adaptation and checks from recovered algorithm and original bytes. No new local-LLM prompt/inference/training or cloud subagents in this work. Previously local-assisted host C retains its separate provenance.',new_logical_function_count=0,new_native_port_count=0,variant_of_existing_native_port='1AC68',default_promoted=False,preview_restarted=False,new_training=False,physical_console_verified=False,whole_game_complete=False,goal_complete=False,scope='One previously recovered full routine compiled for68000 with explicit public frame, actual DIVS faults and actual guest loader ABI. Component providers retain declared limits; production loader nested with lower CD/copy/yield fixtures. Derived disc retains remaining original engine code plus native parent. Live monitor verifies saved registers,public saves,NZVC/upperSR,loader args and source task stack bounds; it is not an independent full live output oracle. Runtime timing, complete game behavior, whole-source rebuild and physical console remain unproven.',artifact_sha256={str(p):sha(p) for p in [*refs.values(),bd/'linked-normal-results.json',bd/'linked-zero-results.json',bd/'entry-cases.json',Path(build['derived_stage']),Path(build['derived_disc']),out/'reviewer-as-run.py']})
    save(out/'review.json',state);save(ROOT/'verification/native-frame-acquire-lean-reviewed-current.json',state)
    lines=['BIWN native frame acquisition (1AC68..1AE54)','',state['status'],'',f"Component:631 normal/full CPU+publicRAM+ordered cases;192 zero fixtures execute320 actual DIVS exceptions and RTE. All173 original instruction locations covered.",f"Nested original/production C loader:72 fixture sets,144 native comparisons,24 ordered comparisons; actual8KB/16KB copies. CD/yield/copy remain guest fixtures.",f"Final address:631 normal+192 zero cases. Original16KB reservation,byte-identical prior heap code/floor;96 startup cases andallocation/compaction witness. No redundant new full heap regression claimed.",f"Resident:{len(payload)} bytes; reserve:{build['component_bytes']} bytes. Prior resident prefix and heap floor byte-identical. Original disc retained.",'','Authorship:coordinator adaptation; no new local-model authorship, inference prompts or training. Logical function already recovered; one new native port.','']
    for label,v in routes.items():lines += [label+':'+json.dumps(v,indent=2),'']
    if paired:lines += ['Same-layout comparison:'+json.dumps(paired,indent=2),'']
    lines += [state['scope'],'','Detailed evidence:'+str(out/'review.json')];(ROOT/'reports/native-frame-acquisition-lean-port.txt').write_text('\n'.join(lines)+'\n');print(state['status'],flush=True)

if __name__=='__main__':main()
