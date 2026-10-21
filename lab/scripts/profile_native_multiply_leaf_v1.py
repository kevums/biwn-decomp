"""Pinned-emulator full entry/return CPU cost; no physical/game timing claim."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_native_multiply_leaf_v1 as p
h=p.h;ROOT=p.ROOT;V=ROOT/'verification'
def read(path):return json.loads(Path(path).read_text())
def save(path,x):Path(path).write_text(json.dumps(x,indent=2)+'\n')
def sha(path):return h.sha(Path(path).read_bytes())
def main():
 gp=V/'native-multiply-leaf-v1-current.json';g=read(gp);assert g['completed']==2192 and g['fallbacks']==320
 for path,digest in g['source_sha256'].items():assert sha(path)==digest,path
 out=V/'native-multiply-leaf-cost-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);payload=Path(g['payload']).read_bytes();entry=g['symbols']['biwn_v14_multiply'];e=h.Engine();rows=[]
 try:
  for ram,initial,case in p.contract.fixtures():
   i=case['variant']
   if i not in [0,64,256,448,512,640,896,2191]:continue
   task=p.POOL+(i%p.SLOTS)*p.STRIDE;sp=task+768;s=h.CPU.from_buffer_copy(bytes(initial));s.registers[15]=sp
   if s.sr&0x2000:s.ssp=sp
   else:s.usp=sp
   memory=bytearray(ram);memory[p.CODE:p.CODE+len(payload)]=payload;memory[p.ARENA:p.ARENA+p.SLOTS*p.STRIDE]=bytes([0xa5])*(p.SLOTS*p.STRIDE);memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');memory[sp-64:sp+32]=ram[p.contract.GSP-64:p.contract.GSP+32];memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
   for slot in range(p.SLOTS):memory[p.ARENA+slot*p.STRIDE+130:p.ARENA+slot*p.STRIDE+134]=bytes(4)
   memory=bytes(memory);costs={};results={}
   for lane,start in [('original',0xe540),('native',entry)]:
    e.native.device.seed(memory,0);physical=h.CPU.from_buffer_copy(bytes(s));physical.pc=start;e.set_cpu(physical,True);cycles=steps=0
    while e.core.m68k_get_reg(None,16)!=h.STOP:
     assert steps<10000;cycles+=e.core.m68k_execute(1);steps+=1
    actual=bytearray(e.native.device.ram());actual[p.ARENA:p.ARENA+p.SLOTS*p.STRIDE]=memory[p.ARENA:p.ARENA+p.SLOTS*p.STRIDE];results[lane]=(h.cpu_dict(e.cpu()),bytes(actual));costs[lane]=dict(cycles=cycles,instructions=steps)
   assert results['original']==results['native'];rows.append(dict(case=case,costs=costs,native_to_original_ratio=round(costs['native']['cycles']/costs['original']['cycles'],4),full_return_CPU_public_RAM_match=True))
 finally:e.native.close()
 assert len(rows)==8;save(out/'cases.json',rows);proof=dict(status='terminal_native_public_multiply_cost_eight_cases_measured',directory=str(out),cases=rows,new_training=False,new_predictions=0,disc_changed=False,source_sha256={str(path):sha(path)for path in [Path(__file__),Path(p.__file__),gp,Path(g['payload']),out/'cases.json']},scope=__doc__+' Eight fixed operands,entry-to-RTS includingprivatecontext/guard costs;no fixtureeffects,gueststate repairs orclock normalization. All samples deliberatelyuser mode;the2192/320functional matrix separately coversbothmodes/allCCR. No speedacceptancecriterion ordiscqualification inferred.');save(out/'review.json',proof);save(V/'native-multiply-leaf-cost-v1-current.json',proof);print([(row['case']['variant'],row['costs']['original']['cycles'],row['costs']['native']['cycles'])for row in rows])
if __name__=='__main__':main()
