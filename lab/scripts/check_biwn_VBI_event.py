"""TOM IRQ2 user/supervisor entry and sourceVBI/actual304E/RTE comparison."""
import ctypes as c,json,os,subprocess,random
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_bios_transport_cpu as transport
media=transport.media;ROOT=transport.ROOT;save=transport.save;sha=transport.sha
class Runtime(transport.Runtime):
    def __init__(self,*args):
        super().__init__(*args);self.video_body=self.lib.biwn_video_cpu_body;self.video_body.argtypes=self.fn.argtypes;self.video_body.restype=c.c_int;self.vbi_event=self.lib.biwn_vbi_event;self.vbi_event.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.vbi_event.restype=c.c_int;self.core.TOMSetPendingVideoInt.argtypes=[]
    def reset(self,ram,seed):
        super().reset(ram,seed);self.write(0xf000e0,2,3)
    def original_event(self,ram,s,seed):
        self.reset(ram,seed);self.seed_cpu(s);self.core.TOMSetPendingVideoInt();self.core.m68k_set_irq2(2);assert self.core.m68k_get_reg(None,16)==0xe7d4, (hex(self.core.m68k_get_reg(None,16)),media.scheduler.cpu_dict(self.cpu()),hex(self.read(0xf000e0,2)))
        entry=dict(CPU=media.scheduler.cpu_dict(self.cpu()),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware']);pcs=[]
        for _ in range(1000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==s.pc:break
            assert pc in self.rows,hex(pc);pcs.append(pc);self.core.m68k_execute(1)
        else:raise AssertionError('VBI original bound')
        return entry,self.cpu(),self.device.ram(),self.snapshot()['hardware'],pcs
    def translated_event(self,ram,initial,seed):
        self.reset(ram,seed);s=media.CPU.from_buffer_copy(bytes(initial));self.core.TOMSetPendingVideoInt();self.core.m68k_set_irq(0)
        def rd(w):
            def f(_,a,v):v[0]=self.read(a,w);return 0
            return f
        def wr(w):
            def f(_,a,v):self.write(a,w,v);return 0
            return f
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8];callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4)),types[5](wr(1))];bus=media.Bus(*callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        assert self.vbi_event(c.byref(bus),c.byref(s))==0;entry=dict(CPU=media.scheduler.cpu_dict(s),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'])
        def service(_,passed,cpu,target):
            assert target==0x304e;return self.mode_body(passed,cpu,callbacks[5],cb,None,100000,0)
        cb=media.world_cpu.SERVICE(service);assert self.video_body(c.byref(bus),c.byref(s),callbacks[5],cb,None,10000,0)==0;return entry,s,self.device.ram(),self.snapshot()['hardware']
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);rows=json.loads((session/'bios-transport-fullCPU-generation.json').read_text())['instructions_decoded']+json.loads((session/'video-fullCPU-generation.json').read_text())['instructions_decoded'];out=ROOT/'verification/BIWN-VBI-event'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_vbi_event.c','biwn_video_cpu.c','biwn_bios_transport_cpu.c','biwn_media_setup_cpu.c'];lib=out/'libVBI-event.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    runtime=Runtime(lib,rows);runtime.prequeue=0;bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();ram=bytearray(0x200000);stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert sha(stage)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';ram[0x4000:0x4000+len(stage)]=stage;ram[0x3000:0x3e00]=bios[0x84a6:0x92a6];ram[0x3074:0x3078]=(0xf03050).to_bytes(4,'big');ram[0x100:0x104]=(0xe7d4).to_bytes(4,'big');rng=random.Random(0xe7d4c);results=[]
    try:
        for case in range(32):
            runtime.initial_progress=0 if case%2 else 0x1bfffc;s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];s.usp=0x180000 if case%2 else 0x1ff000;s.ssp=0x1ff000 if case%2 else 0x200000;s.sr=(0x2000 if case%2 else 0)|(case%32);s.pc=0x17c40;save(out/'status.json',dict(status='running',case=case));ea,a,ra,ha,pcs=runtime.original_event(bytes(ram),s,case%3);eb,b,rb,hb=runtime.translated_event(bytes(ram),s,case%3)
            if ea!=eb or bytes(a)!=bytes(b)or ra!=rb or ha!=hb:save(out/'mismatch.json',dict(case=case,native_entry=ea,C_entry=eb,native_CPU=media.scheduler.cpu_dict(a),C_CPU=media.scheduler.cpu_dict(b),native_hardware=ha,C_hardware=hb));raise AssertionError(str(out/'mismatch.json'))
            assert a.pc==s.pc and a.registers[:]==s.registers[:]and a.sr==s.sr;results.append(dict(case=case,user_mode=not bool(s.sr&0x2000),CPU=media.scheduler.cpu_dict(b),RAM_sha256=sha(rb),PC_trace=pcs,private_frame_and_source304E_progress_match=True));save(out/'cases.json',results)
        report=dict(status='source_VBI_IRQ2_frame_304E_progress_RTE_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=32,source_handler=True,period_or_global_scheduling_verified=False,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,limits=['Explicit TOM VBI event at an unmasked boundary;user/supervisor inputCPU/private frames. No period/global timing,masked/pending/concurrent interrupts or full game adoption proof.']);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/VBI-event-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.core.CDIntfCloseImage();runtime.oracle.close()
if __name__=='__main__':main()
