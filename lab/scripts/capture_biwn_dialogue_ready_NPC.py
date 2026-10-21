"""Replay source world/task creation and stop at the merchant's first live yield."""
import ctypes as c,json,hashlib,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduled_world_NPC_render as world
from check_biwn_scheduled_world_NPC_render import ROOT,read,save,sha,CPU,WORLD,SSP,STOP,RUNNABLE,loader_gen,actor,startup
class Captured(Exception):pass
class Runtime(world.Runtime):
    def event(self,kind,state):
        row=super().event(kind,state)
        if kind=='yield' and self.host_phase>=5 and self.current()==0xc1528 and self.npc_iterations==1:
            self.captured=dict(CPU=world.loading.cd.scheduler.cpu_dict(state),RAM=self.device.ram(),current_task=self.current(),events=list(self.events),calls=list(self.calls))
            raise Captured()
        return row
def main():
    out = ROOT / 'verification/BIWN-dialogue-ready-NPC' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_interior_loading_cpu.c', 'biwn_transition_cpu.c', 'biwn_doorway_cpu.c',
             'biwn_actor_factory_cpu.c', 'biwn_resource_cpu.c', 'biwn_cd_cpu.c', 'biwn_actor_task.c',
             'biwn_actor_navigation.c', 'biwn_rng_cpu.c', 'biwn_signed_division.c', 'biwn_camera.c',
             'biwn_scheduler.c', 'biwn_task_loops.c', 'biwn_npc_cpu.c', 'biwn_animation_cpu.c', 'biwn_actor_movement.c', 'biwn_actor_direction.c', 'biwn_movement_submit_cpu.c', 'biwn_actor_collision.c', 'biwn_geometry_cpu.c', 'biwn_render_queue_cpu.c', 'biwn_scene_draw_cpu.c', 'biwn_geometry_records_cpu.c', 'biwn_gpu_interior_submit_cpu.c', 'biwn_gpu_projection_submit_cpu.c', 'biwn_gpu_draw_submit_cpu.c', 'biwn_display_list_cpu.c', 'biwn_formatter_cpu.c', 'biwn_overlay_text_cpu.c', 'biwn_world_flow_cpu.c', 'biwn_input_poll_cpu.c', 'biwn_input_dispatch_cpu.c', 'biwn_camera_cpu.c', 'biwn_targeting_cpu.c']
    library = out / 'libscheduled-world-NPC-render.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror'] + [str(source / name) for name in names] + ['-o', str(library)]
    compiler = subprocess.run(command, capture_output=True, text=True,
                             env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(compiler.stdout + compiler.stderr)
    assert compiler.returncode == 0, compiler.stderr
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    generated = []
    for name in ['interior-loading-fullCPU-generation.json', 'transition-fullCPU-generation.json',
                 'doorway-fullCPU-generation.json', 'actor-factory-fullCPU-generation.json',
                 'resource-fullCPU-generation.json', 'cd-wrapper-fullCPU-generation.json', 'npc-fullCPU-generation.json', 'render-queue-fullCPU-generation.json', 'scene-draw-fullCPU-generation.json', 'geometry-records-fullCPU-generation.json', 'gpu-interior-submit-fullCPU-generation.json', 'gpu-projection-submit-fullCPU-generation.json', 'gpu-draw-submit-fullCPU-generation.json', 'display-list-fullCPU-generation.json', 'formatter-fullCPU-generation.json', 'overlay-text-fullCPU-generation.json', 'world-flow-fullCPU-generation.json']:
        generated += read(session / name)['instructions_decoded']
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    generated += loader_gen.base.binary_tools.m68k_instructions(snapshot[0x13c9a:0x13f12],0x13c9a)[0]
    rows = {row['address']: row for row in generated}
    for lo, hi in actor.navigation.RANGES + actor.rng_cpu.RANGES + [(0xf4d8, 0xf712), (0xdfa6, 0xdfb2),
                   (0xdf60, 0xdf6c), (0xdf7a, 0xdf7c), (0xde08, 0xde5c), (0xdeb6, 0xdee2),
                   (0xf360, 0xf368), (0xf880, 0xf888), (0xeac4,0xec04), (0xeb04,0xeb3a)] + actor.motion.direction.RANGES + actor.motion.submit_cpu.RANGES + actor.motion.collision.RANGES + [(0x1028e,0x10430),(0x10652,0x106c4),(0xe4c0,0xe53c),(0xf0fa,0xf35e),(0x20820,0x20a9c),(0x191f4,0x192a2),(0x192bc,0x19f2c)]:
        rows.update({row['address']: row for row in loader_gen.base.binary_tools.m68k_instructions(snapshot[lo:hi], lo)[0]})
    for address in [0x303c, 0x3042]:
        rows[address] = {'address': address, 'assembly': 'declared BIOS preserve-register RTS adapter'}
    runtime = Runtime(library, list(rows.values()), generated)
    runtime.output = out
    capture_dir=ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z'
    capture=(capture_dir/'startup-C-0.bin').read_bytes();info=read(capture_dir/'startup-capture-0.json');assert sha(capture)==info['C_RAM_sha256']
    gate=next(g for g in read(ROOT/'verification/biwn-startup-loaded-doorway-candidates.json')['candidates'] if g['target']==312)
    ram,world_cpu=world.fixture(capture,info,gate);ram=bytearray(ram)
    put=lambda a,w,v:ram.__setitem__(slice(a,a+w),v.to_bytes(w,'big'))
    put(0xc0920,4,startup.RENDER);put(WORLD+12,4,world_cpu.registers[15]);put(WORLD+16,4,world_cpu.pc);put(WORLD+20,2,world_cpu.sr)
    initial=CPU();initial.registers[:]=info['CPU']['registers'];initial.pc=info['CPU']['pc'];initial.sr=info['CPU']['sr'];initial.usp=info['CPU']['usp'];initial.ssp=SSP
    runtime.clock_step=8;runtime.gate=gate;runtime.requested_iterations=1;snapshots={}
    try:
        for mode in ['native','C']:
            save(out/'status.json',dict(status='running',mode=mode))
            try:
                runtime.native(bytes(ram),initial,set()) if mode=='native' else runtime.translated(bytes(ram),initial)
            except Captured:pass
            else:raise AssertionError('Merchant ready boundary not captured')
            snap=runtime.captured;path=out/(mode+'-ready-RAM.bin');path.write_bytes(snap['RAM']);meta={k:v for k,v in snap.items() if k!='RAM'};meta['RAM_sha256']=sha(snap['RAM']);meta['RAM_file']=str(path);save(out/(mode+'-ready.json'),meta);snapshots[mode]=snap
        assert snapshots['native']['RAM']==snapshots['C']['RAM'] and snapshots['native']['CPU']==snapshots['C']['CPU']
        result=dict(status='source_created_merchant_live_after_asset_init_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),CPU=snapshots['C']['CPU'],RAM_file=str(out/'C-ready-RAM.bin'),RAM_sha256=sha(snapshots['C']['RAM']),current_task=hex(snapshots['C']['current_task']),actor_slot=int.from_bytes(snapshots['C']['RAM'][0xc1528+30:0xc1528+34],'big'),whole_game_complete=False,
            limits=['Replays checked controlled world gates/pose/pad/disc/clock inputs; captured before host NPC kill. Actual task creation/model21 acquisition/output allocation/firstsourceNPCyield, no supplied replacementmerchantTCB or asset references. Wholeboot/unblockedworld/physicaltiming remain separate.'])
        save(out/'report.json',result);save(ROOT/'verification/BIWN-dialogue-ready-NPC.json',result);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),task=result['current_task'],actor=result['actor_slot'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.device.close()
if __name__=='__main__':main()
