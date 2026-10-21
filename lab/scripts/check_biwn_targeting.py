"""Complete target/cursor routine with real original and C math dependencies."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_camera as camera
world=camera.world;ROOT=world.ROOT;ENTRY=0x20820;END=0x20a9c
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
camera.RANGES[ENTRY]=END

def bind(lib):
 fn=lib.biwn_targeting_update;fn.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn

def translated(fn,helpers,division,script,case,missing=None):
 def reader(w):
  def cb(_,a,v):
   try:v[0]=script.read(a,w);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def write(_,a,v):
  try:script.write(a,2,v);return 0
  except Exception as error:script.errors.append(str(error));return 1
 def call(_,a,args,n,result):
  try:
   if script.fail_call==a:raise RuntimeError('injected dependency failure')
   values=list(args[:n]);script.trace.append(['call',a,values])
   if a==0xe540:result[0]=helpers[a](*values);return 0
   if a==0x13440:return helpers[a](c.byref(bus),*values,result[0],result)
   if a==0xe588:remainder=c.c_uint32();return division(*values,result,c.byref(remainder))
   raise AssertionError(hex(a))
  except Exception as error:script.errors.append(str(error));return 1
 types=[world.R8,world.R16,world.R32,world.W16,world.CALL];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](write),types[4](call)]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(*callbacks[:4],world.W32(),callbacks[4],None,0);out=c.c_uint32(0xa55aa55a);status=fn(c.byref(bus),case['incoming'][0],c.byref(out));return status,out.value

def cases(snapshot):
 rng=random.Random(0x20820);rows=[];words=[0,1,9,90,112,171,223,224,0x7fff,0x8000,0xffff];depths=[0,15,16,17,100,1024,1025,0x7fff,0x8000,0xffff];pairs=[(0,-10),(1,-32),(-1,-32),(10,-10),(-10,-10),(0,-181),(0,-182),(0x10000,-10),(0x80000000,-10),(0xffff,-1)]
 angles={}
 for dx,dz in pairs:
  q={'entry':0x13440,'params':[(0-dx)&0xffff,(0-dz)&0xffff],'incoming':[0]*len(world.REGS),'initial':[],'default_helper_return':0};angles[(dx,dz)]=camera.original(camera.Script(snapshot,q),q,set())[0]&255
 def make(kind):
  case={'entry':ENTRY,'params':[],'kind':kind,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':[[0x49c50,4,rng.getrandbits(32)],[0x49c56,4,rng.getrandbits(32)],[0x49d5c,2,rng.choice([0,1,0xffff])],[0x49d5e,2,0xa55a],[0x49d60,2,0xffff],[0x49d64,2,0xa55a],[0x49d66,2,0xa55a],[0x49d68,2,rng.choice(words)],[0x49d6a,2,rng.choice(words)]],'default_helper_return':0}
  for i in range(40):case['initial'] += [[0x49d6c+i*206,2,0],[0x49dd8+i*206,2,0]]
  return case
 def put_candidate(case,index,dx,dz,depth=100,active=1,state=1,frame_index=None,x=0,y=20):
  px=next(v for a,w,v in case['initial']if a==0x49c50);pz=next(v for a,w,v in case['initial']if a==0x49c56);record=0x49d6c+index*206;frame_index=index+4 if frame_index is None else frame_index;matrix=0x47b88+frame_index*64
  case['initial'] += [[record,2,active],[record+0x6c,2,state],[record+4,4,(px-dx)&0xffffffff],[record+10,4,(pz-dz)&0xffffffff],[record+0xc0,2,frame_index&0xffff],[matrix+0x16,2,depth&0xffff],[matrix+0x12,2,x&0xffff],[matrix+0x14,2,y&0xffff]]
 def range_table(case,slot,value):case['initial'] += [[0x49d5a,2,slot&0xffff],[0x4c280+slot*4,4,value]]
 for i in range(1024):
  kind=i%8;case=make(['no_candidate','filter','cone','tie','multiple','overflow','cursor','range'][kind]);dx,dz=pairs[(i//8)%len(pairs)];view=angles[(dx,dz)]
  case['initial'].append([0x49cba,1,(view+[-6,-5,0,5,6][(i//3)%5])&255]);slot=rng.choice([-1,0,1,4]);range_table(case,slot,rng.choice([0,1,100,101,0xfffff,0x7fffffff,0x80000000,0xffffffff]))
  if kind==1:put_candidate(case,i%40,dx,dz,depths[(i//8)%len(depths)],active=0 if i%3==0 else 1,state=0 if i%5==0 else 1)
  elif kind in[2,5,6,7]:
   put_candidate(case,i%40,dx,dz,depth=rng.choice([16,100,1024]),x=rng.choice([0,1,-1,20,128,-128,0x7fff,0x8000]),y=rng.choice([0,20,21,-20,128,0x7fff,0x8000]))
   if kind==6:case['initial'].append([0x49cba,1,view]);range_table(case,slot,0x7fffffff)
  elif kind==3:
   put_candidate(case,0,0,-10);put_candidate(case,39,0,-10);case['initial'].append([0x49cba,1,0]);range_table(case,slot,101)
  elif kind==4:
   for j in range(6):put_candidate(case,j,*pairs[j],depth=[16,100,1024][j%3],x=j*5,y=j*10)
   case['initial'].append([0x49cba,1,0]);range_table(case,slot,0x7fffffff)
  if i%97==0 and kind==6:case['read_queues']=[{'address':0x49d68,'width':2,'values':[223,1,0xffff,112]},{'address':0x49d6a,'width':2,'values':[171,9,0x8000,90]}]
  rows.append(case)
 case=make('checked_no_candidate');case['incoming'][0]=0xabcd1234;case['initial'].append([0x49cba,1,0]);range_table(case,0,0x7fffffff);rows.append(case)
 case=make('checked_signed_low_distance');put_candidate(case,0,0,-182);case['initial'] += [[0x49cba,1,0],[0x49d5c,2,1],[0x49d68,2,112],[0x49d6a,2,90]];range_table(case,0,0xfffff);rows.append(case)
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-targeting'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libtargeting.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_targeting.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 fn=bind(c.CDLL(str(library)));cp=json.loads((ROOT/'verification/biwn-camera-checks.json').read_text());helpers=camera.bind(c.CDLL(str(Path(cp['directory'])/'libcamera.dylib')));dp=json.loads((ROOT/'verification/biwn-signed-division-checks.json').read_text());division=c.CDLL(str(Path(dp['directory'])/'libdivision.dylib')).biwn_signed_division;division.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];division.restype=c.c_int
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA and snapshot[ENTRY:END]==image[ENTRY-0x4000:END-0x4000]
 vectors=cases(snapshot);vectors=vectors[:opts.limit]if opts.limit else vectors;coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});a=camera.Script(snapshot,case);b=camera.Script(snapshot,case);d0,steps=camera.original(a,case,coverage,instruction_limit=200000);status,result=translated(fn,helpers,division,b,case)
   if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory:
    save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':result,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'full_D0':d0,'original_CPU_instructions':steps,'trace':a.trace,'target_slot':int.from_bytes(a.memory[0x49d60:0x49d62],'big'),'distance_low_word':int.from_bytes(a.memory[0x49d64:0x49d66],'big'),'radius_word':int.from_bytes(a.memory[0x49d66:0x49d68],'big'),'whole_RAM_trace_stack_and_callee_save_match':True})
 except Exception as error:save(out/'error-case.json',case);save(out/'status.json',{'status':'terminal_failed','case':i,'error':repr(error)});raise
 save(out/'fixtures.json',rows);decoded,_=world.select.binary_tools.m68k_instructions(snapshot[ENTRY:END],ENTRY);missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing})
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'covered':len(decoded)-len(missing),'total':len(decoded),'directory':str(out)}));return
 assert not missing,[hex(x['address'])for x in missing]
 guards=[];dummy=world.Bus();output=c.c_uint32(0xa55aa55a);assert fn(None,0,c.byref(output))==1 and output.value==0xa55aa55a;assert fn(c.byref(dummy),0,None)==1;guards += [{'null_argument':kind,'status':1}for kind in['bus','output']]
 for index in range(5):
  case=vectors[0];script=camera.Script(snapshot,case);status,d0=translated(fn,helpers,division,script,case,missing=index);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'missing_callback':index,'status':1})
 for target in[0xe540,0x13440,0xe588]:
  case=next(row['parameters']for row in rows if any(t[:2]==['call',target]for t in row['trace']));script=camera.Script(snapshot,case);script.fail_call=target;status,d0=translated(fn,helpers,division,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'dependency_error':hex(target),'status':3})
 for action,width in[('r',1),('r',2),('r',4),('w',2)]:
  row=next(x for x in rows if any(t[0]==action and t[2]==width for t in x['trace']));event=next(t for t in row['trace']if t[0]==action and t[2]==width);case=row['parameters'];script=camera.Script(snapshot,case);setattr(script,'fail_read'if action=='r'else'fail_write',(event[1],width));status,d0=translated(fn,helpers,division,script,case);assert status==2 and d0==0xa55aa55a;guards.append({'bus_error':[action,event[1],width],'status':2})
 save(out/'guards.json',guards);examples=[{key:row[key]for key in['full_D0','target_slot','distance_low_word','radius_word']}|{'kind':row['parameters']['kind']}for row in rows if row['parameters']['kind'].startswith('checked_')];assert examples[0]['full_D0']==0xabcd1234 and examples[1]['distance_low_word']==33124 and examples[1]['radius_word']==255 and examples[1]['full_D0']==1;save(ROOT/'verification/targeting-checked-examples.json',examples)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'complete_targeting_update_matches_original_CPU','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'portable_components':1,'interval':'[0x20820,0x20a9c)','original_bytes':END-ENTRY,'stage_sha256':world.select.stage.STAGE_SHA,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in['biwn_targeting.c','biwn_targeting.h']},'compiler':command,'matched':['Complete original caller with real original/C direction,multiply andsigneddivision dependencies; fullD0,callee-saved registers,balanced stack andwholevisibleRAM.','Every external memory read/write width/address/value/order andnestedcalltarget/argumentorder. Candidateangle fixtures derive from originaldirection execution, not the reconstructed target algorithm.','40fixedrecords,stride206,depth16..1024,signedbyte angle-5..5,wrapped/signedweightedscore,firstties,weaponrange,wordprojection/cursorapproach andsignedlowdistance radius loop.'],'limits':['Analyst target/cursor label from behavior, not recovered originalsymbols. Candidate/transform producers, full actorAI/collision/gameplay andrenderedcrosshair/fullscene/game/hardware outside proof.','Finite synthetic records/matrices andcontrolledrereads; arbitraryaliases/concurrency,zero-divisor processor exceptions andfullCCR/caller-savedregisterABI excluded.','Added callbackerrors preserve earlierwrites andoutD0onfailure.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-targeting-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
