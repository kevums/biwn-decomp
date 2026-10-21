"""Original/C BIOS mode plus real pinned BUTCH queue and complete device state."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
class Runtime(media.Runtime):
    def __init__(self,*args):
        super().__init__(*args);self.mode_call=self.lib.biwn_bios_mode_cpu_call;self.mode_body=self.lib.biwn_bios_mode_cpu_body
        for f in [self.mode_call,self.mode_body]:f.argtypes=self.fn.argtypes;f.restype=c.c_int
        self.core.CDROMReset.argtypes=[];self.core.CDROMStateSave.argtypes=[c.c_void_p];self.core.CDROMStateSave.restype=c.c_size_t
        self.core.CDIntfOpenImage.argtypes=[c.c_char_p];self.core.CDIntfOpenImage.restype=c.c_bool;self.core.CDROMInit.argtypes=[];self.core.CDIntfCloseImage.argtypes=[]
        image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
        assert self.core.CDIntfOpenImage(str(image).encode()),'Preserved CDI could not be attached to BUTCH model'
        self.core.CDROMInit()
        self.core.BUTCHExec.argtypes=[c.c_uint32]
    def reset(self,ram,seed):
        super().reset(ram,seed);self.core.CDROMReset()
        for a,w,v in [(0xdfff00,4,0x180000),(0xdfff04,4,0x10000),(0xdfff10,4,7),(0xdfff10,4,1)]:self.write(a,w,v)
        if self.prequeue:self.write(0xdfff0a,2,self.prequeue)
        self.butch_ticks=0
    def tick(self):self.core.BUTCHExec(0);self.butch_ticks+=1
    def read(self,a,w):
        if a==0xdfff00 and w==4:self.tick()
        return super().read(a,w)
    def native(self,ram,initial,seed,coverage):
        self.reset(ram,seed);self.seed_cpu(initial);steps=0
        for _ in range(100000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==media.STOP:break
            assert pc in self.rows,hex(pc);coverage.add(pc)
            if pc==0x3544:self.tick()
            self.core.m68k_execute(1);steps+=1
        else:raise AssertionError(('Native BIOS mode limit',hex(pc)))
        return self.device.ram(),self.cpu(),{**self.snapshot(),'CPU_steps':steps,'BUTCH_ticks':self.butch_ticks}
    def snapshot(self):
        s=super().snapshot();b=c.create_string_buffer(200000);n=self.core.CDROMStateSave(b);assert 0<n<=len(b);s['hardware']['BUTCH_CDROM_full_state']=dict(size=n,sha256=sha(b.raw[:n]));self.core.CDROMStateExtSave.argtypes=[c.c_void_p];self.core.CDROMStateExtSave.restype=c.c_size_t;e=c.create_string_buffer(16);m=self.core.CDROMStateExtSave(e);assert m==9;s['hardware']['BUTCH_timing_extension']=dict(size=m,sha256=sha(e.raw[:m]));return s
    def translated_mode(self,ram,initial,seed):
        self.reset(ram,seed);s=media.CPU.from_buffer_copy(bytes(initial));errors=[]
        def rd(w):
            def callback(_,a,v):v[0]=self.read(a,w);return 0
            return callback
        def wr(w):
            def callback(_,a,v):self.write(a,w,v);return 0
            return callback
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8];callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4)),types[5](wr(1))];bus=media.Bus(*callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        def service(_,passed,cpu,target):
            if target==0x3544:return self.mode_body(passed,cpu,callbacks[5],callback,None,100000,0)
            errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);status=self.mode_call(c.byref(bus),c.byref(s),callbacks[5],callback,None,100000,0);assert not status and not errors,(status,errors,hex(s.pc));return self.device.ram(),s,self.snapshot()
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'bios-mode-fullCPU-generation.json').read_text());out=ROOT/'verification/BIWN-BIOS-mode-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbios-mode.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_bios_mode_cpu.c'),str(src/'biwn_media_setup_cpu.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    runtime=Runtime(library,mapping['instructions_decoded']);bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();ram=bytearray(0x200000);ram[0x3000:0x3e00]=bios[0x84a6:0x92a6];ram[0x1ff000:0x1ff004]=media.STOP.to_bytes(4,'big');rng=random.Random(0x3006c);coverage=set();results=[]
    try:
        for case in range(24):
            runtime.prequeue=[0,0x7001,0x0400][case//8];s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];s.registers[0]=(s.registers[0]&~3)|(case%4);s.pc=0x3006;s.sr=(0x2000 if case%2 else 0)|(case%32);s.usp=0x180000 if s.sr&0x2000 else 0x1ff000;s.ssp=0x1ff000 if s.sr&0x2000 else 0x200000
            save(out/'status.json',dict(status='running',case=case));left,expected,native=runtime.native(bytes(ram),s,case%3,coverage);right,actual,translated=runtime.translated_mode(bytes(ram),s,case%3)
            if left!=right or bytes(expected)!=bytes(actual)or native['hardware']!=translated['hardware']:
                save(out/'mismatch.json',dict(case=case,prequeue=runtime.prequeue,native_CPU=media.scheduler.cpu_dict(expected),C_CPU=media.scheduler.cpu_dict(actual),native_hardware=native['hardware'],C_hardware=translated['hardware'],RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:50]));raise AssertionError(str(out/'mismatch.json'))
            assert int.from_bytes(right[0x3e00:0x3e02],'big')==1 and native['BUTCH_ticks']==runtime.butch_ticks
            results.append(dict(case=case,mode=s.registers[0]&3,prequeued_command=hex(runtime.prequeue),CPU=media.scheduler.cpu_dict(actual),RAM_sha256=sha(right),native_instructions=native['CPU_steps'],complete_CPU_RAM_BUTCH_queue_peripherals_match=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};report=dict(status='actual_user_BIOS3006_mode_DSA_wait_retry_status_source_CPU_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=24,source_instruction_coverage=[len(selected&coverage),len(selected)],covered_PC=sorted(coverage),four_speed_audio_data_modes_verified=True,queued_reply_retry_and_status_branches_verified=True,BUTCH_full_state_compared=True,BIOS_sha256=mapping['BIOS_sha256'],source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,full_BIOS_firmware_boot_verified=False,limits=['Resident BIOS explicitly loaded from suppliedROM84A6 atRAM3000. Actual pinned BUTCH queue/status model provides command15nn->17nn response; prequeued7001 and0400 force source retry/status paths. Preserved internal CDI attached read-only; initial controller register setup is supplied, and one BUTCH tick is delivered at each source3544poll to traverse its4tick DSA response delay.','Source readiness busy-wait executes under declared controller-poll ticks; physicalcontroller timing, all errors/commands/TOC/CDGPUISR/transport/firmwareboot/globalgame remain unverified. Complete CPU/privateRAM and BUTCH full state plus prior GPU/DSP/TOM/JERRY/DAC/cart snapshots compare.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/bios-mode-CPU-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler','covered_PC']}))
    except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.core.CDIntfCloseImage();runtime.oracle.close()
if __name__=='__main__':main()
