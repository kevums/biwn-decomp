"""Qualify complete-root register, read-order and foreign-arena defect rejection."""
import json,subprocess,ctypes as c,hashlib
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_family_arena_engine_v1 as e
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 proof=read(e.ROOT/'verification/GPU-command-family-hybrid-current.json');assert proof['component_pass'] and proof['component_cases']==10048
 source=Path(proof['source']);assert e.sha(source)==proof['source_sha256'];text=source.read_text();signature='void biwn_native_gpu_mailbox_body(uint32_t *r)';assert text.count(signature)==1
 helper=text.replace(signature,'static void checked_original_body(uint32_t *r)');out=e.ROOT/'verification/GPU-family-checker-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();rows=[]
 mutations=dict(register='checked_original_body(r);r[0]^=1u;',read_order='(void)GMR32(0xf03204u);checked_original_body(r);',foreign_arena='checked_original_body(r);GMW32(0x168110u,0x12345678u);')
 try:
  for kind,body in mutations.items():
   folder=out/kind;folder.mkdir();candidate=folder/'defect.c';candidate.write_text(helper+'\n'+signature+'{'+body+'}\n');run=subprocess.run(['make','-f','Makefile.gpu-family-arena-v1','gpu-mailbox','BUILD='+str(folder/'build'),'MAILBOX_SOURCE='+str(candidate)],cwd=e.ND,capture_output=True,text=True,timeout=60);(folder/'compiler.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
   payload=(folder/'build/gpu-mailbox.bin').read_bytes();nm=subprocess.check_output([str(e.ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(folder/'build/gpu-mailbox.elf')],text=True);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
   for entry in e.ROOTS:
    case=next(x for x in e.arena_cases()if x['entry']==entry and x['slot']==0 and x['helper']=='original')
    original=e.execute(snapshot,case,payload,symbols,False)
    if kind=='register':
     bad=e.execute(snapshot,case,payload,symbols,True);assert original['trace']==bad['trace'] and original['ram']==bad['ram'] and original['mmio']==bad['mmio'];left=e.replay(native,snapshot,case,payload,symbols,False,original);right=e.replay(native,snapshot,case,payload,symbols,True,bad);changed=[i for i,(a,b)in enumerate(zip(left['registers'],right['registers']))if a!=b];assert changed==[0] and left['SR']==right['SR'];result=dict(kind=kind,entry=hex(entry),rejected=True,native_register_differences=changed,public_bus_and_RAM_unchanged=True)
    else:
     try:e.execute(snapshot,case,payload,symbols,True)
     except AssertionError as error:
      if kind=='foreign_arena':assert 'Writeoutsideownedarena' in str(error)
      result=dict(kind=kind,entry=hex(entry),rejected=True,reason=repr(error))
     else:raise AssertionError('Seeded defect accepted: '+kind+' '+hex(entry))
    rows.append(result)
 finally:native.close()
 assert len(rows)==24;save(out/'defect-results.json',rows);inputs=[Path(__file__),Path(e.__file__),source,Path(proof['component_receipt']),out/'defect-results.json',*[p for p in out.rglob('*')if p.is_file()]]
 state=dict(status='terminal_eight_roots_24_semantic_defects_rejected',directory=str(out),register_defects=8,read_order_defects=8,foreign_arena_defects=8,all_rejected=True,new_predictions=0,new_training=False,source_sha256={str(p):e.sha(p)for p in inputs},scope=__doc__+' Mutation controls qualify stated gates;not arbitrary correctness,IRQ,game or hardware proof.');save(out/'protocol.json',state);save(e.ROOT/'verification/GPU-family-checker-qualification-current.json',state);print(json.dumps({k:state[k]for k in ['status','directory','register_defects','read_order_defects','foreign_arena_defects']}))
if __name__=='__main__':main()
