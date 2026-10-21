"""Measure actual disc redirect and retained-core startup costs, no FPS claim."""
from datetime import datetime,timezone
from pathlib import Path
import json,random,ctypes as c
from check_biwn_scheduler import Native
from check_biwn_native_button_digit import ROOT,sha,save
SP=0x1e0000;STOP=0x1f0000

def main():
    build_path=ROOT/'verification/native-controller-lean-disc-build-current.json';build=json.loads(build_path.read_text());entry_path=ROOT/'verification/native-controller-lean-disc-entry-current.json';entry=json.loads(entry_path.read_text());candidate=(Path(entry['directory'])/'installed-and-heap-initialized-RAM.bin').read_bytes();original=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0xe4c0);regs=[rng.getrandbits(32)for _ in range(15)];n=Native();results=[]
    try:
        for name,image in [('original',original),('controller_lean_CDI',candidate)]:
            ram=bytearray(image);ram[0x49ba4:0x49ba8]=bytes(4);ram[SP:SP+4]=STOP.to_bytes(4,'big');n.device.seed(bytes(ram),0);l=n.lib;l.JoystickReset()
            for port in [0,1]:(c.c_uint8*84).in_dll(l,'joypad'+str(port)+'Buttons')[:]=bytes(84)
            l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x201f)
            for i,v in enumerate(regs+[SP]):l.m68k_set_reg(i,v)
            l.m68k_set_reg(16,0xe4c0);cycles=steps=0
            for _ in range(1000):
                pc=l.m68k_get_reg(None,16)
                if pc==STOP:break
                assert 0xe4c0<=pc<0xe53c or build['resident_address']<=pc<build['resident_address']+build['component_bytes']
                cycles+=l.m68k_execute(1);steps+=1
            else:raise AssertionError('No return')
            results.append(dict(name=name,cycles=cycles,instructions=steps,CPU=[l.m68k_get_reg(None,i)for i in range(18)]))
    finally:n.close()
    assert results[0]['CPU']==results[1]['CPU']
    old=json.loads((ROOT/'verification/native-controller-current.json').read_text());lean=json.loads((ROOT/'verification/native-controller-lean-current.json').read_text())
    old_rows=json.loads((Path(old['directory'])/'native-results.json').read_text());lean_rows=json.loads((Path(lean['directory'])/'native-results.json').read_text());entry_rows=json.loads((Path(entry['directory'])/'entry-cases.json').read_text())
    result=dict(status='terminal_controller_component_and_disc_entry_costs_measured',recorded_at=datetime.now(timezone.utc).isoformat(),disc_call=results,initial_C_wrapper_cycle_pairs=sorted(set((x['original_cycles'],x['compiled_cycles'])for x in old_rows)),lean_C_wrapper_cycle_pairs=sorted(set((x['original_cycles'],x['compiled_cycles'])for x in lean_rows)),CDI_loader_cycles=sorted(set(row['new_entry_cycles']for row in entry_rows)),CDI_loader_instructions=sorted(set(row['new_instruction_count']for row in entry_rows)),build_proof=str(build_path),build_proof_sha256=sha(build_path),source_sha256={str(Path(__file__)):sha(__file__)},scope='Pinned native CPU: one actual on-disc redirect call with no pressed buttons/zero previousheld/declaredCPU/SR, no IRQ/event progression. Separate1216component cases cover all32CCR/modes and pad patterns. Startup96cases. No frames-per-second, wallclock throughput, physical-bus timing or complete machine equivalence claim.')
    save(ROOT/'verification/native-controller-cost-current.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
