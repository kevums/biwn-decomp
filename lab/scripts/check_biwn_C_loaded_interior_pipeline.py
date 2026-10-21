"""C source loading and scene rendering retain one device/RAM context.
Host invokes1AA40/20F78/17E0E; originalCPU/GPU reference vs fixedC stages.
"""
import ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_interior_loading_cpu as loading
import check_biwn_interior_scene_cpu as scene
import check_biwn_actor_full_movement_runtime as actor
ROOT=loading.ROOT;CPU=loading.CPU;save=loading.save;read=loading.read;sha=loading.sha
class Runtime(loading.Runtime):
 def __init__(self,library,rows):
  super().__init__(library,rows);self.device.close();self.device=actor.Device(ROOT/'tools/libbiwn-interior-render-device.dylib');self.native_oracle.device=self.device;self.entry_points=[0x1aa40,0x20f78,0x17e0e];lib=self.device.lib
  for target,name in scene.BODY_ENTRIES.items():
   for table,suffix in [(self.bodies,'body'),(self.fullcalls,'call')]:
    fn=getattr(self.lib,'biwn_'+name+'_cpu_'+suffix);fn.argtypes=self.bodies[0x1aa40].argtypes;fn.restype=c.c_int;table[target]=fn
  lib.lab_scene_render_GPU_RAM.argtypes=[c.c_void_p,c.c_uint];lib.lab_scene_render_GPU_RAM.restype=c.c_int;fixture=(ROOT/'render-assets/biwn-geometry-GPU-RAM-fixture.bin').read_bytes();assert lib.lab_scene_render_GPU_RAM(c.create_string_buffer(fixture),4096)==0
  lib.lab_scene_render_submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];lib.lab_scene_render_submit.restype=c.c_int;lib.lab_scene_render_stat.argtypes=[c.c_uint];lib.lab_scene_render_stat.restype=c.c_uint64;lib.lab_scene_render_PC_hash.restype=c.c_uint64;lib.lab_interior_render_stat.argtypes=[c.c_uint];lib.lab_interior_render_stat.restype=c.c_uint64;self.core.GPUStateSave.argtypes=[c.c_void_p];self.core.GPUStateSave.restype=c.c_size_t
  old_write=self.device.write
  def write(a,value):
   if a&0xffffff==0xf03204 and value in [0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:return self.submit(value)
   return old_write(a,value)
  self.device.write=write
 def prepare(self,ram,mode):
  super().prepare(ram,mode);self.device.lib.lab_scene_render_reset();self.GPU_events=[]
 def submit(self,command):
  lib=self.device.lib;status=lib.lab_scene_render_submit(None,0xf03204,command)
  if status:
   save(self.output/'failed-GPU-command.json',dict(command=hex(command),status=status,header=hex(self.core.GPUReadLong(0xf03208,0))))
  assert not status,(hex(command),status)
  raw=c.create_string_buffer(8192);size=self.core.GPUStateSave(raw);assert size>4396;self.GPU_events.append(dict(command=hex(command),RAM_sha256=sha(self.device.ram()),GPU_architecture_and_RAM_sha256=sha(raw.raw[:4396]),direct_PC_count=lib.lab_scene_render_stat(9),direct_PC_hash=hex(lib.lab_scene_render_PC_hash())))
 def before_native_entry(self,entry,ram):
  if entry==0x17e0e:
   for address in [0x303c,0x3042]:self.device.direct(address,2,int.from_bytes(ram[address:address+2],'big'))
 def after_native_instruction(self,pc):
  command=self.core.GPUReadLong(0xf03204,0)
  if command in [0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:self.submit(command)
  elif command==0x4320:self.device.write(0xf03204,command)
 def statistics(self):
  row=self.device.stats();lib=self.device.lib;row['scene_render']=[lib.lab_scene_render_stat(i)for i in range(12)];row['interior_render']=[lib.lab_interior_render_stat(i)for i in range(4)];return row
 def initial_CPU(self,entry):
  state=super().initial_CPU(entry)
  if self.case_number%2:state.sr=0;state.ssp=0x1fa000
  return state
 def native(self,ram,coverage):
  memory,stages,result=super().native(ram,coverage);result.update(GPU_submission_events=list(self.GPU_events),device=self.statistics());return memory,stages,result
 def translated(self,ram):
  memory,stages,result=super().translated(ram);result.update(GPU_submission_events=list(self.GPU_events),device=self.statistics());return memory,stages,result
def main():
 out=ROOT/'verification/biwn-C-loaded-interior-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';previous=read(ROOT/'verification/biwn-interior-scene-cpu-checks.json');names=[Path(v).name for v in previous['compiler']if v.endswith('.c')];names.append('biwn_interior_loading_cpu.c');library=out/'libC-loaded-interior.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert not run.returncode,run.stderr
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'interior-loading-fullCPU-generation.json');rows=[]
 for filename in ['interior-loading-fullCPU-generation.json','cd-wrapper-fullCPU-generation.json','scene-draw-fullCPU-generation.json','gpu-interior-submit-fullCPU-generation.json','gpu-projection-submit-fullCPU-generation.json','gpu-draw-submit-fullCPU-generation.json','render-queue-fullCPU-generation.json','geometry-records-fullCPU-generation.json','resource-fullCPU-generation.json','display-list-fullCPU-generation.json']:rows+=read(session/filename)['instructions_decoded']
 runtime=Runtime(library,rows);runtime.output=out;capture=Path(read(ROOT/'verification/biwn-interior-original-loading-probes.json')['directory']);fixtures=read(capture/'cases.json');matrices=[[16384,0,0,0,16384,0,0,0,16384],[0,0,16384,0,16384,0,-16384,0,0],[-16384,0,0,0,16384,0,0,0,-16384],[0,0,-16384,0,16384,0,16384,0,0]];results=[];coverage=set()
 try:
  for fixture in fixtures:
   for rotation,matrix in enumerate(matrices):
    i=len(results);runtime.case_number=i;save(out/'status.json',dict(status='running',case=i));ram=bytearray((capture/f"interior-{fixture['interior']}-room-{fixture['selected_room']}-before-RAM.bin").read_bytes());assert sha(ram)==fixture['before_RAM_sha256']
    for j,value in enumerate(matrix+[0,0,0]):ram[0x47b88+j*2:0x47b8a+j*2]=(value&65535).to_bytes(2,'big')
    left,expected,native=runtime.native(bytes(ram),coverage);right,actual,rebuilt=runtime.translated(bytes(ram));keys=['calls','disc_requests','disc_completions','disc_stops','GPU_submission_events']
    if rebuilt['status']or left!=right or expected!=actual or any(native[k]!=rebuilt[k]for k in keys):
     (out/'original-final-RAM.bin').write_bytes(left);(out/'C-final-RAM.bin').write_bytes(right);save(out/'mismatch.json',dict(case=i,interior=fixture['interior'],room=fixture['selected_room'],rotation=rotation,native_stages=expected,C_stages=actual,native=native,C=rebuilt,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:80]));raise AssertionError(str(out/'mismatch.json'))
    stats=rebuilt['device'];assert not stats['original_GPUExec1_calls']and not stats['scene_render'][4]and not stats['scene_render'][8]and stats['interior_render'][0]==1 and stats['interior_render'][1]>0
    pointer=int.from_bytes(right[0x43daa:0x43dae],'big');assert pointer==int.from_bytes(right[0xbd844:0xbd848],'big');raw=right[pointer:pointer+80640]
    if i==5:
     import animation_renderer
     (out/'original-sample-final-RAM.bin').write_bytes(left);(out/'C-sample-final-RAM.bin').write_bytes(right);(out/'C-loaded-corridor.raw16be').write_bytes(raw);(out/'C-loaded-corridor.png').write_bytes(animation_renderer.image_png(raw,224,180,3))
    results.append(dict(case=i,interior=fixture['interior'],selected_room=fixture['selected_room'],camera_rotation=rotation,initial_SR=0 if i%2 else 0x2000,stage_states=actual,native_CPU_steps=len(native['steps']),helper_calls=rebuilt['calls'],disc_requests=rebuilt['disc_requests'],disc_completions=rebuilt['disc_completions'],disc_stops=rebuilt['disc_stops'],GPU_submission_events=rebuilt['GPU_submission_events'],C_statistics=stats,original_statistics=native['device'],geometry_plane_sha256=sha(raw),loader_to_renderer_without_device_RAM_reset=True,full_CPU_RAM_privateframes_helperstates_disc_GPU_states_PCcount_hash_match=True));save(out/'cases.json',results)
  decoded={r['address']for r in mapping['instructions_decoded']};covered=coverage&decoded;save(out/'loader-coverage.json',dict(instructions=mapping['instructions_decoded'],uncovered=[r for r in mapping['instructions_decoded']if r['address']not in covered]));report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='C_source_mode2_loading_texture_position_and_scene_on_retained_device_context_match_original',directory=str(out),cases=len(results),source_group_instruction_coverage=[len(covered),len(decoded)],source_interiors=[1,2,3],native_CPU_steps=sum(r['native_CPU_steps']for r in results),disc_transfers=sum(len(r['disc_requests'])for r in results),transferred_bytes=sum(sum(q['bytes']for q in r['disc_requests'])for r in results),GPU_submissions=sum(len(r['GPU_submission_events'])for r in results),cases_with_resident_raster=sum(r['C_statistics']['scene_render'][11]>0 for r in results),C_resident_blits=sum(r['C_statistics']['scene_render'][11]for r in results),C_room_consumer6E80_calls=sum(r['C_statistics']['interior_render'][3]for r in results),original_CPU_or_GPU_execution_on_C_side=False,loader_to_renderer_device_or_RAM_reset=False,C_loader_verified_for_declared_cases=True,original_loader_prefix_used_on_C_side=False,host_directly_invokes_three_source_entries=True,actual_boundary_transition_or_scheduler_loading_yields=False,source_mode1_fullCPU_loader_verified=False,interior0_actor_creation_verified=False,global_GPU_context_proved=False,geometry_GPU_reset_fixture_retained=True,original_CPU_reference_input_directory=str(capture),source_sha256={n:sha((source/n).read_bytes())for n in names},device_library_sha256=sha((ROOT/'tools/libbiwn-interior-render-device.dylib').read_bytes()),generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,new_published_components=0,whole_game_complete=False,playable=False,limits=['ActualC1AA40(mode2),20F78(mode2),texturecache/parser/indoorposition/copy/CDmath/wrappers then17E0Escene/clear/visibility/perroommesh/projection/draw/rotation/displaylist execute on sameRAM/device withoutresetbetweenloadingandrendering. AllthreeentryCPUstates/main2MBRAM/privateframes/helperstates anddisc/GPUevents matchoriginal; originalCPU/GPUexecuteonlyonreferenceside. Sharedpinnedblitter servescopyandraster.', 'Hostinvokes3sourceentrieswithsuppliedCPUregisters/stack between calls; noactualsourceboundarytransition/cleanup orschedulerloadingyield. BIOS303C/3042preserve-register RTSadapters andsynchronousDF60completion retained; assistedstartupbaseline anddeclaredroom/camera/matrixpositions. Per6AE0GPUreset/seed/fixedRAM/residentinjectionremains; nofullboot/globalGPU/timing/hardwareclaim.', 'Onlyactualinteriors1/2/3withsourceemptyactorlists; interior0twoactors/taskreuse unverified.807instructionCgroup containsunreachedoutdoor/otherbranches,partialcoverageexplicit. Otherworld/input/tasks/audio/OPscanout/rasterbackendaccuracy/fullgameunfinished; residentstill83unexercisedstandaloneinstructions.'])
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification/biwn-C-loaded-interior-pipeline-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['compiler','source_sha256']}))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:runtime.close()
if __name__=='__main__':main()
