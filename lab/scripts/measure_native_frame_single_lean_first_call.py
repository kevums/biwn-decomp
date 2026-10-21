"""Isolated cost/stack measurement of the lean port using a captured live caller."""
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone
from run_biwn_native_fast_gameplay_route import ROOT, sha, save
from check_biwn_scheduler import Native
from review_biwn_native_frame_single_first_call import cpu, differences

def main():
    proof_path=ROOT/'verification/native-frame-reference-single-lean-current.json';proof=json.loads(proof_path.read_text());assert proof['source_accepted']and proof['native_cases']==1376 and proof['trace_cases']==1632
    captured=json.loads((ROOT/'verification/native-frame-single-first-call-reviewed-current.json').read_text());entry=Path(captured['directory'])/'control';image=(entry/'entry.ram').read_bytes();start=cpu(entry/'entry.cpu');expected=cpu(entry/'return.cpu')
    payload=Path(proof['compiled_binary']).read_bytes();elf=Path(proof['compiled_binary']).with_suffix('.elf');assembly=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-d',str(elf)],text=True)
    stops=[int(line.split(':',1)[0].strip(),16)for line in assembly.splitlines()if '\trts'in line];assert stops;stop=stops[0];assert 0x148000<=stop<0x148000+len(payload)
    candidate=bytearray(image);candidate[0x148000:0x148000+len(payload)]=payload;candidate[0x1ae56:0x1ae5c]=b'\x4e\xf9'+(0x148000).to_bytes(4,'big')
    n=Native();l=n.lib;n.device.seed(candidate,0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,start[18]);l.m68k_set_reg(17,0);l.m68k_set_reg(15,start[17]);l.m68k_set_reg(17,start[19])
    for i,v in enumerate(start[:16]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,start[16]);cycles=0;pcs=[];minimum=start[15]
    try:
        for _ in range(10000):
            pc=l.m68k_get_reg(None,16);minimum=min(minimum,l.m68k_get_reg(None,15))
            if pc==stop:break
            assert pc==0x1ae56 or 0x148000<=pc<0x148000+len(payload),hex(pc)
            pcs.append(pc);cycles+=l.m68k_execute(1)
        else:raise AssertionError('No pre-RTS boundary')
        regs=[l.m68k_get_reg(None,i)for i in range(17)];sr=l.m68k_get_reg(None,17);result=regs+[n.prefix[16]if sr&0x2000 else regs[15],regs[15]if sr&0x2000 else n.prefix[17],sr];ram=n.device.ram()
    finally:n.close()
    assert all(x==y for i,(x,y)in enumerate(zip(result,expected))if i!=16)
    baseline=Path(captured['directory'])/'control/entry.ram';original_cost=captured['stopped_device_replays']['control'];old_C_cost=captured['stopped_device_replays']['candidate']
    # Compare with the stopped-device original, rather than live RAM with device writes.
    from review_biwn_native_frame_single_first_call import replay
    n=Native()
    try:_,reference=replay(n,image,start,expected[16])
    finally:n.close()
    diff=differences(ram,reference);public=[i for i in diff if not(0x1ae56<=i<0x1ae5c or 0x148000<=i<0x148000+len(payload)or minimum<=i<start[15]-4)];assert not public
    out=ROOT/'verification/native-frame-single-lean-cost'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());(out/'disassembly.txt').write_text(assembly)
    review=dict(status='terminal_lean_single_first_call_isolated_cost_and_stack_verified',directory=str(out),component_proof=str(proof_path),component_proof_sha256=sha(proof_path),captured_caller_review=str(Path(captured['directory'])/'review.json'),payload_bytes=len(payload),instructions=len(pcs),emulator_CPU_cycles=cycles,max_private_stack_depth=start[15]-minimum,CPU_equal_except_code_PC=True,public_RAM_difference_bytes=0,original_instructions=original_cost['instructions'],original_emulator_CPU_cycles=original_cost['emulator_CPU_cycles'],context_array_instructions=old_C_cost['instructions'],context_array_emulator_CPU_cycles=old_C_cost['emulator_CPU_cycles'],context_array_private_stack_depth=96,new_training=False,local_model_authored=False,default_promoted=False,game_frames=0,scope='Same actual caller replayed without asynchronous GPU/DSP/OP clocks or interrupts,at standalone scratch link address. CPU/RAM/ordered full fixture gate separately passes. Cycle counts are isolated emulator costs,not physical timing,gameplay equality or FPS. No new disc has been built or preview changed.',artifact_sha256={str(p):sha(p)for p in [baseline,entry/'entry.cpu',Path(proof['compiled_binary']),elf,Path(__file__)]})
    save(out/'review.json',review);save(ROOT/'verification/native-frame-single-lean-cost-current.json',review);print(json.dumps(review),flush=True)

if __name__=='__main__':main()
