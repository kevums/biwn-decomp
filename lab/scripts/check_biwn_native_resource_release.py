"""Native resource release plus actual source-built free dependency.
Full native CPU/publicRAM and separate ordered public accesses; no host free.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,random,subprocess
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as sched
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x140000;PROVIDER=0x15edc0;ENTRY=0x1b002;END=0x1b044;SP=0x1e0000;STOP=0x1f0000
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def private(a,w):return SP-8192<=a and a+w<=SP-12
def normalize(ram,ref,length,provider_length):
 b=bytearray(ram);b[BASE:BASE+length]=ref[BASE:BASE+length];b[PROVIDER:PROVIDER+provider_length]=ref[PROVIDER:PROVIDER+provider_length];b[SP-8192:SP-12]=ref[SP-8192:SP-12]
 for a,size in [(ENTRY,8),(0x1545c,8)]:b[a:a+size]=ref[a:a+size]
 return b
def seed(image,case):
 b=bytearray(image)
 for a,w,v in case['initial']:b[a:a+w]=v.to_bytes(w,'big')
 b[SP:SP+4]=STOP.to_bytes(4,'big');b[SP+4:SP+6]=case['id'].to_bytes(2,'big');return bytes(b)
def allowed(pc,length,provider_length,original):
 return(ENTRY<=pc<END or 0x1545c<=pc<0x1557a)if original else(BASE<=pc<BASE+length or PROVIDER<=pc<PROVIDER+provider_length or pc in [ENTRY,0x1545c])
def native(n,image,case,length,provider_length,original):
 n.device.seed(seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
 l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if case['sr']&0x2000 else 0x1fc000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000 if case['sr']&0x2000 else SP);l.m68k_set_reg(17,case['sr'])
 for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,ENTRY);pcs=[];calls=[];cycles=0
 for _ in range(200000):
  pc=l.m68k_get_reg(None,16)
  if pc==STOP:break
  assert allowed(pc,length,provider_length,original),hex(pc)
  if pc==0x1545c:calls.append(n.device.read(l.m68k_get_reg(None,15)+4,4))
  pcs.append(pc);cycles+=l.m68k_execute(1)
 else:raise AssertionError('Resource release did not return')
 cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17));cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17];assert cpu['registers'][15]==SP+4
 return n.device.ram(),cpu,pcs,calls,cycles
def trace(image,case,length,provider_length,original):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,case));u.reg_write(UC_M68K_REG_SR,case['sr'])
 for reg,v in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,v)
 events=[]
 def code(e,a,w,_):
  assert allowed(a,length,provider_length,original),hex(a)
  if a==0x1545c:events.append(['free',int.from_bytes(e.mem_read(e.reg_read(UC_M68K_REG_A7)+4,4),'big')])
 def read(e,t,a,w,v,_):
  if not private(a,w):events.append(['read',a,w,int.from_bytes(e.mem_read(a,w),'big')])
 def write(e,t,a,w,v,_):
  if not private(a,w):events.append(['write',a,w,v&((1<<(8*w))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,STOP,count=200000,timeout=3000000);assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4
 return bytes(u.mem_read(0,0x200000)),[u.reg_read(reg)for reg in REGS],events

def vectors():
 rng=random.Random(0x1b002);cases=[]
 layouts=['none','first_one','last_one','all_one','alternating','underflow','retained_refs','all_FFFF','null_handle','empty_handle','last_merge','sparse_reverse']
 for kind in layouts:
  for mode in [0,0x2000]:
   for ccr in range(32):
    id=0xffff if kind=='all_FFFF'else[0,1,0x7fff,0x8000,0xfffe][ccr%5];initial=[[0x112d60,4,0],[0x112d64,4,0]]
    for i in range(50):
     match={'none':False,'first_one':i==0,'last_one':i==49,'all_one':True,'alternating':i%2==0,'underflow':True,'retained_refs':True,'all_FFFF':True,'null_handle':i in [0,49],'empty_handle':i in [0,49],'last_merge':i in [48,49],'sparse_reverse':i%7==0 or i==49}[kind]
     count=0 if kind=='underflow'else([2,3,0x7fff,0x8000,0xffff][i%5]if kind=='retained_refs'else 1)
     handle=0 if kind=='null_handle'else 0x110000+i*4;block=0x170000+(49-i if kind=='sparse_reverse'else i)*64;entry=0x15b534+i*12
     initial += [[entry,2,id if match else(id+1)&65535],[entry+2,4,handle],[entry+6,2,count],[entry+8,4,rng.getrandbits(32)],[block,4,64],[block+4,4,handle],[block+8,4,0xdeadbeef]]
     if handle:initial.append([handle,4,0 if kind=='empty_handle'else block+8])
    cases.append(dict(kind=kind,id=id,initial=initial,incoming=[rng.getrandbits(32)for _ in range(15)],sr=mode|ccr|((ccr%8)<<8)))
 return cases

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--limit',type=int);p.add_argument('--bundle',action='store_true');args=p.parse_args();ap=ROOT/'verification/local-native-resource-release-current.json';a={}if args.source else json.loads(ap.read_text());source=args.source or Path(a['source']);assert args.source or sha(source)==a['source_sha256']
 global BASE
 if args.bundle:BASE=PROVIDER
 provider_path=ROOT/'verification/native-free-bundle-current.json';provider=json.loads(provider_path.read_text());assert provider['source_accepted']and provider['native_cases']==1411;provider_binary=Path(provider['compiled_binary']);assert sha(provider_binary)==provider['compiled_binary_sha256'];provider_payload=provider_binary.read_bytes()
 name='native-resource-release-bundle'if args.bundle else'native-resource-release';out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),raw_source_sha256=sha(source),limit=args.limit,source_accepted=False,game_frames=0)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
 mark()
 try:
  nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'build';p=subprocess.run(['make','-f','Makefile.resource-bundle'if args.bundle else'Makefile.resource-release','resource-bundle'if args.bundle else'resource-release','BUILD='+str(build),'RELEASE_SOURCE='+str(source)],cwd=nd,capture_output=True,text=True);(out/'make.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  stem='native-resource-bundle'if args.bundle else'native-resource-release';binary=build/(stem+'.bin');payload=binary.read_bytes();prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
  for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
   t=line.split()
   if len(t)==3:symbols[t[2]]=int(t[0],16)
  if args.bundle:provider_payload=payload;provider={**provider,'symbols':symbols}
  save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/(stem+'.elf'))],text=True))
  image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[PROVIDER:PROVIDER+len(provider_payload)]=provider_payload
  for address,key in [(ENTRY,'biwn_native_resource_release'),(0x1545c,'biwn_native_free')]:candidate[address:address+8]=b'\x4e\xf9'+(symbols if address==ENTRY else provider['symbols'])[key].to_bytes(4,'big')+b'\x4e\x71'
  cases=vectors()
  if args.limit:cases=[next(c for c in cases if c['kind']==kind)for kind in dict.fromkeys(c['kind']for c in cases)][:args.limit]
  save(out/'fixtures.json',cases);n=sched.Native();rows=[];traces=[];coverage=set()
  try:
   for i,case in enumerate(cases):
    left=native(n,image,case,len(payload),len(provider_payload),True);right=native(n,candidate,case,len(payload),len(provider_payload),False)
    if left[1]!=right[1]or left[3]!=right[3]or normalize(right[0],left[0],len(payload),len(provider_payload))!=left[0]:
     save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=left[1],compiled_CPU=right[1],original_calls=left[3],compiled_calls=right[3],RAM_differences=[hex(j)for j,(x,y)in enumerate(zip(left[0],normalize(right[0],left[0],len(payload),len(provider_payload))))if x!=y][:32]));raise AssertionError(str(out/'mismatch.json'))
    ta=trace(image,case,len(payload),len(provider_payload),True);tb=trace(candidate,case,len(payload),len(provider_payload),False)
    if ta[1:]!=tb[1:]or normalize(tb[0],ta[0],len(payload),len(provider_payload))!=ta[0]:save(out/'trace-mismatch.json',dict(case=i,original=ta[1:],compiled=tb[1:]));raise AssertionError(str(out/'trace-mismatch.json'))
    assert right[0][BASE:BASE+len(payload)]==payload and right[0][PROVIDER:PROVIDER+len(provider_payload)]==provider_payload
    coverage.update(left[2]);rows.append(dict(case=i,kind=case['kind'],CPU=right[1],free_arguments=right[3],compiled_free_C_calls=right[2].count(provider['symbols']['biwn_native_free_body']),full_CPU_public_RAM_and_calls_match=True));traces.append(dict(case=i,events=ta[2]))
    if i%64==0:state['completed']=len(rows);mark();print('Release',len(rows),'/',len(cases),flush=True)
  finally:n.close()
  save(out/'native-results.json',rows);save(out/'trace-results.json',traces);paths=[Path(__file__),ROOT/'scripts/check_biwn_scheduler.py',source,*[nd/k for k in ['resource-release-native.h','resource-release-shim.S','resource-release.ld','Makefile.resource-release','Makefile']]]
  if args.bundle:paths += [q for pattern in ['Makefile*','*.ld','*.S','*.c','*.h']for q in nd.glob(pattern)]
  state.update(status='terminal_resource_release_preflight_pass'if args.limit else'terminal_native_resource_release_full_CPU_RAM_and_ordered_access_pass',source_accepted=not args.limit,native_cases=len(rows),trace_cases=len(traces),binary_bytes=len(payload),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),symbols=symbols,original_instruction_coverage=sorted(coverage),free_C_entry_hits=sum(x['compiled_free_C_calls']for x in rows),source_sha256={str(p):sha(p)for p in paths},provider_proof=str(provider_path),provider_proof_sha256=sha(provider_path),execution_dependencies_sha256={str(p):sha(p)for p in [provider_binary,ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']},scope='Stable cache/heap fixtures cover50slot full scan, multiple matches, count underflow/retainedrefs, last-slot child clobbers, null/empty handles and coalescing in two CPU stack modes/all32CCR. Native fullD/A/PC/SR/USP/SSP/public2MBRAM including original12MOVEMsave bytes; separate Unicorn ordered public reads/writes/RTS and nested free arguments. Actual target-compiled free dependency, no host release/free effects. Child/private8KBstack below public saves and redirects/code excluded. No changing-read/IRQ/device concurrency/fault/arbitrary alias/livegame/physical-console or whole-game proof.')
  mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),len(payload),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
