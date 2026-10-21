"""Early CPU initialization helpers against native CPU with declared BIOS/DSP inputs."""
import ctypes as c,json,random,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha;SP=0x1ff000;STOP=0x190000;BIOS={0x3048,0x3006,0x305a};ENTRIES=[0xe6a0,0x1557a,0x17340,0xdff4,0xe942,0xe96c,0xea08]
class Runtime(media.Runtime):
    def __init__(self,*args):
        super().__init__(*args);self.entry_body=self.lib.biwn_entry_setup_cpu_body;self.entry_call=self.lib.biwn_entry_setup_cpu_call
        for f in [self.entry_body,self.entry_call]:f.argtypes=self.fn.argtypes;f.restype=c.c_int
    def provider(self,s,target):
        # Deliberate ABI adversary for firmware bodies, not a TOC implementation.
        value=(target+self.case*1234567)&0xffffffff
        for r in [0,1,8,9]:s.registers[r]=(value*(r+1)+0xaabbccdd)&0xffffffff
        s.sr=(s.sr&0xffe0)|(value&31)
    def read(self,a,w):
        if a==0xf1badc and w==4:
            self.mailbox_reads+=1
            if self.mailbox_reads==3:self.core.DSPWriteLong(a,0,6)
        return super().read(a,w)
    def native_entry(self,ram,state,case):
        self.case=case;self.mailbox_reads=0;self.mode='native';self.reset(ram,case%3);self.seed_cpu(state)
        for a in BIOS:self.device.direct(a,2,0x4e75)
        pcs=[]
        try:
            for _ in range(100000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP:break
                if pc in BIOS:
                    s=self.cpu();self.provider(s,pc)
                    for r in [0,1,8,9]:self.core.m68k_set_reg(r,s.registers[r])
                    self.core.m68k_set_reg(17,s.sr)
                else:
                    assert pc in self.rows,hex(pc);pcs.append(pc)
                    if pc==0xea08:self.read(0xf1badc,4)
                self.core.m68k_execute(1)
            else:raise AssertionError(('native entry limit',hex(pc)))
        finally:
            for a in BIOS:self.device.direct(a,2,int.from_bytes(ram[a:a+2],'big'))
        return self.device.ram(),self.cpu(),self.snapshot()['hardware'],pcs
    def C_entry(self,ram,state,case):
        self.case=case;self.mailbox_reads=0;self.reset(ram,case%3);errors=[]
        def reader(w):
            def cb(_,a,v):v[0]=self.read(a,w);return 0
            return cb
        def writer(w):
            def cb(_,a,v):self.write(a,w,v);return 0
            return cb
        callbacks=[media.scheduler.cleanup.world.R8(reader(1)),media.scheduler.cleanup.world.R16(reader(2)),media.scheduler.cleanup.world.R32(reader(4)),media.scheduler.cleanup.world.W16(writer(2)),media.scheduler.cleanup.world.W32(writer(4)),media.W8(writer(1))];bus=media.Bus(*callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        def service(_,passed,cpu,target):
            if target in BIOS:self.provider(cpu.contents,target);return 0
            if target in [0xe96c,0xea08]:return self.entry_body(passed,cpu,callbacks[5],callback,None,100000,0)
            errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);cpu=media.CPU.from_buffer_copy(bytes(state));status=self.entry_call(c.byref(bus),c.byref(cpu),callbacks[5],callback,None,100000,0);assert not status and not errors,(status,errors)
        return self.device.ram(),cpu,self.snapshot()['hardware']
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'entry-setup-fullCPU-generation.json').read_text());out=ROOT/'verification/BIWN-entry-setup-helpers'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libentry-helpers.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_entry_setup_cpu.c'),str(src/'biwn_media_setup_cpu.c'),'-o',str(library)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert not run.returncode,run.stderr
    runtime=Runtime(library,mapping['instructions_decoded']);runtime.core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x4000c);results=[];coverage=set()
    try:
        for entry in ENTRIES:
            for i in range(8):
                case=len(results);ram=bytearray(baseline);ram[SP:SP+4]=STOP.to_bytes(4,'big');s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];s.pc=entry;s.sr=(0x2000 if case%2 else 0)|((i%8)<<8)|rng.randrange(32);s.usp=0x180000 if s.sr&0x2000 else SP;s.ssp=SP if s.sr&0x2000 else 0x200000
                save(out/'status.json',dict(status='running',case=case,entry=hex(entry)));left,expected,hw,pcs=runtime.native_entry(bytes(ram),s,case);right,actual,observed=runtime.C_entry(bytes(ram),s,case)
                if left!=right or bytes(expected)!=bytes(actual)or hw!=observed:
                    (out/'native-RAM.bin').write_bytes(left);(out/'C-RAM.bin').write_bytes(right);save(out/'mismatch.json',dict(case=case,entry=hex(entry),native_CPU=media.scheduler.cpu_dict(expected),C_CPU=media.scheduler.cpu_dict(actual),native_hardware=hw,C_hardware=observed,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:60]));raise AssertionError(str(out/'mismatch.json'))
                coverage.update(pcs);results.append(dict(case=case,entry=hex(entry),CPU=media.scheduler.cpu_dict(actual),RAM_sha256=sha(right),native_instructions=len(pcs),full_CPU_RAM_private_frames_peripherals_match=True))
        report=dict(status='early_video_heap_list_disc_music_CPU_helpers_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),entries=list(map(hex,ENTRIES)),source_instruction_coverage=[len(coverage),len(mapping['instructions_decoded'])],covered_PC=sorted(coverage),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,full4000caller_verified=False,whole_game_complete=False,limits=['Standalone source helpers with supplied FrozenRAM/CPU/both stack banks, actual default region hardware, three BIOS ABI adversaries and declared DSP mailbox completion after3reads. DSP program copying/control/register effects compare; DSPmusic instructions/firmware/timing are not executed by this proof.','142generated instructions include4000caller and alternate video-region branch not covered here. No globalboot, actualPAL device profile, live timer/scheduler/movie/game or physicalscanout claim.'])
        save(out/'cases.json',results);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/entry-setup-helpers-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler','covered_PC']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
