"""Actual movie BIOS/controller/GPU FIFO with explicit nominal transfer pacing."""
import ctypes as c,hashlib
import check_biwn_full_video_cpu_gpu as video
from check_biwn_media_setup_cpu import world_cpu
class MovieTransportMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);parent=self.service;self.movie_transport_active=False
        def service(_,bus,cpu,target):
            if self.movie_scope()and target in [0x303c,0x304e,0x3042,0x3712]:
                if target==0x303c:self.begin_movie_transfer(cpu.contents)
                before=self.transport_active;self.transport_active=True
                try:return self.transport_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
                finally:self.transport_active=before
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def reset(self,*args,**kwargs):
        result=super().reset(*args,**kwargs);self.pending=None;self.movie_controller_ticks=0;self.movie_GPU_IRQs=0;self.movie_VBIs=0;return result
    def transport_tick(self):
        movie=self.movie_scope();before=len(self.transport_IRQs);result=super().transport_tick()
        if movie:self.movie_controller_ticks+=1;self.movie_GPU_IRQs+=len(self.transport_IRQs)-before
        return result
    def movie_scope(self):return self.full_running and self.movie_started
    def real_transport_scope(self):return self.real_asset_scope()or self.movie_scope()
    def begin_movie_transfer(self,s):
        packed=s.registers[0];lba=((packed>>16)&127)*4500+((packed>>8)&255)*75+(packed&255)-150;start=s.registers[8];end=s.registers[9];assert start<end<=0x1ffc00
        self.pending=dict(dest=start,end=end,written=0,lba=lba,index=len(self.deliveries));self.deliveries.append(dict(lba=lba,dest=hex(start),end=hex(end),bytes=end-start,transport='actual_BIOS_CPU_BUTCH_GPU_FIFO'))
        self.queries.append(dict(target='0x303c',D0=s.registers[0],D1=s.registers[1],A0=start,A1=end))
    def native_asset_call(self,target,consume_RTS=True):
        if not self.movie_scope():return super().native_asset_call(target,consume_RTS)
        s=self.cpu();ret=self.device.read(s.registers[15],4)
        if target==0x303c:self.begin_movie_transfer(s)
        before=self.transport_active;self.transport_active=True
        try:
            for _ in range(100000):
                pc=self.core.m68k_get_reg(None,16)
                if (consume_RTS and pc==ret)or(not consume_RTS and pc=={0x303c:0x3710,0x3042:0x3740,0x304e:0x3622}[target]):return
                assert pc in self.rows,hex(pc)
                if pc in [0x3630,0x36c4,0x371a]:self.transport_tick()
                self.core.m68k_execute(1)
            raise AssertionError('Movie BIOS CPU bound')
        finally:self.transport_active=before
    def bios(self,s,target):
        if self.movie_scope()and target in [0x303c,0x304e,0x3042]:
            if self.mode=='native':self.native_asset_call(target,False);actual=self.cpu();c.memmove(c.byref(s),bytes(actual),c.sizeof(s));return
            if target==0x303c:self.begin_movie_transfer(s)
            before=self.transport_active;self.transport_active=True
            try:assert self.transport_body(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,100000,0)==0
            finally:self.transport_active=before
            return
        return super().bios(s,target)
    def advance_dma(self,ticks):
        p=self.pending
        if not p:return
        wanted=min(p['end']-p['dest'],p['written']+ticks*588);target=p['dest']-4+((wanted+4)//32)*32
        if wanted==p['end']-p['dest']:target=p['end']+28
        for _ in range(100000):
            self.transport_tick();base=self.device.read(0x3074,4);progress=self.read(base,4)if self.mode=='C'else self.core.GPUReadLong(base,6)
            if progress>=target:break
        else:raise AssertionError(('Movie FIFO pacing bound',self.mode,self.phase,p,target,progress,hex(self.gpu.pc)if self.mode=='C'else hex(self.core.GPUGetPC()),hex(self.gpu.flags)if self.mode=='C'else hex(self.core.GPUReadLong(0xf02100,3)),hex(self.gpu.control)if self.mode=='C'else hex(self.core.GPUReadLong(0xf02114,3)),hex(self.core.GPUReadLong(0xdfff00,3))))
        p['written']=wanted;self.progress=progress
    def after_dispatch(self,cpu):
        result=super().after_dispatch(cpu)
        if len(self.stages)==1:
            raw=video.gpu_state(self.core)[0][:4396]if self.mode=='native'else video.logical(self.gpu)
            (self.out/f'{self.mode}-movie-first-dispatch-GPU.bin').write_bytes(raw)
        return result
    def source_vbi(self,cpu):
        self.movie_VBIs+=1;return self.transport_VBI(cpu)
