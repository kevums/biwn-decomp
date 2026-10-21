"""Full CPU direction13440 calls including actual signed division/private frames."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_rng_cpu as prior
ROOT=prior.ROOT;world=prior.world;SP=prior.SP;STOP=prior.STOP
RANGES=[(0x13440,0x134dc),(0xe588,0xe60a)]
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')

def bind(lib,full_call=False):
 fn=lib.biwn_actor_direction_call if full_call else lib.biwn_actor_direction_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(prior.CPU)];fn.restype=c.c_int;return fn

def cases():
 rng=random.Random(0x13440);rows=[];words=[0,1,2,0x7fff,0x8000,0xffff]
 for i in range(2048):
  x=words[i%6]if i<512 else rng.randrange(65536);z=words[(i//6)%6]if i<512 else rng.randrange(65536)
  registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=SP
  if i in[0,5]:registers[0]=0xaabbccdd
  initial=[[SP,4,STOP],[SP+4,2,x],[SP+6,2,z]]
  if i%5==1:initial += [[0x41f00+n*4,4,0x80000000]for n in range(64)]
  elif i%5==2:initial += [[0x41f00+n*4,4,0x7fffffff]for n in range(64)]
  elif i%5==3:initial += [[0x41f00+n*4,4,n*1024]for n in range(64)]
  elif i%5==4:initial += [[0x41f00+n*4,4,rng.getrandbits(32)]for n in range(64)]
  rows.append({'entry':0x13440,'registers':registers,'SR':rng.randrange(32)|((i%8)<<8),'initial':initial,'read_queues':[]})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opt=parser.parse_args();out=ROOT/'verification/biwn-actor-direction'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_actor_direction.c','biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c'];library=out/'libactor-direction.dylib'
 subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 fn=bind(c.CDLL(str(library)),full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();vectors=vectors[:opt.limit]if opt.limit else vectors;rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});left=prior.Memory(snapshot,case);right=prior.Memory(snapshot,case);expected,steps=prior.original(left,case,coverage,allowed_ranges=RANGES);status,actual,_=prior.translated(fn,right,case)
   if status or expected!=actual or left.ram!=right.ram or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left.ram,right.ram))if a!=b][:40]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'complete_CPU_RAM_flags_private_frames_RTS_and_bus_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(image[0x13440-0x4000:0x134dc-0x4000],0x13440);addresses={x['address']for x in decoded};unreachable={0x134be};assert addresses-unreachable<=coverage,[hex(x)for x in sorted(addresses-unreachable-coverage)]
 guards=[]
 for index in range(4):
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(fn,memory,vectors[0],missing=index);assert status==1 and same and not memory.trace;guards.append({'missing_callback':index})
 for kwargs in [{'null_bus':True},{'null_cpu':True}]:
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(fn,memory,vectors[0],**kwargs);assert status==1 and same and not memory.trace;guards.append(kwargs)
 for case in [{**vectors[0],'entry':0},{**vectors[0],'SR':0x2000}]:
  memory=prior.Memory(snapshot,case);status,_,same=prior.translated(fn,memory,case);assert status==1 and same and not memory.trace;guards.append({'unsupported_entry_or_supervisor':True})
 for fail in [('read',2),('read',4),('write',2),('write',4)]:
  case=vectors[6];memory=prior.Memory(snapshot,case);status,_,same=prior.translated(fn,memory,case,fail=fail);assert status==2 and same;guards.append({'bus_error':fail})
 case=vectors[6];memory=prior.Memory(snapshot,case);memory.queues={(SP-24,4):[0]};status,_,same=prior.translated(fn,memory,case);assert status==4 and same;guards.append({'corrupt_math_return':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'direction_full_CPU_private_frames_and_math_match_original','directory':str(out),
  'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'reachable_instruction_coverage':[len((addresses-unreachable)&coverage),len(addresses-unreachable)],
  'unreachable_instructions':['0x134be'],'unreachable_reason':'The four sign branches assign D3 only1..4; final tests exhaust those values before the default BRA.',
  'host_guards':len(guards),'new_components':0,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},
  'matched':['Full direction function including original signed division, CPU/SR/stack banks, private save/argument frames, completeRAM/ordered accesses andRTS match.',
             'Signed word extremes including8000, zeroZ upperD0 preservation, all quadrants, early/late/full64threshold scans and raw mutable threshold data covered.'],
  'limits':['Already counted13440 gains full CPU/private-frame interface; no new component. Threshold memory is supplied data. No movement/GPU/collision/actorstartup/fullgame/hardware completion implied.','Usermode only; host bus/argument/return failures retain RAM and callerCPU input; no original exceptions/interrupts/tracing/timing.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-actor-direction-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
