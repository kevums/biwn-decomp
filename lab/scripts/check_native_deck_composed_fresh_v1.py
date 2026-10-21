"""Controlled Deck roundtrip on a restored fresh native-disc machine.

Both lanes retain the installed native GPU family and all other native code.
Only the coordinate root differs. CPU entry, two-task ring, debug flags and
selector/count13 are explicit fixtures; this is not natural Deck activation.
"""
import hashlib
import json
import os
import signal
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as restore

ROOT = restore.ROOT
V = ROOT / 'verification'
read = restore.read
save = restore.save
sha = restore.sha

def replace(text, old, new, count=1):
    assert text.count(old) == count, (old[:100], text.count(old), count)
    return text.replace(old, new)

def main():
    out = V / 'native-Deck-composed-fresh' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    restore_path = V / 'native-Deck-fresh-machine-restore-current.json'
    recorded = read(restore_path)
    assert recorded['status'] == 'terminal_fresh_native_disc_machine_byte_exact_restore_verified'
    for key in ['core', 'disc', 'state', 'RAM', 'build']:
        assert sha(recorded[key+'_path']) == recorded[key+'_sha256']
    build = read(recorded['build_path'])
    template = ROOT / 'scripts/check_mode3_source_flow.py'
    text = template.read_text()
    anchor = next(line for line in text.splitlines() if line.lstrip().startswith("proof_name='mode3-recorded-world-loop-roundtrip'"))
    text = replace(text, anchor, " proof_name='native-Deck-composed-fresh-world-loop-v1'")
    text = text.replace("if mode=='native':", "if mode in ['native','C']:").replace("int(mode=='C')", '0')
    text = replace(text, "ROOT/'verification/mode3-recorded-machine-restore-current.json'", 'Path('+repr(str(restore_path))+')')
    original_ram_expr = "ROOT/'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin'"
    # The old report's captured-RAM locator is rewritten as well as both reads.
    text = text.replace(original_ram_expr, 'Path('+repr(recorded['RAM_path'])+')')
    text = replace(text, "str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode()", "recorded['disc_path'].encode()")
    # All execution is native on both lanes. The canonical C instruction map
    # intentionally contains original bytes at installed native redirect roots.
    text = replace(text,
        " for instructions in rows.values():\n  for row in instructions:assert ram[row['address']:row['address']+row['size']].hex()==row['bytes']",
        " # Original C instruction maps are not used for either native lane.\n assert bytes(ram[0x11d1a:0x11d20])==INSTALLED_ROOT")
    original_reference = ROOT / 'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin'
    original_root = original_reference.read_bytes()[0x11d1a:0x11d20]
    installed_root = Path(recorded['RAM_path']).read_bytes()[0x11d1a:0x11d20]
    assert installed_root == bytes.fromhex('4ef9') + build['deck_code_address'].to_bytes(4, 'big')
    syms = build['deck_symbols']
    constants = dict(NATIVE_ENTRY=syms['biwn_native_deck_coordinate'],
                     HELPER_RETURN=syms['biwn_native_deck_helper_return'],
                     ROOT_RETURN=syms['biwn_native_deck_coordinate_return'],
                     DECK_ARENA=build['deck_arena_address'], DECK_BYTES=build['deck_arena_bytes'],
                     GPU_ARENA=build['arena_address'], GPU_BYTES=build['reserved_arena_bytes'],
                     GPU_NATIVE=build['mailbox_roots']['0xe26c']['native_entry'],
                     GPU_NATIVE_RETURN=build['mailbox_symbols']['biwn_native_gpu_submit_4720_return'],
                     INSTALLED_ROOT=installed_root, ORIGINAL_ROOT=original_root)
    text = replace(text, '   disc=Disc();cpu=', '''   # Finish the GPU work already pending in the restored machine. The old
   # fixture began idle; do not zero its mailbox or seed resident registers.
   runtime.core.GPUExec.argtypes=[c.c_int32]
   drain_steps=0
   for drain_steps in range(200000):
    if runtime.core.GPUReadLong(0xf03204,0)==0xffffffff and runtime.core.GPUReadLong(0xf03200,0)==0:break
    runtime.core.GPUExec(1)
   else:raise AssertionError(('Restored GPU idle drain bound',hex(runtime.core.GPUReadLong(0xf03200,0)),hex(runtime.core.GPUReadLong(0xf03204,0))))
   save(out/(mode+'-restored-GPU-drain.json'),dict(instructions_requested=drain_steps,GPU=sha(GPU_bytes()),RAM=sha(bytes(runtime.device.ram()))))
   if mode=='native':
    for index,value in enumerate(ORIGINAL_ROOT):runtime.device.direct(0x11d1a+index,1,value)
   native_active=None;native_entries=0;native_returns=0;native_helper_yields=0;gpu_native_entries=0;gpu_native_returns=0;nested_gpu_entries=0;coordinate_original_steps=0;gpu_original_steps=0
   def normalized(raw):
    data=bytearray(raw)
    for a,n in [(DECK_ARENA,DECK_BYTES),(GPU_ARENA,GPU_BYTES)]:data[a:a+n]=ram[a:a+n]
    data[0x11d1a:0x11d20]=INSTALLED_ROOT
    if mode=='C'and native_active is not None:
     sp,ret=native_active
     if int.from_bytes(data[sp:sp+4],'big')==HELPER_RETURN:data[sp:sp+4]=ret.to_bytes(4,'big')
    return bytes(data)
   def guards():
    raw=runtime.device.ram()
    for lo,hi in IMMUTABLE_RANGES:assert raw[lo:hi]==ram[lo:hi],('immutable resident bytes',hex(lo),hex(hi))
    for a,n,stride in [(DECK_ARENA,101,1024),(GPU_ARENA,102,256)]:
     for i in range(n):
      lo=a+i*stride
      assert raw[lo:lo+16]==ram[lo:lo+16]and raw[lo+stride-16:lo+stride]==ram[lo+stride-16:lo+stride],('arena guard',hex(lo))
   disc=Disc();cpu=''')
    text = text.replace('sha(runtime.device.ram())', 'sha(normalized(runtime.device.ram()))')
    text = replace(text, "assert sha(normalized(runtime.device.ram()))==recorded['RAM_sha256']", "assert sha(runtime.device.ram())==recorded['RAM_sha256']")
    text = replace(text, '   def mark(name):', '   def mark(name):\n    guards()')
    text = replace(text, 'final=runtime.device.ram();(out/', 'guards();final=normalized(runtime.device.ram());(out/')
    text = replace(text, '    nonlocal cpu', '    nonlocal cpu,native_active,native_entries,native_returns,native_helper_yields,gpu_native_entries,gpu_native_returns,nested_gpu_entries,coordinate_original_steps,gpu_original_steps')
    # Count the actual executed instruction visits, never unique-address counts.
    text = replace(text, '      trace.append(pc)\n      if pc==0x11e6c', '''      if pc==NATIVE_ENTRY:native_entries+=1
      if pc==ROOT_RETURN:native_returns+=1;native_active=None
      if pc==GPU_NATIVE:gpu_native_entries+=1
      if pc==GPU_NATIVE and mode=='C'and native_active is not None:nested_gpu_entries+=1
      if pc==GPU_NATIVE_RETURN:gpu_native_returns+=1
      if 0x11d20<=pc<0x11e64:coordinate_original_steps+=1
      if 0xe272<=pc<0xe2b8:gpu_original_steps+=1
      if mode=='C'and pc in [0xe26c,0xe540]:
       current=runtime.cpu();sp=current.registers[15]
       if runtime.device.read(sp,4)==HELPER_RETURN:
        frame=DECK_ARENA+16+runtime.device.read(0xc0920,4)-0xc0928
        assert runtime.device.read(frame+88,4)==sp
        native_active=(sp,runtime.device.read(frame+92,4))
      trace.append(pc)
      if pc==0x11e6c''')
    text = replace(text,
        'if step and pc in [0xdf60,BOUNDARY,0x190000,*([0x1a54a]if options.world_loop else [])]:cpu=runtime.cpu();return',
        '''if step and pc in [0xdf60,BOUNDARY,0x190000,*([0x1a54a]if options.world_loop else [])]:
       if mode=='C'and native_active is not None and pc==0xdf60:native_helper_yields+=1
       cpu=runtime.cpu();return''')
    text = replace(text, "     mark('boundary_'+str(frame));frame+=1", "     mark('boundary_'+str(frame));frame+=1\n     if frame==1:pads.set_buttons([0])")
    # These loops now traverse the installed compiled scheduler/loader. Keep
    # finite bounds but allow more instructions than the original assembly.
    text = text.replace('range(512):', 'range(8192):')
    text = replace(text, 'range(150000):', 'range(1500000):')
    text = replace(text, "raise AssertionError(('Native flow limit',hex(pc)))", "raise AssertionError(('Native flow limit',hex(pc),media.scheduler.cpu_dict(runtime.cpu()),trace[-32:]))")
    text = replace(text, "    if options.inventory_entry:\n     if mode in ['native','C']:\n      for _ in range(8192):", "    if options.inventory_entry:\n     resume_target=runtime.device.read(cpu.registers[15],4)\n     if mode in ['native','C']:\n      for _ in range(8192):")
    text = text.replace('runtime.cpu().pc==0x1b0da and runtime.device.read(0xc0920,4)==MAIN', 'runtime.cpu().pc==resume_target and runtime.device.read(0xc0920,4)==MAIN')
    text = text.replace("assert cpu.pc==0x1b0da and runtime.device.read(0xc0920,4)==MAIN;mark", "assert cpu.pc==resume_target and runtime.device.read(0xc0920,4)==MAIN;mark")
    text = replace(text, "raise AssertionError('Frozen-ring source yield limit')", "raise AssertionError(('Frozen-ring source yield limit',media.scheduler.cpu_dict(runtime.cpu()),hex(runtime.device.read(0xc0920,4)),trace[-32:]))")
    text = replace(text, 'original_CPU_instructions=len(trace)', 'native_coordinate_entries=native_entries,native_coordinate_returns=native_returns,native_helper_yields=native_helper_yields,native_GPU4720_entries=gpu_native_entries,native_GPU4720_returns=gpu_native_returns,nested_coordinate_GPU4720_entries=nested_gpu_entries,coordinate_original_steps=coordinate_original_steps,GPU4720_original_steps=gpu_original_steps,original_CPU_instructions=len(trace)')
    text = replace(text, "runtime.device.read(0x15b530,2)==2", "runtime.device.read(0x15b530,2)==int.from_bytes(ram[0x15b530:0x15b532],'big')")
    text = replace(text,
        "  assert results[1]['original_CPU_instructions']==results[1]['original_GPU_opcodes']==results[1]['statistics'][4]==results[1]['statistics'][8]==0",
        """  assert all(row['original_CPU_instructions']>0 and row['original_GPU_opcodes']>0 for row in results)
  assert results[0]['native_coordinate_entries']==0 and results[0]['coordinate_original_steps']>0
  assert results[1]['native_coordinate_entries']==results[1]['native_coordinate_returns']>0
  assert results[1]['coordinate_original_steps']==0
  assert results[1]['nested_coordinate_GPU4720_entries']==results[1]['native_coordinate_entries']
  assert all(row['native_GPU4720_entries']==row['native_GPU4720_returns']>0 and row['GPU4720_original_steps']==0 for row in results)
""")
    # Override inherited report language at its final save; preserve raw checks.
    text = replace(text, "  save(out/'report.json',report);", """  report.update(status='terminal_restored_fresh_native_coordinate_and_GPU_family_controlled_roundtrip_match',original_CPU_GPU_on_C_path=True,both_lanes_execute_native_CPU_GPU=True,natural_source_caller_verified=False,initial_CPU_entry_supplied=True,initial_GPU_resident_context_supplied=False,native_disc_changed=False,new_training=False,default_promoted=False,whole_game_complete=False,coordinate_root_original_bytes=ORIGINAL_ROOT.hex(),coordinate_root_installed_bytes=INSTALLED_ROOT.hex(),restored_fresh_machine=recorded,scope='Fresh native experimental CDI final serialized machine and matching core mounted/restored exactly before identical controlled RAM/CPU entry/two-task-ring/debug/selector13 edits. Both lanes retain all installed native GPU-family and other recovered routines; only coordinate root on/off differs. Real native CPU/GPU instructions; synchronous render completion and image-specific BIOS/disc completion providers retained. Full CPU/SR/banks, normalized 2MB RAM, checked hardware/GPU logical bytes and all command histories/checkpoints must match. Only declared Deck/GPU private arenas, six-byte coordinate redirect and active compiler helper-return word are normalized; arena guards remain checked. This is controlled composed coverage, not naturally reached Deck input, fresh uninterrupted gameplay, arbitrary helper suspension/IRQ/reentrancy, physical-console or full-game/source-rebuild proof.')
  save(out/'report.json',report);""")
    constants['IMMUTABLE_RANGES'] = [(build['resident_address'],build['arena_address']),(build['arena_end'],build['deck_arena_address'])]
    prefix = ''.join(k+'='+repr(value)+'\n' for k, value in constants.items())
    runner = out / 'pipeline-as-run.py'
    runner.write_text(prefix + text)
    state = dict(status='running_controlled_composed_fresh_machine', pid=os.getpid(), directory=str(out),
                 runner=str(runner), source_sha256={str(p): sha(p) for p in [Path(__file__), template, runner]},
                 restore_proof=str(restore_path), restore_proof_sha256=sha(restore_path),
                 original_root_source=str(original_reference), original_root_source_sha256=sha(original_reference),
                 whole_game_complete=False, native_disc_changed=False, new_training=False)
    pointer = V / 'native-Deck-composed-fresh-current.json'
    def mark(): save(out / 'protocol.json', state); save(pointer, state)
    mark()
    child = None
    try:
        with (out / 'pipeline.log').open('w') as log:
            child = subprocess.Popen([str(ROOT/'.venv/bin/python3.12'), '-u', str(runner), '--frames', '16', '--inline-selector', '--inventory-entry', '--exit-viewer', '--world-entry', '--world-loop', '--recorded-machine'], stdout=log, stderr=subprocess.STDOUT, env={**os.environ, 'PYTHONPATH': str(ROOT/'scripts')}, start_new_session=True)
            state['child_pid'] = child.pid; mark()
            try: code = child.wait(timeout=600)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL); child.wait(); raise
        state['child_pid'] = None
        assert code == 0, (out/'pipeline.log').read_text()[-6000:]
        result = read(V / 'native-Deck-composed-fresh-world-loop-v1-current.json')
        state.update(status=result['status'], proof_directory=result['directory'],
                     paired_checkpoints=result['paired_checkpoints'],
                     GPU_commands=[len(row['events']) for row in result['results']],
                     native_coordinate_calls=result['results'][1]['native_coordinate_entries'],
                     native_GPU4720_calls=[row['native_GPU4720_entries'] for row in result['results']],
                     nested_coordinate_GPU4720_calls=result['results'][1]['nested_coordinate_GPU4720_entries'],
                     active_helper_yields=result['results'][1]['native_helper_yields'], scope=__doc__)
        mark(); print(state['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error), child_pid=None if child is None or child.poll() is not None else child.pid)
        mark(); raise

if __name__ == '__main__': main()
