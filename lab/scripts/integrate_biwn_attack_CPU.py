"""Check a proposed CPU-compatible attack body, then use it in real frames.

This is an instruction-boundary compatibility implementation, distinct from
the higher-level biwn_attack_effect API. The proposed body owns all forty
attack PCs; helpers and all other game code retain their existing source
implementations. Native CPU fixtures and complete original gameplay traces
are the acceptance evidence, never a model review.
"""
import argparse
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import capstone
import check_biwn_media_setup_cpu as media

ROOT = Path(__file__).resolve().parents[1]
RESTORE = ROOT / 'projects/black-ice-white-noise/restoration'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def compile_source(command, log):
    result = subprocess.run(command, capture_output=True, text=True,
                            env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    log.write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr


def inspect_model_source(source, out):
    directives = re.findall(r'(?m)^\s*#([^\n]+)', source.read_text())
    for directive in directives:
        match = re.fullmatch(r'\s*include\s*[<"]([^>"\n]+)[>"]\s*', directive)
        assert match and match[1] in ['biwn_input_dispatch_cpu.h', 'stdint.h', 'stddef.h'], directive
    result = subprocess.run(['clang', '-std=c99', '-I', str(RESTORE), '-fsyntax-only',
                             '-Xclang', '-ast-dump=json', str(source)], capture_output=True, text=True)
    (out / 'syntax.log').write_text(result.stderr)
    assert result.returncode == 0, result.stderr
    tree = json.loads(result.stdout)
    definitions = [node for node in tree['inner'] if node['kind'] == 'FunctionDecl'
                   and any(child['kind'] == 'CompoundStmt' for child in node.get('inner', []))]
    names = {node['name'] for node in definitions}
    assert 'biwn_attack_CPU_step' in names
    assert all(node['name'] == 'biwn_attack_CPU_step' or node.get('storageClass') == 'static' for node in definitions)
    assert not any(node['kind'] in ['VarDecl', 'FileScopeAsmDecl'] for node in tree['inner'])

    def inspect(node):
        assert node['kind'] not in ['GCCAsmStmt', 'MSAsmStmt']
        assert node.get('castKind') not in ['IntegralToPointer', 'PointerToIntegral', 'BitCast']
        if node['kind'] in ['BinaryOperator', 'CompoundAssignOperator'] and node.get('opcode') in ['>>', '>>=']:
            left = node['inner'][0]
            left_type = left['type']
            unsigned = 'unsigned' in left_type.get('desugaredQualType', left_type['qualType'])
            # uint8/16 undergo integer promotion to int but remain nonnegative;
            # their right shifts are defined. Arbitrary signed operands are not.
            if not unsigned and left.get('castKind') == 'IntegralCast':
                inner_type = left['inner'][0]['type']
                source_type = inner_type.get('desugaredQualType', inner_type['qualType'])
                unsigned = source_type in ['unsigned short', 'unsigned char']
            assert unsigned, 'Potentially negative signed right shift violates portable C99 contract'
        if node['kind'] == 'CallExpr':
            target = node['inner'][0]
            while target['kind'] in ['ImplicitCastExpr', 'ParenExpr']:
                target = target['inner'][0]
            assert ((target['kind'] == 'MemberExpr' and target['name'] in ['read16', 'read32', 'write16', 'write32'])
                    or (target['kind'] == 'DeclRefExpr' and target['referencedDecl']['name'] in names)), target
        for child in node.get('inner', []):
            inspect(child)

    for definition in definitions:
        inspect(definition)
    save(out / 'source-inspection.json', dict(status='bounded_source_interface_inspected', functions=sorted(names),
        forbidden='No mutable global state, assembly, integer-pointer conversions or calls beyond own helpers and declared bus callbacks.'))


def native_fixtures(library, atlas, rows, out, cost_library):
    """Exercise every attack PC, CCR, active stack bank and edge operands."""
    oracle = media.scheduler.Native(diagnostic_core=Path(json.loads(
        (ROOT / 'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']))
    runtime = media.Runtime.__new__(media.Runtime)
    runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
    lib = c.CDLL(str(library))
    fn = lib.biwn_attack_CPU_step
    fn.argtypes = [c.POINTER(media.Bus), c.POINTER(media.CPU)]
    fn.restype = c.c_int
    cost_lib = c.CDLL(cost_library)
    cost = cost_lib.biwn_native_cycle_cost
    cost.argtypes = [c.c_uint16, c.POINTER(media.CPU), c.POINTER(c.c_uint8)]
    cost.restype = c.c_int
    world = media.scheduler.cleanup.world
    results = []
    try:
        for row in rows:
            pc = row['address']
            count, destinations = 0, set()
            for sr in list(range(32)) + list(range(0x2000, 0x2020)):
                for operand in [0, 1, 0x7fff, 0x8000, 0xffff, 0x80000000, 0x7fffffff, 0xffffffff]:
                    cpu = media.CPU()
                    cpu.registers[:] = [operand, 0xaaaa5555, 0x98765432, 7, 9, 11, 13, 15,
                                        0x72000, 0x70000, 0x71000, 0x73000, 0x74000, 0x75000, 0x76000, 0]
                    cpu.pc, cpu.usp, cpu.ssp, cpu.sr = pc, 0x180800, 0x1e0000, sr
                    cpu.registers[15] = cpu.ssp if sr & 0x2000 else cpu.usp
                    # Indexed reads must remain aligned in RAM for this fixture.
                    if pc == 0x18e58:
                        cpu.registers[0] = (operand & 0xfffe) if operand < 0x10000 else 0xfffffff0
                    cpu.registers[10] = operand
                    fixture = bytearray(atlas)
                    for address in [0x49d5e, 0x49d5c, 0x49d62, 0x49d66, 0x49d12, 0x49d60, 0x49d5a, 0x70000]:
                        fixture[address:address + 2] = (operand & 0xffff).to_bytes(2, 'big')
                    for address in [0x49c50, 0x49c56]:
                        fixture[address:address + 4] = operand.to_bytes(4, 'big')
                    sp = cpu.registers[15]
                    fixture[sp:sp + 4] = (0x18e92).to_bytes(4, 'big')
                    indexed = (cpu.registers[8] + cpu.registers[0]) & 0xffffffff
                    if pc == 0x18e58:
                        fixture[indexed:indexed + 2] = (operand & 0xffff).to_bytes(2, 'big')
                    runtime.device.seed(bytes(fixture), 0)
                    runtime.seed_cpu(cpu)
                    actual_cycles = runtime.core.m68k_execute(1)
                    expected_cpu, expected_ram = runtime.cpu(), runtime.device.ram()
                    cost_ram = (c.c_uint8 * len(fixture)).from_buffer(fixture)
                    predicted_cycles = cost(int(row['bytes'][:4], 16), c.byref(cpu), cost_ram)
                    if predicted_cycles != actual_cycles:
                        failure = dict(PC=hex(pc), sr=hex(sr), operand=hex(operand),
                                       predicted=predicted_cycles, native=actual_cycles,
                                       scope='Existing cycle-cost dependency mismatch; not a proposed CPU-state verdict.')
                        save(out / 'cycle-first-failure.json', failure)
                        raise AssertionError(failure)
                    memory, accesses = bytearray(fixture), []

                    def reader(width):
                        def read(_, address, result):
                            if address + width > len(memory):
                                return 1
                            accesses.append(['read', width, address])
                            result[0] = int.from_bytes(memory[address:address + width], 'big')
                            return 0
                        return read

                    def writer(width):
                        def write(_, address, value):
                            if address + width > len(memory):
                                return 1
                            accesses.append(['write', width, address, value])
                            memory[address:address + width] = value.to_bytes(width, 'big')
                            return 0
                        return write

                    callbacks = [world.R8(reader(1)), world.R16(reader(2)), world.R32(reader(4)),
                                 world.W16(writer(2)), world.W32(writer(4))]
                    bus = media.Bus(*callbacks, world.CALL(), None, 0)
                    translated = media.CPU.from_buffer_copy(bytes(cpu))
                    status = fn(c.byref(bus), c.byref(translated))
                    if status or media.scheduler.cpu_dict(translated) != media.scheduler.cpu_dict(expected_cpu) or memory != expected_ram:
                        failure = dict(PC=hex(pc), sr=hex(sr), operand=hex(operand), status=status,
                                       proposed=media.scheduler.cpu_dict(translated), expected=media.scheduler.cpu_dict(expected_cpu),
                                       RAM_matches=memory == expected_ram, accesses=accesses)
                        save(out / 'native-first-failure.json', failure)
                        raise AssertionError(failure)
                    destinations.add(translated.pc)
                    count += 1
            results.append(dict(PC=hex(pc), assembly=row['assembly'], cases=count,
                                destination_PCs=list(map(hex, sorted(destinations)))))
            print(hex(pc), count, 'native full CPU/RAM/cycle cases passed', flush=True)
    finally:
        oracle.close()
    save(out / 'native-fixtures.json', dict(status='all_attack_PCs_native_full_state_match',
        instructions=results, cases=sum(row['cases'] for row in results),
        scope='Every declared PC, all32CCR values, user/supervisor active stacks, eight declared operands. Full CPU/RAM and existing cost model versus pinned original M68000. Not a physical hardware claim.'))
    # These are explicit host-interface failure requirements, separate from
    # the original CPU comparisons above. Failing callbacks may already have
    # written RAM; the function must retain effects but not commit its CPU.
    guards = []
    for case in ['null_bus', 'null_cpu', 'missing_read16', 'missing_read32', 'missing_write16', 'missing_write32',
                 'bad_PC', 'read16_failure', 'read32_failure', 'write16_failure', 'write32_failure']:
        memory, effects = bytearray(atlas), []

        def read16(_, address, result):
            effects.append(['read16', address])
            if case == 'read16_failure':
                return 1
            result[0] = int.from_bytes(memory[address:address + 2], 'big')
            return 0

        def read32(_, address, result):
            effects.append(['read32', address])
            if case == 'read32_failure':
                return 1
            result[0] = int.from_bytes(memory[address:address + 4], 'big')
            return 0

        def writer(width):
            def write(_, address, value):
                effects.append(['write', width, address, value])
                memory[address:address + width] = value.to_bytes(width, 'big')
                return int(case == 'write' + str(width * 8) + '_failure')
            return write

        callbacks = [world.R8(), world.R16(read16), world.R32(read32), world.W16(writer(2)), world.W32(writer(4))]
        missing = {'missing_read16': 1, 'missing_read32': 2, 'missing_write16': 3, 'missing_write32': 4}
        if case in missing:
            callbacks[missing[case]] = type(callbacks[missing[case]])()
        bus = media.Bus(*callbacks, world.CALL(), None, 0)
        cpu = media.CPU()
        cpu.pc = {'bad_PC': 0, 'read16_failure': 0x18df4, 'read32_failure': 0x18e66,
                  'write16_failure': 0x18e20}.get(case, 0x18df2)
        cpu.registers[10], cpu.registers[15], cpu.usp, cpu.ssp = 0x12345678, 0x180800, 0x180800, 0x1e0000
        before = media.scheduler.cpu_dict(cpu)
        code = fn(None if case == 'null_bus' else c.byref(bus), None if case == 'null_cpu' else c.byref(cpu))
        expected = 7 if case == 'bad_PC' else 2 if case.endswith('_failure') else 1
        assert code == expected and media.scheduler.cpu_dict(cpu) == before, (case, code)
        if expected in [1, 7]:
            assert not effects and memory == atlas, (case, effects)
        if case in ['write16_failure', 'write32_failure']:
            assert memory != atlas and len(effects) == 1, (case, effects)
        guards.append(dict(case=case, status=code, CPU_unchanged=True, callbacks=effects))
    save(out / 'host-contract-guards.json', dict(status='declared_host_error_effects_match', cases=guards))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    out = ROOT / 'verification/live-attack-CPU' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = out / 'biwn_attack_cpu.c'
    shutil.copy2(args.source, source)
    original = json.loads((ROOT / 'verification/main-static-CPU-experimental-candidate.json').read_text())
    bridge = json.loads((ROOT / 'verification/main-static-native-CPU-experimental-candidate.json').read_text())
    atlas = Path(original['instruction_RAM_source']).read_bytes()
    cs = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    rows = [dict(address=i.address, size=i.size, bytes=i.bytes.hex(), assembly=i.mnemonic + ' ' + i.op_str)
            for i in cs.disasm(atlas[0x18df2:0x18e92], 0x18df2)]
    assert len(rows) == 40 and rows[-1]['address'] == 0x18e90
    state = dict(status='compiling', directory=str(out), pid=os.getpid(), source=str(source), source_sha256=sha(source),
                 commands=[], goal_complete=False, compatibility_stage=True, high_level_attack_effect_API_used=False)

    def checkpoint():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/live-attack-CPU-active.json', state)

    checkpoint()
    try:
        inspect_model_source(source, out)
        standalone = out / 'libattack-CPU.dylib'
        cmd = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE), str(source), '-o', str(standalone)]
        state['commands'].append(cmd)
        compile_source(cmd, out / 'compiler.log')
        state['status'] = 'checking_native_fixtures'
        checkpoint()
        native_fixtures(standalone, atlas, rows, out, bridge['cost_library'])
        addresses = ','.join(str(row['address']) for row in rows)
        wrapper = out / 'attack_dispatch.c'
        wrapper.write_text('''#include <stdio.h>
#include "biwn_input_dispatch_cpu.h"
extern int biwn_attack_CPU_step(struct biwn_world_bus*,struct biwn_task_cpu*);
extern int biwn_main_static_CPU_step(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);
static const uint32_t pcs[]={''' + addresses + '''};
static uint64_t hits[40];
int biwn_live_attack_CPU_step(struct biwn_world_bus*b,struct biwn_task_cpu*s,biwn_input_write8 w,biwn_world_cpu_service f,void*x){
 unsigned i;int status;if(s->pc>=0x18df2u&&s->pc<0x18e92u){
  for(i=0;i<40;i++)if(pcs[i]==s->pc){status=biwn_attack_CPU_step(b,s);if(!status)hits[i]++;return status;}
  return 7;
 }return biwn_main_static_CPU_step(b,s,w,f,x);
}
int biwn_attack_stats_write(const char*path){unsigned i;FILE*f;if(!path)return 1;f=fopen(path,"w");if(!f)return 1;
 for(i=0;i<40;i++)if(fprintf(f,"%u %llu\\n",pcs[i],(unsigned long long)hits[i])<0){fclose(f);return 1;}
 return fclose(f)!=0;}
''')
        library = out / 'liblive-attack-CPU.dylib'
        cmd = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE),
               str(source), str(wrapper), original['library'], '-o', str(library)]
        state['commands'].append(cmd)
        compile_source(cmd, out / 'dispatcher-compiler.log')
        candidate = out / 'CPU-candidate.json'
        save(candidate, dict(original, directory=str(out), library=str(library), function='biwn_live_attack_CPU_step',
                             source_sha256=sha(source), local_attack_PC_override=True))
        old_source = Path(bridge['directory']) / 'fast_CPU_bridge.c'
        assert sha(old_source) == bridge['source_sha256']
        new_bridge = '#include <stdlib.h>\nextern int biwn_attack_stats_write(const char*);\n' + old_source.read_text()
        new_bridge = new_bridge.replace('biwn_main_static_CPU_step', 'biwn_live_attack_CPU_step')
        needle = 'const struct stats*biwn_fast_CPU_end(void){'
        assert new_bridge.count(needle) == 1
        new_bridge = new_bridge.replace(needle, needle + 'const char*p=getenv("BIWN_LIVE_ATTACK_COUNTERS");if(p&&biwn_attack_stats_write(p))fail(0,178);')
        bridge_source = out / 'fast_CPU_bridge.c'
        bridge_source.write_text(new_bridge)
        shutil.copytree(Path(bridge['directory']) / 'pinned-CPU-headers', out / 'pinned-CPU-headers')
        bridge_lib = out / 'liblive-attack-bridge.dylib'
        cmd = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE),
               str(bridge_source), str(library), bridge['cost_library'], '-o', str(bridge_lib)]
        state['commands'].append(cmd)
        compile_source(cmd, out / 'bridge-compiler.log')
        bridge_candidate = out / 'native-CPU-candidate.json'
        save(bridge_candidate, dict(bridge, directory=str(out), library=str(bridge_lib), CPU_library=str(library),
                                    source_sha256=sha(bridge_source), local_attack_PC_override=True))
        gameplay = json.loads((ROOT / 'verification/ordinary-gameplay-damage-current.json').read_text())
        cases = []
        for case in gameplay['cases']:
            baseline = Path(case['comparison']).parent
            protocol = json.loads((baseline / 'protocol.json').read_text())
            command = next(row['command'][:] for row in protocol['commands'] if row['phase'] == 'C')
            folder = out / case['name']
            folder.mkdir()
            command[command.index('--CPU-candidate') + 1] = str(candidate)
            command[command.index('--native-CPU-candidate') + 1] = str(bridge_candidate)
            command[command.index('--output') + 1] = str(folder / 'C')
            counters = folder / 'attack-owner-counts.txt'
            state['commands'].append(command)
            with (folder / 'runtime.log').open('w') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                         env={**os.environ, 'BIWN_LIVE_ATTACK_COUNTERS': str(counters)})
                state.update(status='live_frames_' + case['name'], child_pid=child.pid)
                checkpoint()
                print(case['name'], 'PID', child.pid, flush=True)
                code = child.wait()
            assert code == 0, (case['name'], folder / 'runtime.log')
            compare = next(row['command'][:] for row in protocol['commands'] if row['phase'] == 'compare')
            compare[compare.index('--C-run') + 1] = str(folder / 'C')
            compare[compare.index('--output') + 1] = str(folder / 'comparison.json')
            with (folder / 'comparison.log').open('w') as log:
                subprocess.run(compare, stdout=log, stderr=subprocess.STDOUT)
            comparison = json.loads((folder / 'comparison.json').read_text())
            failed = [name for name, passed in comparison['checks'].items() if not passed]
            assert failed == ['DSP_owned_positive'], failed
            assert comparison['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
            counts = {int(pc): int(count) for pc, count in (line.split() for line in counters.read_text().splitlines())}
            assert set(counts) == {row['address'] for row in rows}
            assert counts[0x18df2] > 0 and counts[0x18e5c] == 1
            cases.append(dict(name=case['name'], frames=comparison['frames'], CPU_instructions=comparison['owned_CPU_instructions'],
                              comparison=str(folder / 'comparison.json'), raw_failed_gate=failed,
                              qualification='DSP was inactive in both executions; no DSP execution/audio claim.',
                              attack_calls=counts[0x18df2], damage_instructions=counts[0x18e5c],
                              source_attack_instruction_hits=sum(counts.values()),
                              reached_instruction_locations=sum(count > 0 for count in counts.values()),
                              unreached_instruction_locations=[hex(pc) for pc, count in counts.items() if not count],
                              instruction_hits={hex(pc): count for pc, count in counts.items()}))
        proof = dict(status='native_authored_attack_CPU_live_gameplay_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                     directory=str(out), source=str(source), source_sha256=sha(source), native_fixtures=str(out / 'native-fixtures.json'),
                     native_fixture_cases=json.loads((out / 'native-fixtures.json').read_text())['cases'],
                     cases=cases, CPU_candidate=str(candidate), native_CPU_candidate=str(bridge_candidate),
                     compatibility_stage=True, high_level_attack_effect_API_used=False, new_training=False, whole_game_complete=False,
                     artifacts_sha256={str(path): sha(path) for path in [source, wrapper, library, bridge_source, bridge_lib,
                                                                       Path(original['library']), Path(bridge['cost_library'])]},
                     scope='All40attack PCs are overridden by the proposed CPU-compatible body; per-case counters identify the subset actually reached in live source frame execution. RNG/helper instructions remain existing source implementations; all other PCs use the existing source dispatcher. Unmodified original merchant checkpoint and ordinary120/300frame unarmed/Beretta inputs; all CPU/cycle/frameRAM/video/PCM/final-machine gates pass, except raw DSP-positive gate qualified by inactive counters. Concurrent OP writes are executed by original device runtime, not supplied from capture. Not the higher-level biwn_attack_effect API, a new logical function, standalone or whole-game proof.')
        save(out / 'verdict.json', proof)
        save(ROOT / 'verification/live-attack-CPU-current.json', proof)
        state.update(status='terminal_live_attack_CPU_match', cases=cases)
        checkpoint()
        print(proof['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        checkpoint()
        raise


if __name__ == '__main__':
    main()
