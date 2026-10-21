"""Source E19E/E202+GPU projection/drawing on captured mode3 geometry.

Same device/RAM/GPU context between these two supplied source entries. Initial
captured geometry/RAM/GPU and matching reset device state are declared inputs;
not uninterrupted loading/geometry/drawing or natural gameplay.
"""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
import check_biwn_actor_full_movement_runtime as actor
ROOT=media.ROOT;CPU=media.CPU;save=media.save;sha=media.sha;SP=0x1fe000;STOP=0x190000

def main():
 before=json.loads((ROOT/'verification/selector13-loaded-scene-GPU-current.json').read_text());capture=Path(before['directory'])
 device_build=json.loads((ROOT/'verification/mode3-scene-render-device-build-current.json').read_text());device_path=Path(device_build['library']);assert sha(device_path.read_bytes())==device_build['library_sha256']
 out=ROOT/'verification/selector13-projection-draw'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';files=[source/n for n in ['biwn_gpu_projection_submit_cpu.c','biwn_gpu_draw_submit_cpu.c','biwn_render_queue_cpu.c','biwn_media_setup_cpu.c','biwn_scene_draw_cpu.c']]
 library=out/'libprojection-draw-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*map(str,files),'-o',str(library)]
 compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert not compiled.returncode,compiled.stderr
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);rows=[];groups={}
 for group,name in [('projection','gpu-projection-submit'),('draw','gpu-draw-submit'),('queue','render-queue'),('media','media-setup'),('clear','scene-draw')]:
  decoded=json.loads((session/(name+'-fullCPU-generation.json')).read_text())['instructions_decoded'];rows+=decoded;groups[group]={r['address']for r in decoded}
 runtime=media.Runtime(library,rows);runtime.device.close();runtime.device=actor.Device(device_path);runtime.oracle.device=runtime.device
 lib=runtime.device.lib;submit=lib.lab_scene_render_submit;submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];submit.restype=c.c_int
 renderer_mode=lib.lab_retained_renderer_mode;renderer_mode.argtypes=[c.c_uint];renderer_mode.restype=c.c_int
 stat=lib.lab_scene_render_stat;stat.argtypes=[c.c_uint];stat.restype=c.c_uint64
 pc_hash=lib.lab_scene_render_PC_hash;pc_hash.restype=c.c_uint64
 runtime.core.GPUStateLoad.argtypes=[c.c_void_p];runtime.core.GPUStateLoad.restype=c.c_size_t
 runtime.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];runtime.core.GPUReadLong.restype=c.c_uint32
 functions={}
 for group,name in [('projection','biwn_gpu_projection_submit_cpu'),('draw','biwn_gpu_draw_submit_cpu'),('queue','biwn_render_queue_cpu'),('clear','biwn_scene_draw_cpu')]:
  for suffix in ['body','call']:
   fn=getattr(runtime.lib,name+'_'+suffix);fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;functions[group,suffix]=fn
 results=[];coverage=set();rng=random.Random(0x1352e057a0)
 def gpu_bytes():
  raw=c.create_string_buffer(8192);size=runtime.savers['GPU'](raw);assert size>4396;return raw.raw[:size]
 def gpu_submit(value):
  status=submit(None,0xf03204,value)
  if status:save(out/'failed-command.json',dict(command=hex(value),status=status,GPU_header=hex(runtime.core.GPUReadLong(0xf03208,0)),GPU_raw_sha256=sha(gpu_bytes())))
  assert status==0,(hex(value),status)
  return dict(command=hex(value),GPU=sha(gpu_bytes()[:4396]),RAM=sha(runtime.device.ram()),PC_count=stat(9),PC_hash=hex(pc_hash()))
 try:
  for index,sample in enumerate(r for r in before['results']if not r['debug']):
   ram=(capture/f"asset-{sample['ordinal']}-C-geometry-RAM.bin").read_bytes();gpu=(capture/f"asset-{sample['ordinal']}-C-geometry-GPU.bin").read_bytes()
   initial=CPU();initial.registers[:15]=[rng.getrandbits(32)for _ in range(15)];initial.registers[15]=SP;initial.usp=SP;initial.ssp=0x1ff000;initial.sr=index%32
   pair={}
   for mode in ['native','C']:
    save(out/'status.json',dict(status='running',case=index,asset=sample['asset'],mode=mode));runtime.reset(ram,0);assert renderer_mode(int(mode=='C'))==0;assert runtime.core.GPUStateLoad(c.create_string_buffer(gpu))==len(gpu);lib.lab_scene_render_reset();events=[];cpu=CPU.from_buffer_copy(bytes(initial));stages=[];errors=[]
    def reader(width):
     def callback(_,a,v):v[0]=runtime.read(a,width);return 0
     return callback
    def writer(width):
     def callback(_,a,v):
      if a&0xffffff==0xf03204 and v in [0x52e0,0x57a0]:events.append(gpu_submit(v))
      else:runtime.write(a,width,v)
      return 0
     return callback
    world=media.scheduler.cleanup.world;callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),media.W8(writer(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
    def service(_,passed,state,target):
     if target==0xe098:return functions['queue','body'](passed,state,callbacks[5],service_cb,None,10000,0)
     errors.append(hex(target));return 1
    service_cb=media.world_cpu.SERVICE(service)
    for group,entry in [('clear',0xe03a),('projection',0xe19e),('draw',0xe202)]:
     runtime.device.direct(SP,4,STOP);cpu.registers[15]=SP;cpu.usp=SP;cpu.pc=entry
     if entry==0xe03a:
      # Actual source11EB6 caller clears BD83C with zero before preparing
      # geometry. Separate captured-RAM checks establish unchanged framebuffer
      # bytes across GPU4720 preparation; retain outputs and run source clear.
      runtime.device.direct(SP+4,4,runtime.device.read(0xbd83c,4));runtime.device.direct(SP+8,4,0)
     if mode=='native':
      runtime.seed_cpu(cpu)
      for step in range(10000):
       pc=runtime.cpu().pc
       if pc==STOP:break
       assert pc in groups[group]or pc in groups['queue'],hex(pc);coverage.add(pc);runtime.core.m68k_execute(1)
       value=runtime.core.GPUReadLong(0xf03204,0)
       if value in [0x52e0,0x57a0]:events.append(gpu_submit(value))
      else:raise AssertionError(('Native source driver worklimit',hex(pc)))
      cpu=runtime.cpu()
     else:
      status=functions[group,'call'](c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,10000,0);assert status==0 and not errors,(group,status,errors)
     assert cpu.pc==STOP and cpu.registers[15]==SP+4
     stages.append(dict(entry=hex(entry),CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),GPU=sha(gpu_bytes()[:4396]),events=list(events)))
    final=runtime.device.ram();(out/f'{index}-{mode}-final-RAM.bin').write_bytes(final)
    pair[mode]=dict(stages=stages,RAM_sha256=sha(final),events=events,statistics=[stat(i)for i in range(12)])
   if pair['native']['stages']!=pair['C']['stages']or pair['native']['RAM_sha256']!=pair['C']['RAM_sha256']:
    save(out/'mismatch.json',dict(case=index,sample=sample,pair=pair));raise AssertionError(str(out/'mismatch.json'))
   assert not pair['C']['statistics'][4]and not pair['C']['statistics'][8]
   results.append(dict(case=index,asset=sample['asset'],ordinal=sample['ordinal'],stages=pair['C']['stages'],C_statistics=pair['C']['statistics'],native_statistics=pair['native']['statistics'],initial_RAM_sha256=sha(ram),initial_GPU_capture_sha256=sha(gpu)))
  report=dict(status='selector13_captured_geometry_source_clear_projection_draw_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),assets=sorted({r['asset']for r in results}),GPU_commands=sum(len(r['stages'][-1]['events'])for r in results),C_resident_blits=sum(r['C_statistics'][11]for r in results),source_framebuffer_clear_executed=True,clear_parameters='E03A(BD83C,0),following original11EB6 argument values',results=results,source_sha256={str(p):sha(p.read_bytes())for p in files},device_build_proof=str(ROOT/'verification/mode3-scene-render-device-build-current.json'),device_library_sha256=sha(device_path.read_bytes()),geometry_capture_proof=str(ROOT/'verification/selector13-loaded-scene-GPU-current.json'),geometry_capture_sha256=sha((ROOT/'verification/selector13-loaded-scene-GPU-current.json').read_bytes()),original_CPU_GPU_on_C_path=False,whole_game_complete=False,default_promoted=False,native_Chat_verified=False,new_training=False,scope='Captured experimental selector13 source-loaded RAM and checked GPU4720 geometry continuation,with matching reset device/ROM/DSP inputs. Actual sourceE03A(BD83C,0),E19E/E202 andE098 plus sourceGPU52E0/57A0/consumer/material/resident/dispatcher retainGPU/RAM/devicecontext across three controlled sourcecalls. E03A follows original11EB6 argumentvalues; capturedgeometryGPU4720 had no framebufferwrites, but complete originalcaller/order is not executed. AllCPU/SR/USP/SSP/privateRAM,complete2MBRAM,GPU4396bytes and percommandPC/count/hash compare. No originalCPU/GPU on C path. Initial geometry/capturedGPU privatepipeline state andCPUcallerframes supplied; not uninterrupted loading/geometry/raster,natural gameplay,intendedmode3schema,physicalpixels/scanout/timing orwholegame.')
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/selector13-projection-draw-current.json',report);print(report['status'],len(results),'blits',report['C_resident_blits'],flush=True)
 except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
 finally:runtime.oracle.close()
if __name__=='__main__':main()
