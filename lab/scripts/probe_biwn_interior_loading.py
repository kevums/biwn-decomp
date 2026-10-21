"""Capture original source mode2 loading on preserved disc bytes.
Direct declared mode2 entry; BIOS transfer/DF60 completion are synchronous adapters.
No reconstructed C loader or actual outdoor-to-indoor transition claim.
"""
import ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_interior_cpu_gpu_chain as chain
from biwn_disc_backend import Disc
ROOT=chain.ROOT;save=chain.save;read=chain.read;sha=chain.sha;SP=chain.SP;STOP=chain.STOP
RANGES=[(0x1aa40,0x1aade),(0x20f78,0x21242),(0x20cf8,0x20e40),(0x20aa0,0x20b2a),(0x1ac3c,0x1ae56),(0x10520,0x10652),(0x1b044,0x1b154),(0xe3e0,0xe4aa),(0xd1e0,0xd2a0),(0xd2f0,0xd30a)]
LOGGED={0x1aa40,0x20f78,0x20cf8,0x20d7c,0x1ac68,0x1ac3c,0x10520,0x20aa0,0x1b044,0xe3e0,0xd206,0xd2f0,0xd306}
def main():
 out=ROOT/'verification/biwn-interior-original-loading'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-interior-submit-fullCPU-generation.json');baseline=(ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z/startup-C-0.bin').read_bytes();prior=read(ROOT/'verification/biwn-gpu-interior-submit-cpu-checks.json');wait,_=chain.wrappers.queue.cd.gen.base.binary_tools.m68k_instructions(baseline[0xe098:0xe0a6],0xe098);runtime=chain.Runtime(Path(prior['directory'])/'libinterior-submit-cpu.dylib',mapping['instructions_decoded']+wait);disc=Disc();rows=[]
 try:
  for interior,position in [(i,p)for i in [1,2,3]for p in [0,1]]:
   save(out/'status.json',dict(status='running',interior=interior));ram=bytearray(baseline);marker=disc.data.find((0x6000+interior).to_bytes(4,'big')*16);payload=disc.data[marker+64:marker+64+0x1260];count=int.from_bytes(payload[:2],'big');selected=0 if position==0 else max(range(count),key=lambda j:int.from_bytes(payload[20+j*24:22+j*24],'big')*int.from_bytes(payload[22+j*24:24+j*24],'big'));room=payload[14+selected*24:38+selected*24];x=int.from_bytes(room[2:4],'big')*64+(32 if position==0 else int.from_bytes(room[6:8],'big')*32);z=int.from_bytes(room[4:6],'big')*64+(32 if position==0 else int.from_bytes(room[8:10],'big')*32)
   def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
   for a,w,v in [(0x49c64,2,interior),(0x49c50,4,x),(0x49c54,2,32 if position==0 else 64),(0x49c56,4,z),(0x49c6a,4,0),(0x49c72,4,0),(SP,4,STOP),(SP+4,2,2)]:put(a,w,v)
   runtime.device.seed(ram,0);disc.reset();before=runtime.device.ram();calls=[];steps=[]
   for target in [0x303c,0x3042]:runtime.device.direct(target,2,0x4e75)
   stage_states=[]
   for entry in [0x1aa40,0x20f78]:
    cpu=chain.CPU();cpu.registers[:]=[0]*15+[SP];cpu.pc=entry;cpu.usp=SP;cpu.ssp=SP;cpu.sr=0x2000;chain.wrappers.queue.lifecycle.seed_cpu(runtime,cpu)
    for _ in range(1000000):
     pc=runtime.core.m68k_get_reg(None,16)
     if pc==STOP:break
     assert any(a<=pc<b for a,b in RANGES)or pc in [0x303c,0x3042,0xdf60],hex(pc);steps.append(pc)
     if pc in LOGGED:calls.append(dict(target=hex(pc),SP=hex(runtime.core.m68k_get_reg(None,15)),D0=runtime.core.m68k_get_reg(None,0)))
     if pc==0x303c:disc.start(runtime.core.m68k_get_reg(None,8),runtime.core.m68k_get_reg(None,9),runtime.core.m68k_get_reg(None,0))
     elif pc==0x3042:disc.stop()
     elif pc==0xdf60:
      assert disc.pending,'Original loader yielded without pending disc read';disc.tick(lambda a,b:c.memmove(runtime.device.pointer+a,b,len(b)),lambda a,v:runtime.device.direct(a,4,v));stack=runtime.core.m68k_get_reg(None,15);runtime.core.m68k_set_reg(16,runtime.device.read(stack,4));runtime.core.m68k_set_reg(15,stack+4);continue
     runtime.core.m68k_execute(1)
    else:raise AssertionError(('Mode2 original loader worklimit',interior,hex(pc),calls[-8:]))
    stage_states.append(dict(entry=hex(entry),CPU=chain.wrappers.queue.cd.scheduler.cpu_dict(runtime.cpu())))
   for target in [0x303c,0x3042]:runtime.device.direct(target,2,int.from_bytes(baseline[target:target+2],'big'))
   after=runtime.device.ram();get=lambda a,w=4:int.from_bytes(after[a:a+w],'big');assert get(0x49c60,2)==2 and get(0x49c76,2)==selected and get(get(0x49c18),2)==int.from_bytes(payload[:2],'big');assert get(0x15ece0,2)==0 and get(0x15ed46,2)==0
   (out/f'interior-{interior}-room-{selected}-before-RAM.bin').write_bytes(before);(out/f'interior-{interior}-room-{selected}-after-RAM.bin').write_bytes(after)
   rows.append(dict(interior=interior,selected_room=selected,after_RAM_path=str(out/f'interior-{interior}-room-{selected}-after-RAM.bin'),source_payload_sha256=sha(payload),before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),source_CPU_instructions=len(steps),source_CPU_PC_samples=steps,calls=calls,stage_states=stage_states,mode=2,player_room=selected,relative_camera=[get(0x49b8c+i*2,2)for i in range(3)],texture_cache=[dict(id=get(0x15b4a0+i*4,2),references=get(0x15b4a2+i*4,2))for i in range(36)],disc_requests=disc.requests,disc_completions=disc.completions,disc_stops=disc.stops,source_loader_and_texture_fixups_executed=True));save(out/'cases.json',rows)
  report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_mode2_scene_loads_texture_fixups_and_declared_room_cameras_captured_C_loader_unverified',directory=str(out),cases=len(rows),interior_ids=[r['interior']for r in rows],source_CPU_steps=sum(r['source_CPU_instructions']for r in rows),disc_payload_transfers=sum(len(r['disc_requests'])for r in rows),loaded_transfer_bytes=sum(sum(q['bytes']for q in r['disc_requests'])for r in rows),pinned_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),probe_script_sha256=sha(Path(__file__).read_bytes()),source_CPU_scene_rendered=False,C_loader_verified=False,whole_game_complete=False,limits=['Direct original1AA40(mode2)then20F78(mode2)with source preservedinteriorIDs1/2/3, supplied playerinsidefirstorlargestroom/origin0/stack and priorassistedstartupRAM. This is not actual source boundarytransition/cleanup or uninterrupted boot.', 'Original68000loader/parser/copy/textureacquire/cachelookup/indoorposition/emptyactorlist execute. BIOS303C/3042RTSadapters transfer preserveddisc bytes,DF60synchronouscompletion manuallyreturns; no physicalCD/timing/task-switch claim.', 'Interior0has two sourceactorrecords and requires separatelycheckingnewtaskallocation/reuse; not replacedbyemptyfixture. Threeactualsourceemptyactorlists with two camera positions each are tested here. SourceCloader/fullsceneGPUdraw not yet compared.'])
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-interior-original-loading-probes.json',report);print(json.dumps(report))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:runtime.close()
if __name__=='__main__':main()
