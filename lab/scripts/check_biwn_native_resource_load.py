"""Full native loader ABI with controlled target CPU dependencies.
No actual CD/IRQ/concurrency/game or physical-console acceptance in this checker.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,random,subprocess
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as sched
from check_biwn_native_resource_release import REGS
from check_biwn_native_button_digit import ROOT,sha,save
BASE,PROVIDER,ENTRY,END,SP,STOP=0x148000,0x14c000,0x1b044,0x1b154,0x1e0000,0x1f0000
HELPERS={0xdf60:('yield',0),0xd206:('seek',2),0xd2f0:('start',3),0xd306:('stop',0),0xe3e0:('copy',3)}
def private(a,w):return SP-8192<=a and a+w<=SP-24

def normalize(ram,ref,length):
 b=bytearray(ram)
 for a,z in [(BASE,length),(ENTRY,8),(SP-8192,8192-24)]:b[a:a+z]=ref[a:a+z]
 return b

def seed(image,c):
 b=bytearray(image);b[0x134000:0x135000]=bytes(4096);b[0x1c0000:0x1c8400]=bytes(0x8400);b[0x120000:0x120800]=bytes([0xa9])*0x800
 for a,w,v in c['initial']:b[a:a+w]=v.to_bytes(w,'big')
 b[SP:SP+4]=STOP.to_bytes(4,'big')
 for i,v in enumerate(c['args']):b[SP+4+i*4:SP+8+i*4]=v.to_bytes(4,'big')
 return bytes(b)

def allowed(pc,length,plen,original):return pc in HELPERS or PROVIDER<=pc<PROVIDER+plen or (ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length)

def native(n,image,c,length,plen,original):
 n.device.seed(seed(image,c),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
 l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if c['sr']&0x2000 else 0x1fc000)
 l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000 if c['sr']&0x2000 else SP);l.m68k_set_reg(17,c['sr'])
 for i,v in enumerate(c['incoming']+[SP]):l.m68k_set_reg(i,v)
 l.m68k_set_reg(16,ENTRY);pcs=[];calls=[];minimum=SP;cycles=0
 for _ in range(2000000):
  pc=l.m68k_get_reg(None,16)
  if pc==STOP:break
  assert allowed(pc,length,plen,original),hex(pc)
  stack=l.m68k_get_reg(None,15);minimum=min(minimum,stack)
  if pc in HELPERS:
   name,argc=HELPERS[pc];calls.append(dict(helper=name,args=[n.device.read(stack+4+4*i,4)for i in range(argc)],registers=[l.m68k_get_reg(None,i)for i in range(16)],SR=l.m68k_get_reg(None,17)))
  pcs.append(pc);cycles+=l.m68k_execute(1)
 else:raise AssertionError('Loader did not return')
 cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17))
 cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
 assert cpu['registers'][15]==SP+4
 return n.device.ram(),cpu,pcs,calls,minimum,cycles

def trace(image,c,length,plen,original):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,c));u.reg_write(UC_M68K_REG_SR,c['sr'])
 for reg,v in zip(REGS,c['incoming']+[SP]):u.reg_write(reg,v)
 events=[]
 def code(e,a,w,_):
  assert allowed(a,length,plen,original),hex(a)
  if a in HELPERS:
   name,argc=HELPERS[a];sp=e.reg_read(UC_M68K_REG_A7);events.append([name,*[int.from_bytes(e.mem_read(sp+4+4*i,4),'big')for i in range(argc)]])
 def read(e,t,a,w,v,_):
  if not private(a,w):events.append(['read',a,w,int.from_bytes(e.mem_read(a,w),'big')])
 def write(e,t,a,w,v,_):
  if not private(a,w):events.append(['write',a,w,v&((1<<(8*w))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start(ENTRY,STOP,count=2000000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
 return bytes(u.mem_read(0,0x200000)),[u.reg_read(reg)for reg in REGS],events

def vectors():
 rng=random.Random(0x1b044);cases=[]
 kinds=['copy_ready','copy_no_ready','copy_zero','copy_one','copy_large','null_handle','busy_first','lock_first','both_busy','delayed_read','partial_marker','retry_absent','retry_cross_boundary','marker_end_boundary']
 for kind in kinds:
  # Long-scan retries need boundary/control coverage, not32identical CCR repetitions.
  ccrs=[0,16,31]if kind.startswith('retry_')else range(32)
  for mode in [0,0x2000]:
   for ccr in ccrs:
    tag=0x53524300+ccr;marker=0x1c0020;size={'copy_zero':0,'copy_one':1,'copy_large':513}.get(kind,37)
    if kind=='marker_end_boundary':marker=0x1c7fc0;size=4
    initial=[[0x47b80,2,int(kind in ['lock_first','both_busy'])],[0x47b82,2,int(kind in ['busy_first','both_busy'])],[0x118000,4,0x120000],[0x118004,2,0x1357],[0x134004,2,2],[0x134006,2,3 if kind in ['lock_first','both_busy']else 0],[0x134020,2,3 if kind=='delayed_read'else 1],[0x13403c,2,ccr],[0x134040,4,0xa5f01234^ccr],[0x134044,4,0x88776600+ccr],[0x134048,4,0x90919200+ccr],[0x13404c,4,0x10203000+ccr],[0x1126a0,4,0xcafebabe],[0xbd848,4,0xdeadbeef]]
    if kind=='retry_absent':initial += [[0x134010,4,marker],[0x134014,4,tag],[0x134018,4,2]]
    else:
     start=0x1c7fc4 if kind=='retry_cross_boundary'else marker
     initial += [[start+j*4,4,tag]for j in range(16)]
     if kind=='retry_cross_boundary':initial += [[0x134010,4,marker],[0x134014,4,tag],[0x134018,4,2]]
    if kind=='partial_marker':initial += [[0x1c0000+j*4,4,tag]for j in range(3)]
    initial += [[marker+64+j,1,rng.randrange(256)]for j in range(size)]
    args=[0x10203000+ccr,tag,0 if kind=='null_handle'else 0x118000,size,0 if kind=='copy_no_ready'else 0x118004]
    cases.append(dict(kind=kind,args=args,initial=initial,incoming=[rng.getrandbits(32)for _ in range(15)],sr=mode|ccr|((ccr%8)<<8),trace=ccr in [0,16,31]))
 return cases

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--limit',type=int);p.add_argument('--kind');p.add_argument('--label',default='native-resource-load');args=p.parse_args()
 nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';source=(args.source or nd/'resource-load-reference.c').resolve();out=ROOT/'verification'/args.label/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),coordinator_reference=source==nd/'resource-load-reference.c',limit=args.limit,kind_filter=args.kind,controlled_component_pass=False,source_accepted=False,real_CD_verified=False,game_frames=0,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(args.label+'-active.json'),state)
 mark()
 try:
  build=out/'build';r=subprocess.run(['make','-f','Makefile.resource-load','resource-load','BUILD='+str(build),'LOAD_SOURCE='+str(source)],cwd=nd,capture_output=True,text=True);(out/'make.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
  prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
  for stem in ['native-resource-load','load-providers']:
   for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
    t=line.split()
    if len(t)==3:symbols[t[2]]=int(t[0],16)
   (out/(stem+'.asm')).write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/(stem+'.elf'))],text=True))
  save(out/'symbols.json',symbols);binary=build/'native-resource-load.bin';payload=binary.read_bytes();providers=(build/'load-providers.bin').read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
  asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000','--start-address='+hex(ENTRY),'--stop-address='+hex(END),str(baseline)],text=True);(out/'original-loader.asm').write_text(asm)
  image=bytearray(baseline.read_bytes());image[PROVIDER:PROVIDER+len(providers)]=providers
  for addr,(name,argc)in HELPERS.items():image[addr:addr+8]=b'\x4e\xf9'+symbols['load_provider_'+name].to_bytes(4,'big')+b'\x4e\x71'
  candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_resource_load'].to_bytes(4,'big')+b'\x4e\x71'
  cases=vectors()
  if args.kind:cases=[c for c in cases if c['kind']==args.kind]
  if args.limit:cases=[next(c for c in cases if c['kind']==kind)for kind in dict.fromkeys(c['kind']for c in cases)][:args.limit]
  assert cases;save(out/'fixtures.json',cases);n=sched.Native();rows=[];coverage=set();trace_count=0
  try:
   for i,c in enumerate(cases):
    left=native(n,image,c,len(payload),len(providers),True);right=native(n,candidate,c,len(payload),len(providers),False);norm=normalize(right[0],left[0],len(payload))
    if left[1]!=right[1]or left[3]!=right[3]or norm!=left[0]:
     save(out/'mismatch.json',dict(case=i,parameters=c,original_CPU=left[1],compiled_CPU=right[1],original_calls=left[3],compiled_calls=right[3],RAM_differences=[dict(address=hex(j),original=x,compiled=y)for j,(x,y)in enumerate(zip(left[0],norm))if x!=y][:128]));raise AssertionError(str(out/'mismatch.json'))
    final_lock=int.from_bytes(right[0][0x47b80:0x47b82],'big');assert final_lock==(1 if c['kind']=='null_handle'else 0),(c['kind'],final_lock)
    ready_word=int.from_bytes(right[0][0x118004:0x118006],'big');assert ready_word==(0x1357 if c['kind']in ['null_handle','copy_no_ready']else 1),(c['kind'],ready_word)
    if c['trace']:
     ta=trace(image,c,len(payload),len(providers),True);tb=trace(candidate,c,len(payload),len(providers),False)
     if ta[1:]!=tb[1:]or normalize(tb[0],ta[0],len(payload))!=ta[0]:save(out/'trace-mismatch.json',dict(case=i,original=ta[1:],compiled=tb[1:]));raise AssertionError(str(out/'trace-mismatch.json'))
     trace_count+=1
    assert right[0][BASE:BASE+len(payload)]==payload and right[0][PROVIDER:PROVIDER+len(providers)]==providers
    coverage.update(left[2]);rows.append(dict(case=i,kind=c['kind'],sr=c['sr'],CPU=right[1],helper_calls=right[3],minimum_compiled_SP=right[4],original_cycles=left[5],compiled_cycles=right[5],ordered_trace_checked=c['trace'],full_CPU_public_RAM_and_helper_semantics_match=True))
    if i%32==0:state['completed']=len(rows);mark();print('Loader',len(rows),'/',len(cases),flush=True)
  finally:n.close()
  save(out/'results.json',rows)
  expected={int(line.split(':',1)[0].strip(),16)for line in asm.splitlines()if ':'in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()}
  if not args.limit and not args.kind:assert expected<=coverage,sorted(hex(x)for x in expected-coverage)
  state.update(status='terminal_controlled_loader_preflight_pass'if args.limit or args.kind else'terminal_controlled_loader_full_CPU_RAM_helper_and_ordered_access_pass',controlled_component_pass=not(args.limit or args.kind),native_cases=len(rows),trace_cases=trace_count,binary_bytes=len(payload),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),symbols=symbols,original_body_instruction_coverage=[len(expected&coverage),len(expected)],original_range_sha256=hashlib.sha256(baseline.read_bytes()[ENTRY:END]).hexdigest(),source_sha256={str(q):sha(q)for q in [Path(__file__),source,baseline,Path(sched.__file__),*[nd/k for k in ['resource-load-native.h','resource-load-shim.S','resource-load-providers.S','resource-load.ld','Makefile.resource-load','Makefile']]]},scope='Original272byte load versus compiled C, five declared target68000providers. FullD/A/PC/SR/USP/SSP/public2MBRAM/original24savebytes/helperentryD/A/SR/SP/argument lifetimes checked. Separate orderedUnicorn reads/writes in3CCRprofilespermode/path. Longscanretry matrix3CCRprofiles, otherpaths32. Private8KBstack belowpublicsavearea andcandidatecode excluded. No realCD/math/kernel/copy/interrupt/nested-acquire/disc/game/physical proof.')
  mark();save(ROOT/'verification'/(args.label+'-current.json'),state);print(state['status'],len(rows),trace_count,len(payload),state['original_body_instruction_coverage'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
