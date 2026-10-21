"""Four full CPU geometry interfaces against original functions and existing edge vectors."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_rng_cpu as prior
import check_biwn_geometry as legacy
ROOT=prior.ROOT;world=prior.world;SP=prior.SP;STOP=prior.STOP
RANGES=[(0x1028e,0x10430),(0x10652,0x106c4)]
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')

def bind(lib,full_call=False):
 fn=lib.biwn_geometry_cpu_call if full_call else lib.biwn_geometry_cpu_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(prior.CPU),c.c_uint32];fn.restype=c.c_int;return fn

def cases(snapshot):
 rng=random.Random(0x102c4);rows=[]
 for old in legacy.cases(snapshot):
  if old['entry']==0x10430:continue
  initial=list(old['initial'])+[[SP,4,STOP],[SP+4,4,old['params'][0]]]
  if len(old['params'])>1:initial.append([SP+8,2,old['params'][1]])
  rows.append({'entry':old['entry'],'registers':old['incoming']+[SP],'SR':rng.randrange(32)|((len(rows)%8)<<8),
               'initial':initial,'read_queues':old.get('read_queues',[]),'kind':old['kind']})
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opt=parser.parse_args();out=ROOT/'verification/biwn-geometry-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libgeometry-cpu.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_geometry_cpu.c'),'-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 fn=bind(c.CDLL(str(library)),full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases(snapshot)
 if opt.limit:vectors=sum([[x for x in vectors if x['entry']==entry][:opt.limit]for entry in [0x1028e,0x102c4,0x1039c,0x10652]],[])
 rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});left=prior.Memory(snapshot,case);right=prior.Memory(snapshot,case);expected,steps=prior.original(left,case,coverage,allowed_ranges=RANGES);status,actual,_=prior.translated(lambda bus,state:fn(bus,state,64),right,case)
   if status or expected!=actual or left.ram!=right.ram or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left.ram,right.ram))if a!=b][:50]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'full_CPU_flags_RTS_private_RAM_and_bus_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for start,end in RANGES:
  decoded,_=world.select.binary_tools.m68k_instructions(image[start-0x4000:end-0x4000],start);addresses.update(x['address']for x in decoded)
 assert addresses<=coverage,[hex(x)for x in sorted(addresses-coverage)]
 guards=[]
 for index in range(4):
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,vectors[0],missing=index);assert status==1 and same and not memory.trace;guards.append({'missing_callback':index})
 for kwargs in [{'null_bus':True},{'null_cpu':True}]:
  memory=prior.Memory(snapshot,vectors[0]);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,vectors[0],**kwargs);assert status==1 and same and not memory.trace;guards.append(kwargs)
 for case in [{**vectors[0],'entry':0},{**vectors[0],'SR':0x2000}]:
  memory=prior.Memory(snapshot,case);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,case);assert status==1 and same and not memory.trace;guards.append({'unsupported_entry_or_supervisor':True})
 selected=next(x for x in vectors if x['entry']==0x1039c and any(a==SP+8 and v==0 for a,w,v in x['initial'])and any(a==0x82000 and v>0 for a,w,v in x['initial']))
 for fail in [('read',2),('read',4),('write',2),('write',4)]:
  memory=prior.Memory(snapshot,selected);status,_,same=prior.translated(lambda b,s:fn(b,s,64),memory,selected,fail=fail);assert status==3 and same;guards.append({'bus_error':fail})
 scanning=next(x for x in vectors if x['entry']==0x102c4 and x['kind']=='scan_none'and any(a==0x82000 and v==5 for a,w,v in x['initial']))
 for limit,status_expected in [(0,1),(1,2)]:
  memory=prior.Memory(snapshot,scanning);status,_,same=prior.translated(lambda b,s:fn(b,s,limit),memory,scanning);assert status==status_expected and same;guards.append({'scan_limit':limit,'CPU_unchanged':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'four_geometry_full_CPU_interfaces_match_original','directory':str(out),
  'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],'host_guards':len(guards),'new_components':0,
  'entries':['0x1028e','0x102c4','0x1039c','0x10652'],'source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest()for name in ['biwn_geometry_cpu.c','biwn_geometry_cpu.h']},
  'matched':['All four complete functions including RTS match fullCPU/materializedSR/private stack frames, complete2MBRAM and ordered accesses.',
             'Existing raw/signed index, count, coordinate, extent and controlled-reread vectors now also check caller-saved registers and X/N/Z/V/C effects.'],
  'limits':['Already counted geometry functions gain full CPU/private-frame interfaces; no new component. No portal10430fullCPU interface, collision/game/hardware completion or concurrent timing claim.',
            'Host scan bounds/bus/argument errors retain RAM effects and unchanged CPU. No original exceptions or arbitrary code/stack aliases.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-geometry-cpu-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
