"""Actual game180000 loader to4000 with source BIOS/marker GPU/boot GPU.

Initial60000byte BIOS-loaded game stub/userROM/device seed is supplied.
Firmware TOC prelude uses declared host API frames; CPU then follows the
actual game prefix/JMP4000. Controller ticks and VCOUNT remain providers.
"""
import ctypes as c,hashlib,json,struct
from pathlib import Path
import check_biwn_media_setup_cpu as media
import check_biwn_full_video_cpu_gpu as video
import check_biwn_movie_GPU as gpu
import check_biwn_dsp_media_audio as dsp
from check_biwn_game_firstboot_GPU import Bus as BootBus
from check_biwn_main_GPU_boot import W16
ROOT=media.ROOT;sha=media.sha
class GameFirstbootMixin:
    def __init__(self,*args,**kwargs):
        self.firstboot_active=False;self.firstboot_transport=False
        super().__init__(*args,**kwargs);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        self.firstboot_rows={r['address']for r in json.loads((session/'game-firstboot-fullCPU-generation.json').read_text())['instructions_decoded']}
        self.firstboot_call=self.lib.biwn_game_firstboot_cpu_call;self.firstboot_call.argtypes=self.fn.argtypes;self.firstboot_call.restype=c.c_int
        self.marker_setup=self.lib.biwn_bios_marker_setup_cpu_body;self.marker_setup.argtypes=self.fn.argtypes;self.marker_setup.restype=c.c_int
        self.marker_run=self.lib.biwn_gpu_cd_marker_ISR_run;self.marker_run.argtypes=self.CD_GPU_run.argtypes;self.marker_run.restype=c.c_int
        self.marker_assert=self.lib.biwn_gpu_cd_marker_ISR_assert;self.marker_assert.argtypes=self.CD_GPU_assert.argtypes;self.marker_assert.restype=c.c_int
        self.firstboot_GPU=self.lib.biwn_game_firstboot_GPU_run;self.firstboot_GPU.argtypes=[c.POINTER(BootBus),c.POINTER(gpu.State),c.c_uint32,c.c_uint32];self.firstboot_GPU.restype=c.c_int
        self.core.GPUReadByte.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadByte.restype=c.c_uint8
        def observer(_,pc):self.gpu_trace.update(pc.to_bytes(4,'big'));self.gpu_blocks+=1
        self.fb_callbacks=[gpu.R8(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadByte(a,3)),0)[1]),gpu.R16(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(self.core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(self.core.GPUWriteLong(a,v,3),0)[1]),gpu.OBS(observer)]
        self.fb_bus=BootBus(*self.fb_callbacks,None);parent=self.service
        def service(_,bus,cpu,target):
            if self.firstboot_active and target in self.firstboot_rows:
                self.fb_cpu_trace.update(target.to_bytes(4,'big'));self.fb_cpu_steps+=1;self.fb_CPU_coverage.add(target);return 0
            if self.firstboot_active and target==0x3060:
                self.BIOS_calls.append(dict(target=hex(target),D0=cpu.contents.registers[0],A0=cpu.contents.registers[8],A1=cpu.contents.registers[9],implementation='actual_marker_setup_CPU'))
                return self.marker_setup(bus,cpu,self.callbacks[5],self.service,None,100000,0)
            if self.firstboot_active and target in [0x303c,0x304e,0x3042,0x3712]:
                if target==0x303c:self.fb_request=dict(D0=cpu.contents.registers[0],D1=cpu.contents.registers[1],D2=cpu.contents.registers[2],A0=cpu.contents.registers[8],A1=cpu.contents.registers[9])
                if target==0x304e:self.transport_tick()
                old=self.transport_active;self.transport_active=True
                try:return self.transport_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
                finally:self.transport_active=old
            return parent(_,bus,cpu,target)
        self.service=media.world_cpu.SERVICE(service)
        self.core.DACStateLoad.argtypes=[c.c_void_p,c.c_uint32];self.core.DACStateLoad.restype=c.c_size_t
        self.core.JERRYStateLoad.argtypes=[c.c_void_p];self.core.JERRYStateLoad.restype=c.c_size_t
        # Canonicalize DAC rate-derived state before preserving the shared,
        # pre-execution initial fixture. No earlier game result is captured.
        d=self.serial_state('DAC');assert self.core.DACStateLoad(c.create_string_buffer(d),9)==len(d)
        self.initial_serial_fixture={name:self.serial_state(name)for name in ['DAC','JERRY']}
        for name,data in self.initial_serial_fixture.items():(self.out/f'initial-{name}-state.bin').write_bytes(data)
    def serial_state(self,name):
        b=c.create_string_buffer(200000);n=self.savers[name](b);assert 0<n<=len(b);return b.raw[:n]
    def prepare_initial_serial_fixture(self):
        d=self.initial_serial_fixture['DAC'];j=self.initial_serial_fixture['JERRY']
        assert self.core.DACStateLoad(c.create_string_buffer(d),9)==len(d)
        assert self.core.JERRYStateLoad(c.create_string_buffer(j))==len(j)
        assert all(self.serial_state(name)==value for name,value in self.initial_serial_fixture.items())
    def read(self,a,w):
        if self.firstboot_active and self.mode=='C' and self.transport_active and a==0xdfff00 and w==4:
            self.transport_tick();return media.Runtime.read(self,a,w)
        if self.firstboot_active and self.mode=='C' and a==0xf02114 and w==4 and self.gpu.control&1 and int.from_bytes(bytes(self.gpu.local_RAM[0x800:0x804]),'big')==1:
            self.run_firstboot_GPU(0xf03328)
        return super().read(a,w)
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.firstboot_active and self.mode=='C' and a==0xf02114 and w==4 and v==1 and self.gpu.pc==0xf03200:
            self.run_firstboot_GPU(0xf032ce)
    def run_firstboot_GPU(self,stop):
        self.gpu_trace=hashlib.sha256();self.gpu_blocks=0;counter=self.gpu_counter.value
        if self.mode=='native':
            image=c.string_at(self.core.GPUGetRAM(),4096);delays=0
            for _ in range(1000000):
                pc=self.core.GPUGetPC()
                if pc==stop:break
                self.gpu_trace.update(pc.to_bytes(4,'big'));self.gpu_blocks+=1;word=int.from_bytes(image[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if word>>10 in [52,53]and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError('Game prefix GPU bound')
            instructions=self.gpu_blocks+delays;raw=video.gpu_state(self.core)[0][:4396]
        else:
            before=self.gpu.instructions;status=self.firstboot_GPU(c.byref(self.fb_bus),c.byref(self.gpu),1000000,stop);assert status==0,(status,hex(self.gpu.pc))
            instructions=self.gpu.instructions-before;raw=video.logical(self.gpu);assert self.gpu_counter.value==counter;self.mirror_transport_GPU()
        self.fb_GPU_calls.append(dict(stop=hex(stop),blocks=self.gpu_blocks,instructions=instructions,PC_sha256=self.gpu_trace.hexdigest(),GPU_sha256=media.sha(raw)))
    def transport_tick(self):
        if not self.firstboot_active:return super().transport_tick()
        idle=self.core.GPUGetPC()if self.mode=='native'else self.gpu.pc;assert idle==0xf032ce,hex(idle)
        self.mirror_transport_GPU();self.core.BUTCHExec(0);self.fb_ticks+=1
        if self.mode=='C':self.gpu.flags=(self.gpu.flags&~7)|self.gpu.z|(self.gpu.c<<1)|(self.gpu.n<<2)
        if not self.core.GPUReadLong(0xf02100,3)&8:return
        self.gpu_trace=hashlib.sha256();self.gpu_blocks=0;counter=self.gpu_counter.value
        if self.mode=='native':
            code=c.string_at(self.core.GPUGetRAM(),4096);delays=0
            for _ in range(500):
                pc=self.core.GPUGetPC()
                if pc==idle:break
                self.gpu_trace.update(pc.to_bytes(4,'big'));self.gpu_blocks+=1;word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if word>>10 in [52,53]and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError('Firstboot marker IRQ bound')
            instructions=self.gpu_blocks+delays;raw=video.gpu_state(self.core)[0][:4396]
        else:
            before=self.gpu.instructions;assert self.marker_assert(c.byref(self.boot_bus),c.byref(self.gpu))==0
            assert self.marker_run(c.byref(self.boot_bus),c.byref(self.gpu),500,idle)==0
            instructions=self.gpu.instructions-before;raw=video.logical(self.gpu);assert counter==self.gpu_counter.value;self.mirror_transport_GPU()
        self.fb_IRQs+=1;self.fb_irq_digest.update(struct.pack('>III',self.fb_ticks,self.gpu_blocks,instructions)+bytes.fromhex(self.gpu_trace.hexdigest())+raw)
    def firmware_api(self,s,target):
        s.pc=target;s.registers[15]-=4;s.ssp=s.registers[15];self.device.direct(s.registers[15],4,media.STOP)
        if self.mode=='native':
            self.seed_cpu(s)
            for _ in range(100000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==media.STOP:return self.cpu()
                if pc==target:self.entry_bios(self.cpu(),target)
                self.before_entry_CPU(pc);assert pc in self.rows,hex(pc);self.core.m68k_execute(1)
            raise AssertionError('Initial firmware API bound')
        self.entry_bios(s,target);fn=getattr(self.lib,{0x3048:'biwn_bios_controller_cpu_call',0x3006:'biwn_bios_mode_cpu_call',0x305a:'biwn_bios_toc_cpu_call'}[target]);fn.argtypes=self.fn.argtypes;fn.restype=c.c_int
        assert fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,100000,0)==0
        if target==0x305a:self.bios_toc_active=False
        return s
    def firstboot_to_stage(self,ram,case,mode):
        self.firstboot_active=False;self.entry_active=False;self.C_DSP=None;self.pending_overlay=False;video.Runtime.start(self,ram,case%3,mode);self.entry_active=True
        self.BIOS_calls=[];self.music_calls=[];self.queries=[];self.deliveries=[];self.music_started=False;self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0
        if mode=='C':self.C_DSP=dsp.state_from_raw(self.raw_DSP())
        # Supplied firmware GPU stack/register context; no later GPU reseed.
        if mode=='native':
            raw=bytearray(video.gpu_state(self.core)[0]);struct.pack_into('=I',raw,4139+31*4,0xf04000);assert self.core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw)
        else:self.gpu.registers[0][31]=0xf04000;self.mirror_transport_GPU()
        self.tom[6]=0;self.tom[7]=4
        s=media.CPU();s.sr=0x2700;s.registers[15]=s.ssp=0x1fe000;s.usp=0x180000
        s=self.firmware_api(s,0x3048);s.registers[0]=0;s=self.firmware_api(s,0x3006);s.registers[8]=0x2c00;s=self.firmware_api(s,0x305a)
        prelude=dict(CPU=media.scheduler.cpu_dict(s),RAM=media.sha(self.device.ram()),hardware=self.hardware(),BIOS_calls=list(self.BIOS_calls),mode_ticks=self.bios_mode_ticks,TOC_ticks=self.bios_toc_ticks,host_API_frames=True)
        self.fb_ticks=self.fb_IRQs=self.fb_cpu_steps=0;self.fb_CPU_coverage=set();self.fb_GPU_calls=[];self.fb_request=None;self.fb_cpu_trace=hashlib.sha256();self.fb_irq_digest=hashlib.sha256();self.firstboot_active=True
        initial=media.scheduler.cpu_dict(s);s.pc=0x180000
        if mode=='native':
            self.seed_cpu(s)
            for _ in range(3000000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0x4000:break
                if pc in self.firstboot_rows:self.fb_cpu_trace.update(pc.to_bytes(4,'big'));self.fb_cpu_steps+=1;self.fb_CPU_coverage.add(pc)
                if pc==0x1800c8:self.run_firstboot_GPU(0xf032ce)
                if pc==0x180178 and self.core.GPUGetPC()!=0xf03328:self.run_firstboot_GPU(0xf03328)
                if pc in [0x3048,0x3006]:self.entry_bios(self.cpu(),pc)
                if pc==0x3060:self.BIOS_calls.append(dict(target=hex(pc),D0=self.cpu().registers[0],A0=self.cpu().registers[8],A1=self.cpu().registers[9],implementation='actual_marker_setup_CPU'))
                if pc==0x303c:
                    p=self.cpu();self.fb_request=dict(D0=p.registers[0],D1=p.registers[1],D2=p.registers[2],A0=p.registers[8],A1=p.registers[9])
                if pc==0x304e:self.transport_tick()
                if pc in [0x3630,0x36c4,0x371a]:self.transport_tick()
                self.before_entry_CPU(pc);assert pc in self.rows,hex(pc);self.core.m68k_execute(1)
            else:raise AssertionError(('Original game prefix CPU bound',hex(pc)))
            s=self.cpu()
        else:
            guard=self.gpu_counter.value;self.C_CPU=s;status=self.firstboot_call(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,3000000,0);assert status==8,(status,self.errors[-5:],hex(s.pc));assert self.gpu_counter.value==guard
        self.firstboot_active=False;self.entry_active=False
        assert s.pc==0x4000 and media.sha(self.device.ram()[0x4000:0x100000])=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
        return s,dict(resident_install=self.resident_install_summary,firmware_API_prelude=prelude,initial_CPU=initial,CPU=media.scheduler.cpu_dict(s),RAM=media.sha(self.device.ram()),hardware=self.hardware(),source_CPU_steps=self.fb_cpu_steps,source_CPU_PC_sha256=self.fb_cpu_trace.hexdigest(),controller_ticks=self.fb_ticks,GPU_IRQs=self.fb_IRQs,IRQ_trace_state_sha256=self.fb_irq_digest.hexdigest(),GPU_calls=self.fb_GPU_calls,marker_request=self.fb_request,BIOS_calls=list(self.BIOS_calls),game_stage_hostloaded=False,initial60000byte_boot_stub_supplied=True,initial_serial_fixture_supplied=True,initial_serial_fixture_sha256={k:media.sha(v)for k,v in self.initial_serial_fixture.items()},complete_firmware_boot_verified=False)

