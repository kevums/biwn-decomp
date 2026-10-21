"""Both actor collision bodies with real geometry: full CPU/RAM/access proof."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_geometry_cpu as geometry
import check_biwn_rng_cpu as prior
ROOT=prior.ROOT;world=prior.world;SP=prior.SP;STOP=prior.STOP
RANGES=[(0x13b5a,0x13c9a)]+geometry.RANGES
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def bind(lib,full_call=False):
 fn=lib.biwn_actor_collision_call if full_call else lib.biwn_actor_collision_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(prior.CPU),c.c_uint32];fn.restype=c.c_int;return fn
def sx(v):return v if v<32768 else v-65536
def asr6(v):return((v>>6)|(0xfc00 if v&0x8000 else 0))&65535

def cases():
 rng=random.Random(0x13b5a);rows=[];obj=0x80000;record=0x81000;container=0x82000;scene=0x84000;tiles=0x100000;regions=0x110000
 for entry in [0x13b5a,0x13bb0]:
  for i in range(2048):
   regs=[rng.getrandbits(32)for _ in range(16)];regs[15]=SP;initial=[[SP,4,STOP],[SP+4,4,obj]];queues=[];kind=i%10
   x=0x2400;z=0x9800
   if kind==6:x=0x10000
   if kind==9:z=0x10000
   initial += [[obj+4,4,x],[obj+10,4,z],[obj+30,4,0xffff0000],[obj+26,4,0x10000],[obj+38,4,0xffff0000],[obj+34,4,0x10000],
               [obj+48,4,0x10000],[obj+52,4,0xffff0000],[obj+56,4,0x10000],[obj+60,4,0xffff0000],
               [obj+20,2,2],[obj+22,2,1 if kind==4 else 0],[0x49c18,4,scene],[scene,2,2],[scene+4,4,regions],[scene+8,4,tiles]]
   if entry==0x13b5a:
    edge=[0,1,2,0xfff,0x1000,0x7000,0xf000,0xffff][i%8];delta=[0,1,5,0xffff,0xfffb][(i//8)%5];room=[0,1,0xffff][i%3];changed=(room+delta)&65535;count=[0,1,2,0x8000][(i//40)%4]
    initial += [[SP+8,2,edge],[SP+10,2,rng.randrange(65536)],[SP+12,2,delta],[obj+64,2,room],[container,2,count],[container+8,4,tiles]]
    for indexroom in {room,changed}:initial.append([0x49bb4+sx(indexroom)*4,4,container])
    for index in set([0,1,(count-1)&65535]if count else[0]):
     address=tiles+sx(index)*20
     initial += [[address+10,2,0 if count==0x8000 or index==0 else 20],[address+14,2,0],[address+16,2,16],[address+18,2,16]]
    if edge==0xffff and count==0 and i%3==0:queues=[{'address':obj+64,'width':2,'values':[room,changed,0x1234]}]
   else:
    direction=[0,1,2,3,4,0xffff,0x8000,0x7fff][i%8];portal=[0,1,0x7fff,0x8000,0xffff][(i//8)%5];actualportal=1 if i%17==0 and portal!=0xffff else portal
    initial += [[SP+8,4,record],[SP+12,2,direction],[record+6,2,3],[record+8,2,16],[record+22,2,portal]]
    if actualportal!=portal:queues=[{'address':record+22,'width':2,'values':[portal,actualportal]}]
    xlow=x&65535;zlow=z&65535
    if direction==0:key=(asr6(xlow)+16)&65535
    elif direction==1:key=(asr6((-xlow)&65535)+35)&65535
    elif direction==2:key=(asr6((-zlow)&65535)+19)&65535
    elif direction==3:key=asr6(zlow)
    else:key=regs[1]&65535
    address=tiles+sx(actualportal)*6;flags=0 if kind==1 else 0x7000;target=3 if kind==3 else 0xffff if kind in[4,5,6,9]else 0
    for j in range(3):
     match=(kind not in[7,8]and j==0)or(kind==7 and j==1)
     initial += [[address+j*6,2,key if match else(key+1+j)&65535],[address+j*6+2,2,flags if match else 0x8000 if j==2 or(kind==8 and j==1)else 0],[address+j*6+4,2,target]]
    for j in range(2):
     for off in [2,4,6,8]:initial.append([regions+j*24+off,2,rng.choice([0,1,16,0x7fff,0x8000,0xffff])])
   rows.append({'entry':entry,'registers':regs,'SR':rng.randrange(32)|((i%8)<<8),'initial':initial,'read_queues':queues,'kind':kind})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opt=parser.parse_args();out=ROOT/'verification/biwn-actor-collision'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_actor_collision.c','biwn_geometry_cpu.c'];library=out/'libactor-collision.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 fn=bind(c.CDLL(str(library)),full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opt.limit:vectors=sum([[x for x in vectors if x['entry']==entry][:opt.limit]for entry in[0x13b5a,0x13bb0]],[])
 rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});left=prior.Memory(snapshot,case);right=prior.Memory(snapshot,case);expected,steps=prior.original(left,case,coverage,allowed_ranges=RANGES);status,actual,_=prior.translated(lambda b,s:fn(b,s,64),right,case)
   if status or expected!=actual or left.ram!=right.ram or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left.ram,right.ram))if a!=b][:50]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'full_CPU_flags_RTS_private_RAM_and_bus_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(image[0x13b5a-0x4000:0x13c9a-0x4000],0x13b5a);addresses={x['address']for x in decoded};assert addresses<=coverage,[hex(x)for x in sorted(addresses-coverage)];assert {0x1028e,0x102c4,0x1039c,0x10652}<=coverage
 guards=[]
 for index in range(4):
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,vectors[0],missing=index);assert status==1 and same and not memory.trace;guards.append({'missing_callback':index})
 for kwargs in [{'null_bus':True},{'null_cpu':True}]:
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,vectors[0],**kwargs);assert status==1 and same and not memory.trace;guards.append(kwargs)
 for case in [{**vectors[0],'entry':0},{**vectors[0],'SR':0x2000}]:
  memory=prior.Memory(snapshot,case);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,case);assert status==1 and same and not memory.trace;guards.append({'unsupported_entry_or_supervisor':True})
 for fail in [('read',2),('read',4),('write',2),('write',4)]:
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,vectors[0],fail=fail);assert status==3 and same;guards.append({'bus_error':fail})
 scan=next(x for x in vectors if x['entry']==0x13bb0 and x['kind']==7 and any(a==0x81000+22 and v!=0xffff for a,w,v in x['initial']))
 for limit,status_expected in [(0,1),(1,2)]:
  memory=prior.Memory(snapshot,scan);status,_,same=prior.translated(lambda b,s:fn(b,s,limit),memory,scan);assert status==status_expected and same;guards.append({'scan_limit':limit,'CPU_unchanged':True})
 case=vectors[0];memory=prior.Memory(snapshot,case);memory.queues={(SP-18,4):[0]};status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,case);assert status==4 and same;guards.append({'corrupt_geometry_return':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'two_actor_collision_bodies_with_real_geometry_match_original_CPU','directory':str(out),
  'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'host_guards':len(guards),'new_components':2,'nested_helper_scripts':0,
  'geometry_entries_reached':['0x1028e','0x102c4','0x1039c','0x10652'],'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},
  'matched':['Both complete collision bodies with actual geometry/RTS match allCPU/SR/private frames, full2MBRAM and ordered bus accesses.',
             'Raw edges and directions, room change/rollback/rereads, indoor first/later/no match and signed sentinels, actual region selection/outside predicate, mode transition and partial D0 returns covered.'],
  'limits':['Geometry and scene structures are bounded input fixtures. This is not yet a full actor/world/render integration or physical collision validation.',
            'Host scan/bus/argument/return errors retain RAM effects and unchanged CPU. No original exceptions, arbitrary code/stack aliases, interrupts/tracing/timing.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-actor-collision-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
