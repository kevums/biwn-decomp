"""Original GPU versus source-specific material6860 C, from the live failure."""
import ctypes as c,json,os,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_gpu_materials as material
from probe_biwn_gpu_projection import gpu_state
ROOT=material.ROOT;save=material.save;sha=material.sha
source_session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
source=Path(json.loads((source_session/'gpu-render-6860-overlay/initial-linear-decode.json').read_text())['source_failure'])
if not source.is_absolute():source=ROOT/source
assert (source/'C-failure-GPU.json').exists()
session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);candidate=session/'gpu-material6860-candidate';mapping=json.loads((candidate/'material6860-generation.json').read_text());rows=mapping['instructions_decoded'];pcs={r['address']:r for r in rows}
out=ROOT/'verification/material6860-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
library=out/'libmaterial6860.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(candidate/'biwn_gpu_material6860.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
fn=c.CDLL(str(library)).biwn_gpu_material6860_run;fn.argtypes=[c.POINTER(material.Bus),c.POINTER(material.State),c.c_uint32];fn.restype=c.c_int
device=material.frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-material-probe.dylib');core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.GPUGetPC.restype=c.c_uint32
baseline=(source/'C-failure-RAM.bin').read_bytes();raw=(source/'C-failure-GPU.bin').read_bytes();regs=[int.from_bytes(raw[4139+i*4:4143+i*4],'little')for i in range(32)]
u=lambda a,w:int.from_bytes(baseline[a:a+w],'big');record=regs[24];polygon=u(record+34,2);model=u(record+60,4);descriptor=u(model+8,4)+polygon*20;texture=u(model+12,4)+(u(descriptor+4,2)&0xfff)*28
assert raw[0x240:0x360]==baseline[0x6868:0x6988]
vectors=[None]+[(flags,width,height,match)for flags in range(8)for width in [1,2,4,7,11]for height in [0,1,5,6,14,0xffff]for match in [False,True]]
results=[];coverage=set()
try:
 for index,vector in enumerate(vectors):
  ram=bytearray(baseline);initial_raw=bytearray(raw)
  if vector is not None:
   flags,width,height,match=vector;initial_raw[4136]=(flags>>2)&1;initial_raw[4137]=(flags>>1)&1;initial_raw[4138]=flags&1;ram[descriptor+16:descriptor+18]=width.to_bytes(2,'big');ram[texture+8:texture+10]=height.to_bytes(2,'big');ram[texture+12]=(polygon if match else polygon+1)&255;ram[texture+13]=7
  views={};RAMs={};GPUs={};controls={}
  for mode in ['native','C']:
   device.seed(bytes(ram),1);buf=c.create_string_buffer(bytes(initial_raw));assert core.GPUStateLoad(buf)==len(initial_raw);events=[];trace=[];errors=[]
   if mode=='native':
    for step in range(10000):
     pc=core.GPUGetPC()
     if pc==0xf03440:break
     assert pc in pcs,hex(pc);trace.append(pc);coverage.add(pc)
     if int(pcs[pc]['bytes'][:4],16)>>10 in [52,53]:coverage.add(pc+2)
     core.GPUExec(1)
    else:raise AssertionError('original material bound')
    state=None
   else:
    state=material.State();state.registers[0][:]=[int.from_bytes(initial_raw[4139+i*4:4143+i*4],'little')for i in range(32)];state.registers[1][:]=[int.from_bytes(initial_raw[4267+i*4:4271+i*4],'little')for i in range(32)];state.pc=0xf03240;state.z=initial_raw[4136];state.n=initial_raw[4137];state.c=initial_raw[4138]
    def reader(width):
     def call(_,address,value):
      try:value[0]=device.read(address&0xffffff,width);events.append(['r',address&0xffffff,width,value[0]]);return 0
      except Exception as e:errors.append(repr(e));return 1
     return call
    def writer(width):
     def call(_,address,value):
      try:
       address&=0xffffff
       if address<0x200000:device.direct(address,width,value)
       elif width==4 and 0xf03000<=address<=0xf03ffc:core.GPUWriteLong(address,value,0)
       else:raise AssertionError(('unsupported_write',hex(address),width))
       events.append(['w',address,width,value]);return 0
      except Exception as e:errors.append(repr(e));return 1
     return call
    callbacks=[material.R8(reader(1)),material.R16(reader(2)),material.R32(reader(4)),material.W16(writer(2)),material.W32(writer(4)),material.TRACE(lambda _,pc:trace.append(pc))];bus=material.Bus(*callbacks,None);status=fn(c.byref(bus),c.byref(state),100000);assert status==0 and not errors,(index,status,errors)
   after,hardware=gpu_state(core);GPUs[mode]=after;RAMs[mode]=device.ram();controls[mode]={k:hardware[k]for k in ['accumulator','remainder','hidata','matrix_control','matrix_pointer','division_control','data_organization','control','active_bank']}
   views[mode]=dict(registers=hardware['registers']if mode=='native'else[list(state.registers[i])for i in range(2)],pc=hardware['pc']if mode=='native'else state.pc,z=hardware['z']if mode=='native'else state.z,c=hardware['c']if mode=='native'else state.c,n=hardware['n']if mode=='native'else state.n,PC_order=trace)
  if views['native']!=views['C']or RAMs['native']!=RAMs['C']or GPUs['native'][:4096]!=GPUs['C'][:4096]:save(out/'mismatch.json',dict(case=index,vector=vector,views=views,RAM_equal=RAMs['native']==RAMs['C']));raise AssertionError(str(out/'mismatch.json'))
  # C state is owned outside the core; all other GPU controls must stay unchanged.
  assert controls['native']==controls['C'],controls
  results.append(dict(case=index,vector=vector,native_C_match=True,PC_count=len(views['native']['PC_order'])))
 report=dict(status='material6860_original_GPU_C_match',directory=str(out),source_failure=str(source),cases=len(results),instruction_coverage=[len(coverage),len(rows)],missing_instruction_addresses=[hex(pc)for pc in sorted(set(pcs)-coverage)],captured_live_entry_case=True,declared_descriptor_variants=True,all_registers_flags_PC_RAM_GPU_RAM_and_other_controls_match=True,exact_direct_PC_order=True,source_sha256=mapping['source_sha256'],coordinator_authored=True,local_model_case_bodies=False,whole_game_complete=False,limits=['Original pinned GPU is the oracle; supplied saved failure state plus declared width/height/byte/flag variants.','Stops at F03440 before resident raster. Full draw/task integration is separate. Native-only cycle/pipeline counters and cached raw flags word are not the compared logical architecture.'])
 save(out/'cases.json',results);save(out/'report.json',report);save(ROOT/'verification/material6860-check-current.json',report);print(report['status'],len(results),report['instruction_coverage'],flush=True)
finally:device.close()
