"""Extend scene component fixtures with actual original185B2 and native boundary records."""
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,read

def dependencies():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    return [Path(__file__),session/'display-list-fullCPU-generation.json',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v2/coordinator-reference.inc']

def install(bridge):
    bridge.base.queue.ENTRIES.add(0x185b2);bridge.base.queue.RETURNS.add(0x18852);bridge.base.queue.SCRIPTS.discard(0x185b2)
    original=bridge.support.Runtime
    class Runtime(original):
        def __init__(self,library,rows):
            display=read(dependencies()[1])['instructions_decoded'];super().__init__(library,list(rows)+display)
    bridge.support.Runtime=Runtime

def boundary(bridge,runtime,syms,slot,physical,row):
    raw=runtime.device.ram()[slot+bridge.OFFSET+4:slot+bridge.OFFSET+82];cpu=bridge.base.CPU()
    cpu.registers[:]=[int.from_bytes(raw[i:i+4],'big')for i in range(0,64,4)];cpu.pc=int.from_bytes(raw[64:68],'big');cpu.usp=int.from_bytes(raw[68:72],'big');cpu.ssp=int.from_bytes(raw[72:76],'big');cpu.sr=int.from_bytes(raw[76:78],'big')
    if cpu.sr&0x2000:cpu.usp=physical.usp
    else:cpu.ssp=physical.ssp
    if physical.pc==syms['biwn_v27_display_begin']:
        assert row is None and cpu.pc==0x185b2
        row=dict(target=0x185b2,actual_body=True,incoming=bridge.base.cd.scheduler.cpu_dict(cpu));runtime.calls.append(row);return row
    assert row is not None and cpu.pc==0x18852
    row['return']=bridge.base.cd.scheduler.cpu_dict(cpu);return None
