"""Actual17E0E mode2 scene caller: original CPU/GPU vs fixed C CPU/GPU.
Input RAM comes from original source loader captures; C loader remains unverified.
"""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_interior_cpu_gpu_chain as chain
ROOT=chain.ROOT;CPU=chain.CPU;save=chain.save;read=chain.read;sha=chain.sha;SP=chain.SP;STOP=chain.STOP
BODY_ENTRIES={0x17e0e:'scene_draw',0xe03a:'scene_draw',0x17f14:'scene_draw',0xe0f2:'gpu_interior_submit',0xe148:'gpu_interior_submit',0xe19e:'gpu_projection_submit',0xe202:'gpu_draw_submit',0xe098:'render_queue',0x170a0:'geometry_records',0xe220:'geometry_records',0xe3e0:'resource',0xe3ee:'resource',0x185b2:'display_list'}
class Runtime(chain.Runtime):
 def __init__(self,library,rows):
  super().__init__(library,rows);functions={}
  for target,name in BODY_ENTRIES.items():
   fn=getattr(self.lib,'biwn_'+name+'_cpu_body');fn.argtypes=self.wait_fn.argtypes;fn.restype=c.c_int;functions[target]=fn
  self.fn=lambda bus,state,*args:functions[c.cast(state,c.POINTER(CPU)).contents.pc](bus,state,*args)
  self.call=self.lib.biwn_scene_draw_cpu_call;self.call.argtypes=self.wait_fn.argtypes;self.call.restype=c.c_int;chain.wrappers.queue.ENTRIES=set(BODY_ENTRIES)
 def submit(self,command):
  try:return super().submit(command)
  except AssertionError:
   raw=c.create_string_buffer(8192);size=self.core.GPUStateSave(raw);(self.diagnostics/'failed-C-GPU-state.bin').write_bytes(raw.raw[:size]);(self.diagnostics/'failed-C-RAM.bin').write_bytes(self.device.ram());save(self.diagnostics/'failed-C-GPU-entry.json',dict(command=hex(command),pc=hex(self.core.GPUGetPC()),header=hex(self.core.GPUReadLong(0xf03208,0)),mailbox=hex(self.core.GPUReadLong(0xf03204,0))));raise
 def write(self,a,w,v):
  if a&0xffffff==0xf03204 and v in [0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:self.trace.append(['w',a,w,v]);self.submit(v);return
  if a&0xffffff==0xf03204 and v==0x4320:self.trace.append(['w',a,w,v]);self.device.write(a,v);return
  return super().write(a,w,v)
 def native(self,ram,case,coverage):
  self.reset(ram,case,0);chain.wrappers.queue.lifecycle.seed_cpu(self,chain.wrappers.queue.make_cpu(case));steps=[];stack=[];pending=None
  for _ in range(2000000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==STOP:break
   assert pc in self.rows,hex(pc);row=self.rows[pc]
   if pending==pc:
    call=dict(target=pc,actual_body=True,incoming=chain.wrappers.queue.cd.scheduler.cpu_dict(self.cpu()));self.calls.append(call);stack.append(call);pending=None
   if row['assembly']=='rts'and stack:stack.pop()['return']=chain.wrappers.queue.cd.scheduler.cpu_dict(self.cpu())
   if row['assembly'].startswith('jsr '):
    target=int(row['assembly'].split('$')[1].split('.')[0],16);assert target in BODY_ENTRIES,hex(target);pending=target
   coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
   command=self.core.GPUReadLong(0xf03204,0)
   if command in [0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:self.submit(command)
   elif command==0x4320:self.device.write(0xf03204,command)
  else:raise AssertionError(('Mode2 source scene worklimit',hex(pc)))
  assert not stack
  return self.device.ram(),self.cpu(),dict(steps=steps,calls=self.calls,device=self.stats())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--case',type=int);options=ap.parse_args();out=ROOT/'verification/biwn-interior-scene-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';previous=read(ROOT/'verification/biwn-disc-world-overlay-text-checks.json');command=previous['compiler'];names=[Path(v).name for v in command if v.endswith('.c')];names.append('biwn_gpu_interior_submit_cpu.c');library=out/'libinterior-scene-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
 for mapping in ['scene-draw-fullCPU-generation.json','gpu-interior-submit-fullCPU-generation.json','gpu-projection-submit-fullCPU-generation.json','gpu-draw-submit-fullCPU-generation.json','render-queue-fullCPU-generation.json','geometry-records-fullCPU-generation.json','resource-fullCPU-generation.json','display-list-fullCPU-generation.json']:
  manifest=read(session/mapping);rows+=manifest['instructions_decoded']
 runtime=Runtime(library,rows);runtime.diagnostics=out;capture=Path(read(ROOT/'verification/biwn-interior-original-loading-probes.json')['directory']);captures=read(capture/'cases.json');matrices=[[16384,0,0,0,16384,0,0,0,16384],[0,0,16384,0,16384,0,-16384,0,0],[-16384,0,0,0,16384,0,0,0,-16384],[0,0,-16384,0,16384,0,16384,0,0]];vectors=[(row,rotation)for row in captures for rotation in range(4)];vectors=(vectors[options.case:options.case+1]if options.case is not None else vectors[:options.limit or None]);results=[];coverage=set();rng=random.Random(0x17e0e2)
 try:
  for i,(row,rotation)in enumerate(vectors):
   save(out/'status.json',dict(status='running',case=i,interior=row['interior'],rotation=rotation));memory=bytearray(Path(row['after_RAM_path']).read_bytes());assert sha(memory)==row['after_RAM_sha256'];memory[SP:SP+4]=STOP.to_bytes(4,'big')
   for j,value in enumerate(matrices[rotation]+[0,0,0]):memory[0x47b88+j*2:0x47b8a+j*2]=(value&65535).to_bytes(2,'big')
   supervisor=i%2;case=dict(id=i,entry=0x17e0e,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if supervisor else 0)|rng.randrange(32),usp=0x170000 if supervisor else SP,ssp=SP if supervisor else 0x1d0000,body=False,render=False,outer_RTS=0x17f12,read_queues=[])
   runtime.first=True;left,expected,original=runtime.native(bytes(memory),case,coverage);original_events=list(runtime.events);(out/f'case-{i:02d}-original-final-RAM.bin').write_bytes(left);runtime.first=True;right,actual,rebuilt=runtime.translated(bytes(memory),case,budget=1000000);C_events=list(runtime.events)
   if rebuilt['status']or left!=right or bytes(expected)!=bytes(actual)or original['calls']!=rebuilt['calls']or original_events!=C_events:
    save(out/'mismatch.json',dict(case=case,interior=row['interior'],rotation=rotation,CPU_original=chain.wrappers.queue.cd.scheduler.cpu_dict(expected),CPU_C=chain.wrappers.queue.cd.scheduler.cpu_dict(actual),original=original,rebuilt=rebuilt,original_GPU_events=original_events,C_GPU_events=C_events,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:80]));raise AssertionError(str(out/'mismatch.json'))
   assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['scene_render'][8]and rebuilt['device']['interior_render'][0]==1 and rebuilt['device']['interior_render'][1]>0,rebuilt['device']
   if True:
    import animation_renderer
    pointer=int.from_bytes(right[0x43daa:0x43dae],'big');raw=right[pointer:pointer+224*180*2];assert len(raw)==80640;(out/f'case-{i:02d}-C-interior-geometry.raw16be').write_bytes(raw);(out/f'case-{i:02d}-C-interior-geometry.png').write_bytes(animation_renderer.image_png(raw,224,180,3));(out/f'case-{i:02d}-original-final-RAM.bin').write_bytes(left);(out/f'case-{i:02d}-C-final-RAM.bin').write_bytes(right)
   results.append(dict(case=i,interior=row['interior'],source_room=row['selected_room'],camera_rotation=rotation,input_RAM_sha256=sha(memory),CPU=chain.wrappers.queue.cd.scheduler.cpu_dict(actual),original_CPU_steps=len(original['steps']),helper_calls=rebuilt['calls'],GPU_submission_events=C_events,original_device=original['device'],C_device=rebuilt['device'],whole2MBRAM_allCPU_privateframes_helperstates_GPUstates_PCcount_hash_match=True));save(out/'fixtures.json',results)
  report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='source17E0E_mode2_fullCPU_C_GPU_scene_matches_original_on_original_loaded_inputs',directory=str(out),cases=len(results),interior_ids=sorted({r['interior']for r in results}),GPU_submissions=sum(len(r['GPU_submission_events'])for r in results),cases_with_resident_raster=sum(r['C_device']['scene_render'][11]>0 for r in results),source_wrappers_reached={hex(t):sum(sum(c['target']==t for c in r['helper_calls'])for r in results)for t in [0xe0f2,0xe148,0xe19e,0xe202]},C_dispatcher_calls=sum(r['C_device']['scene_render'][5]for r in results),C_resident_blits=sum(r['C_device']['scene_render'][11]for r in results),original_GPU_steps_on_C_side=0,original_CPU_loader_capture_directory=str(capture),C_loader_verified=False,source_CPU_scene_caller_executed=True,geometry_GPU_reset_fixture_retained=True,global_GPU_context_proved=False,full_game_complete=False,playable=False,new_published_components=0,compiler=command,source_sha256={n:sha((source/n).read_bytes())for n in names},device_library_sha256=sha((ROOT/'tools/libbiwn-interior-render-device.dylib').read_bytes()),test_script_sha256=sha(Path(__file__).read_bytes()),limits=['Source mode2 scene caller/clear/visibility-roomlist/perroomGPUgeometry/actorgeometry/projection/draw/rotation/displaylist execute with allCPU/main2MBRAM/privateframes/helperstates and eachGPUlogicalarchitecture/4KBRAM/directPCcount/hash compared. Source CCPU/GPU run under originalGPUguard; shared pinnedblitter remains.', 'Inputs are captured originalmode2loader results for actualinteriors1/2/3 with empty sourceactorlists, first/largestroomcamera entries and fourdeclaredidentity/axisrotations. SourceCloader, boundarytransition/cleanup, interior0twoactorrecords, scheduledworld/interactivemovement/audio/boot/globalGPUcontext/OPscanout/backendaccuracy/fullgame remain.', 'Per6AE0entryGPUreset/seed/fixedRAM/resident injection and synchronousGPUcompletion retained; subsequent6DA0/projection/draw/dispatcher state inherited within scene. Experimentalresident still has unexercised standalonepaths. No physicaltiming/FPS/gameplay claim.'])
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification/biwn-interior-scene-cpu-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['compiler','source_sha256']}))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:runtime.close()
if __name__=='__main__':main()
