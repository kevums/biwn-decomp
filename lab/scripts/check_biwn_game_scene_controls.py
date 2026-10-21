"""Readable191F4 dispatcher through elevator display, polling and disc setup.

Original nativeCPU and linked C share actual emulated blitter and normalized
disc bytes. Raw controller read values are fixtures; held/edge and scene
outcomes are computed. Firmware/context/task boundaries remain adapters.
"""
import ctypes as c
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import check_biwn_scene_stream as scene
import check_biwn_game_controls as controls

ROOT=scene.ROOT
SP=scene.SP
save=scene.save
sha=scene.sha
CONTROL_SOURCES=['biwn_game_scene_controls.c','biwn_game_controls.c','biwn_input_dispatch.c',
 'biwn_attack_effect.c','biwn_rng.c','biwn_camera.c','biwn_animation.c',
 'biwn_elevator_display.c','biwn_elevator_formatter.c','biwn_formatter_cpu.c',
 'biwn_panel_refresh.c','biwn_text.c','biwn_input_poll.c']
SOURCES=list(dict.fromkeys(scene.SOURCES+CONTROL_SOURCES))
# Extend the independent native lane's executable intervals. No additional
# helper body is replaced by a fixture for this exercised dispatcher route.
scene.RANGES.update(controls.SOURCE)
scene.RANGES[0x191f4]=0x19f2c
scene.ENTRIES.update(controls.SOURCE)
scene.ENTRIES.update([0x191f4,0x190bc,0x1b45a,0x12620,0x149ae,0xe4c0])


class Runtime(scene.Runtime):
    def __init__(self,library):
        super().__init__(library)
        self.controls=self.lib.biwn_game_scene_controls
        self.controls.argtypes=[c.POINTER(scene.world.Bus),type(self.device.write8),*[c.c_uint32]*5,c.POINTER(c.c_uint32)]
        self.controls.restype=c.c_int
        self.poll_cursor=0;self.io=[]

    def raw_read(self,case):
        group=self.poll_cursor//4;row=self.poll_cursor%4
        held=case['poll_values'][min(group,len(case['poll_values'])-1)]
        value=controls.raw_rows(held)[row];self.poll_cursor+=1
        self.io.append(['r',0xf14000,4,value]);return value

    def before_step(self,pc,case):
        if pc in controls.POLL_SELECT_PCS:self.io.append(['w',0xf14000,2,controls.POLL_SELECT_PCS[pc]])

    def after_step(self,pc,case):
        super().after_step(pc,case)
        if pc in controls.POLL_READ_PCS:
            value=self.raw_read(case);sr=self.core.m68k_get_reg(None,17)
            self.core.m68k_set_reg(0,value)
            self.core.m68k_set_reg(17,(sr&0xfff0)|(4 if not value else 0)|(8 if value&0x80000000 else 0))

    def native(self,ram,case):
        self.poll_cursor=0;self.io=[]
        memory,value,result=super().native(ram,case)
        result.update(raw_controller_IO=list(self.io),raw_read_count=self.poll_cursor)
        return memory,value,result

    def translated(self,ram,case,**overrides):
        self.gpu_mode=1;self.seed(ram);self.disc.reset();self.poll_cursor=0;self.io=[];calls=[];errors=[]
        def read32(_,address,out):
            try:
                if address==0xf14000:out[0]=self.raw_read(case);return 0
                return self.device.r32(None,address,out)
            except Exception as error:errors.append(repr(error));return 1
        def write16(_,address,value):
            try:
                if address==0xf14000:
                    assert value==controls.POLL_SELECTS[self.poll_cursor%4]
                    self.io.append(['w',address,2,value])
                    self.core.m68k_write_memory_16(address,value)
                    return 0
                return self.device.w16(None,address,value)
            except Exception as error:errors.append(repr(error));return 1
        def call(_,target,args,n,out):
            try:
                assert target in scene.EXTERNAL,hex(target)
                values=list(args[:n])if n else[]
                if target==0x303c:assert n==3;self.disc.start(*values)
                elif target==0x3042:assert not n;self.disc.stop()
                elif target==0xdf60:assert not n;self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v))
                else:assert len(values)==len(scene.EXTERNAL[target]);out[0]=case['external_D0']
                calls.append([hex(target),values]);return 0
            except Exception as error:errors.append(repr(error));return 1
        callbacks=[scene.world.R32(read32),scene.world.W16(write16),scene.world.CALL(call)]
        bus=scene.world.Bus(self.device.r8,self.device.r16,callbacks[0],callbacks[1],self.device.w32,callbacks[2],None,32768)
        args=dict(display_scratch=SP-46,stream_scratch=SP-512,word_scan=case['word_scan'],budget=1024,incoming=case['incoming'][0]);args.update(overrides)
        result=c.c_uint32(0xa55aa55a)
        status=self.controls(c.byref(bus),self.device.write8,*args.values(),c.byref(result))
        return self.device.ram(),result.value,dict(status=status,errors=errors,calls=calls,disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops,hardware=self.hardware(),device=self.device.stats(),raw_controller_IO=list(self.io),raw_read_count=self.poll_cursor)


def main():
    out=ROOT/'verification/game-scene-controls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libgame-scene-controls.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(restore/name)for name in SOURCES],'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=Runtime(library)
    snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes()
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    address=int(patch['address'],16);before=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement']);assert snapshot[address:address+len(before)]==before
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text())
    captured=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(captured)==diagnosis['buffer_sha256']
    historical=runtime.disc.stream_phase;witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],captured);elevator=runtime.disc.stream_phase
    rng=random.Random(0x191f420f78);rows=[]
    try:
        for phase,word_scan in [(historical,0),(historical,1),(elevator,1)]:
            runtime.disc.stream_phase=phase
            for cold,waits in [(cold,waits)for cold in [False,True]for waits in [False,True]]:
                ram=bytearray(snapshot);ram[0x47b80:0x47b84]=bytes(4);ram[0x46250:0x46252]=bytes(2);ram[0x49ba4:0x49bb0]=bytes(12)
                if cold:
                    for i in range(36):ram[0x15b4a0+i*4:0x15b4a4+i*4]=b'\xff\xff\0\0'
                if word_scan:ram[address:address+len(before)]=replacement
                values=[0,0x00100000,0,0x00200000,0x10000000]if waits else[0x00100000,0x00200000,0x10000000]
                case=dict(entry=0x191f4,mode=2,cold_texture_cache=cold,neutral_waits=waits,word_scan=word_scan,stream_phase=phase,poll_values=values,incoming=[rng.getrandbits(32)for _ in scene.world.REGS],external_D0=0xc001d00d)
                save(out/'status.json',dict(status='running',case=case))
                left,expected,reference=runtime.native(bytes(ram),case)
                right,value,rebuilt=runtime.translated(bytes(ram),case)
                same=scene.native.masked(left)==scene.native.masked(right)and value==expected and rebuilt['status']==0 and not rebuilt['errors']and all(reference[k]==rebuilt[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware','raw_controller_IO','raw_read_count'])
                if not same:
                    save(out/'mismatch.json',dict(case=case,original_D0=expected,C_D0=value,original=reference,C=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(scene.native.masked(left),scene.native.masked(right)))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
                get=scene.native.get
                assert get(right,0x49c62,2)==2 and get(right,0x49c64,2)==314 and get(right,0x49c60,2)==2 and get(right,0x47b80,2)==0
                assert reference['entries']['0x20f78']==reference['entries']['0x20f0c']==2 and reference['entries']['0xe4c0']==len(values)
                assert reference['raw_read_count']==len(values)*4
                assert len(rebuilt['disc_requests'])==(4 if cold else 2)
                assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
                framebuffer=get(right,0xbd830);pixels=right[framebuffer:framebuffer+224*240*2]
                if not rows:
                    (out/'original-framebuffer.bin').write_bytes(left[framebuffer:framebuffer+224*240*2])
                    (out/'C-framebuffer.bin').write_bytes(pixels)
                    controls.diagnostic_png(runtime.core,pixels,out/'native-matched-elevator-panel.png',palette_source=ROOT/'tools/virtualjaguar-runtime-source/src/tom/tom.c')
                row=dict(case=case,full_D0=value,original=reference,rebuilt=rebuilt,created_task_records_checked=scene.check_task_records(left,right,reference),full_public_RAM_matches=True,framebuffer_address=hex(framebuffer),framebuffer_sha256=sha(pixels),final_floor=2,final_scene_index=314)
                rows.append(row);save(out/'cases.json',rows)
        guards=[]
        for overrides in [dict(display_scratch=0),dict(stream_scratch=0),dict(word_scan=2),dict(budget=0)]:
            _,value,check=runtime.translated(bytes(ram),case,**overrides)
            assert check['status']==1 and value==0xa55aa55a and not check['calls']and not check['raw_controller_IO']and runtime.device.ram()==bytes(ram)
            guards.append(overrides)
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error),native_diagnostic=getattr(runtime,'failure',None)));raise
    finally:runtime.close()
    report=dict(status='readable_dispatcher_display_poll_cleanup_actual_scene_stream_roundtrips_match_native',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),elevator_roundtrips=len(rows),elevator_scene_actions=len(rows)*2,guards=guards,verified_API='biwn_game_scene_controls',entry='0x191f4',source_sha256={n:sha((restore/n).read_bytes())for n in SOURCES+[n.replace('.c','.h')for n in SOURCES]},script_sha256=sha(Path(__file__).read_bytes()),native_helper_sha256=sha((ROOT/'scripts/check_biwn_scene_stream.py').read_bytes()),controller_encoder_evidence=str(controls.CONTROLLER_MAPPING_PATH),raw_controller_results_supplied=True,held_and_edge_results_supplied=False,scene_setup_results_supplied=False,scene_cleanup_results_supplied=False,formatted_text_and_pixels_supplied=False,source_disc_sha256=runtime.disc.manifest['normalized_track_sha256'],stream_phases=[historical,elevator],elevator_stream_witness=witness,native_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),C_blitter_commands=sum(row['rebuilt']['device']['blit_commands']for row in rows),reached_external_targets=sorted({call[0]for row in rows for call in row['rebuilt']['calls']}),existing_controls_API_changed=False,high_level_frame_runtime_substitution=False,new_training=False,native_Chat_verified=False,default_promoted=False,scope='One complete191F4dispatcher invocation contains readable elevator labels/formatter/panel/text withactualblitter, originalE4C0controllerdecode from suppliedrawrows,UpandDowninput,sourcecleanup,actualscene/texturedisc loading,fixups,playerposition andactorfactory.12controlled roundtrips cover warm/emptytexturecache,immediate/neutralwaitpollsequences,original674andexplicitwordscan674/672. Originalnative/C fullD0,public2MBRAM,rawIOorder,externalhelperargs,disc events and7blitterregisters match. Frozen merchant RAM/TOC/heap/cache; timer and initialheldstate edited to enter elevator. DF6Ctaskcreation computes actual task-list/frame records (checked outside private-stack exclusion); executing those tasks is not part of this synchronous call. Firmware303C/3042 andDF60completiontick remain adapters; E2B8uses source CPUprotocol andhostGPUdevice (not reached by these two-floorcases);outdoor geometry is linked in scene stream; otherdispatcher/equipmentservices remain external butunreached. Fullscheduler,interrupts,CPUABI/cycles,physicalcontroller/disc/scanout,audibleaudio,naturalentrycapture,frame-runtimeintegration andfullgame remain unproved. Existing2069case API unchanged; new API explicitly selectable.')
    report['task_creation_results_supplied']=False
    report['created_task_records_checked']=sum(len(row['created_task_records_checked'])for row in rows)
    report['diagnostic_image']=str(out/'native-matched-elevator-panel.png')
    report['diagnostic_image_scope']='Palette-rendered150x61crop of actual matched original/C framebuffer from supplied merchant RAM, scaled4x. Not natural scanout,physicaldisplay or frame-runtime substitution.'
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)));save(ROOT/'verification/game-scene-controls-current.json',report)
    print(json.dumps({k:report[k]for k in ['status','cases','elevator_scene_actions','C_blitter_commands','directory']}),flush=True)


if __name__=='__main__':main()
