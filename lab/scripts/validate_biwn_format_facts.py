"""Compare typed instruction facts with actual original CPU and ordered reads."""
import copy,json,sys,shutil
from pathlib import Path
from datetime import datetime,timezone
import m68k_fact_packet as facts
import check_biwn_native_format_pad as oracle
ROOT=facts.ROOT
def main():
 pointer=json.loads((ROOT/'verification/m68k-fact-packet-current.json').read_text());p=Path(pointer['packet']);assert oracle.sha(p)==pointer['packet_sha256'];packet=json.loads(p.read_text());assert[packet['start'],packet['stop']]==[oracle.ENTRY,oracle.END]
 out=p.parent/'validation';out.mkdir();print(out,flush=True);image=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();cases=oracle.vectors();n=oracle.Native();rows=[];coverage=set();traces=0
 state=dict(status='running_original_CPU_fact_validation',directory=str(out),packet=str(p),packet_sha256=oracle.sha(p),completed=0)
 def save():oracle.save(out/'protocol.json',state);oracle.save(ROOT/'verification/m68k-fact-validation-current.json',state)
 save()
 try:
  for i,c in enumerate(cases):
   native=oracle.native(n,image,c,0,True);result=facts.execute(packet,oracle.seed(image,c),c['incoming'],c['sr'],oracle.SP)
   cpu=result['registers']+[result['pc'],result['sr']]+([0x1fe000,result['registers'][15]]if c['sr']&0x2000 else[result['registers'][15],0x1ff000])
   assert cpu==native[1]and result['RAM']==native[0],('CPU/RAM facts mismatch',i,cpu,native[1])
   trace=oracle.trace(image,c,0,True);assert result['events']==trace[1]and result['RAM']==trace[0],('ordered facts mismatch',i)
   traces+=1;coverage.update(result['coverage']);rows.append(dict(case=i,steps=result['steps'],events=len(result['events'])))
   if i%128==0:state['completed']=len(rows);save();print('Facts',len(rows),'/',len(cases),flush=True)
  for c in cases[:16]:
   result=facts.execute(packet,oracle.seed(image,c),c['incoming'],c['sr'],oracle.SP,{(0x130000,2):[2,4,2,1]});trace=oracle.trace(image,c,0,True,True);assert result['events']==trace[1]and result['RAM']==trace[0];traces+=1
  negatives=[]
  for name,pc,kind in [('wrong_stack_offset',0x1b162,'stack'),('clear_upper_word',0x1b16a,'mask'),('unsigned_nonzero_branch',0x1b172,'branch'),('lost_X_on_restore',0x1b19c,'X')]:
   bad=copy.deepcopy(packet);row=next(f for f in bad['instructions']if f['pc']==pc)
   if kind=='stack':row['src']['entry_SP_offset']+=4
   elif kind=='mask':row['dst']['write_mask']=0xffffffff
   elif kind=='branch':row['condition']='ne'
   else:row['ccr']['X']='clear'
   caught=None
   for i,c in enumerate(cases[:512]):
    try:
     result=facts.execute(bad,oracle.seed(image,c),c['incoming'],c['sr'],oracle.SP);native=oracle.native(n,image,c,0,True)
     if result['registers']+[result['pc'],result['sr']]!=native[1][:18]or result['RAM']!=native[0]:caught=dict(case=i,reason='original_CPU_RAM_difference');break
    except AssertionError as error:caught=dict(case=i,reason=str(error));break
   assert caught is not None,name;negatives.append(dict(name=name,**caught))
  assert coverage=={f['pc']for f in packet['instructions']}
  oracle.save(out/'results.json',rows);state.update(status='terminal_fact_packet_original_CPU_RAM_ordered_validation_pass',native_cases=len(rows),trace_cases=traces,coverage=[len(coverage),len(packet['instructions'])],negative_controls=negatives,source_sha256={str(q):oracle.sha(q)for q in [Path(__file__),Path(facts.__file__),Path(oracle.__file__),ROOT/'scripts/check_biwn_scheduler.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},scope='This27instruction fact packet matches original nativeCPU/full2MBRAM on1668stable fixtures and ordered accesses on1668stable+16changing-read fixtures. Four deliberate stack/partial-register/signed-branch/X errors rejected. Not proof of all instruction operands,unknown instructions,IRQ,faults,timing or arbitrary functions. No C target,model generation or weight training in this validator.');save()
  for q in [Path(__file__),Path(facts.__file__)]:shutil.copy2(q,out/q.name)
  print(state['status'],len(rows),traces,negatives,flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));save();raise
 finally:n.close()
if __name__=='__main__':main()
