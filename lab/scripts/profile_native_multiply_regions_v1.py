"""Instruction-cycle attribution of the existing v14 entry, not a new timing gate.
Three cases from the prior eight-sample cost receipt. No game execution or edits.
"""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import check_native_multiply_public_v1 as p
h=p.h;ROOT=p.ROOT;V=ROOT/'verification'
def save(path,x):Path(path).write_text(json.dumps(x,indent=2)+'\n')
def sha(path):return h.sha(Path(path).read_bytes())
def main():
 g=json.loads((V/'native-multiply-public-v1-current.json').read_text())
 assert sha(g['payload'])==g['payload_sha256']
 out=V/'native-multiply-regions-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 syms=g['symbols'];ordered=sorted((a,n)for n,a in syms.items());entry=syms['biwn_v14_multiply'];body=syms['native_multiply_context'];wrapper=syms['biwn_v14_multiply_body'];endbody=min(a for a,n in ordered if a>body);endwrapper=min(a for a,n in ordered if a>wrapper)
 payload=Path(g['payload']).read_bytes();engine=h.Engine();rows=[]
 try:
  for ram,initial,case in p.contract.fixtures():
   i=case['variant']
   if i not in [0,512,2191]:continue
   task=p.POOL+(i%p.SLOTS)*p.STRIDE;sp=task+768;s=h.CPU.from_buffer_copy(bytes(initial));s.registers[15]=sp
   if s.sr&0x2000:s.ssp=sp
   else:s.usp=sp
   memory=bytearray(ram);memory[p.CODE:p.CODE+len(payload)]=payload;memory[p.ARENA:p.ARENA+p.SLOTS*p.STRIDE]=bytes([0xa5])*(p.SLOTS*p.STRIDE);memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');memory[sp-64:sp+32]=ram[p.contract.GSP-64:p.contract.GSP+32];memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
   for slot in range(p.SLOTS):memory[p.ARENA+slot*p.STRIDE+130:p.ARENA+slot*p.STRIDE+134]=bytes(4)
   memory=bytes(memory);engine.native.device.seed(memory,0);s.pc=entry;engine.set_cpu(s,True);regions={k:dict(cycles=0,instructions=0)for k in ['entry_guard_capture_and_return','C_wrapper_setup','recovered_context_body']};trace=[]
   for step in range(10000):
    pc=engine.core.m68k_get_reg(None,16)
    if pc==h.STOP:break
    region='recovered_context_body'if body<=pc<endbody else'C_wrapper_setup'if wrapper<=pc<endwrapper else'entry_guard_capture_and_return'
    cycles=engine.core.m68k_execute(1);regions[region]['cycles']+=cycles;regions[region]['instructions']+=1;trace.append(dict(PC=hex(pc),cycles=cycles,region=region))
   else:raise AssertionError('no return')
   total=sum(x['cycles']for x in regions.values());prior=json.loads((V/'native-multiply-public-cost-v1-current.json').read_text());old=next(x for x in prior['cases']if x['case']['variant']==i);assert total==old['costs']['native']['cycles']
   row=dict(variant=i,regions=regions,total_cycles=total,original_cycles=old['costs']['original']['cycles']);rows.append(row);save(out/('trace-'+str(i)+'.json'),trace)
 finally:engine.native.close()
 result=dict(status='terminal_v14_multiply_three_case_cycle_attribution',directory=str(out),rows=rows,new_predictions=0,new_training=False,disc_changed=False,scope=__doc__,source_sha256={str(x):sha(x)for x in [Path(__file__),V/'native-multiply-public-v1-current.json',V/'native-multiply-public-cost-v1-current.json']})
 save(out/'review.json',result);save(V/'native-multiply-regions-v1-current.json',result);print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
