"""Source startup using resident dispatcher/full inherited sprite GPU state.

Initial source GPU/DSP setup and synchronous CD completion remain providers.
This is the next integration boundary, not full DD40 boot or scheduler proof.
"""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_continuous_loading_movie_world as joined
import check_biwn_startup_rng_cpu as fixtures
import check_biwn_render_actors_runtime as topology
ROOT=joined.ROOT;media=joined.media;save=joined.save;sha=joined.sha
class Runtime(joined.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.startup_active=False;self.full_running=False;self.dialogue_returned=False
        self.new_groups={};self.new_rows={}
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        for name,manifest in [('startup','startup'),('startup_HUD','startup-HUD'),('static_factory','static-factory'),('system','system')]:
            fn=getattr(self.lib,'biwn_'+name+'_cpu_body');fn.argtypes=self.fn.argtypes;fn.restype=c.c_int
            for row in json.loads((session/(manifest+'-fullCPU-generation.json')).read_text())['instructions_decoded']:self.new_groups[row['address']]=fn;self.new_rows[row['address']]=row
        self.startup_call=self.lib.biwn_startup_cpu_call;self.startup_call.argtypes=self.fn.argtypes;self.startup_call.restype=c.c_int
        self.startup_math=self.lib.biwn_startup_rng_math_cpu_body;self.startup_math.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.startup_math.restype=c.c_int
        self.geometry=self.lib.biwn_geometry_cpu_body;self.geometry.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];self.geometry.restype=c.c_int
        self.system_fn=self.lib.biwn_system_cpu_body;self.system_fn.argtypes=self.fn.argtypes;self.system_fn.restype=c.c_int
        self.system_dispatch=self.lib.biwn_scheduler_dispatch;self.system_dispatch.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];self.system_dispatch.restype=c.c_int
        parent=self.service
        def service(_,bus,cpu,target):
            try:
                if self.startup_active:
                    if target==0xde08:return self.system_dispatch(bus,cpu,128)
                    if target in [0x4088,0x303c,0x3042,0xdf60]:self.startup_provider(cpu.contents,target);return 0
                    if target in [0xe540,0xe588,0xe60a,0x1a77c]:return self.startup_math(bus,cpu)
                    if target in [0x1028e,0x102c4,0x1039c,0x10652]:return self.geometry(bus,cpu,4096)
                    if target in self.new_groups:return self.new_groups[target](bus,cpu,self.callbacks[5],self.service,None,1000000,0)
                    if target in self.render_groups:return self.render_CPU[self.render_groups[target]](bus,cpu,self.callbacks[5],self.service,None,1000000,0)
                return parent(_,bus,cpu,target)
            except Exception as error:self.errors.append(repr(error));return 1
        self.service=media.world_cpu.SERVICE(service)
    def startup_provider(self,s,target):
        if target==0x4088:return # source RTS
        if target==0x303c:self.asset_disc.start(s.registers[8],s.registers[9],s.registers[0])
        elif target==0x3042:self.asset_disc.stop()
        elif target==0xdf60:
            assert self.asset_disc.pending is not None
            self.asset_disc.tick(lambda a,data:c.memmove(self.device.pointer+a,data,len(data)),lambda a,v:self.device.direct(a,4,v))
        else:raise AssertionError(hex(target))
    def source_startup(self,ram,case,mode):
        self.startup_active=False;self.full_running=False;self.loading_active=False;self.prefix_running=False;self.renderer_active=False;self.pending_render=None;self.pending_movement=False;self.movie_started=False;self.pad.set_buttons([]);self.asset_disc.reset();self.start(ram,case['id']%3,mode)
        s=media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x1fe000;s.pc=0xd3ec;s.sr=0x2000;self.device.direct(s.registers[15],4,joined.controller.STOP)
        self.run_native(s,set())if mode=='native'else self.run_C(s);self.run_boot_exit('movie_exit');self.run_dispatch(True)
        self.startup_active=True;self.loading_active=True;self.pad.set_buttons(case['buttons']);start_calls=len(self.gpu_calls)
        initial=fixtures.queue.make_cpu(case);initial.pc=0x17c40;initial.registers[15]=initial.usp=0xc1128;initial.ssp=0x200000;initial.sr&=~0x2000
        system_start=case.get('system_start',False)
        if system_start:initial.pc=0xdd40;initial.registers[1]=0;initial.registers[15]=initial.ssp=0x200000;initial.usp=0x180000;initial.sr=0x2700
        GPU_before=self.gpu_counter.value;DSP_before=self.counter.value;begin_hardware=self.hardware()
        if mode=='native':
            self.seed_cpu(initial);steps=0
            for _ in range(2000000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0x17dc2:break
                if system_start and pc==0xddd8:self.clock_tick()
                if pc in [0x303c,0x3042,0xdf60]:
                    state=self.cpu();self.startup_provider(state,pc);opcode=self.device.read(pc,2);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,opcode)
                else:assert pc in self.rows,hex(pc);self.native_coverage.add(pc);self.core.m68k_execute(1)
                command=self.core.GPUReadLong(0xf03204,6)
                if command==0x4b00:self.run_render_request(command)
                steps+=1
            else:raise AssertionError(('Native retained startup bound',hex(pc)))
            result=self.cpu()
        else:
            if system_start:
                for _ in range(10000):
                    if initial.pc==0x17c40:break
                    if initial.pc==0xddd8:self.clock_tick()
                    self.C_CPU=initial;status=self.system_fn(c.byref(self.bus),c.byref(initial),self.callbacks[5],self.service,None,1,0);assert status in [4,6]and not self.errors,(status,self.errors)
                else:raise AssertionError('Source system bootstrap budget')
            self.C_CPU=initial;status=self.startup_call(c.byref(self.bus),c.byref(initial),self.callbacks[5],self.service,None,1000000,0);assert status==8 and not self.errors,(status,self.errors);result=initial;steps=None
            assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        assert result.pc==0x17dc2 and not self.pending_render and not self.asset_disc.pending
        final=self.device.ram();contexts=self.task_table(final)if system_start else topology.task_table(final)
        snapshot=dict(CPU=media.scheduler.cpu_dict(result),RAM=sha(final),hardware=self.hardware(),begin_hardware=begin_hardware,contexts=contexts,disc=dict(requests=self.asset_disc.requests,completions=self.asset_disc.completions,stops=self.asset_disc.stops),sprite_GPU_calls=self.gpu_calls[start_calls:])
        (self.out/f'case-{case["id"]}-{mode}-RAM.bin').write_bytes(final);self.startup_active=False;self.loading_active=False
        return snapshot,dict(native_CPU_steps=steps,original_CPU_attempts=self.C_original_CPU_attempts)
    def clock_tick(self):self.device.direct(0x778cc,4,(self.device.read(0x778cc,4)+1)&0xffffffff)
    def task_table(self,ram):
        get=lambda a,w=4:int.from_bytes(ram[a:a+w],'big');rows=[];seen=set();obj=topology.RENDER
        while obj not in seen:
            assert obj in topology.CONTEXTS;seen.add(obj);rows.append(dict(context=obj,next=get(obj),prev=get(obj+4),entry=get(obj+8),SP=get(obj+12),saved_PC=get(obj+16),SR=get(obj+20,2),deadline=get(obj+22),blocked=get(obj+26),argument=get(obj+30),suspend_count=get(obj+34)));obj=get(obj)
        assert obj==topology.RENDER and len(rows)==21 and get(0xc0924)==0xc5d28
        for row in rows:assert get(row['next']+4)==row['context']and get(row['prev'])==row['context']
        for obj,entry in zip(topology.CREATED,topology.TASKS):assert get(obj+8)==get(obj+16)==entry and get(obj+12)==obj+0x400
        return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cases',type=int,default=2);ap.add_argument('--system',action='store_true');opt=ap.parse_args();assert opt.cases>0
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);category='BIWN-system-startup-retained-GPU'if opt.system else 'BIWN-startup-retained-GPU';out=ROOT/'verification'/category/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';prior=json.loads((ROOT/'verification/BIWN-continuous-loading-movie-world.json').read_text());names=list(prior['source_sha256'])+['biwn_startup_cpu.c','biwn_startup_rng_math_cpu.c','biwn_static_factory_cpu.c','biwn_startup_HUD_cpu.c','biwn_system_cpu.c'];names=list(dict.fromkeys(names));lib=out/'libstartup-retained-GPU.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(lib)];built=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];rows=[]
    for n in ['movie','video','media-setup','GPU-boot','movie-privilege','npc','interior-loading','transition','doorway','actor-factory','cd-wrapper','world-flow','resource','render-queue','scene-draw','gpu-interior-submit','gpu-projection-submit','gpu-draw-submit','geometry-records','display-list','formatter','overlay-text','startup','startup-HUD','static-factory','system']:rows+=json.loads((session/(n+'-fullCPU-generation.json')).read_text())['instructions_decoded']
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows+=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text())['instructions']
    for a,b in [(0x4088,0x408a),(0xe540,0xe61c),(0x1a77c,0x1a7f4),(0xe4c0,0xe53c),(0x1028e,0x10430),(0x10652,0x106c4),(0xde08,0xde5c)]:rows+=fixtures.gen.loader.base.binary_tools.m68k_instructions(snapshot[a:b],a)[0]
    disc=joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';runtime=Runtime(lib,rows,*[m['instructions_decoded']for m in mappings],disc=disc,out=out,frame_directory=frames);results=[]
    try:
        for ram,case in fixtures.caller_cases(snapshot,opt.cases):
            base=bytearray(snapshot if opt.system else ram);base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();toc=joined.controller.make_toc(disc.layout);base[0x2c00:0x2c00+len(toc)]=toc;case['buttons']=[]if case['id']%2==0 else [3];case['system_start']=opt.system;observed={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',case=case['id'],mode=mode));observed[mode],checks=runtime.source_startup(bytes(base),case,mode);save(out/f'case-{case["id"]}-{mode}.json',observed[mode])
            if observed['native']!=observed['C']:save(out/'mismatch.json',observed);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(case=case,snapshot=observed['C'],C_checks=checks));save(out/'cases.json',results)
        report=dict(status='source_startup_retained_GPU_DSP_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),sprite_requests_per_case=[sum(g.get('program')=='sprite_4B00'for g in r['snapshot']['sprite_GPU_calls'])for r in results],initial_startup_capture_supplied=False,initial_Frozen_RAM_and_contexts_supplied=True,source_startup_scheduler_verified=False,intermediate_GPU_reset_or_reseed=False,full_CPU_RAM_logical_GPU4396_DSP8496_peripherals_disc_and_GPU_trace_compared=True,source_boot_verified=False,whole_game_complete=False,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,limits=['Source GPU/DSP bootstrap/media setup and source movie exit precede17C40 startup; supplied FrozenRAM/context/freepool/CPU/buttons and device initialization remain. Not source4000/DD40/systemDDCC/globalboot.','BIOS303C/3042 and file-backed674phase completion/RTS atDF60 remain; no actual startup scheduler switching/physicalCDtiming. Shared pinned synchronous blitter and GPU completion at CPU poll remain; full inherited logical GPU/DSP state now compares.','Standalone startup has not yet been linked to the later loading/movie/world run; its earlier startup capture remains in that separate proof. Modal11E6C branch, other tasks, scanout, physical timing/playability unverified.'])
        if opt.system:
            report.update(status='source_DD40_first_handoff_and_retained_GPU_startup_native_C_match',initial_Frozen_RAM_and_contexts_supplied=False,initial_Frozen_RAM_supplied=True,initial_context_ring_or_freepool_supplied=False,source_system_DD40_DDCC_first_handoff_verified=True,source_initial_freepool_records=100,source_contexts_after_startup=21,source_freepool_records_remaining=80)
            report['limits'][0]='Source GPU/DSP bootstrap/media setup and source movie exit precedeDD40 setup. Supplied FrozenRAM/CPU/supervisorstack/buttons/device initialization remain; context ring/freepool are created by sourceDD40, one external system-clock tick atDDD8 enables actualTRAP0/RTE into17C40 startup. Not source4000/globalboot/firmware.'
        pointer='system-startup-retained-GPU-checks.json'if opt.system else 'startup-retained-GPU-checks.json'
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/pointer,report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error),errors=runtime.errors[-5:]));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()
