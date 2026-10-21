"""Original three-pass display list packing versus bounded callback C."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;RECORDS=0x120000;OUTPUT=0x150000
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));args=case['records'].to_bytes(4,'big')+case['output'].to_bytes(4,'big');cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,v in zip(world.REGS,case['incoming']):cpu.reg_write(reg,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(e,a,w,_):assert 0x185b2<=a<0x18854 and not 0x18690<=a<0x1869a,hex(a);coverage.add(a);steps.append(a)
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x185b2,STOP,count=50000,timeout=2000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if i not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
 assert bytes(cpu.mem_read(SP+4,8))==args
 ram=bytes(cpu.mem_read(0,0x200000));assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+16:]==script.memory[SP+16:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 fn=lib.biwn_display_list;fn.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def translated(fn,script,case,capacity=64,budget=4096,missing=None,null_workspace=False,null_output=False):
 def reader(w):
  def cb(_,a,v):
   try:v[0]=script.read(a,w);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def write(_,a,v):
  try:script.write(a,4,v);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R16(reader(2)),world.R32(reader(4)),world.W32(write)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(world.R8(),callbacks[0],callbacks[1],world.W16(),callbacks[2],world.CALL(),None,0);links=(c.c_uint32*64)();out=c.c_uint32(0xa55aa55a);status=fn(c.byref(bus),case['records'],case['output'],None if null_workspace else links,capacity,budget,None if null_output else c.byref(out));return status,out.value,list(links)
def cases(snapshot):
 rng=random.Random(0x185b2);rows=[]
 for i in range(1024):
  n=1 if i==0 else 2+i%23;types=[rng.choice([0,1,2,3,5,0xffff])for _ in range(n-1)]+[4]
  if i<8:types=[[4],[0,4],[1,4],[2,4],[3,4],[5,4],[0,1,2,3,4],[1,0,3,1,0,4]][i];n=len(types)
  case={'records':RECORDS,'output':OUTPUT+(i%4)*0x1000,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[],'default_helper_return':0,'read_queues':[]}
  for j,typ in enumerate(types):
   a=RECORDS+j*36
   for k in range(18):case['initial'].append([a+k*2,2,rng.randrange(65536)])
   case['initial'].append([a,2,typ]);case['initial'].append([a+6,4,rng.randrange(n)if typ==3 else rng.randrange(n+1)if typ in[0,1]else rng.getrandbits(32)])
   if typ in[0,1]and i%7==0:case['read_queues'].append({'address':a+6,'width':4,'values':[1,n]})
   if typ in[0,1]and i%11==0:case['read_queues'].append({'address':a+18,'width':2,'values':[0xffff,0x0001]})
  rows.append(case)
 # Preserved real descriptor list, with original output argument and literal
 # link origin deliberately distinct. All resources are frozen RAM bytes.
 rows.append({'records':0x43da0,'output':0x777c0,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[],'default_helper_return':0,'read_queues':[],'real_captured_descriptors':True})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-display-list'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libdisplay-list.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_display_list.c'),'-o',str(lib)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases(snapshot);vectors=vectors[:opts.limit]if opts.limit else vectors;rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=boundary.Script(snapshot,case);b=boundary.Script(snapshot,case);d0,steps=original(a,case,coverage);status,result,links=translated(fn,b,case)
   if status or d0!=result or a.memory!=b.memory or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'original_D0':d0,'C_D0':result,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   writes=[e for e in b.trace if e[0]=='w'];raw=b''.join(e[3].to_bytes(4,'big')for e in writes);rows.append({'case':i,'parameters':case,'original_CPU_instructions':steps,'full_D0':d0,'trace':b.trace,'output_longs':len(writes),'output_sha256':hashlib.sha256(raw).hexdigest(),'host_links':links,'whole_visible_RAM_and_bus_trace_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded=[]
 for lo,hi in [(0x185b2,0x18690),(0x1869a,0x18854)]:
  part,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);decoded+=part
 addresses={x['address']if isinstance(x['address'],int)else int(x['address'],16)for x in decoded};covered=addresses&coverage;missing=addresses-coverage
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(missing)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(missing)]}));return
 assert missing=={0x185ec,0x18642},[hex(a)for a in sorted(missing)]
 guards=[];case=vectors[1]
 for missing_callback in range(3):
  status,result,_=translated(fn,boundary.Script(snapshot,case),case,missing=missing_callback);assert status==1 and result==0xa55aa55a;guards.append({'missing_callback':missing_callback,'rejected':True})
 for kwargs in[{'capacity':0},{'budget':0},{'capacity':1},{'budget':1},{'null_workspace':True},{'null_output':True}]:
  status,result,_=translated(fn,boundary.Script(snapshot,case),case,**kwargs);assert status and result==0xa55aa55a;guards.append({'arguments':kwargs,'rejected':True})
 for kind in['read16','read32','write32','bad_bitmap_link','bad_branch_link','changed_jump_table']:
  script=boundary.Script(snapshot,case if kind!='bad_branch_link'else vectors[4])
  if kind=='read16':script.fail_read=(RECORDS,2)
  elif kind=='read32':script.fail_read=(RECORDS+6,4)
  elif kind=='write32':script.fail_write=(case['output'],4)
  elif kind=='bad_bitmap_link':script.put(RECORDS+6,4,0x40000000)
  elif kind=='bad_branch_link':script.put(RECORDS+6,4,64)
  else:script.put(0x18690,2,0xffff)
  status,result,_=translated(fn,script,case if kind!='bad_branch_link'else vectors[4]);assert status and result==0xa55aa55a;guards.append({'kind':kind,'rejected':True,'output_unchanged':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'display_list_three_pass_original_CPU_matches_C','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'reachable_instruction_coverage':[len(covered),len(addresses)-2],'unreachable_instructions':[hex(a)for a in sorted(missing)],'unreachable_reason':'Two alternate negative-literal MOVEs follow BGE tests of the fixed positive776F0 literal; no allowed input changes it.','host_guards':len(guards),'portable_components':1,'original_bytes':0x18854-0x185b2,'jump_table_bytes':10,'original_interval':'[0x185b2,0x18854)','source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_display_list.c','biwn_display_list.h']},'nested_helper_calls':0,'matched':['Whole visible RAM, every external read/write width/address/value/order including jump-table data reads, fullD0, callee saves and balanced stack/args.','Three passes, aligned host link table, output padding/type0/1bitmap/type2/type3branch/type4stop and unknown-type skipping; original type3 packing cursor does not advance.','Zero/one-based link references, source field/handle rereads, word/long wrapping/bitfields, output argument independent of fixed776F0link origin; captured real descriptor list matches.'],'limits':['Private stack and private link table excluded/replaced by bounded host workspace. Finite valid record lists/table indices; arbitrary private-stack references/aliases/concurrent mutation and fullCCR/caller-saved ABI exceptD0 excluded.','Descriptor/phrase generation only; no object processor execution, actual display scanout, whole viewport/game or physicalhardware validation. Added host capacity/work/link errors preserve earlier effects and leave fullD0 output unchanged.']};save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-display-list-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
