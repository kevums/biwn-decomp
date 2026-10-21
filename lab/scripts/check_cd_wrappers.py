"""Original CD wrapper register ABI versus portable C, with explicit BIOS fixtures."""
import ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world


def main():
    restore=ROOT/'projects/black-ice-white-noise/restoration';source=restore/'biwn_cd_wrappers.c'
    out=ROOT/'verification/CD-wrappers'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    library=out/'libcd-wrappers.dylib'
    subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));read=lib.biwn_cd_read_wrapper;read.argtypes=[c.POINTER(w.Bus),*[c.c_uint32]*3,c.POINTER(c.c_uint32)];read.restype=c.c_int
    stop=lib.biwn_cd_stop_wrapper;stop.argtypes=[c.POINTER(w.Bus),c.c_uint32,c.POINTER(c.c_uint32)];stop.restype=c.c_int
    atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();mapping=json.loads((ROOT/'verification/main_CPU_execution_coverage-current.json').read_text());manifest=json.loads(Path(mapping['static_manifest']).read_text());instructions=[x for x in manifest['instructions']if 0xd2f0<=int(x['address'],16)<0xd30a]
    for row in instructions:pc=int(row['address'],16);assert atlas[pc:pc+row['size']]==bytes.fromhex(row['bytes'])
    coverage=set();rng=random.Random(0xd2f0303c);rows=[];guards=[]
    for entry,target in [(0xd2f0,0x303c),(0xd306,0x3042)]:
        for case in range(32):
            incoming=rng.getrandbits(32);args=[rng.getrandbits(32)for _ in range(3)];returned=rng.getrandbits(32);original_trace=[]
            cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,atlas);cpu.mem_write(target,b'\x4e\x75');cpu.mem_write(SP,STOP.to_bytes(4,'big')+b''.join(x.to_bytes(4,'big')for x in args));cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.reg_write(UC_M68K_REG_D0,incoming)
            def code(e,pc,width,_):
                if pc==target:
                    values=[e.reg_read(UC_M68K_REG_A0),e.reg_read(UC_M68K_REG_A1),e.reg_read(UC_M68K_REG_D0)]if target==0x303c else[]
                    original_trace.append([target,values,e.reg_read(UC_M68K_REG_D0)]);e.reg_write(UC_M68K_REG_D0,returned)
                else:coverage.add(pc)
            cpu.hook_add(UC_HOOK_CODE,code);cpu.emu_start(entry,STOP,count=20)
            assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
            trace=[]
            def callback(_,which,p,count,out):trace.append([which,list(p[:count])if count else[],out[0]]);out[0]=returned;return 0
            cb=w.CALL(callback);bus=w.Bus(w.R8(),w.R16(),w.R32(),w.W16(),w.W32(),cb,None,0);value=c.c_uint32(0xa55aa55a)
            status=read(c.byref(bus),*args,c.byref(value))if entry==0xd2f0 else stop(c.byref(bus),incoming,c.byref(value))
            assert status==0 and value.value==cpu.reg_read(UC_M68K_REG_D0)==returned and trace==original_trace
            rows.append(dict(entry=hex(entry),case=case,BIOS_call=trace[0],D0=returned))
        for invalid in ['bus','call','out','failure']:
            cb=w.CALL(lambda *unused:1);bus=w.Bus(w.R8(),w.R16(),w.R32(),w.W16(),w.W32(),w.CALL()if invalid=='call'else cb,None,0);value=c.c_uint32(0xa55aa55a);bp=None if invalid=='bus'else c.byref(bus);op=None if invalid=='out'else c.byref(value)
            status=read(bp,*args,op)if entry==0xd2f0 else stop(bp,incoming,op)
            assert status==(3 if invalid=='failure'else 1)and value.value==0xa55aa55a;guards.append(dict(entry=hex(entry),invalid=invalid))
    expected={int(x['address'],16)for x in instructions};assert coverage==expected
    report=dict(status='CD_read_stop_wrapper_original_register_ABI_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),instruction_address_coverage=[len(expected),len(expected)],guards=guards,coordinator_authored=True,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),new_training=False,native_Chat_verified=False,scope='CompleteD2F0..D304 andD306 against bytechecked originalUnicorn: BIOS303C register seedsA0/A1/D0,BIOS3042 noargs,incoming/returnedD0 and returnSP. BIOS responses are fixtures. Host guards added; privateA2 save/restore,otherCPUregisters/CCR,actualBIOS/device behavior,timing andnaturalgameplay excluded.')
    (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/CD-wrappers-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(expected))


if __name__=='__main__':main()
