"""Readable170A0 against its actual inherited disc copy/matrix providers.

Both lanes load the same built stage/resident,including older native global
E3E0/E220/E098 redirects. Reference executes original170A0; target executes new
compiled body/capture assembly. Synchronous originalGPU4320 is a declared device
provider. This compares the new body against inherited restoration behavior,
not original helper equivalence,gameplay,arbitraryIRQ or console timing.
"""
import argparse,ctypes as c,os
from pathlib import Path
from datetime import datetime,timezone
import check_geometry_records_structured_native_v4 as native
host=native.host
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 bp=V/'native-input-arena-disc-build-v1-current.json';b=read(bp);gate=read(V/'scene17-input-arena-image-final-bridge-v1-current.json');CODE=b['shared_Deck_code_address'];ARENA=b['deck_arena_address'];base=b['resident_address'];resident=Path(b['component']).read_bytes();stage=Path(b['derived_stage']).read_bytes();syms=gate['symbols'];payload=Path(gate['payload']).read_bytes();assert resident[CODE-base:CODE-base+len(payload)]==payload
 out=V/'input-arena-image-disc-providers-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='checking',pid=os.getpid(),directory=str(out),completed=0,new_predictions=0,new_training=False,disc_changed=False)
 def mark():save(out/'protocol.json',state)
 mark();runtime=None
 try:
  for p,h in b['source_sha256'].items():assert sha(p)==h,p
  g=read(V/'geometry-record-strides-host-v1-current.json');session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'geometry-records-fullCPU-generation.json');resource=read(session/'resource-fullCPU-generation.json')
  runtime=host.Runtime(g['library'],mapping['instructions_decoded']+[x for x in resource['instructions_decoded']if 0xe3e0<=x['address']<0xe4aa]);core=runtime.core
  def symbol(name):
   matches=[v for k,v in syms.items()if k==name or k.startswith(name+'.lto_priv.')];assert len(matches)==1,(name,matches);return matches[0]
  entry=symbol('geometry_records_body');service=symbol('service_scene');memory_symbol=symbol('memory');helper_return=syms['biwn_v4_scene_helper_return'];capture_end=syms['biwn_v4_scene_capture_end'];transfers={syms[name]+delta for name in ['biwn_v4_capture_scene_record_copy','biwn_v4_capture_scene_record_matrix']for delta in [40,44,48]}
  snapshot=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());snapshot[0x4000:0x4000+len(stage)]=stage;snapshot[base:base+len(resident)]=resident
  original=bytes(snapshot[0x170a0:0x17326]);assert original==(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x170a0:0x17326]
  vectors=[dict(x,body=True)for x in host.cases()]
  if args.limit:vectors=[vectors[i]for i in [0,1,32,33,64,65,96,97,128,129,130,131,159,160,161,162,163,164,192,255,256,511][:args.limit]]
  rows=[]
  for i,case in enumerate(vectors):
   slot=ARENA+(i%101)*1024;ctx=slot+144;csp=slot+816-8;task=native.POOL+(i%101)*1024;initial=host.queue.make_cpu(case)
   memory=bytearray(host.fixture(snapshot,case));memory[ARENA:ARENA+101*1024]=bytes([0xa5])*(101*1024);memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
   memory[ctx:ctx+118]=memory_symbol.to_bytes(4,'big')+native.pack(initial)+service.to_bytes(4,'big')+ctx.to_bytes(4,'big')+(0xffffffff).to_bytes(4,'big')+bytes(4)+bytes(16)+(1).to_bytes(4,'big');memory[csp:csp+8]=host.STOP.to_bytes(4,'big')+ctx.to_bytes(4,'big');ram=bytes(memory)
   def execute(compiled):
    runtime.reset(ram,case,0);physical=host.queue.make_cpu(case)
    if compiled:
     physical.pc=entry;physical.registers[15]=csp;physical.sr=case['SR']&0xfff0
     if physical.sr&0x2000:physical.ssp=csp
     else:physical.usp=csp
    host.lifecycle.seed_cpu(runtime,physical);calls=[];pending=None;active=None;low=816;seen_records=0;provider_steps=0
    for steps in range(2000000):
     cpu=runtime.cpu();pc=cpu.pc;sp=cpu.registers[15]
     if pc==(host.STOP if compiled else 0x17324):break
     if pc in [0xe3e0,0xe220]:
      assert active is None
      ret=runtime.device.read(ctx+110,4)if compiled else runtime.device.read(sp,4)
      active=dict(target=pc,return_PC=ret,incoming=host.cd.scheduler.cpu_dict(cpu));calls.append(active)
     if active and pc==(helper_return if compiled else active['return_PC']):
      returned=host.CPU.from_buffer_copy(bytes(cpu));returned.pc=active['return_PC'];active['returned']=host.cd.scheduler.cpu_dict(returned);active=None
     if compiled and CODE<=pc<CODE+len(payload):
      if pc in transfers:assert sp==runtime.device.read(ctx+106,4)
      elif pc==helper_return:assert sp==runtime.device.read(ctx+106,4)+4
      elif pc==helper_return+6:assert sp==task
      elif helper_return+12<=pc<capture_end:
       displacement={12:0,16:0,20:64}.get(pc-helper_return,4);assert sp==ctx+displacement
      else:low=min(low,sp-slot);assert slot+608<=sp<=slot+816,('C stack',hex(pc),sp-slot)
     elif 0x170a0<=pc<0x17326:
      assert not compiled;seen_records+=1
     elif base<=pc<base+len(resident):provider_steps+=1
     else:assert pc in [0xe3e0,0xe220,0xe098],('Unexpected physical PC',hex(pc))
     core.m68k_execute(1)
     if core.GPUReadLong(0xf03204,0)==0x4320:runtime.device.write(0xf03204,0x4320)
    else:raise AssertionError('Inherited provider instruction bound')
    assert active is None
    actual=runtime.device.ram();logical=native.unpack(actual[ctx+4:ctx+82])if compiled else runtime.cpu()
    return actual,logical,calls,dict(instructions=steps,C_stack_bytes=816-low,original_record_instructions=seen_records,provider_instructions=provider_steps)
   left,expected,old_calls,old=execute(False);right,actual,new_calls,new=execute(True)
   def normal(raw):
    value=bytearray(raw)
    for lo,hi in [(ctx,ctx+118),(slot+608,slot+816)]:value[lo:hi]=ram[lo:hi]
    return bytes(value)
   error=int.from_bytes(right[ctx+94:ctx+98],'big')
   if error or bytes(expected)!=bytes(actual)or normal(left)!=normal(right)or old_calls!=new_calls:
    save(out/'counterexample.json',dict(case=case,error=error,expected_CPU=host.cd.scheduler.cpu_dict(expected),actual_CPU=host.cd.scheduler.cpu_dict(actual),RAM_differences=[hex(j)for j,(a,z)in enumerate(zip(normal(left),normal(right)))if a!=z][:64],reference_calls=old_calls,compiled_calls=new_calls,reference=old,native=new));raise AssertionError(out/'counterexample.json')
   assert new['original_record_instructions']==0 and old['original_record_instructions']>0
   rows.append(dict(case=case['id'],CPU_all_nonprivate_RAM_and_inherited_provider_entry_return_match=True,actual_inherited_provider_calls=len(new_calls),**new));state['completed']=len(rows);mark()
   if len(rows)%16==0:print('disc providers',len(rows),'/',len(vectors),flush=True)
  save(out/'cases.json',rows);state.update(status='terminal_disc_inherited_provider_preflight_pass'if args.limit else'terminal_readable_records_actual_inherited_providers_CPU_RAM_boundaries_pass',maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),actual_inherited_provider_calls=sum(x['actual_inherited_provider_calls']for x in rows),source_sha256={str(p):sha(p)for p in [Path(__file__),Path(native.__file__),Path(host.__file__),bp,V/'scene17-input-arena-image-final-bridge-v1-current.json',Path(b['component']),Path(b['derived_stage']),out/'cases.json']},scope=__doc__+' No bus-order proof in this fixture. All2MBRAM except supplied118byte context and208byteCstack compares,including inherited helper guest-stack bytes. Physical return-PC at capture seam alone is normalized to original guest continuation for CPU snapshot comparison. Both lanes execute the identical older provider machine code.');mark()
  if not args.limit:save(V/'input-arena-image-disc-providers-v1-current.json',state)
  print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:
  if runtime:runtime.close()
if __name__=='__main__':main()
