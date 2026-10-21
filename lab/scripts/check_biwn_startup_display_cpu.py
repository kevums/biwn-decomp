"""Source startup clear/display/input bodies connected to source caller.

Optional scene/player/HUD source bodies replace helper ABI providers. Disc
completion and sprite-device models remain explicit; not source boot.
"""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_startup_rng_cpu as old
import emulated_pad_input as pad
from biwn_disc_backend import Disc
ROOT=old.ROOT;CPU=old.CPU;SP=old.SP;STOP=old.STOP;save=old.save;sha=old.sha
PROVIDERS={0x21242,0x18ba8}
old.CALLER_PROVIDERS=PROVIDERS
old.ENTRIES|={0x4088,0xe03a,0x185b2,0x18160,0xe2f4,0xdfc0,0xe4c0}
class Runtime(old.Runtime):
    def __init__(self,library,rows,scene=False):
        super().__init__(library,rows);self.startup_body=self.fn;self.groups={}
        for target,name in [(0xe03a,'scene_draw'),(0x185b2,'display_list'),(0x18160,'media_setup')]:
            fn=getattr(self.lib,'biwn_'+name+'_cpu_body');fn.argtypes=self.call.argtypes;fn.restype=c.c_int;self.groups[target]=fn
        self.disc=Disc()if scene else None
        if scene:
            for name in ['interior_loading','resource','cd','render_queue','actor_factory','geometry_records','static_factory','startup_HUD','formatter','overlay_text']:
                fn=getattr(self.lib,'biwn_'+name+'_cpu_body');fn.argtypes=self.call.argtypes;fn.restype=c.c_int
                manifest={'interior_loading':'interior-loading','resource':'resource','cd':'cd-wrapper','render_queue':'render-queue','actor_factory':'actor-factory','geometry_records':'geometry-records','static_factory':'static-factory','startup_HUD':'startup-HUD','formatter':'formatter','overlay_text':'overlay-text'}[name]
                session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
                for row in json.loads((session/(manifest+'-fullCPU-generation.json')).read_text())['instructions_decoded']:self.groups[row['address']]=fn
                old.ENTRIES.update(self.groups)
        self.poll=self.lib.biwn_input_poll_cpu_body;self.poll.argtypes=self.math.argtypes;self.poll.restype=c.c_int
        self.geometry=self.lib.biwn_geometry_cpu_body;self.geometry.argtypes=[c.POINTER(old.queue.world.Bus),c.POINTER(CPU),c.c_uint32];self.geometry.restype=c.c_int
        old.ENTRIES|={0x1028e,0x102c4,0x1039c,0x10652}
        self.fn=self.dispatch
        self.core.JaguarReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.JaguarReadLong.restype=c.c_uint32
        self.core.JaguarWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
        self.core.TOMReadWord.argtypes=[c.c_uint32,c.c_uint32];self.core.TOMReadWord.restype=c.c_uint16
        self.pad=pad.Backend(self.core,self.device)
    def dispatch(self,bus,cpu,w8,service,ctx,budget,yield_flag):
        pc=c.cast(cpu,c.POINTER(CPU)).contents.pc
        if pc==0x4088:return 0 # actual source body is a single RTS
        if pc==0xe4c0:return self.poll(bus,cpu)
        if pc in [0x1028e,0x102c4,0x1039c,0x10652]:return self.geometry(bus,cpu,4096)
        return self.groups.get(pc,self.startup_body)(bus,cpu,w8,service,ctx,budget,yield_flag)
    def reset(self,ram,case,mode):
        super().reset(ram,case,mode);self.pad.set_buttons(case['buttons'])
        if self.disc:self.disc.reset()
        for address in range(0xf02200,0xf022a0,4):
            if address!=0xf02238:self.device.write(address,0)
        # These four words are fixture initialization, before source code.
        for address in range(0xf00400,0xf00408,2):self.core.JaguarWriteWord(address,0xaaaa,6)
    def read(self,a,w):
        if a<0x200000:return super().read(a,w)
        assert w==4
        v=self.core.JaguarReadLong(a,6)if a==0xf14000 else self.device.read(a,w)
        self.trace.append(['r',a,w,v]);return v
    def script_provider(self,state,target):
        if target in [0x303c,0x3042,0xdf60]:
            assert self.disc is not None
            if target==0x303c:self.disc.start(state.registers[8],state.registers[9],state.registers[0])
            elif target==0x3042:self.disc.stop()
            else:
                assert self.disc.pending is not None,'completion adapter without pending transfer'
                self.disc.tick(lambda a,data:c.memmove(self.device.pointer+a,data,len(data)),lambda a,v:self.device.direct(a,4,v))
            self.calls.append(dict(target=hex(target),declared_disc_or_completion_provider=True));return
        return super().script_provider(state,target)
    def write(self,a,w,v):
        if a<0x200000:return super().write(a,w,v)
        self.trace.append(['w',a,w,v])
        if w==2:self.core.JaguarWriteWord(a,v,6)
        else:assert w==4;self.device.write(a,v)
    def hardware(self):
        return dict(TOM_display_words=[self.core.TOMReadWord(a,6)for a in range(0xf00400,0xf00408,2)],blitter_words=[self.device.read(a,4)for a in range(0xf02200,0xf022a0,4)if a!=0xf02238],blitter_status=self.device.read(0xf02238,4))
    def disc_state(self):
        return dict(requests=list(self.disc.requests),completions=list(self.disc.completions),stops=self.disc.stops)if self.disc else None
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);old.queue.lifecycle.seed_cpu(self,old.queue.make_cpu(case));steps=0
        for target in PROVIDERS:self.device.direct(target,2,0x4e75)
        try:
            for _ in range(2000000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0x17dc2:break
                if pc in PROVIDERS:
                    state=self.cpu();self.script_provider(state,pc)
                    for r in [0,1,8,9]:self.core.m68k_set_reg(r,state.registers[r])
                    self.core.m68k_set_reg(17,state.sr)
                else:assert pc in self.rows,hex(pc);coverage.add(pc);steps+=1
                self.core.m68k_execute(1)
                if pc==0xe2d6:self.device.write(0xf03204,0x4b00)
            else:raise AssertionError(('native worklimit',hex(pc)))
        finally:
            for target in PROVIDERS:self.device.direct(target,2,int.from_bytes(ram[target:target+2],'big'))
        return self.device.ram(),self.cpu(),dict(instructions=steps,providers=list(self.calls))
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);e=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);e.ctl_set_cpu_model(UC_CPU_M68K_M68000);e.mem_map(0,0x200000);e.mem_map(0xf00000,0x20000);e.mem_write(0,ram);e.reg_write(UC_M68K_REG_SR,case['SR'])
        for r,v in zip(old.queue.cd.REGS,case['registers']):e.reg_write(r,v)
        for target in PROVIDERS:e.mem_write(target,b'\x4e\x75')
        def code(cpu,pc,w,_):
            if pc==0x17dc2:cpu.emu_stop();return
            if pc in PROVIDERS:
                state=old.queue.make_cpu(case);state.registers[:]=[cpu.reg_read(r)for r in old.queue.cd.REGS];self.script_provider(state,pc)
                for r in [0,1,8,9]:cpu.reg_write(old.queue.cd.REGS[r],state.registers[r])
                cpu.reg_write(UC_M68K_REG_SR,state.sr)
                if pc==0xdf60:
                    cpu.mem_write(0,self.device.ram())
                    for target in PROVIDERS:cpu.mem_write(target,b'\x4e\x75')
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def reader(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def writer(cpu,access,a,w,v,_):
            self.write(a,w,v&((1<<(w*8))-1))
            if a==0xf02238 or(a==0xf03204 and v==0x4b00):
                # The shared synchronous blitter writes RAM outside the CPU.
                # Deliver that DMA result to the independent CPU's view.
                cpu.mem_write(0,self.device.ram())
                for target in PROVIDERS:cpu.mem_write(target,b'\x4e\x75')
        hooks=[e.hook_add(UC_HOOK_CODE,code),e.hook_add(UC_HOOK_MEM_READ,reader),e.hook_add(UC_HOOK_MEM_WRITE,writer)]
        e.emu_start(case['entry'],STOP,count=2000000,timeout=30000000)
        s=old.queue.make_cpu(case);s.registers[:]=[e.reg_read(r)for r in old.queue.cd.REGS];s.pc=e.reg_read(UC_M68K_REG_PC);assert s.pc==0x17dc2
        if s.sr&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
        for target in PROVIDERS:e.mem_write(target,ram[target:target+2])
        output=self.device.ram();assert bytes(e.mem_read(0,0x200000))==output
        trace=list(self.trace)
        for h in hooks:e.hook_del(h)
        e.mem_write(STOP,b'\x40\xc7');e.emu_start(STOP,STOP+2,count=1);s.sr=e.reg_read(UC_M68K_REG_D7)&65535
        return output,s,dict(trace=trace)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cases',type=int,default=8);ap.add_argument('--scene',action='store_true');ap.add_argument('--player',action='store_true');ap.add_argument('--hud',action='store_true');opt=ap.parse_args();assert opt.cases>0;assert not opt.player or opt.scene;assert not opt.hud or opt.player
    global PROVIDERS
    if opt.scene:PROVIDERS={0x18ba8,0x303c,0x3042,0xdf60};old.CALLER_PROVIDERS=PROVIDERS;old.ENTRIES|={0x21242,0x1aeda,0xf0c0}
    if opt.player:PROVIDERS={0x1b786,0x18888,0x303c,0x3042,0xdf60};old.CALLER_PROVIDERS=PROVIDERS;old.ENTRIES.add(0x18ba8)
    if opt.hud:PROVIDERS={0x303c,0x3042,0xdf60};old.CALLER_PROVIDERS=PROVIDERS
    category='BIWN-startup-source-fullCPU'if opt.hud else 'BIWN-startup-player-fullCPU'if opt.player else 'BIWN-startup-scene-fullCPU'if opt.scene else 'BIWN-startup-display-fullCPU'
    out=ROOT/'verification'/category/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_startup_cpu.c','biwn_startup_rng_math_cpu.c','biwn_signed_division.c','biwn_camera.c','biwn_actor_factory_cpu.c','biwn_render_queue_cpu.c','biwn_scene_draw_cpu.c','biwn_display_list_cpu.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c','biwn_geometry_cpu.c'];library=out/'libstartup-display-cpu.dylib'
    if opt.scene:names+=['biwn_interior_loading_cpu.c','biwn_resource_cpu.c','biwn_cd_cpu.c','biwn_geometry_records_cpu.c','biwn_static_factory_cpu.c','biwn_startup_HUD_cpu.c','biwn_formatter_cpu.c','biwn_overlay_text_cpu.c']
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    built=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);rows=[]
    for name in ['startup','actor-factory','scene-draw','display-list','media-setup']:rows+=json.loads((session/(name+'-fullCPU-generation.json')).read_text())['instructions_decoded']
    if opt.scene:
        for name in ['interior-loading','resource','cd-wrapper','render-queue','geometry-records','static-factory','startup-HUD','formatter','overlay-text']:rows+=json.loads((session/(name+'-fullCPU-generation.json')).read_text())['instructions_decoded']
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    for a,b in [(0xe540,0xe61c),(0x1a77c,0x1a7f4),(0x4088,0x408a),(0xe4c0,0xe53c),(0x1028e,0x10430),(0x10652,0x106c4)]:rows+=old.gen.loader.base.binary_tools.m68k_instructions(snapshot[a:b],a)[0]
    runtime=Runtime(library,rows,opt.scene);coverage=set();results=[]
    try:
        for ram,case in old.caller_cases(snapshot,opt.cases):
            if opt.player:
                # Source DD40 supplies user-mode task entries with this real
                # render context's stack top; no outer return is seeded there.
                case['SR']&=~0x2000;case['registers'][15]=0xc1128;case['usp']=0xc1128;case['ssp']=0x200000
            case['buttons']=[3]if case['id']%2 else [] # no source bit0/modal entry
            save(out/'status.json',dict(status='running',case=case['id']));left,expected,native=runtime.native(ram,case,coverage);native_hw=runtime.hardware();native_disc=runtime.disc_state();observed,observer,independent=runtime.unicorn(ram,case,coverage);independent_hw=runtime.hardware();independent_disc=runtime.disc_state();right,actual,rebuilt=runtime.translated(ram,case);rebuilt_hw=runtime.hardware();rebuilt_disc=runtime.disc_state()
            if rebuilt['status']!=8 or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or independent['trace']!=rebuilt['trace']or native_hw!=rebuilt_hw or independent_hw!=rebuilt_hw or native_disc!=rebuilt_disc or independent_disc!=rebuilt_disc:
                (out/'native-RAM.bin').write_bytes(left);(out/'C-RAM.bin').write_bytes(right);save(out/'mismatch.json',dict(case=case,native_CPU=old.queue.cd.scheduler.cpu_dict(expected),Unicorn_CPU=old.queue.cd.scheduler.cpu_dict(observer),C_CPU=old.queue.cd.scheduler.cpu_dict(actual),native=native,Unicorn=independent,C=rebuilt,native_hardware=native_hw,Unicorn_hardware=independent_hw,C_hardware=rebuilt_hw,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:80]));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
            row=dict(case=case,CPU=old.queue.cd.scheduler.cpu_dict(actual),RAM_sha256=sha(right),hardware=rebuilt_hw,disc=rebuilt_disc,device=rebuilt['device'],native_instructions=native['instructions'],ordered_bus_operations=len(rebuilt['trace']),ordered_bus_sha256=sha(json.dumps(rebuilt['trace'],separators=(',',':')).encode()),full_CPU_RAM_TOM_blitter_private_frames_and_bus_match=True)
            if opt.player:
                import check_biwn_render_actors_runtime as topology
                row['contexts']=topology.task_table(right);row['source_task_creations']=len(row['contexts'])-2;assert row['source_task_creations']==19
                for obj in [0xc1128,0xc1528,0xc1928]:assert int.from_bytes(right[obj+20:obj+22],'big')==0
                final_ram=out/f'case-{case["id"]}-C-startup-RAM.bin';final_ram.write_bytes(right);row['final_RAM_path']=str(final_ram)
            results.append(row)
        covered=lambda a,b:[sum(a<=pc<b for pc in coverage),sum(a<=row['address']<b for row in rows)]
        report=dict(status='startup_caller_clear_display_input_native_Unicorn_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),native_CPU_instructions=sum(r['native_instructions']for r in results),source_caller_coverage=covered(0x17c40,0x17dc2),full_2MB_RAM_compared_without_masks=True,all_CPU_registers_SR_USP_SSP_compared=True,ordered_bus_compared_to_independent_Unicorn=True,TOM_display_and_blitter_state_compared=True,real_helpers=['0x4088','0xe03a','0x185b2','0x18160','0xe2f4','0xdfc0','0xe4c0'],remaining_caller_scripts=sorted(map(hex,PROVIDERS)),source_task_creations_per_case=16,original_CPU_or_GPU_execution_on_C_path=False,startup_snapshot_removed=False,whole_game_complete=False,new_published_components=0,source_sha256={n:sha((source/n).read_bytes())for n in names+[n.replace('.c','.h')for n in names]},test_script_sha256=sha(Path(__file__).read_bytes()),imported_checker_sha256=sha(Path(old.__file__).resolve().read_bytes()),compiler=cmd,limits=['Supplied source RAM/two-context ring/freepool, source startup caller and16sourcecreations; scene21242 andplayer18BA8 remain two ABI scripts. Source input poll uses declared emulated buttons with modalbit0 clear; source11E6C modal branch is not exercised.','Shared pinned synchronous emulator blitter plus fixture-initialized registers and Frozen descriptor data; complete source CPU/RAM/privateframes and ordered bus effects compare, not actual GPU/DSP boot/objectprocessor/physical display timing. Existing connected game still uses earlierstartupcapture.'])
        report['remaining_caller_scripts']=sorted(hex(x)for x in PROVIDERS if x not in [0x303c,0x3042,0xdf60])
        report['declared_BIOS_or_completion_adapters']=sorted(hex(x)for x in PROVIDERS if x in [0x303c,0x3042,0xdf60])
        report['source_helper_coverage']={hex(a):covered(a,b)for a,b in [(0xe03a,0xe098),(0x185b2,0x18854),(0x18160,0x181da),(0x21242,0x212e8),(0x18ba8,0x18df2),(0x137e0,0x13ae0),(0x1b786,0x1bc78),(0x18888,0x18b86),(0xdfc0,0xdff4)]}
        # Use unique instruction addresses; inline callback tables are data.
        for key,bounds in list(report['source_helper_coverage'].items()):
            a=int(key,16);b={0xe03a:0xe098,0x185b2:0x18854,0x18160:0x181da,0x21242:0x212e8,0x18ba8:0x18df2,0x137e0:0x13ae0,0x1b786:0x1bc78,0x18888:0x18b86,0xdfc0:0xdff4}[a];report['source_helper_coverage'][key]=[sum(a<=pc<b for pc in coverage),len({r['address']for r in rows if a<=r['address']<b})]
        if opt.player:
            report.update(source_task_creations_per_case=19,contexts_after_startup=21,source_mode='user task SR0 bank at render stack topC1128; supplied SSP200000',disc_requests_per_case=[len(r['disc']['requests'])for r in results],disc_bytes_per_case=[sum(q['bytes']for q in r['disc']['requests'])for r in results],source_GPU_context_or_scanout_compared=False)
        if opt.hud:
            report['status']='startup_source_caller_scene_player_static_HUD_CPU_RAM_bus_match'
            report['real_helpers']+=['0x21242','0x18ba8','0x1aa40','0x1aeda','0xea20','0xf0c0','0x137e0','0x1b786','0x18888','0x1b45a','0x149ae']
            report['limits']=['Supplied Frozen source RAM/two initial contexts/nineteen free records, source user-mode render stack and SSP. Reconstructed source runs17C40 through17DC2 including initialization, scene/player/static objects/HUD and19 creations forming21 contexts. No reached game helper is an ABI script; modal11E6C branch remains unexercised because supplied buttons keep bit0 clear.','BIOS303C/3042 preserve-register adapters, file bytes normalized with captured674phase and synchronous completion/RTS at sourceDF60 remain explicit. Actual scheduler switching during startup, sourceDD40/systemDDCC/global boot clocks/firmware are unverified.','Source sprite submission uses isolated nativeGPU versus Cdecoder/mailbox fixture with GPUreset/reseed, and shared pinned synchronous blitter. CPU/privateRAM/TOM-display/blitter/bus/disc compare without masks; inherited fullGPU/DSP context, objectprocessor/physical timing are not compared. This standalone source startup is not yet linked into the retained loading/movie/world test; its earlier startup capture remains.']
        pointer='startup-source-fullCPU-checks.json'if opt.hud else 'startup-player-fullCPU-checks.json'if opt.player else 'startup-scene-fullCPU-checks.json'if opt.scene else 'startup-display-fullCPU-checks.json'
        save(out/'cases.json',results);save(out/'coverage.json',dict(covered=sorted(coverage)));save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/pointer,report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except Exception as error:
        (out/'failed-current-RAM.bin').write_bytes(runtime.device.ram())
        save(out/'failure-state.json',dict(CPU=old.queue.cd.scheduler.cpu_dict(runtime.cpu()),disc_requests=runtime.disc.requests if runtime.disc else [],disc_completions=runtime.disc.completions if runtime.disc else [],disc_pending=runtime.disc.pending is not None if runtime.disc else False,calls=runtime.calls[-20:]))
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()
