"""Native CPU + Unicorn ordered bus + fixed C for three source media interfaces.

Shared pinned hardware models handle MMIO/blitter/ignored cartridge writes.
No GPU/DSP execution or frames are requested; loading audio code is not audio
playback. Complete hardware snapshots and ROM retention are compared.
"""
import ctypes as c
import hashlib
import json
import os
import random
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as scheduler
import check_biwn_world_cpu as world_cpu
import generate_biwn_media_setup_cpu as generator

ROOT=generator.ROOT
CPU=scheduler.CPU
Bus=scheduler.cleanup.world.Bus
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
STOP=0x190000
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()


class Runtime:
    def __init__(self,library,rows,diagnostic_core=None):
        self.oracle=scheduler.Native(diagnostic_core=diagnostic_core);self.device=self.oracle.device;self.core=self.oracle.lib
        self.rows={r['address']:r for r in rows};self.lib=c.CDLL(str(library))
        self.fn=self.lib.biwn_media_setup_cpu_call
        self.body=self.lib.biwn_media_setup_cpu_body
        for fn in [self.fn,self.body]:
            fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
        self.rom=c.c_void_p.in_dll(self.core,'jaguarMainROM').value
        self.core.DSPGetRAM.restype=c.c_void_p
        self.core.GPUGetRAM.restype=c.c_void_p
        self.tom=(c.c_uint8*0x4000).in_dll(self.core,'tomRam8')
        self.readers={};self.writers={}
        for width in [1,2,4]:
            rd=getattr(self.core,'m68k_read_memory_'+str(width*8));rd.argtypes=[c.c_uint32];rd.restype=c.c_uint32;self.readers[width]=rd
            wr=getattr(self.core,'m68k_write_memory_'+str(width*8));wr.argtypes=[c.c_uint32,c.c_uint32];wr.restype=None;self.writers[width]=wr
        self.savers={}
        for name in ['DSP','GPU','TOM','JERRY','DAC']:
            fn=getattr(self.core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t;self.savers[name]=fn

    def reset(self,ram,seed):
        self.device.seed(ram,1)
        self.core.JERRYReset();self.core.DSPReset()
        # GPUReset fills local RAM from an advancing emulator PRNG. Supply
        # identical declared RAM inputs instead of comparing different resets.
        c.memmove(self.core.GPUGetRAM(),bytes([(seed*11+0xcc)&255])*4096,4096)
        c.memmove(self.core.DSPGetRAM(),bytes([(seed*41+0x5a)&255])*8192,8192)
        c.memmove(self.rom+0x2000,bytes([(seed*73+0xa5)&255])*0x100000,0x100000)
        self.trace=hashlib.sha256();self.trace_count=0;self.errors=[];self.bus_events=[]

    def observe(self,kind,address,width,value):
        self.trace.update(struct.pack('>BBII',kind,width,address&0xffffff,value&0xffffffff));self.trace_count+=1
        if len(self.bus_events)<24:self.bus_events.append([kind,hex(address),width,hex(value)])

    def read(self,address,width):
        address&=0xffffff
        value=self.readers[width](address)&((1<<(width*8))-1)
        self.observe(0,address,width,value);return value

    def write(self,address,width,value):
        address&=0xffffff;value&=(1<<(width*8))-1
        self.observe(1,address,width,value);self.writers[width](address,value)

    def snapshot(self):
        states={}
        for name,fn in self.savers.items():
            raw=c.create_string_buffer(200000)
            size=fn(raw);assert 0<size<=len(raw),(name,size)
            states[name]=dict(size=size,sha256=sha(raw.raw[:size]))
        states['TOM_raw_registers_and_RAM']=sha(bytes(self.tom))
        states['cart_ROM_802000_902000']=sha(c.string_at(self.rom+0x2000,0x100000))
        return dict(hardware=states,main_RAM_sha256=sha(self.device.ram()),ordered_bus_sha256=self.trace.hexdigest(),
            ordered_bus_events=self.trace_count,first_bus_events=list(self.bus_events),device=self.device.stats())

    def seed_cpu(self,state):
        core=self.core;core.m68k_pulse_reset();core.m68k_set_irq(0)
        core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,state.ssp)
        core.m68k_set_reg(17,0);core.m68k_set_reg(15,state.usp)
        core.m68k_set_reg(17,state.sr)
        for i,value in enumerate(state.registers):core.m68k_set_reg(i,value)
        core.m68k_set_reg(16,state.pc)

    def cpu(self):
        state=CPU();state.registers[:]=[self.core.m68k_get_reg(None,i) for i in range(16)]
        state.pc=self.core.m68k_get_reg(None,16);state.sr=self.core.m68k_get_reg(None,17)
        state.usp=self.oracle.prefix[16] if state.sr&0x2000 else state.registers[15]
        state.ssp=state.registers[15] if state.sr&0x2000 else self.oracle.prefix[17]
        return state

    def native(self,ram,initial,seed,coverage):
        self.reset(ram,seed);self.seed_cpu(initial);steps=0
        while steps<1100000:
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:break
            assert pc in self.rows,hex(pc)
            coverage.add(pc);self.core.m68k_execute(1);steps+=1
        else:raise AssertionError(('Native media work bound',hex(pc)))
        return self.device.ram(),self.cpu(),{**self.snapshot(),'CPU_steps':steps}

    def unicorn(self,ram,initial,seed,coverage):
        self.reset(ram,seed)
        engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        engine.mem_map(0,0x200000);engine.mem_map(0x800000,0x110000);engine.mem_map(0xf00000,0x20000)
        engine.mem_write(0,ram);engine.reg_write(UC_M68K_REG_SR,initial.sr)
        for reg,value in zip(REGS,initial.registers):engine.reg_write(reg,value)
        def code(cpu,address,size,_):assert address in self.rows,hex(address);coverage.add(address)
        def read(cpu,access,address,width,value,_):cpu.mem_write(address,self.read(address,width).to_bytes(width,'big'))
        def write(cpu,access,address,width,value,_):self.write(address,width,value)
        engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write)
        engine.emu_start(initial.pc,STOP,count=1100000,timeout=30000000)
        assert engine.reg_read(UC_M68K_REG_PC)==STOP
        # Full private main RAM reflects source bus writes, including both
        # source MOVEM frames and the original RTS return read.
        return self.device.ram(),self.snapshot()

    def translated(self,ram,initial,seed,**options):
        self.reset(ram,seed);state=CPU.from_buffer_copy(bytes(initial))
        types=[scheduler.cleanup.world.R8,scheduler.cleanup.world.R16,scheduler.cleanup.world.R32,
            scheduler.cleanup.world.W16,scheduler.cleanup.world.W32,W8]
        def reader(width):
            def callback(_,address,out):
                if options.get('fail')==('read',width):return 1
                try:out[0]=self.read(address,width);return 0
                except Exception as error:self.errors.append(repr(error));return 1
            return callback
        def writer(width):
            def callback(_,address,value):
                if options.get('fail')==('write',width):return 1
                try:self.write(address,width,value);return 0
                except Exception as error:self.errors.append(repr(error));return 1
            return callback
        callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if 'missing' in options:callbacks[options['missing']]=types[options['missing']]()
        bus=Bus(*callbacks[:5],scheduler.cleanup.world.CALL(),None,0)
        service=world_cpu.SERVICE() if options.get('null_service') else world_cpu.SERVICE(lambda *_:1)
        if options.get('bad_pc'):state.pc=0
        before=bytes(state)
        status=self.fn(None if options.get('null_bus') else c.byref(bus),None if options.get('null_cpu') else c.byref(state),
            callbacks[5],service,None,options.get('budget',1100000),options.get('stop_flag',0))
        return self.device.ram(),state,{**self.snapshot(),'status':status,'CPU_unchanged':bytes(state)==before,'errors':self.errors}


def main():
    out=ROOT/'verification/biwn-media-setup-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'media-setup-fullCPU-generation.json').read_text())
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libmedia-setup.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_media_setup_cpu.c'),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.txt').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    runtime=Runtime(library,mapping['instructions_decoded']);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    results=[];coverage=set();uc_coverage=set();rng=random.Random(0x18160e840)
    try:
        for entry in generator.RANGES:
            for supervisor in [False,True]:
                for seed in [0,1,2]:
                    case=len(results);save(out/'status.json',dict(status='running',case=case,entry=hex(entry)))
                    initial=CPU();initial.registers[:]=[rng.getrandbits(32) for _ in range(15)]+[0x1ff000 if supervisor else 0x1fe000]
                    initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.pc=entry;initial.sr=0x700|(0x2000 if supervisor else 0)|[0,15,31][seed]
                    ram=bytearray(snapshot);sp=initial.registers[15];ram[sp:sp+4]=STOP.to_bytes(4,'big');ram=bytes(ram)
                    left,expected,native=runtime.native(ram,initial,seed,coverage)
                    middle,independent=runtime.unicorn(ram,initial,seed,uc_coverage)
                    right,actual,rebuilt=runtime.translated(ram,initial,seed)
                    if left!=right or middle!=right or bytes(expected)!=bytes(actual) or native['hardware']!=rebuilt['hardware'] or independent['hardware']!=rebuilt['hardware'] or (independent['ordered_bus_sha256'],independent['ordered_bus_events'])!=(rebuilt['ordered_bus_sha256'],rebuilt['ordered_bus_events']):
                        save(out/'mismatch.json',dict(case=case,entry=hex(entry),CPU_native=scheduler.cpu_dict(expected),CPU_C=scheduler.cpu_dict(actual),native=native,Unicorn=independent,C=rebuilt,
                            RAM_diff=[hex(i) for i,(a,b) in enumerate(zip(left,right)) if a!=b][:30],Unicorn_RAM_diff=[hex(i) for i,(a,b) in enumerate(zip(middle,right)) if a!=b][:30]))
                        raise AssertionError(str(out/'mismatch.json'))
                    assert rebuilt['status']==0 and not rebuilt['device']['GPUExec1_calls'] and not rebuilt['device']['game_frames_executed']
                    if entry==0xe840:
                        image=bytearray(ram[0x8460:0x85e0])
                        image[0x130:0x134]=(0).to_bytes(4,'big')
                        image[0x134:0x138]=(0x0481db08).to_bytes(4,'big')
                        assert c.string_at(runtime.core.DSPGetRAM()+16,384)==image
                    if entry==0xdc7c:
                        assert c.string_at(runtime.rom+0x2000,0x100000)==bytes([(seed*73+0xa5)&255])*0x100000
                    results.append(dict(case=case,entry=hex(entry),supervisor=supervisor,seed=seed,CPU=scheduler.cpu_dict(actual),native=native,Unicorn=independent,C=rebuilt))
                    save(out/'fixtures.json',results)
        save(out/'coverage.json',dict(native_PC_coverage=sorted(coverage),Unicorn_PC_coverage=sorted(uc_coverage)))
        assert coverage==uc_coverage==set(runtime.rows)
        guards=[];base=CPU();base.registers[:]=[0]*15+[0x1fe000];base.pc=0xe840;base.usp=0x1fe000;base.ssp=0x1ff000;base.sr=0x700
        ram=bytearray(snapshot);ram[base.registers[15]:base.registers[15]+4]=STOP.to_bytes(4,'big');ram=bytes(ram)
        for options in [dict(missing=i) for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2),dict(bad_pc=True),dict(budget=1)]:
            _,_,record=runtime.translated(ram,base,0,**options)
            expected=7 if options.get('bad_pc') else 4 if options.get('budget')==1 else 1
            assert record['status']==expected and record['CPU_unchanged'],(options,record)
            guards.append(dict(options=options,status=record['status']))
        for failure in [('read',4),('write',4)]:
            _,_,record=runtime.translated(ram,base,0,fail=failure)
            assert record['status']==2 and record['CPU_unchanged'],(failure,record)
            guards.append(dict(failure=failure,status=record['status']))
        record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='media_setup_native_Unicorn_C_fullCPU_RAM_hardware_and_ordered_bus_match',directory=str(out),cases=len(results),
            source_instruction_coverage=[len(coverage),len(runtime.rows)],native_CPU_steps=sum(x['native']['CPU_steps'] for x in results),
            host_guards=len(guards),guards=guards,source_sha256=mapping['source_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=command,
            pinned_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),
            actual_DSP_image_copy_bytes=384,cart_ROM_writes_ignored_and_contents_retained=True,full_main_RAM_and_private_frames_compared=True,
            DSP_source_postcopy_data_writes={'0xf1b140':'0x00000000','0xf1b144':'0x0481db08'},
            supplied_equal_GPU_and_DSP_RAM_inputs=True,
            full_CPU_SR_USP_SSP_compared=True,serialized_GPU_DSP_TOM_JERRY_DAC_and_TOM_RAM_compared=True,Unicorn_C_ordered_bus_compared=True,
            original_CPU_execution_on_C_side=False,original_GPU_or_DSP_execution_requested=False,game_frames_executed=0,
            new_published_components=0,movie_state_machine_verified=False,audio_playback_verified=False,merchant_dialogue_verified=False,whole_game_complete=False,
            limits=['Three standalone source setup routines, supplied incoming registers/stacks/ROM poison patterns and interrupt mask7; no unmasked interrupt execution or physical hardware accuracy.',
                'Shared pinned emulator implements blitter/MMIO and ignored cartridge writes. Source DSP image is copied and control registers initialized; DSP program execution, video GPU overlay, streaming, timing/audio/dialogue integration are unverified.'])
        save(out/'report.json',record);save(ROOT/'verification/biwn-media-setup-cpu-checks.json',record);save(out/'status.json',dict(status='terminal_pass'))
        print(json.dumps(dict(directory=str(out),cases=len(results),source_instructions=len(coverage),host_guards=len(guards))))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()


if __name__=='__main__':main()
