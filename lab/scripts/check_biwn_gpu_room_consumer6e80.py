"""Compare source6E80 on saved full-scene entry and declared portal-bit variants."""
import ctypes as c,hashlib,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_gpu_interior as common
ROOT=common.ROOT;save=common.save;read=common.read;sha=common.sha
ENTRY=ROOT/'verification/biwn-interior-scene-cpu/20261014T041855.944627Z'
def main():
 out=ROOT/'verification/biwn-gpu-room-consumer6e80'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';libpath=out/'libroom-consumer6e80.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_gpu_room_consumer6e80.c'),'-o',str(libpath)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert not run.returncode,run.stderr
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-render-6e80-overlay/C-generation.json');decoded={x['address']:x for x in mapping['instructions_decoded']};lib=c.CDLL(str(libpath));fn=lib.biwn_gpu_room_consumer6e80_run;fn.argtypes=[c.POINTER(common.common.Bus),c.POINTER(common.common.State),c.c_uint32];fn.restype=c.c_int;corepath=ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib';device=common.common.frame.Device(corepath,ROOT/'render-assets',1);core=c.CDLL(str(corepath));core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUGetPC.restype=c.c_uint32;core.GPUExec.argtypes=[c.c_int32];core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(common.Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint];assert core.vjtrace_watch_add(0,0x1fffff,3)>=0
 base=(ENTRY/'failed-C-RAM.bin').read_bytes();incoming=(ENTRY/'failed-C-GPU-state.bin').read_bytes();scene=int.from_bytes(base[0x49c18:0x49c1c],'big');portals=int.from_bytes(base[scene+8:scene+12],'big');count=int.from_bytes(base[scene+2:scene+4],'big');coverage=set();rows=[];guards=[]
 def translated(memory,initial,**opts):
  mem=bytearray(memory);state=common.common.State.from_buffer_copy(bytes(initial));events=[];pcs=[];errors=[]
  def reader(width):
   def cb(_,a,value):
    physical=a&0xffffff
    if opts.get('fail')==('read',width):return 1
    if not 0<=physical<=len(mem)-width:errors.append(['read',hex(a),width]);return 1
    value[0]=int.from_bytes(mem[physical:physical+width],'big');events.append(['r',physical,width,value[0]]);return 0
   return cb
  def writer(width):
   def cb(_,a,value):
    physical=a&0xffffff
    if opts.get('fail')==('write',width):return 1
    if not 0<=physical<=len(mem)-width:errors.append(['write',hex(a),width]);return 1
    mem[physical:physical+width]=value.to_bytes(width,'big');events.append(['w',physical,width,value]);return 0
   return cb
  types=[common.common.R16,common.common.R32,common.common.W16,common.common.W32];callbacks=[types[0](reader(2)),types[1](reader(4)),types[2](writer(2)),types[3](writer(4)),common.common.TRACE(lambda _,pc:pcs.append(pc))]
  if 'missing'in opts:callbacks[opts['missing']]=types[opts['missing']]()
  if opts.get('bad_pc'):state.pc=0
  if opts.get('bad_flag'):state.z=2
  prior=bytes(state);bus=common.common.Bus(*callbacks,None);status=fn(None if opts.get('null_bus')else c.byref(bus),None if opts.get('null_state')else c.byref(state),opts.get('budget',200000))
  return bytes(mem),state,dict(status=status,state_unchanged=bytes(state)==prior,events=events,PC_samples=pcs,errors=errors)
 try:
  for i,bits in enumerate([None]+list(range(16))):
   save(out/'status.json',dict(status='running',case=i));memory=bytearray(base)
   if bits is not None:
    for j in range(count):
     a=portals+j*6+2;v=int.from_bytes(memory[a:a+2],'big');memory[a:a+2]=((v&~0x7800)|(bits<<11)).to_bytes(2,'big')
   device.seed(memory,0);buf=c.create_string_buffer(incoming);assert core.GPUStateLoad(buf)==len(incoming);before_raw,before_info=common.gpu_state(core);initial=common.from_raw(before_raw,before_info);begin=core.vjtrace_ring_head();core.vjtrace_arm();pcs=[]
   for _ in range(200000):
    pc=core.GPUGetPC()
    if pc==0xf03440:break
    assert pc in decoded,hex(pc);pcs.append(pc);core.GPUExec(1)
   core.vjtrace_disarm();end=core.vjtrace_ring_head();after=device.ram();after_raw,after_info=common.gpu_state(core);assert after_info['pc']==0xf03440;native=[]
   for seq in range(begin,end):
    event=common.Event();assert core.vjtrace_ring_read(seq,c.byref(event))
    if event.who!=3 or event.type not in [11,12]:continue
    op=int(decoded[event.pc-2]['bytes'][:4],16)>>10;width={40:2,41:4,46:2,47:4}[op];native.append(['r'if event.type==11 else'w',event.addr,width,event.value])
   right,actual,result=translated(memory,initial);diff=common.compare_state(actual,after_raw,after_info);shape=[e[:3]for e in native]==[e[:3]for e in result['events']];writes=[e for e in native if e[0]=='w']==[e for e in result['events']if e[0]=='w']
   if result['status']or right!=after or diff or pcs!=result['PC_samples']or not shape or not writes:
    save(out/'mismatch.json',dict(case=i,portal_bits=bits,state_diff=diff,C=result,native_PCs=pcs,native_events=native,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(right,after))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
   coverage.update(pcs)
   for pc in pcs:
    if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:coverage.add(pc+2)
   rows.append(dict(case=i,portal_bits=bits,direct_PC_samples=pcs,native_events=native,state=common.common.state_dict(actual),RAM_sha256=sha(right),all_state_RAM_PC_bus_match=True))
   if i==0:
    (out/'original-after-RAM.bin').write_bytes(after);(out/'C-after-RAM.bin').write_bytes(right);(out/'original-after-GPU-state.bin').write_bytes(after_raw)
    checks=[(dict(missing=n),1)for n in range(4)]+[(dict(null_bus=True),1),(dict(null_state=True),1),(dict(budget=0),1),(dict(bad_flag=True),1),(dict(bad_pc=True),3),(dict(budget=1),4)]+[(dict(fail=(kind,w)),2)for kind,w in [('read',2),('read',4),('write',2),('write',4)]]
    for opts,status in checks:
     _,_,guard=translated(memory,initial,**opts);assert guard['status']==status and guard['state_unchanged'],(opts,guard);guards.append(opts)
  missing=[decoded[pc]for pc in sorted(set(decoded)-coverage)];save(out/'coverage.json',dict(instructions=mapping['instructions_decoded'],uncovered=missing));save(out/'fixtures.json',rows);save(out/'guards.json',guards)
  report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fixed_C_room_consumer6E80_matches_original',directory=str(out),cases=len(rows),source_instruction_coverage=[len(coverage),222],uncovered_instructions=[hex(r['address'])for r in missing],guards=len(guards),source_sha256=mapping['source_sha256'],payload_sha256=mapping['payload_sha256'],generator_sha256=mapping['generator_sha256'],entry_snapshot_directory=str(ENTRY),original_GPU_instructions_on_C_side=0,new_published_components=0,full_game_complete=False,scope='Saved matchingfullsceneCprefixentry6E80onactualsource-loadedroom6 plus16declaredportalbits11..14variants retainingterminationbit15 andotherdata. Bothbanks/flags/matrix/divider/4KBlocalRAM/2MBmainRAM/directPCsequence/orderedexternalreadshape/writevalues match originalGPU. StopsatresidentF03440; resident/material/raster/fullscene not executed here. SoleGPUoracle/nohardwaretiming; hosterrorsleaveinputstateunchanged/priorRAMstoresretained.')
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification/biwn-gpu-room-consumer6e80-checks.json',report);print(json.dumps(report))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:core.vjtrace_disarm();device.close()
if __name__=='__main__':main()
