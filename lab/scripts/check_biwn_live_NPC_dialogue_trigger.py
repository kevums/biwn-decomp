"""Source-created merchant warm yield -> close-player/cash branch -> source207CC.

Controlled player/cash inputs and other-task quiescence; no new merchant TCB,
asset pointers, private frames, selected message or movie args supplied.
"""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
class Reached(Exception):pass

def main():
    ready=json.loads((ROOT/'verification/BIWN-dialogue-ready-NPC.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);npc=json.loads((session/'npc-fullCPU-generation.json').read_text());out=ROOT/'verification/BIWN-live-NPC-dialogue-trigger'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libNPC-dialogue.dylib';names=['biwn_npc_cpu.c','biwn_rng_cpu.c','biwn_rng.c','biwn_camera.c','biwn_signed_division.c','biwn_scheduler.c','biwn_media_setup_cpu.c']
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)];p=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    runtime=media.Runtime(library,npc['instructions_decoded']);npc_fn=runtime.lib.biwn_npc_cpu_call;npc_fn.argtypes=runtime.fn.argtypes;npc_fn.restype=c.c_int;yield_fn=runtime.lib.biwn_scheduler_yield;yield_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];yield_fn.restype=c.c_int;rng=runtime.lib.biwn_rng_cpu_body;rng.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];rng.restype=c.c_int
    ram=bytearray(Path(ready['RAM_file']).read_bytes());assert sha(ram)==ready['RAM_sha256'];current=int(ready['current_task'],16);actor=0x49d6c+206*ready['actor_slot']
    def put(a,w,v):ram[a:a+w]=v.to_bytes(w,'big')
    obj=current
    for _ in range(128):
        put(obj+26,4,0 if obj==current else 1);obj=int.from_bytes(ram[obj:obj+4],'big')
        if obj==current:break
    else:raise AssertionError('Task ring bound')
    put(0x49c50,4,int.from_bytes(ram[actor+4:actor+8],'big'));put(0x49c56,4,int.from_bytes(ram[actor+10:actor+14],'big'));put(0x49d1e,4,0)
    initial=media.CPU();initial.registers[:]=ready['CPU']['registers'];initial.pc=ready['CPU']['pc'];initial.usp=ready['CPU']['usp'];initial.ssp=0x200000;initial.sr=ready['CPU']['sr'];snapshots={};captured={}
    types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32]
    def rd(w):
        def cb(_,a,v):v[0]=runtime.read(a,w);return 0
        return cb
    def wr(w):
        def cb(_,a,v):runtime.write(a,w,v);return 0
        return cb
    callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4))];bus=media.Bus(*callbacks,media.scheduler.cleanup.world.CALL(),None,0);w8=media.W8(wr(1));found=[]
    def service(_,b,cpu,target):
        if target==0x207cc:found.append(media.CPU.from_buffer_copy(bytes(cpu.contents)));return 1
        if target==0xe540:return rng(b,cpu)
        if target==0x10252:return runtime.lib.biwn_npc_cpu_body(b,cpu,w8,svc,None,10000,1)
        raise AssertionError(hex(target))
    svc=media.world_cpu.SERVICE(service);runtime.lib.biwn_npc_cpu_body.argtypes=npc_fn.argtypes;runtime.lib.biwn_npc_cpu_body.restype=c.c_int
    try:
        for mode in ['native','C']:
            runtime.reset(bytes(ram),0);cpu=media.CPU.from_buffer_copy(bytes(initial));coverage=[]
            if mode=='native':
                runtime.seed_cpu(cpu)
                for _ in range(1000):
                    pc=runtime.core.m68k_get_reg(None,16)
                    if pc==0x207cc:cpu=runtime.cpu();break
                    assert pc in runtime.rows or 0xdf60<=pc<0xdf6c or 0xde08<=pc<0xde5c or 0xe540<=pc<0xe588,hex(pc);coverage.append(pc);runtime.core.m68k_execute(1)
                else:raise AssertionError('Merchant trigger native bound')
            else:
                assert yield_fn(c.byref(bus),c.byref(cpu),128)==0 and cpu.pc==0xef88
                found.clear();status=npc_fn(c.byref(bus),c.byref(cpu),w8,svc,None,100000,1);assert status==3 and len(found)==1;cpu=found[0]
            msg=runtime.device.read(cpu.registers[15]+4,2);assert msg==60
            snapshots[mode]=dict(CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],source_message=msg,actor_address=hex(actor),native_PC_coverage=coverage if mode=='native' else None);captured[mode]=runtime.device.ram();(out/(mode+'-message-RAM.bin')).write_bytes(captured[mode])
        assert captured['native']==captured['C'] and all(snapshots['native'][k]==snapshots['C'][k] for k in ['CPU','RAM','hardware','source_message'])
        report=dict(status='source_created_live_merchant_distance_cash_branch_message60_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),CPU=snapshots['C']['CPU'],RAM_file=str(out/'C-message-RAM.bin'),RAM_sha256=sha(captured['C']),source_message=60,actor_slot=ready['actor_slot'],task=current,source_ready_capture=ready['directory'],source_sha256={n:sha((src/n).read_bytes()) for n in names},native_PC_coverage=snapshots['native']['native_PC_coverage'],whole_game_complete=False,limits=['Controlled close-player coordinates/cash0 and blockedothercontexts; captured merchant/task/assets originate in source worldload/creation/initialization. Actualscheduler selfyield/resumption/merchant loop/distance/cash branch suppliesmessage60 and its JSRframe. Message207CC/movie not executed in this proof yet.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-live-NPC-dialogue-trigger.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),task=hex(current),message=60)))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
