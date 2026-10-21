"""Original GPU vs fixed C on explicitly relocated preserved interior fixtures.
No source CPU loader/wrapper, native Chat, full renderer or completion claim.
"""
import argparse,ctypes as c,hashlib,json,os,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_gpu_geometry as common
from probe_biwn_gpu_projection import gpu_state
from biwn_disc_backend import Disc
ROOT=common.ROOT;save=common.save;read=common.read;sha=lambda b:hashlib.sha256(b).hexdigest()
class Event(c.Structure):
 _fields_=[('seq',c.c_uint64),('frame',c.c_uint32),('halfline',c.c_uint16),('type',c.c_uint8),('who',c.c_uint8),('pc',c.c_uint32),('addr',c.c_uint32),('value',c.c_uint32)]
def from_raw(raw,info):
 s=common.State();s.registers[0][:]=info['registers'][0];s.registers[1][:]=info['registers'][1]
 for k in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder']:setattr(s,k,info[k])
 s.local_RAM[:]=raw[:4096];return s
def compare_state(s,raw,info):
 d=common.state_dict(s)
 expected=dict(register_banks=info['registers'],pc=hex(info['pc']),flags=info['z']|(info['c']<<1)|(info['n']<<2),matrix_control=info['matrix_control'],matrix_pointer=info['matrix_pointer'],division_control=info['division_control'],remainder=info['remainder'],local_RAM_sha256=sha(raw[:4096]))
 return {k:dict(expected=v,actual=d[k])for k,v in expected.items()if v!=d[k]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-gpu-interior'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=ROOT/'projects/black-ice-white-noise/restoration';libs={};mappings={}
 for h in [0x6ae0,0x6da0]:
  libpath=out/f'libinterior-{h:x}.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/f'biwn_gpu_interior{h:x}.c'),'-o',str(libpath)]
  run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/f'compiler-{h:x}.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
  libs[h]=c.CDLL(str(libpath));libs[h].prepare=getattr(libs[h],f'biwn_gpu_interior{h:x}_prepare');libs[h].prepare.argtypes=[c.POINTER(common.State),c.c_uint32,c.c_uint32];libs[h].prepare.restype=c.c_int;libs[h].run=getattr(libs[h],f'biwn_gpu_interior{h:x}_run');libs[h].run.argtypes=[c.POINTER(common.Bus),c.POINTER(common.State),c.c_uint32];libs[h].run.restype=c.c_int;mappings[h]=read(session/f'gpu-render-{h:x}-overlay/C-generation.json')
 disc=Disc();payloads=[];provenance=[]
 for i in range(4):
  marker=disc.data.find((0x6000+i).to_bytes(4,'big')*16);assert marker==0x591c90+i*0x1260+674;payload=disc.data[marker+64:marker+64+0x1260];assert len(payload)==0x1260;payloads.append(payload);rooms=int.from_bytes(payload[:2],'big');assert int.from_bytes(payload[4:8],'big')==14 and int.from_bytes(payload[8:12],'big')==14+24*rooms
  provenance.append(dict(interior_id=i,tag=hex(0x6000+i),marker_offset=marker,payload_sha256=sha(payload),rooms=rooms,portals=int.from_bytes(payload[2:4],'big')))
 baseline=(ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z/startup-C-0.bin')
 if not baseline.exists():baseline=next((ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z').glob('startup-C-*.bin'))
 base=baseline.read_bytes();assert len(base)==0x200000 and sha(base)=='dcc373258c14b817df81eea5152e5923baabddbf87c42890c46ee662bf3475e4';corepath=ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib';device=common.frame.Device(corepath,ROOT/'render-assets',1,ROOT/'tools/libbiwn-geometry-probe.dylib');core=c.CDLL(str(corepath))
 core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUGetPC.restype=c.c_uint32;core.GPUExec.argtypes=[c.c_int32];core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int
 core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint];core.vjtrace_watch_add.restype=c.c_int;assert core.vjtrace_watch_add(0,0x1fffff,3)>=0
 fixtures=[]
 for i,payload in enumerate(payloads):
  rooms=provenance[i]['rooms'];offset=int.from_bytes(payload[4:8],'big')
  for sector in [0,rooms//2,rooms-1]:
   record=payload[offset+sector*24:offset+(sector+1)*24];x=int.from_bytes(record[2:4],'big')*64;z=int.from_bytes(record[4:6],'big')*64
   for camera in [[0,0,0],[x,0,z],[x+64,32,z-64]]:
    fixtures.append(dict(interior_id=i,sector=sector,camera=camera))
 if opts.limit:fixtures=fixtures[:opts.limit]
 coverage={h:set()for h in libs};rows=[];guard_results=[];initial_fixture=(ROOT/'render-assets/biwn-geometry-GPU-RAM-fixture.bin').read_bytes();assert len(initial_fixture)==4096 and sha(initial_fixture)=='a9cad7b6078216dd31fb681b741cec9fb53a87d0e32c96cea765bc4aa0c81c6f'
 def translated(h,before,initial,**opts):
  memory=bytearray(before);state=common.State.from_buffer_copy(bytes(initial));events=[];pcs=[];errors=[]
  def reader(width):
   def cb(_,a,value):
    physical=a&0xffffff
    if opts.get('fail')==('read',width):return 1
    if not 0<=physical<=len(memory)-width:errors.append(['read',hex(a),width]);return 1
    value[0]=int.from_bytes(memory[physical:physical+width],'big');events.append(['r',physical,width,value[0]]);return 0
   return cb
  def writer(width):
   def cb(_,a,value):
    physical=a&0xffffff
    if opts.get('fail')==('write',width):return 1
    if not 0<=physical<=len(memory)-width:errors.append(['write',hex(a),width]);return 1
    memory[physical:physical+width]=value.to_bytes(width,'big');events.append(['w',physical,width,value]);return 0
   return cb
  callbacks=[common.R16(reader(2)),common.R32(reader(4)),common.W16(writer(2)),common.W32(writer(4)),common.TRACE(lambda _,pc:pcs.append(pc))]
  if 'missing'in opts:callbacks[opts['missing']]=type(callbacks[opts['missing']])()
  if opts.get('bad_pc'):state.pc=0
  if opts.get('bad_flag'):state.z=2
  prior=bytes(state);bus=common.Bus(*callbacks,None);status=libs[h].run(None if opts.get('null_bus')else c.byref(bus),None if opts.get('null_state')else c.byref(state),opts.get('budget',200000))
  return bytes(memory),state,dict(status=status,state_unchanged=bytes(state)==prior,PC_samples=pcs,events=events,errors=errors)
 try:
  for h in libs:
   decoded={row['address']:row for row in mappings[h]['instructions_decoded']};payload=(session/f'gpu-render-{h:x}-overlay/original-overlay.bin').read_bytes()
   for i,fixture in enumerate(fixtures):
    save(out/'status.json',dict(status='running',header=hex(h),case=i));memory=bytearray(base);scene=0x15b7c0;interior=bytearray(payloads[fixture['interior_id']])
    for p in [4,8]:interior[p:p+4]=(scene+int.from_bytes(interior[p:p+4],'big')).to_bytes(4,'big')
    memory[scene:scene+len(interior)]=interior;memory[0x49c18:0x49c1c]=scene.to_bytes(4,'big');memory[0x49c1c:0x49c20]=fixture['sector'].to_bytes(4,'big')
    for a,value in zip([0x49b8c,0x49b8e,0x49b90],fixture['camera']):memory[a:a+2]=(value&65535).to_bytes(2,'big')
    for j,value in enumerate([16384,0,0,0,16384,0,0,0,16384,0,0,0]):memory[0x47b88+j*2:0x47b8a+j*2]=(value&65535).to_bytes(2,'big')
    device.seed(memory,0);initial_raw,info=gpu_state(core);raw=bytearray(initial_raw);raw[:4096]=initial_fixture;rng=random.Random(h+i);struct.pack_into('=64I',raw,4139,*[rng.getrandbits(32)for _ in range(64)]);raw[4136:4139]=bytes([(i>>n)&1 for n in range(3)]);raw[4395]=0;struct.pack_into('=I',raw,4096,0xf03240);struct.pack_into('=I',raw,4096+8*4,0x2801);struct.pack_into('=I',raw,4096+9*4,0)
    buf=c.create_string_buffer(bytes(raw));assert core.GPUStateLoad(buf)==len(raw);incoming_raw,incoming_info=gpu_state(core);state=from_raw(incoming_raw,incoming_info);assert libs[h].prepare(c.byref(state),scene,fixture['sector'])==0
    original_raw=bytearray(incoming_raw);original_raw[0x240:0x240+len(payload)]=payload;arg0,arg4=(0x47b88,0x10d688)if h==0x6ae0 else(0x47bc8,0x49b88)
    for a,v in [(0x204,h),(0x20c,arg0),(0x210,0x49b8c),(0x214,scene),(0x218,fixture['sector']),(0x21c,arg4)]:original_raw[a:a+4]=v.to_bytes(4,'big')
    buf=c.create_string_buffer(bytes(original_raw));assert core.GPUStateLoad(buf)==len(original_raw);before_raw,before_info=gpu_state(core);assert not compare_state(state,before_raw,before_info);before=device.ram();stem=f'{h:x}-case-{i:03d}'
    begin=core.vjtrace_ring_head();core.vjtrace_arm();pcs=[]
    for _ in range(200000):
     pc=core.GPUGetPC()
     if pc==0xf031be:break
     pcs.append(pc);core.GPUExec(1)
    core.vjtrace_disarm();end=core.vjtrace_ring_head();after=device.ram();after_raw,after_info=gpu_state(core)
    for suffix,data in [('before-RAM',before),('after-RAM',after),('before-GPU-state',before_raw),('after-GPU-state',after_raw)]: (out/f'{stem}-{suffix}.bin').write_bytes(data)
    assert after_info['pc']==0xf031be,(hex(h),i,'worklimit',hex(after_info['pc']))
    original_events=[]
    for seq in range(begin,end):
     event=Event();assert core.vjtrace_ring_read(seq,c.byref(event))
     if event.who!=3 or event.type not in [11,12]:continue
     pc=event.pc-2;op=int(decoded[pc]['bytes'][:4],16)>>10;width={40:2,41:4,46:2,47:4,54:2}[op];original_events.append(['r'if event.type==11 else'w',event.addr,width,event.value])
    right,actual,result=translated(h,before,state);diff=compare_state(actual,after_raw,after_info);shape=[e[:3]for e in original_events]==[e[:3]for e in result['events']];writes=[e for e in original_events if e[0]=='w']==[e for e in result['events']if e[0]=='w'];extras=['accumulator','hidata','data_organization','active_bank','flags_raw','control'];preserved=all(before_info[k]==after_info[k]for k in extras)
    if result['status']or right!=after or diff or pcs!=result['PC_samples']or not shape or not writes or not preserved:
     save(out/'mismatch.json',dict(header=hex(h),case=i,fixture=fixture,state_diff=diff,C=result,native_PCs=pcs,native_events=original_events,bus_shape=shape,writes=writes,preserved_extra_state=preserved,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(right,after))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
    coverage[h].update(pcs)
    for pc in pcs:
     if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:coverage[h].add(pc+2)
    rows.append(dict(header=hex(h),case=i,fixture=fixture,before_GPU=before_info,after_GPU=after_info,before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw),direct_PC_samples=pcs,C_instructions_including_delay=actual.instructions,events=original_events,full_state_RAM_PC_bus_match=True));save(out/'cases.json',rows)
    if i==0:
     checks=[(dict(missing=n),1)for n in range(4)]+[(dict(null_bus=True),1),(dict(null_state=True),1),(dict(budget=0),1),(dict(bad_flag=True),1),(dict(bad_pc=True),3),(dict(budget=1),4)]
     checks += [(dict(fail=(kind,width)),2)for kind,width in sorted({(e[0]=='r'and'read'or'write',e[2])for e in result['events']})]
     for options,expected in checks:
      _,_,guard=translated(h,before,state,**options);assert guard['status']==expected and guard['state_unchanged'],(h,options,guard);guard_results.append(dict(header=hex(h),options=options,status=expected))
     assert libs[h].prepare(None,scene,0)==1;bad=common.State();bad.z=2;assert libs[h].prepare(c.byref(bad),scene,0)==1;guard_results.extend([dict(header=hex(h),prepare_null=True),dict(header=hex(h),prepare_bad_flag=True)])
   save(out/'coverage.json',{hex(k):dict(covered=len(v),total=len(mappings[k]['instructions_decoded']),uncovered=[row for row in mappings[k]['instructions_decoded']if row['address']not in v])for k,v in coverage.items()})
  programs={hex(h):dict(cases=sum(row['header']==hex(h)for row in rows),source_instruction_coverage=[len(coverage[h]),len(mappings[h]['instructions_decoded'])],source_sha256=mappings[h]['source_sha256'],payload_sha256=mappings[h]['payload_sha256'])for h in libs}
  report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status=('standalone_preserved_interior_full_source_coverage_matches_original'if all(len(coverage[h])==mappings[h]['instructions']for h in libs)else'standalone_preserved_interior_partial_source_coverage_matches_original'),directory=str(out),cases=len(rows),programs=programs,guards=len(guard_results),fixture_provenance=provenance,baseline_path=str(baseline),baseline_sha256=sha(base),probe_script_sha256=sha(Path(__file__).read_bytes()),pinned_core_sha256=sha(corepath.read_bytes()),generator_sha256=mappings[0x6ae0]['generator_sha256'],shared_generator_sha256=mappings[0x6ae0]['shared_generator_sha256'],GPU_initial_RAM_sha256=sha(initial_fixture),source_CPU_mode2_loader_executed=False,source_CPU_E0F2_E148_linked=False,new_published_components=0,original_GPU_execution_on_C_side=0,whole_game_complete=False,scope='StandaloneGPUentries with preserved4704byte interior payloads and source two-pointer relocation; declared room sectors/identitycamera/translation/seeds/DIV0/fixedGPUinitialRAM. Texture-ID resolution/CPUscene loader/wrappers/dispatcher/liveinteriorscene are not run. Both banks/flags/matrix/divider/local4KBRAM/main2MBRAM/directPCsequence/orderedexternalreadshape/writevalues match original. Extra accumulator/hidata/dataorganization/activebank/rawflags/control preserved. OriginalGPU sole oracle; watchreadvalues placeholders; no timing/physicalhardware/raster/scanout/playablegame claim.')
  save(out/'guards.json',guard_results);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification/biwn-gpu-interior-checks.json',report);print(json.dumps(report))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:core.vjtrace_disarm();device.close()
if __name__=='__main__':main()
