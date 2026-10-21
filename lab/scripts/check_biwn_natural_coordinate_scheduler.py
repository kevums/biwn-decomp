"""Read-only snapshots of the real coordinate caller's task-switch interval.

Replay the established source checkpoint/input sequence without substituting
the high-level scheduler. Then compare its C scheduler on private captured
RAM/CPU copies. IRQ-bearing spans are explicitly excluded from that claim.
"""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import check_biwn_scheduler as scheduler

ROOT = Path(__file__).resolve().parents[1]
DTYPE = np.dtype({'names': ['registers', 'pc', 'usp', 'ssp', 'sr'],
                 'formats': [('>u4', 16), '>u4', '>u4', '>u4', '>u2'],
                 'offsets': [0, 64, 68, 72, 76], 'itemsize': 78})


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def cpu_record(row):
    return dict(registers=[int(x) for x in row['registers']], entry=int(row['pc']),
                usp=int(row['usp']), ssp=int(row['ssp']), sr=int(row['sr']))


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = ROOT / 'verification/natural-coordinate-scheduler' / stamp
    captures = out / 'captures'
    captures.mkdir(parents=True)
    baseline = ROOT / 'runs/natural-coordinate-confirm-20261017T142910.851410Z'
    natural = ROOT / 'verification/natural-coordinate-gameplay-current.json'
    prior = json.loads(natural.read_text())
    confirm = next(row for row in prior['cases'] if row['case'] == 'confirm')
    assert sha(confirm['source_trace']) == confirm['source_trace_sha256']
    trace = np.memmap(confirm['source_trace'], mode='r', dtype=DTYPE)
    first = int(np.flatnonzero(trace['pc'] == 0x18fa4)[0]) + 1
    last = first + int(np.flatnonzero(trace['pc'][first:] == 0x18faa)[0])
    assert int(trace[first]['pc']) == 0xdf60
    plans = []
    for index in np.flatnonzero(trace['pc'][first:last] == 0xdf60) + first:
        index = int(index)
        rte = index + int(np.flatnonzero(trace['pc'][index:last] == 0xde5a)[0])
        end = rte + 1
        if int(trace[end]['pc']) in (0xdf66, 0xdf96):
            end += 2  # Original MOVEM/RTS; stop at the selected caller.
        pcs = trace['pc'][index:end]
        safe = (((pcs >= 0xde08) & (pcs < 0xde5c)) |
                ((pcs >= 0xdf60) & (pcs < 0xdf6c)) |
                ((pcs >= 0xdf96) & (pcs < 0xdf9c)))
        plans.append(dict(kind='yield', first=index, last=end,
                          asynchronous_PC=[hex(int(x)) for x in np.unique(pcs[~safe])]))
    # The task at DDEA executes TRAP0 directly, rather than the DF60 wrapper.
    for index in np.flatnonzero(trace['pc'][first:last] == 0xde08) + first:
        index = int(index)
        if int(trace[index - 1]['pc']) == 0xdf64:
            continue
        end = index + int(np.flatnonzero(trace['pc'][index:last] == 0xde5a)[0]) + 1
        pcs = trace['pc'][index:end]
        safe = (pcs >= 0xde08) & (pcs < 0xde5c)
        plans.append(dict(kind='dispatch', first=index, last=end,
                          asynchronous_PC=[hex(int(x)) for x in np.unique(pcs[~safe])]))
    plans.sort(key=lambda row: row['first'])
    indices = sorted({index for row in plans for index in (row['first'], row['last'])})
    assert indices == [index for row in plans for index in (row['first'], row['last'])]
    save(out / 'capture-plan.json', dict(first=first, last=last, transitions=plans, indices=indices))
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    base = json.loads(Path(runtime['native_CPU_candidate']).read_text())
    source_path = Path(base['directory']) / 'fast_CPU_bridge.c'
    assert sha(source_path) == base['source_sha256']
    observer = r'''
static const uint64_t capture_indices[] = { CAPTURE_INDICES };
static unsigned capture_next;
static uint64_t capture_trace_head;
static int capture_events(const char *directory,uint64_t index)
{
    char path[4096];uint64_t i,end=vjtrace_ring_head();vjtrace_ev event;
    FILE *f;int length,failed=0;
    if(end<capture_trace_head||end-capture_trace_head>100000)return 1;
    length=snprintf(path,sizeof(path),"%s/%llu-events.txt",directory,(unsigned long long)index);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"w");if(!f)return 1;
    for(i=capture_trace_head;i<end;i++){
        if(!vjtrace_ring_read(i,&event)){failed=1;break;}
        if(fprintf(f,"%llu %u %u %u %u %u %u %u\n",(unsigned long long)event.seq,
             event.frame,(unsigned)event.halfline,(unsigned)event.type,(unsigned)event.who,
             event.pc,event.addr,event.value)<0){failed=1;break;}
    }
    if(fclose(f))failed=1;return failed;
}
static int capture_scheduler(const struct biwn_task_cpu *s)
{
    const char *directory=getenv("BIWN_SCHEDULER_CAPTURE_DIR");
    uint64_t index=S.calls-1;uint8_t cpu[78];char path[4096];FILE *f;
    unsigned i;int length,failed;
    if(capture_next>=sizeof(capture_indices)/sizeof(capture_indices[0]))return 0;
    if(index<capture_indices[capture_next])return 0;
    if(index!=capture_indices[capture_next]||!directory)return 1;
    if(capture_next%2){
        if(capture_events(directory,index))return 1;
        vjtrace_disarm();vjtrace_watch_clear();
    }else{
        if(vjtrace_armed||vjtrace_nwatch)return 1;
        vjtrace_init();capture_trace_head=vjtrace_ring_head();
        if(vjtrace_watch_add(0,0x1fffffu,2)<0)return 1;
        vjtrace_arm();
    }
    for(i=0;i<16;i++)put32(cpu+i*4,s->registers[i]);
    put32(cpu+64,s->pc);put32(cpu+68,s->usp);put32(cpu+72,s->ssp);
    cpu[76]=(uint8_t)(s->sr>>8);cpu[77]=(uint8_t)s->sr;
    length=snprintf(path,sizeof(path),"%s/%llu.cpu",directory,(unsigned long long)index);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"wb");if(!f)return 1;
    failed=fwrite(cpu,1,sizeof(cpu),f)!=sizeof(cpu);if(fclose(f))failed=1;if(failed)return 1;
    length=snprintf(path,sizeof(path),"%s/%llu.ram",directory,(unsigned long long)index);
    if(length<0||(size_t)length>=sizeof(path))return 1;
    f=fopen(path,"wb");if(!f)return 1;
    failed=fwrite(H.RAM,1,0x200000,f)!=0x200000;if(fclose(f))failed=1;
    if(failed)return 1;capture_next++;return 0;
}
'''.replace('CAPTURE_INDICES', ','.join(str(i) + 'ull' for i in indices))
    text = source_path.read_text()
    marker = 'int32_t biwn_fast_CPU_owner(uint32_t PC)'
    assert text.count(marker) == 1
    text = text.replace(marker, observer + '\n' + marker)
    marker = 'if(s.pc!=PC)return fail(PC,91);if(state_file)'
    assert text.count(marker) == 1
    text = text.replace(marker, 'if(s.pc!=PC)return fail(PC,91);if(capture_scheduler(&s))return fail(PC,177);if(state_file)')
    bridge_source = out / 'capture_bridge.c'
    core = Path(runtime['core'])
    assert sha(core) == runtime['core_sha256']
    trace_header = core.parent / 'src/core/vjtrace.h'
    bridge_source.write_text('#include <stdlib.h>\n#define VJ_TRACE 1\n#include "' + str(trace_header) + '"\n' + text)
    shutil.copytree(source_path.parent / 'pinned-CPU-headers', out / 'pinned-CPU-headers')
    library = out / 'libcapture-bridge.dylib'
    command = runtime['commands'][1][:]
    command[command.index(str(source_path))] = str(bridge_source)
    command[-1] = str(library)
    command.insert(command.index('-o'), str(core))
    env = {**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'}
    compiled = subprocess.run(command, capture_output=True, text=True, env=env)
    (out / 'compiler.log').write_text(compiled.stdout + compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr
    candidate = out / 'capture-candidate.json'
    save(candidate, dict(base, directory=str(out), library=str(library), source_sha256=sha(bridge_source),
                         status='read_only_scheduler_observer_unverified'))
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), baseline=str(baseline),
                 prior_proof=str(natural), prior_proof_sha256=sha(natural), compile_command=command,
                 observer_source_sha256=sha(bridge_source), observer_library_sha256=sha(library),
                 OP_source_sha256=sha(core.parent / 'src/tom/op.c'), trace_header_sha256=sha(trace_header),
                 whole_game_complete=False, high_level_scheduler_in_live_frames=False,
                 previous_turn_classification='no_progress: preview control lookup only; no goal artifacts changed')

    def checkpoint():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/natural-coordinate-scheduler-active.json', state)

    checkpoint()
    try:
        protocol = json.loads((baseline / 'protocol.json').read_text())
        run = next(row['command'][:] for row in protocol['commands'] if row['phase'] == 'C')
        run[run.index('--native-CPU-candidate') + 1] = str(candidate)
        run[run.index('--output') + 1] = str(out / 'observed')
        with (out / 'runtime.log').open('w') as log:
            child = subprocess.Popen(run, stdout=log, stderr=subprocess.STDOUT,
                                     env={**env, 'BIWN_SCHEDULER_CAPTURE_DIR': str(captures)})
            state.update(status='capturing', command=run, child_pid=child.pid)
            checkpoint()
            print('capturing', child.pid, out, flush=True)
            code = child.wait()
        state['exit_code'] = code
        assert code == 0, out / 'runtime.log'
        names = ['CPU-before-instructions.bin', 'retired-instruction-costs.bin', 'warm-RAM.bin',
                 'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']
        unchanged = {name: sha(out / 'observed' / name) == sha(baseline / 'C' / name) for name in names}
        assert all(unchanged.values()), unchanged
        assert len(list(captures.glob('*.cpu'))) == len(indices)
        for index in indices:
            assert (captures / f'{index}.cpu').read_bytes() == trace[index].tobytes()
        source = ROOT / 'projects/black-ice-white-noise/restoration/biwn_scheduler.c'
        translated_lib = out / 'libscheduler.dylib'
        compile_scheduler = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
                             str(source), '-o', str(translated_lib)]
        compiled = subprocess.run(compile_scheduler, capture_output=True, text=True, env=env)
        (out / 'scheduler-compiler.log').write_text(compiled.stdout + compiled.stderr)
        assert compiled.returncode == 0, compiled.stderr
        functions = scheduler.bind(c.CDLL(str(translated_lib)))
        rows = []
        for plan in plans:
            begin, end = plan['first'], plan['last']
            before = (captures / f'{begin}.ram').read_bytes()
            after = (captures / f'{end}.ram').read_bytes()
            row = dict(plan, owner_before=int.from_bytes(before[0xc0920:0xc0924], 'big'),
                       owner_after=int.from_bytes(after[0xc0920:0xc0924], 'big'),
                       original_CPU_instructions=end-begin,
                       entry_CPU=cpu_record(trace[begin]), return_CPU=cpu_record(trace[end]))
            if plan['asynchronous_PC']:
                row['status'] = 'excluded_interrupt_execution_not_modeled'
            else:
                case = dict(cpu_record(trace[begin]), initial=[], default_helper_return=0)
                memory = scheduler.cleanup.Script(before, case)
                result, actual = scheduler.translated(functions, memory, case, limit=1024)
                expected = scheduler.make_cpu(cpu_record(trace[end]))
                # Apply only native-attributed OP writes, independently
                # validated against the pinned bitmap writeback formula.
                # Never infer ownership from the addresses that differ.
                merged = bytearray(memory.memory)
                events = [list(map(int, line.split())) for line in (captures / f'{end}-events.txt').read_text().splitlines()]
                current_object, pending_long, op_writes = None, None, []
                for event in events:
                    assert len(event) == 8
                    sequence, frame, halfline, kind, who, pc, address, value = event
                    if kind == 6:
                        current_object = (address, value)
                    if kind != 12 or who != 8:
                        continue
                    assert current_object is not None and current_object[1] == 0
                    base_address = current_object[0]
                    assert base_address % 8 == 0 and base_address + 16 <= len(merged)
                    if address == base_address:
                        assert pending_long is None
                        pending_long = (address, value)
                        continue
                    assert address == base_address + 4 and pending_long is not None
                    assert pending_long[0] == base_address
                    p0 = int.from_bytes(merged[base_address:base_address + 8], 'big')
                    p1 = int.from_bytes(merged[base_address + 8:base_address + 16], 'big')
                    height = (p0 & 0xffc000) >> 14
                    assert p0 & 7 == 0 and height > 0
                    data = ((p0 & 0xfffff80000000000) >> 40) + ((p1 & 0xffc0000) >> 15)
                    predicted = ((p0 & ~0xfffff80000ffc000) | ((height - 1) << 14) | (data << 40)) & 0xffffffffffffffff
                    value64 = (pending_long[1] << 32) | value
                    assert predicted == value64
                    assert not any(event[0] in ('r', 'w') and event[1] < base_address + 8 and event[1] + event[2] > base_address for event in memory.trace)
                    merged[base_address:base_address + 8] = value64.to_bytes(8, 'big')
                    op_writes.append(dict(address=base_address, before=p0, after=value64, writer='OP', source_formula_verified=True))
                    pending_long = None
                assert pending_long is None
                matches = dict(status=result == 0, full_CPU=scheduler.cpu_dict(actual) == scheduler.cpu_dict(expected),
                               full_RAM_with_supplied_OP=bytes(merged) == after, no_bus_errors=not memory.errors)
                row.update(matches=matches, logical_bus_trace=memory.trace,
                           full_RAM_without_OP_matches=bytes(memory.memory) == after,
                           concurrent_OP_writebacks=op_writes, status='matched' if all(matches.values()) else 'mismatch')
                if not all(matches.values()):
                    row['actual_CPU'] = scheduler.cpu_dict(actual)
                    row['RAM_differences'] = [[i, after[i], merged[i]] for i in range(len(after)) if after[i] != merged[i]][:100]
            rows.append(row)
        save(out / 'transitions.json', rows)
        assert all(row['status'] in ('matched', 'excluded_interrupt_execution_not_modeled') for row in rows), out / 'transitions.json'
        matched = [row for row in rows if row['status'] == 'matched']
        state.update(status='terminal_captured_scheduler_matches', unchanged_source_run=unchanged,
                     transition_count=len(rows), matched_transitions=len(matched),
                     excluded_interrupt_transitions=len(rows)-len(matched),
                     supplied_OP_writebacks=sum(len(row.get('concurrent_OP_writebacks', [])) for row in rows),
                     real_contexts=sorted({row['owner_before'] for row in rows} | {row['owner_after'] for row in rows}),
                     scheduler_source=str(source), scheduler_source_sha256=sha(source),
                     scheduler_header_sha256=sha(source.with_suffix('.h')), compile_scheduler=compile_scheduler,
                     scheduler_library_sha256=sha(translated_lib),
                     coordinate_owner=rows[0]['owner_before'], coordinate_resumed_owner=rows[-1]['owner_after'],
                     coordinate_return_PC=hex(int(trace[last]['pc'])),
                     limitations=['Captured-context private replay only; new coordinate request engine not installed in frames.',
                                  'Interrupt-bearing switch is captured but excluded from scheduler equivalence.',
                                  'Concurrent native-traced, formula-checked OP writebacks supplied to private RAM replay.',
                                  'No clock/cycle/device scheduling or standalone Jaguar rebuild established.'])
        checkpoint()
        save(ROOT / 'verification/natural-coordinate-scheduler-current.json', state)
        print(json.dumps({key: state[key] for key in ['status', 'directory', 'matched_transitions', 'excluded_interrupt_transitions', 'real_contexts']}), flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        checkpoint()
        raise


if __name__ == '__main__':
    main()
