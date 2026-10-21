"""Exact new actor watchers: fault controls, pinned CPU off/on, full compilation."""
import ctypes as c
import importlib.util
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
import shared_deck_actor_phased_image_full_observer_v2 as full
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    bp = V / 'actor-phased-disc-build-v1-current.json'
    fp = V / 'actor-phased-fixed-v2-current.json'
    b, proof = read(bp), read(fp)
    assert proof['source_accepted']
    for p, h in proof['dependencies_sha256'].items():
        assert sha(p) == h, p
    out = V / 'actor-phased-watch-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    state = dict(status='qualifying_exact_actor_phased_watchers', directory=str(out), pid=os.getpid(), new_predictions=0, new_training=False)
    def mark():
        save(out / 'protocol.json', state)
        save(V / 'actor-phased-watch-v1-current.json', state)
    mark()
    native = None
    try:
        text, inherited = full.observer_source(b, read(V / 'native-Deck-coordinate-disc-build-current.json'))
        full_source = out / 'observer.c'
        full_source.write_text(text)
        direction = inherited.with_name('direction-shadow-model.c')
        result = subprocess.run(['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(full_source), str(direction), '-o', str(out / 'observer.dylib')], capture_output=True, text=True)
        (out / 'full-compiler.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        blocks = []
        for short, name in [('ad', 'dispatch'), ('ai', 'initialize')]:
            at = text.index('struct ' + short + '_call {')
            end = text.index('\n}', text.index('static void watch_actor_' + name + '(', at)) + 2
            blocks.append(text[at:end])
        at = text.index('static unsigned task_id_valid(')
        bounds = text[at:text.index('\nstatic void arena_check_guards', at)]
        header = '''#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const uint8_t *ram;static struct cpu current;static unsigned arena_active[102];
static uint32_t rd16(uint32_t a){return ((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){return(rd16(a)<<16)|rd16(a+2);}
static void read_cpu(struct cpu *o){*o=current;}
static void emit(uint32_t pc){(void)pc;}
#define BIWN_ACTOR_DISPATCH_TASK() rd32(0xc0920u)
#define BIWN_ACTOR_INITIALIZE_TASK() rd32(0xc0920u)
'''
        exports = '''
void snapshot(const void *m,const struct cpu *cpu){ram=m;current=*cpu;}
void step(uint32_t pc){watch_actor_dispatch(pc);watch_actor_initialize(pc);}
void clear(void){
memset(ad_calls,0,sizeof(ad_calls));memset(ai_calls,0,sizeof(ai_calls));memset(arena_active,0,sizeof(arena_active));
ad_slots=ad_pending=ai_slots=ai_pending=0;
ad_entries=ad_native_entries=ad_returns=ad_old_steps=ad_native_steps=ad_errors=ad_child_entries=ad_child_returns=ad_actor=ad_sprite=ad_full=ad_stack_observations=ad_stack_outside=ad_context_collisions=ad_context_checks=ad_child_below_context=ad_context_SP_inside=0;
ad_max_depth=ad_max_child_depth=0;ad_min_context_clearance=ad_min_headroom=0xffffffffu;
ai_entries=ai_native_entries=ai_returns=ai_old_steps=ai_native_steps=ai_errors=ai_helper_entries=ai_helper_returns=ai_context_checks=ai_context_corruptions=ai_stack_observations=ai_stack_outside=0;
ai_max_depth=0;ai_min_headroom=0xffffffffu;
}
uint64_t stat(unsigned i){switch(i){
case 0:return ad_errors+ad_context_collisions+ai_errors+ai_context_corruptions;
case 1:return ad_stack_outside+ai_stack_outside;
case 2:return ad_pending+ai_pending;
case 3:return ad_entries;case 4:return ad_returns;
case 5:return ai_entries;case 6:return ai_returns;
case 7:return ad_context_checks;case 8:return ai_context_checks;
default:return 0;}}
'''
        source, library = out / 'fixture.c', out / 'fixture.dylib'
        source.write_text(header + bounds + '\n'.join(blocks) + exports)
        result = subprocess.run(['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(library)], capture_output=True, text=True)
        (out / 'fixture-compiler.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        f = c.CDLL(str(library))
        f.snapshot.argtypes = [c.c_void_p, c.POINTER(scheduler.CPU)]
        f.step.argtypes = [c.c_uint32]
        f.stat.argtypes = [c.c_uint]
        f.stat.restype = c.c_uint64
        folder = Path(proof['directory'])
        init, joint = load(folder / 'fixed_init_engine.py', 'actor_watch_init_engine'), load(folder / 'fixed_joint_engine.py', 'actor_watch_joint_engine')
        init.BASE = joint.INITBASE = proof['artifacts']['initialize']['code_address']
        joint.BASE = proof['artifacts']['dispatch']['code_address']
        joint.INIT_PAYLOAD = Path(proof['artifacts']['initialize']['binary']).read_bytes()
        joint.INIT_SYMBOLS = proof['artifacts']['initialize']['symbols']
        native = scheduler.Native()
        baseline = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
        calls = RAM_checks = 0
        results, controls = [], []
        ad = b['actor_phased_symbols']['dispatch']
        ai = b['actor_phased_symbols']['initialize']
        boundary = {0x13ae0, 0x134dc, 0x137e0, 0x102c4, 0x10520, 0xdf6c,
                    ad['biwn_native_actor_dispatch'], ad['biwn_native_actor_dispatch_return'],
                    ai['biwn_native_actor_initialize'], ai['biwn_native_actor_initialize_return'],
                    *[v for k, v in ad.items() if 'after_' in k], *[v for k, v in ai.items() if 'after_' in k]}

        def cpu():
            core = native.lib
            state = scheduler.CPU()
            state.registers[:] = [core.m68k_get_reg(None, i) for i in range(16)]
            state.pc = core.m68k_get_reg(None, 16)
            state.sr = core.m68k_get_reg(None, 17)
            state.usp = native.prefix[16] if state.sr & 0x2000 else state.registers[15]
            state.ssp = state.registers[15] if state.sr & 0x2000 else native.prefix[17]
            return state

        def observed_replay(engine, snapshot, case, payload, symbols, compiled, expected, fault=None):
            nonlocal calls, RAM_checks
            execute = native.lib.m68k_execute
            f.clear()
            injected = False
            def step(*values):
                nonlocal calls, RAM_checks, injected
                current = cpu()
                before = bytes(current)
                raw = native.device.ram() if current.pc in boundary else None
                pointer, mirror = native.device.pointer, None
                if fault and not injected:
                    ad_return = current.pc == ad['biwn_native_actor_dispatch_return']
                    ai_return = current.pc == ai['biwn_native_actor_initialize_return']
                    helper = current.pc in [0x102c4, 0x10520, 0xdf6c]
                    child_return = current.pc in [ad['biwn_actor_dispatch_after_actor'], ad['biwn_actor_dispatch_after_sprite']]
                    helper_return = current.pc in [ai['biwn_actor_initialize_after_' + k] for k in ['outside', 'inside', 'task']]
                    if fault == 'return_D0' and ad_return:
                        current.registers[0] ^= 1
                        injected = True
                    elif fault == 'callee_D2' and ai_return:
                        current.registers[2] ^= 1
                        injected = True
                    elif fault == 'outside_task' and current.pc == ad['biwn_actor_dispatch_phase']:
                        current.registers[15] = int.from_bytes(native.device.ram()[0xc0920:0xc0924], 'big') + 37
                        injected = True
                    elif fault in ['public_AD', 'public_AI', 'return_word', 'helper_argument'] and (
                        (fault == 'public_AD' and child_return) or (fault == 'public_AI' and helper_return) or
                        (fault == 'return_word' and ai_return) or (fault == 'helper_argument' and helper)):
                        memory = bytearray(native.device.ram())
                        if fault == 'public_AD':
                            at = engine.SP - 16
                        elif fault == 'public_AI':
                            at = engine.SP - 32
                        elif fault == 'return_word':
                            at = engine.SP
                        else:
                            at = current.registers[15] + 4
                        memory[at] ^= 1
                        mirror = (c.c_uint8 * len(memory)).from_buffer(memory)
                        pointer = mirror
                        injected = True
                f.snapshot(pointer, c.byref(current))
                f.step(current.pc)
                calls += 1
                assert bytes(cpu()) == before, 'Observer changed CPU'
                if raw is not None:
                    assert native.device.ram() == raw, 'Observer changed actual RAM'
                    RAM_checks += 1
                return execute(*values)
            native.lib.m68k_execute = step
            try:
                result = engine.replay(native, snapshot, case, payload, symbols, compiled, expected)
                ram = native.device.ram()
            finally:
                native.lib.m68k_execute = execute
            stats = [f.stat(i) for i in range(9)]
            if fault:
                assert injected and any(stats[:3]), (fault, injected, stats)
                controls.append(dict(fault=fault, rejected=True, decoded_or_mirror_fault_only=True, stats=stats))
            else:
                assert stats[:3] == [0, 0, 0] and stats[3] == stats[4] and stats[5] == stats[6], stats
            return result, ram, stats

        for kind, engine, artifact in [('initialize', init, proof['artifacts']['initialize']), ('joint', joint, proof['artifacts']['dispatch'])]:
            payload, symbols = Path(artifact['binary']).read_bytes(), artifact['symbols']
            vectors = engine.vectors()
            for slot in [0, 100]:
                task = 0xc0928 + slot * 1024
                engine.SP = task + (520 if kind == 'initialize' else 556)
                snapshot = bytearray(baseline)
                snapshot[0xc0920:0xc0924] = task.to_bytes(4, 'big')
                for i in [0, 4, 5, 6, 70, 118]:
                    case = vectors[i]
                    for compiled in [False, True]:
                        expected = engine.execute(bytes(snapshot), case, payload, symbols, compiled)
                        off = engine.replay(native, bytes(snapshot), case, payload, symbols, compiled, expected)
                        off_ram = native.device.ram()
                        on, on_ram, stats = observed_replay(engine, bytes(snapshot), case, payload, symbols, compiled, expected)
                        assert off == on and off_ram == on_ram, 'Off/on complete CPU/RAM/helper outputs differ'
                        results.append(dict(kind=kind, slot=slot, fixture=i, compiled=compiled, stats=stats, full_off_on_equal_without_exclusions=True))
            # Choose an actual executed helper route for mirror-only fault controls.
            for fault in (['callee_D2', 'public_AI', 'return_word', 'helper_argument'] if kind == 'initialize' else ['return_D0', 'public_AD', 'outside_task']):
                for case in vectors[:128]:
                    expected = engine.execute(bytes(snapshot), case, payload, symbols, True)
                    if kind == 'initialize' and not any(x['pc'] in [0x102c4, 0x10520, 0xdf6c] for x in expected['machine']):
                        continue
                    if kind == 'joint' and not any(x['pc'] in [ad['biwn_actor_dispatch_after_actor'], ad['biwn_actor_dispatch_after_sprite']] for x in expected['machine']):
                        continue
                    observed_replay(engine, bytes(snapshot), case, payload, symbols, True, expected, fault)
                    break
                else:
                    raise AssertionError(('No fault control route', fault))
            engine.SP = init.g.SP
        save(out / 'actual-lanes.json', results)
        save(out / 'fault-controls.json', controls)
        assert len(results) == 48 and len(controls) == 7
        state.update(status='terminal_exact_actor_watchers_fault_controls_actual_CPU_readonly_and_full_compile_pass',
            actual_off_on_pairs=len(results), fault_controls=len(controls), observer_calls=calls,
            whole_RAM_immediate_boundary_checks=RAM_checks, complete_off_on_CPU_RAM_helpers_equal_without_exclusions=True,
            actor_code_at_actual_image_addresses=True, full_prefix_helpers_executed=False,
            other_original_child_bodies_execute=True, outside_geometry_task_leaf_services_prescribed=True,
            protected_context_scope='Original16/32-byte public save frames; no parked C contexts remain.',
            legacy_context_SP_inside_counter_not_applicable=True, arbitrary_IRQ_qualified=False,
            source_sha256={str(p): sha(p) for p in [Path(__file__), Path(full.__file__), bp, fp, full_source,
                out / 'observer.dylib', direction, source, library, out / 'actual-lanes.json', out / 'fault-controls.json']})
        mark()
        print(state['status'], calls, RAM_checks, flush=True)
    except BaseException as error:
        state.update(status='terminal_actor_phased_watch_failed', error=repr(error))
        mark()
        raise
    finally:
        if native:
            native.close()


if __name__ == '__main__':
    main()
