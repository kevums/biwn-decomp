"""Compare read-only live snapshots and replay the first call with devices stopped."""
import json, struct
from pathlib import Path
from datetime import datetime, timezone
from run_biwn_native_fast_gameplay_route import ROOT, sha, save
from check_biwn_scheduler import Native

def cpu(p):return list(struct.unpack('<19IH2x',p.read_bytes()))
def differences(a,b):return [i for i,(x,y)in enumerate(zip(a,b))if x!=y]
def replay(n,image,start,stop):
    n.device.seed(image,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,start[18]);l.m68k_set_reg(17,0);l.m68k_set_reg(15,start[17]);l.m68k_set_reg(17,start[19])
    for i,value in enumerate(start[:16]):l.m68k_set_reg(i,value)
    l.m68k_set_reg(16,start[16]);cycles=0;pcs=[]
    for _ in range(10000):
        pc=l.m68k_get_reg(None,16)
        if pc==stop:break
        assert pc==0x1ae56 or 0x1ae56<=pc<0x1ae88 or 0x162722<=pc<0x162722+240,hex(pc)
        pcs.append(pc);cycles+=l.m68k_execute(1)
    else:raise AssertionError('No pre-RTS boundary')
    registers=[l.m68k_get_reg(None,i)for i in range(17)];sr=l.m68k_get_reg(None,17)
    result=registers+[n.prefix[16]if sr&0x2000 else registers[15],registers[15]if sr&0x2000 else n.prefix[17],sr]
    return dict(instructions=len(pcs),emulator_CPU_cycles=cycles,CPU=result,PCs=pcs),n.device.ram()

def main():
    pointer=ROOT/'verification/native-frame-single-first-call-current.json';source=json.loads(pointer.read_text());assert source['status']=='terminal_read_only_first_call_pair_pending_review'
    out=Path(source['directory']);(out/'reviewer-as-run.py').write_bytes(Path(__file__).read_bytes())
    a,b=out/'candidate',out/'control';entry_a,entry_b=(a/'entry.ram').read_bytes(),(b/'entry.ram').read_bytes();return_a,return_b=(a/'return.ram').read_bytes(),(b/'return.ram').read_bytes();ca,cb=cpu(a/'entry.cpu'),cpu(b/'entry.cpu');ra,rb=cpu(a/'return.cpu'),cpu(b/'return.cpu')
    assert ca==cb;entry_diff=differences(entry_a,entry_b);assert entry_diff==list(range(0x1ae56,0x1ae5c))
    assert all(x==y for i,(x,y)in enumerate(zip(ra,rb))if i!=16)
    sp=ca[15];diff=differences(return_a,return_b);public=[i for i in diff if not (0x1ae56<=i<0x1ae5c or sp-96<=i<sp-4)]
    n=Native();replays={};memories={}
    try:
        for name,image,start,stop,expected in [('candidate',entry_a,ca,ra[16],ra),('control',entry_b,cb,rb[16],rb)]:
            result,memory=replay(n,image,start,stop);assert result['CPU']==expected,(name,'stopped-device replay CPU differs from live return');assert result['instructions']==json.loads((out/name/'return.json').read_text())['steps_between_entry_and_pre_RTS']
            replays[name]=result;memories[name]=memory
    finally:n.close()
    stopped_diff=differences(memories['candidate'],memories['control']);stopped_public=[i for i in stopped_diff if not (0x1ae56<=i<0x1ae5c or sp-96<=i<sp-4)]
    assert not stopped_public
    review=dict(status='terminal_first_call_semantics_equal_extra_live_display_list_updates',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),input_protocol=str(out/'protocol.json'),input_protocol_sha256=sha(out/'protocol.json'),entry_frame=json.loads((a/'entry.json').read_text())['frame'],entry_CPU_equal=True,entry_RAM_differences=entry_diff,pre_RTS_CPU_equal_except_code_PC=True,entry_SP=sp,private_stack_exclusion=[sp-96,sp-4],live_pre_RTS_RAM_difference_bytes=len(diff),live_pre_RTS_differences_outside_entry_and_private_stack=public,live_pre_RTS_words=[dict(address=hex(i),candidate=return_a[i],control=return_b[i])for i in public],stopped_device_replays=replays,stopped_device_public_RAM_difference_bytes=len(stopped_public),stopped_device_CPU_matches_live_return=True,live_instruction_counts_match_stopped_device=True,new_training=False,default_promoted=False,whole_game_complete=False,
      interpretation='Both live lanes enter with identical CPU and RAM except the6entrybytes. Their pre-RTS registers/SR match;live instruction counts equal stopped-device replays. Extra live public RAM differences lie in the display-list area beginning776F0;the stopped-device paired replay has none after excluding the6entrybytes and92private stack bytes. This supports additional asynchronous display/device work during the longer compiled call. Emulator cycle costs are isolated-core measurements,not live walltime or physical timing. This does not establish that all later video/navigation/PCM divergence has one cause,prove audio quality,or justify default promotion.')
    review['artifact_sha256']={str(p):sha(p)for p in [out/'runner-as-run.py',out/'reviewer-as-run.py',*[out/name/(phase+'.'+ext)for name in ['candidate','control']for phase in ['entry','return']for ext in ['ram','cpu','json']]]}
    save(out/'review.json',review);save(ROOT/'verification/native-frame-single-first-call-reviewed-current.json',review)
    print(json.dumps({k:v for k,v in review.items()if k in ['status','entry_frame','live_pre_RTS_differences_outside_entry_and_private_stack','stopped_device_public_RAM_difference_bytes']}),flush=True)
    print('Replay cycles/instructions:',{k:(v['emulator_CPU_cycles'],v['instructions'])for k,v in replays.items()},flush=True)

if __name__=='__main__':main()
