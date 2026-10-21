"""Separate sourceE00A/BIOS3000 caller test from a supplied postmovie fixture.

No claim that this host-invoked caller is reached by the current game path.
GPU pipeline tail/controller baseline are supplied; GPU instructions do not run.
"""
import ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
class Runtime(media.Runtime):
    def __init__(self,library,rows,gpu_input):
        super().__init__(library,rows);self.gpu_input=gpu_input;self.calls=[];self.active_mode='native'
        self.reload=self.lib.biwn_GPU_boot_cpu_call;self.bios=self.lib.biwn_bios_setup_cpu_body
        for f in [self.reload,self.bios]:f.argtypes=self.fn.argtypes;f.restype=c.c_int
        for name in ['CDROM','CDROMStateExt']:
            f=getattr(self.core,'CDROMStateSave'if name=='CDROM'else 'CDROMStateExtSave');f.argtypes=[c.c_void_p];f.restype=c.c_size_t;self.savers[name]=f
        self.core.CDROMReset();self.core.CDROMStateLoad.argtypes=[c.c_void_p,c.c_uint32];self.core.CDROMStateLoad.restype=c.c_size_t
        self.core.CDROMStateExtLoad.argtypes=[c.c_void_p];self.core.CDROMStateExtLoad.restype=c.c_size_t
        self.core.GPUStateLoad.argtypes=[c.c_void_p];self.core.GPUStateLoad.restype=c.c_size_t
        self.controller=[]
        for name in ['CDROM','CDROMStateExt']:
            b=c.create_string_buffer(200000);n=self.savers[name](b);self.controller.append(b.raw[:n])
        def call(bus,cpu,w8,unused,ctx,budget,yield_flag):
            self.active_mode='C'
            def service(_,b,s,target):
                assert target==0x3000;self.record(s.contents)
                return self.bios(b,s,w8,svc,None,budget,0)
            svc=media.world_cpu.SERVICE(service)
            return self.reload(bus,cpu,w8,svc,None,budget,yield_flag)
        self.fn=call
        self.counter=c.c_uint32.in_dll(self.core,'gpu_exec_opcode_count');old=self.core.m68k_execute
        def execute(cycles):
            assert self.active_mode=='native','Original CPU forbidden on C'
            if self.core.m68k_get_reg(None,16)==0x3000:self.record(self.cpu())
            return old(cycles)
        self.core.m68k_execute=execute
    def record(self,s):
        self.calls.append(dict(D0=s.registers[0],A0=s.registers[8],A1=s.registers[9],return_PC=hex(self.device.read(s.registers[15],4))))
    def reset(self,*args):
        super().reset(*args);self.calls=[];self.active_mode='native'
        b=c.create_string_buffer(200000);n=self.savers['GPU'](b);raw=bytearray(b.raw[:n]);raw[:4396]=self.gpu_input
        assert self.core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==n
        assert self.core.CDROMStateLoad(c.create_string_buffer(self.controller[0]),16)==len(self.controller[0])
        assert self.core.CDROMStateExtLoad(c.create_string_buffer(self.controller[1]))==len(self.controller[1])
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    proof=json.loads((ROOT/'verification/movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json').read_text());fixture=Path(proof['directory'])
    assert json.loads((fixture/'status.json').read_text())['status']=='terminal_pass'
    ram=(fixture/'case-0-C-final-RAM.bin').read_bytes();gpu=(fixture/'C-movie_exit-GPU-after.bin').read_bytes();assert len(gpu)==4396
    mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['GPU-boot','bios-setup']]
    rows=sum([x['instructions_decoded']for x in mappings],[])
    out=ROOT/'verification/BIWN-GPU-reload-real-BIOS'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_GPU_boot_cpu.c','biwn_bios_setup_cpu.c','biwn_media_setup_cpu.c'];lib=out/'libGPU-reload.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(lib)]
    build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    runtime=Runtime(lib,rows,gpu);coverage=set();results=[];rng=random.Random(0xe00a3000)
    try:
        for case in range(12):
            s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];s.pc=0xe00a;s.sr=(0x2000 if case%2 else 0)|((case%8)<<8)|rng.randrange(32);s.usp=0x180000 if s.sr&0x2000 else 0x1ff000;s.ssp=0x1ff000 if s.sr&0x2000 else 0x1fe000
            data=bytearray(ram);data[0x1ff000:0x1ff004]=media.STOP.to_bytes(4,'big');save(out/'status.json',dict(status='running',case=case))
            begin=runtime.counter.value;left,a,n=runtime.native(bytes(data),s,case%3,coverage);native_calls=list(runtime.calls)
            right,b,t=runtime.translated(bytes(data),s,case%3)
            if left!=right or bytes(a)!=bytes(b) or n['hardware']!=t['hardware']or native_calls!=runtime.calls or t['status']:
                save(out/'mismatch.json',dict(case=case,native_CPU=media.scheduler.cpu_dict(a),C_CPU=media.scheduler.cpu_dict(b),native_hardware=n['hardware'],C_hardware=t['hardware'],native_calls=native_calls,C_calls=runtime.calls,errors=t['errors'],status=t['status']));raise AssertionError(str(out/'mismatch.json'))
            assert runtime.counter.value==begin and len(runtime.calls)==1 and runtime.calls[0]['return_PC']=='0xe024'
            assert int.from_bytes(right[0x3074:0x3078],'big')==0xf03050
            results.append(dict(case=case,supervisor=bool(s.sr&0x2000),native_instructions=n['CPU_steps'],CPU=media.scheduler.cpu_dict(b),RAM_sha256=sha(right),hardware=t['hardware'],BIOS_calls=list(runtime.calls)));save(out/'cases.json',results)
        selected={r['address']for r in rows};assert selected<=coverage
        report=dict(status='separate_sourceE00A_actual_BIOS3000_caller_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(selected&coverage),len(selected)],GPU_original_execution=False,actual_BIOS3000=True,CPU_private_RAM_full_peripherals_controller_and9byte_extension_match=True,source_fixture=str(fixture),postmovie_mainRAM_sha256=sha(ram),postmovie_logicalGPU_sha256=sha(gpu),host_invoked_caller=True,reached_game_reload_caller=False,whole_game_complete=False,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),limits=['Separate host-invoked sourceE00A from supplied saved postmovie RAM/logicalGPU; initial CPU/device/controller input and GPU pipeline tail supplied. Not continuous source scheduling or a reached game reload call.', 'Original/C executes source159long mainGPU copy and actual resident BIOS3000 vector/56long CDISR installation, with full CPU/SR/USP/SSP/privateRAM/peripherals/controller baseline+9byte extension comparison. GPU instructions do not execute; full firmware/global timing/playability unverified.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/GPU-reload-real-BIOS-checks.json',report);print(json.dumps(dict(status=report['status'],directory=str(out),cases=len(results),coverage=report['source_instruction_coverage'])))
    except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
