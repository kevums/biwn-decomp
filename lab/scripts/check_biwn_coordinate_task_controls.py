"""Remove DF22/DF3E/20E8C fixture helpers from linked readable game controls.

Original oracle executes real task-ring loops. All previous controls inputs
are rechecked with the captured18-task topology supplied as initial data.
This is logical component integration, not live scheduler/timing execution.
"""
import argparse
import copy
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import check_biwn_coordinate_controls as coordinate

base = coordinate.base
ROOT, RESTORE = coordinate.ROOT, coordinate.RESTORE
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): Path(path).write_text(json.dumps(value, indent=2) + '\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--flow',action='store_true');args=parser.parse_args()
    proof_name='coordinate-task-controls-flow' if args.flow else 'coordinate-task-controls'
    out = ROOT / 'verification' / proof_name / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True); print(out, flush=True)
    state = dict(status='preparing', pid=os.getpid(), directory=str(out), live_frame_runtime_changed=False)
    def mark():
        save(out / 'protocol.json', state); save(ROOT / 'verification' / (proof_name+'-active.json'), state)
    mark()
    try:
        gates_path = ROOT / 'verification/task-gates-current.json'; gates = json.loads(gates_path.read_text())
        repair_path = ROOT / 'verification/local-task-gates-repair-current.json'; repair = json.loads(repair_path.read_text())
        candidate = Path(repair['directory']) / 'candidate.c'
        assert sha(candidate) == gates['source_sha256'] and gates['original_cases'] == 69 and gates['native_cases'] == 65
        assert sha(gates['source']) == gates['source_sha256']
        assert sha(gates['header']) == gates['header_sha256']
        # Publish exactly the generated, guided repair; do not silently edit it.
        source = RESTORE / 'biwn_task_gates.c'; shutil.copy2(candidate, source)
        prior_path = ROOT / 'verification/coordinate-controls-current.json'; prior = json.loads(prior_path.read_text())
        for key in ['source', 'header', 'library']: assert sha(prior[key]) == prior[key + '_sha256']
        for path, digest in prior['sources_sha256'].items(): assert sha(path) == digest, path
        fixtures_path = Path(prior['directory']) / 'fixtures.json'
        vectors = json.loads(fixtures_path.read_text())
        assert len(vectors) == prior['cases'] == 2082
        # Copy only source task-link/counter data into the existing controls
        # fixtures; the rest of each fixture and its input schedule is retained.
        captured = gates['captured_game_task_rings'][2]; assert sha(captured['path']) == captured['sha256']
        captured_RAM = Path(captured['path']).read_bytes()
        rd = lambda address: int.from_bytes(captured_RAM[address:address + 4], 'big')
        start = node = rd(0xc0920); topology = []
        while node not in [x['address'] for x in topology]:
            topology.append(dict(address=node, next=rd(node), counter=rd(node + 34))); node = rd(node)
        assert node == start and len(topology) == 18
        for case in vectors:
            case['initial'].append([0xc0920, 4, start])
            for row in topology: case['initial'] += [[row['address'], 4, row['next']], [row['address'] + 34, 4, row['counter']]]
            for i in range(25):
                room=0xb4000+i*0x20
                case['initial'] += [[0x49bb4+i*4,4,room],[room+6,2,0],[room+20,4,0xb5000+i*0x40]]
        # Mixed pause nesting includes wraparound. Pause followed by resume
        # is intentionally not an identity on a starting FFFFFFFF counter.
        confirm = next(row for row in vectors if row['kind'] == 'coordinate_confirm_123_456')
        for label, values in [('mixed',[0,1,2,0xffffffff,0x80000000]), ('nested',[1,2,3])]:
            case = copy.deepcopy(confirm); case['kind'] += '_task_gates_' + label
            for i, row in enumerate(topology): case['initial'].append([row['address'] + 34, 4, values[i % len(values)]])
            vectors.append(case)
        for label,room_counts in [('rooms',[0,1,3]),('duplicate_textures',[3,2,1])]:
            case=copy.deepcopy(confirm);case['kind'] += '_cleanup_' + label
            for i,count in enumerate(room_counts):
                case['initial'].append([0xb4000+i*0x20+6,2,count])
                for j in range(count):case['initial'].append([0xb5000+i*0x40+j*2,2,0x200+(j if label=='rooms' else 0)])
            for i,count in enumerate([0,1,2,0xffff,0x8000]):
                case['initial'] += [[0x15b4a0+i*4,2,0x200+i],[0x15b4a2+i*4,2,count]]
            vectors.append(case)
        library = out / 'libcoordinate-task-controls.dylib'
        wrapper = RESTORE / 'biwn_game_controls_coordinate_tasks.c'
        command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE),
                   str(wrapper), str(source), prior['library'], '-o', str(library)]
        exported='biwn_game_controls_coordinate_tasks_with_scratch'
        if args.flow:
            flow=json.loads((ROOT/'verification/coordinate-flow-current.json').read_text())
            for key in ['source','header','library']:assert sha(flow[key])==flow[key+'_sha256']
            controls_text=(RESTORE/'biwn_game_controls_coordinate.c').read_text()
            assert controls_text.count('biwn_coordinate_entry_with_result')==1
            controls_text=controls_text.replace('biwn_coordinate_entry_with_result','biwn_coordinate_flow_drive_for_check')
            controls_text=controls_text.replace('biwn_game_controls_coordinate_with_scratch','biwn_game_controls_coordinate_flow_with_scratch').replace('biwn_game_controls_coordinate(','biwn_game_controls_coordinate_flow(')
            controls_source=out/'flow_controls.c'
            controls_source.write_text('#include "biwn_coordinate_entry.h"\nextern int biwn_coordinate_flow_drive_for_check(struct biwn_world_bus*,biwn_coordinate_write8,uint32_t,uint32_t,uint32_t*);\n'+controls_text)
            text=wrapper.read_text().replace('biwn_game_controls_coordinate_with_scratch','biwn_game_controls_coordinate_flow_with_scratch').replace(exported,'biwn_game_controls_coordinate_tasks_flow_with_scratch')
            wrapper=out/'flow_task_controls.c'
            wrapper.write_text('#include "biwn_game_controls_coordinate_tasks.h"\nextern enum biwn_dispatch_status biwn_game_controls_coordinate_flow_with_scratch(struct biwn_world_bus*,biwn_input_write8,uint32_t,uint32_t,uint32_t,uint32_t*);\n'+text)
            exported='biwn_game_controls_coordinate_tasks_flow_with_scratch'
            library=out/'libcoordinate-task-controls-flow.dylib'
            command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(RESTORE),str(wrapper),str(controls_source),str(source),
                str(RESTORE/'biwn_coordinate_flow.c'),str(RESTORE/'biwn_coordinate_services.c'),str(ROOT/'scripts/biwn_coordinate_flow_check_driver.c')]+[str(RESTORE/name) for name in coordinate.NAMES]+['-o',str(library)]
        built = subprocess.run(command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
        (out / 'compiler.log').write_text(built.stdout + built.stderr); assert built.returncode == 0, built.stderr
        loaded=c.CDLL(str(library))
        function = getattr(loaded,exported)
        function.argtypes = [c.POINTER(base.world.Bus), base.dispatch.W8, c.c_uint32, c.c_uint32, c.c_uint32, c.POINTER(c.c_uint32)]
        function.restype = c.c_int
        def fn(bus, write8, budget, incoming, output):
            return function(bus, write8, base.DISPLAY_SCRATCH, budget, incoming, output)
        base.FALLBACK = [a for a in coordinate.LEGACY_FALLBACK if a not in [0x18e92, 0xdf22, 0xdf3e]]
        base.SOURCE = dict(base.SOURCE); base.SOURCE.update({0x18e92:0x190b8, 0x1b718:0x1b780, 0xdf22:0xdf3e, 0xdf3e:0xdf60,0x20e8c:0x20f0c,0x20cc4:0x20cf8})
        base.EXTRA_SERVICES[0x20e8c] = []; base.WIDTHS[0x20e8c] = []
        base.Script = coordinate.ConnectedScript
        snapshot = (ROOT / 'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
        coverage, entries, rows, native_vectors, exclusions = set(), {}, [], [], []
        state.update(status='checking_original_and_linked_C', compiler=command); mark()
        for index, case in enumerate(vectors):
            original, rebuilt = coordinate.ConnectedScript(snapshot, case), coordinate.ConnectedScript(snapshot, case)
            expected, steps = base.original(original, case, coverage, entries)
            status, actual = base.dispatch.translated(fn, rebuilt, case, budget=1024)
            public_RAM = rebuilt.memory[:base.SP-0x1000] == original.memory[:base.SP-0x1000] and rebuilt.memory[base.SP+8:] == original.memory[base.SP+8:]
            if status or actual != expected or rebuilt.errors or rebuilt.trace != original.trace or not public_RAM or rebuilt.MMIO != original.MMIO:
                save(out / 'mismatch.json', dict(index=index, kind=case['kind'], status=status, errors=rebuilt.errors,
                    original_D0=expected, C_D0=actual, original_trace=original.trace, C_trace=rebuilt.trace,
                    RAM_differences=[hex(i) for i,(a,b) in enumerate(zip(original.memory,rebuilt.memory)) if a!=b][:32]))
                raise AssertionError(out / 'mismatch.json')
            assert not any(event[0]=='call' and event[1] in [0xdf22,0xdf3e,0x20e8c] for event in rebuilt.trace)
            rows.append(dict(index=index, kind=case['kind'], D0=actual, original_steps=steps,
                trace_sha256=hashlib.sha256(json.dumps(rebuilt.trace).encode()).hexdigest(), all_public_RAM_and_MMIO=True))
            if case.get('coordinate_connected'):
                unsupported = [q for q in case.get('read_queues',[]) if (q['address'],q['width']) != (0x778cc,4)]
                if unsupported: exclusions.append(dict(kind=case['kind'], reason='Arbitrary queued inventory RAM reads not supported by existing native adapter; original/C full logical trace passes.'))
                else: native_vectors.append((case, expected, original.memory))
            if index % 200 == 0:
                state['checked_cases'] = index + 1; mark(); print('original/C', index + 1, flush=True)
        native_rows = []
        oracle = base.media.scheduler.Native(diagnostic_core=Path(gates['core']))
        runtime = base.media.Runtime.__new__(base.media.Runtime); runtime.oracle,runtime.device,runtime.core = oracle,oracle.device,oracle.lib
        try:
            for case, expected, memory in native_vectors:
                state.update(status='checking_native_and_blitter', native_case=case['kind']); mark()
                native_rows.append(base.native_check(runtime,fn,snapshot,case,expected,memory,out))
                print('native',case['kind'],flush=True)
        finally: oracle.close()
        # New nested bus errors are routed through coordinate/dispatch layers.
        case = next(x for x in vectors if x['kind']=='coordinate_confirm_123_456')
        baseline = coordinate.ConnectedScript(snapshot,case)
        assert base.dispatch.translated(fn,baseline,case,budget=1024)[0]==0
        peer = topology[1]['address']; guards=[]
        for kind,address,width in [('r',0xc0920,4),('r',start,4),('r',peer+34,4),('w',peer+34,4),('r',0x49bb4,4),('r',0xb4006,2),('w',0x49d6e,2)]:
            index=next(i for i,x in enumerate(baseline.trace) if x[:3]==[kind,address,width])
            failed=coordinate.ConnectedScript(snapshot,case)
            if kind=='r': failed.fail_read=(address,width)
            else: failed.fail_write=(address,width)
            status,result=base.dispatch.translated(fn,failed,case,budget=1024)
            assert status==3 and result==0xa5a55a5a and failed.trace==baseline.trace[:index]
            prefix=coordinate.ConnectedScript(snapshot,case)
            for event in baseline.trace[:index]:
                if event[0]=='r': assert prefix.read(event[1],event[2])==event[3]
                elif event[0]=='w': prefix.write(*event[1:])
                else: prefix.call(event[1],event[2])
            assert failed.memory==prefix.memory and failed.MMIO==prefix.MMIO
            guards.append(dict(failure=[kind,address,width], original_error_inferred=False, output_unchanged=True, prior_effects_retained=True))
        gate_locations=sorted(x for x in coverage if 0xdf22<=x<0xdf60)
        assert len(gate_locations)==20
        save(out/'case-results.json',rows); save(out/'native-cases.json',native_rows); save(out/'guards.json',guards)
        save(out/'fixtures.json',vectors); save(out/'task-topology.json',topology)
        for name in ['biwn_game_controls_coordinate_tasks.c','biwn_game_controls_coordinate_tasks.h','biwn_task_gates.c','biwn_task_gates.h']:
            shutil.copy2(RESTORE/name,out/name)
        report=dict(status='coordinate_controls_task_gates_and_room_cleanup_original_and_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),
            directory=str(out),cases=len(rows),previous_controls_inputs=len(vectors)-4,native_cases=len(native_rows),
            native_actual_blitter_commands=sum(x['actual_blitter_commands'] for x in native_rows),native_scope_exclusions=exclusions,
            nested_error_guards=len(guards),task_gate_instruction_locations=[len(gate_locations),20],
            task_gate_entries={hex(x):entries.get(x,0) for x in [0xdf22,0xdf3e]},
            room_cleanup_entries={hex(x):entries.get(x,0) for x in [0x20e8c,0x20cc4,0x1ae56]},
            room_cleanup_instruction_locations=len([x for x in coverage if 0x20e8c<=x<0x20f0c]),
            source_panel_text_and_raw_poll_linked=True,
            task_nodes=18,task_topology_source=captured,source_authorship='Guided local27B task-gate C accepted byte-for-byte after original/native checks; coordinator typed ABI prompt, adapter and verification.',
            initial_raw_model_source_accepted=False,coordinator_edited_generated_repair=False,
            generation_proof=str(repair_path),generation_proof_sha256=sha(repair_path),gate_proof=str(gates_path),gate_proof_sha256=sha(gates_path),
            prior_controls_proof=str(prior_path),prior_controls_proof_sha256=sha(prior_path),prior_controls_library=prior['library'],
            prior_controls_library_sha256=prior['library_sha256'],prior_fixtures_sha256=sha(fixtures_path),
            source=str(out/'biwn_game_controls_coordinate_tasks.c'),source_sha256=sha(wrapper),
            library=str(library),library_sha256=sha(library),compiler=command,
            sources_sha256={str(RESTORE/name):sha(RESTORE/name) for name in ['biwn_game_controls_coordinate_tasks.c','biwn_game_controls_coordinate_tasks.h','biwn_task_gates.c','biwn_task_gates.h']},
            coordinate_remaining_fixture_helpers=['0xdf60','0x20f78'],
            linked_readable_components=['input/item dispatch','coordinate entry','digit decoding','panel refresh','text drawing','raw controller polling','task pause traversal','task resume traversal','room texture release and object/actor cleanup'],
            full_D0=True,ordered_bus_and_public_RAM=True,clock_and_raw_controller_rows_supplied=True,
            live_frame_runtime_changed=False,high_level_coordinate_API_installed_in_live_frames=False,new_training=False,whole_game_complete=False,
            scope='All2082previous controls inputs rechecked with supplied captured18-task topology and25room records, actual original/C pause/resume loops and room/texture/object/actor/allocator cleanup, plus two mixed/nested-counter and two nonempty-room coordinate accepts. Three former fixture services are computed. Context switchDF60 and scene setup20F78 remain supplied services. Room topology/texture references and current task topology are initial fixture data, not live capture replay. Native CPU/blitter checks retain raw device/clock injection and private stack/caller-saved/CCR exclusions; one queued inventory fixture remains native-excluded. Not natural live-frame installation or a timing/scheduler/whole-game proof.')
        if args.flow:
            counter=loaded.biwn_coordinate_flow_check_stat;counter.argtypes=[c.c_uint32];counter.restype=c.c_uint64
            stats=dict(zip(['started','requests','external_requests','completed'],[int(counter(i)) for i in range(4)]))
            save(out/'flow-driver-statistics.json',stats)
            # Each deliberate callback failure starts a flow without
            # completing it. The baseline and all comparison cases complete.
            assert stats['started']==stats['completed']+len(guards) and stats['completed']>=37 and stats['external_requests']>0,stats
            extra=['biwn_coordinate_flow.c','biwn_coordinate_flow.h','biwn_coordinate_services.c','biwn_coordinate_services.h']
            report['sources_sha256'].update({str(RESTORE/name):sha(RESTORE/name) for name in extra+coordinate.NAMES})
            for name in extra:shutil.copy2(RESTORE/name,out/name)
            shutil.copy2(ROOT/'scripts/biwn_coordinate_flow_check_driver.c',out/'biwn_coordinate_flow_check_driver.c')
            report.update(status='resumable_coordinate_flow_linked_controls_original_and_native_match',
                source=str(wrapper),source_sha256=sha(wrapper),
                flow_proof=str(ROOT/'verification/coordinate-flow-current.json'),flow_proof_sha256=sha(ROOT/'verification/coordinate-flow-current.json'),
                flow_driver_statistics=stats,verification_driver_is_synchronous=True,flow_engine_callback_free=True,
                helper_services_synchronous_but_bounded=True,actual_Jaguar_context_switch=False,
                code_authorship='Coordinator continuation engine/service adapter/check driver; previously guided local task-gate bodies reused unchanged.',
                scope=report['scope']+' Coordinate calls now pass through the new request/completion engine and real readable service adapter, with explicit test-driver counters. The compatibility test driver deliberately services requests synchronously to reuse the old full-controls comparison; this does not demonstrate async Jaguar context switching. Separate147case flow proof checks request delays/copies/interleaving. Helpers themselves are synchronous bounded C bodies; DF60/20F78 remain external requests.')
        shutil.copy2(__file__,out/Path(__file__).name)
        save(out/'report.json',report); save(ROOT/'verification'/(proof_name+'-current.json'),report)
        state.update(status='terminal_match',proof=str(out/'report.json')); mark()
        print(json.dumps(dict(status=report['status'],cases=len(rows),native=len(native_rows))),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error)); mark(); raise

if __name__=='__main__': main()
