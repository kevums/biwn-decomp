"""Real BIOS CPU/GPU FIFO asset transport with sourceVBI progress reporting.

Controller ticks and VBI at source handoff are declared scheduling inputs.
No payload memcpy or direct RAM progress completion. Movie transport remains
separate. C-owned processor state persists; MMIO GPU shadow is synchronized.
"""
import ctypes as c,hashlib,json
from pathlib import Path
from check_biwn_media_setup_cpu import world_cpu,ROOT
import check_biwn_full_video_cpu_gpu as video
POLLS={0x3630,0x36c4,0x371a}
class AssetTransfers:
    def __init__(self,owner):
        self.owner=owner;self.manifest=json.loads((ROOT/'verification/biwn-disc-resources.json').read_text());self.reset()
    def reset(self):self.pending=None;self.requests=[];self.completions=[];self.stops=0
    def start(self,start,end,packed):
        assert self.pending is None and start==0x1c0000 and start<end<0x200000
        minute,second,frame=(packed>>16)&255,(packed>>8)&255,packed&255;assert not packed>>24 and second<60 and frame<75
        t=self.manifest['track'];relative=minute*4500+second*75+frame-(t['declared_start_lba']+t['pregap_sectors']+150);offset=relative*2352+self.manifest['captured_CD_buffer_witness']['within_sector_phase']
        item=dict(destination_start=start,destination_end=end,packed_binary_MSF=packed,normalized_track_offset=offset,bytes=end-start,transport='actual_BIOS_CPU_BUTCH_GPU_FIFO_sourceVBI');self.requests.append(item);self.pending=item
    def stop(self):self.stops+=1
    def tick(self,*_):raise AssertionError('Host file-disc payload/progress delivery forbidden')
class AssetTransportMixin:
    def __init__(self,*args,**kwargs):
        self.transport_active=False;self.transport_ticks=0;self.transport_IRQs=[];self.transport_VBIs=[];self.transport_shadow_template=None
        super().__init__(*args,**kwargs);self.asset_disc=AssetTransfers(self)
        self.transport_body=self.lib.biwn_bios_transport_cpu_body;self.transport_body.argtypes=self.fn.argtypes;self.transport_body.restype=c.c_int
        self.CD_GPU_run=self.lib.biwn_gpu_cd_ISR_run;self.CD_GPU_run.argtypes=self.movie_exit.argtypes+[c.c_uint32];self.CD_GPU_run.restype=c.c_int
        self.CD_GPU_assert=self.lib.biwn_gpu_cd_ISR_assert;self.CD_GPU_assert.argtypes=self.control5.argtypes;self.CD_GPU_assert.restype=c.c_int
        self.VBI_event=self.lib.biwn_vbi_event;self.VBI_event.argtypes=[c.POINTER(type(self.bus)),c.POINTER(type(self.entry_CPU))]if hasattr(self,'entry_CPU')else [c.POINTER(type(self.bus)),self.fn.argtypes[1]];self.VBI_event.restype=c.c_int
        # Shared initial controller input: Reset retains inactive sector
        # buffers, so preserve one pre-execution fixture for both paths.
        self.core.CDROMReset();self.core.CDROMStateLoad.argtypes=[c.c_void_p,c.c_uint32];self.core.CDROMStateLoad.restype=c.c_size_t;self.core.CDROMStateExtLoad.argtypes=[c.c_void_p];self.core.CDROMStateExtLoad.restype=c.c_size_t
        b=c.create_string_buffer(200000);n=self.core.CDROMStateSave(b);e=c.create_string_buffer(16);m=self.core.CDROMStateExtSave(e);assert m==9;self.transport_controller_input=(b.raw[:n],e.raw[:m])
        (self.out/'initial-controller-state.bin').write_bytes(self.transport_controller_input[0]);(self.out/'initial-controller-timing.bin').write_bytes(self.transport_controller_input[1])
        self.core.TOMSetPendingVideoInt.argtypes=[];self.core.m68k_set_irq2.argtypes=[c.c_uint32];parent=self.service
        def service(_,bus,cpu,target):
            if self.real_asset_scope() and target in [0x303c,0x3042,0x304e,0x3712]:
                if target==0x303c:self.asset_disc.start(cpu.contents.registers[8],cpu.contents.registers[9],cpu.contents.registers[0])
                if target==0x3042:self.asset_disc.stop()
                before=self.transport_active;self.transport_active=True
                try:return self.transport_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
                finally:self.transport_active=before
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def real_asset_scope(self):return self.loading_active and not self.movie_started
    def reset(self,*args,**kwargs):
        result=super().reset(*args,**kwargs);baseline,extension=self.transport_controller_input;assert self.core.CDROMStateLoad(c.create_string_buffer(baseline),16)==len(baseline);assert self.core.CDROMStateExtLoad(c.create_string_buffer(extension))==len(extension);self.transport_ticks=0;self.transport_IRQs=[];self.transport_VBIs=[];self.transport_active=False;self.transport_shadow_template=None;return result
    def mirror_transport_GPU(self):
        if self.mode!='C':return
        if self.transport_shadow_template is None:
            b=c.create_string_buffer(200000);n=self.core.GPUStateSave(b);self.transport_shadow_template=b.raw[:n]
        raw=bytearray(self.transport_shadow_template);raw[:4396]=video.logical(self.gpu);assert self.core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw)
    def transport_tick(self):
        idle=self.core.GPUGetPC()if self.mode=='native'else self.gpu.pc
        self.mirror_transport_GPU();self.core.BUTCHExec(0);self.transport_ticks+=1
        # This host readiness read materializes live Z/N/C in GPU_FLAGS.
        # Apply the same read side effect to the owned C register cache.
        if self.mode=='C':self.gpu.flags=(self.gpu.flags&~7)|self.gpu.z|(self.gpu.c<<1)|(self.gpu.n<<2)
        if not self.core.GPUReadLong(0xf02100,3)&8:return
        before=self.core.GPUGetPC()if self.mode=='native'else self.gpu.pc;trace=hashlib.sha256();blocks=0;delays=0
        if self.mode=='native':
            code=c.string_at(self.core.GPUGetRAM(),4096)
            for _ in range(200):
                pc=self.core.GPUGetPC()
                if pc==idle:break
                trace.update(pc.to_bytes(4,'big'));blocks+=1;word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if word>>10 in [52,53]and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError(('Asset GPU ISR bound',hex(pc)))
            logical=video.gpu_state(self.core)[0][:4396];instructions=blocks+delays
        else:
            self.gpu_trace=trace;self.gpu_blocks=0;begin=self.gpu.instructions;counter=self.gpu_counter.value
            assert idle in [0xf031ce,0xf032c8],hex(idle);assert self.CD_GPU_assert(c.byref(self.boot_bus),c.byref(self.gpu))==0
            assert self.CD_GPU_run(c.byref(self.boot_bus),c.byref(self.gpu),200,idle)==0;assert self.gpu_counter.value==counter;logical=video.logical(self.gpu);instructions=self.gpu.instructions-begin;blocks=self.gpu_blocks;self.mirror_transport_GPU()
        self.transport_IRQs.append(dict(tick=self.transport_ticks,blocks=blocks,instructions=instructions,PC_sha256=trace.hexdigest(),GPU_sha256=hashlib.sha256(logical).hexdigest()))
    def read(self,a,w):
        if self.mode=='C'and self.transport_active and a==0xdfff00 and w==4:self.transport_tick()
        return super().read(a,w)
    def native_asset_call(self,target,consume_RTS=True):
        s=self.cpu();ret=self.device.read(s.registers[15],4)
        if target==0x303c:self.asset_disc.start(s.registers[8],s.registers[9],s.registers[0])
        if target==0x3042:self.asset_disc.stop()
        before=self.transport_active;self.transport_active=True
        try:
            for _ in range(100000):
                pc=self.core.m68k_get_reg(None,16)
                if (consume_RTS and pc==ret)or(not consume_RTS and pc=={0x303c:0x3710,0x3042:0x3740,0x304e:0x3622}[target]):return
                assert pc in self.rows,hex(pc)
                if pc in POLLS:self.transport_tick()
                self.core.m68k_execute(1)
            raise AssertionError('Native asset CPU call bound')
        finally:self.transport_active=before
    def bios(self,s,target):
        if self.real_asset_scope()and target in [0x303c,0x3042,0x304e]:
            if self.mode=='native':
                # Legacy caller driver consumes outerRTS itself. Execute
                # actual BIOS body/private frames first and publish CPU.
                self.native_asset_call(target,False);actual=self.cpu();c.memmove(c.byref(s),bytes(actual),c.sizeof(s));return
            if target==0x303c:self.asset_disc.start(s.registers[8],s.registers[9],s.registers[0])
            if target==0x3042:self.asset_disc.stop()
            before=self.transport_active;self.transport_active=True
            try:assert self.transport_body(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,100000,0)==0
            finally:self.transport_active=before
            return
        return super().bios(s,target)
    def transport_VBI(self,s):
        assert not s.sr&0x0700,hex(s.sr);expected_PC=s.pc;before=self.transport_active;self.transport_active=True
        try:
            self.core.TOMSetPendingVideoInt()
            if self.mode=='native':
                self.core.m68k_set_irq2(2);assert self.core.m68k_get_reg(None,16)==0xe7d4
                for _ in range(1000):
                    pc=self.core.m68k_get_reg(None,16)
                    if pc==expected_PC:break
                    assert pc in self.rows,hex(pc);self.core.m68k_execute(1)
                else:raise AssertionError('Transport VBI native budget')
            else:
                self.core.m68k_set_irq(0);assert self.VBI_event(c.byref(self.bus),c.byref(s))==0
                assert self.body_video(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
                assert s.pc==expected_PC
            self.transport_VBIs.append(dict(CPU=video.media.scheduler.cpu_dict(self.cpu()if self.mode=='native'else s),progress=self.device.read(0xbd848,4),seek_marker=self.device.read(0x1126a0,4),RAM=hashlib.sha256(self.device.ram()).hexdigest()))
        finally:self.transport_active=before
    def pump_asset_transfer(self,s):
        item=self.asset_disc.pending
        if not item:return
        base=self.device.read(0x3074,4);assert base==0xf03050
        for _ in range(100000):
            self.transport_tick();progress=self.read(base,4)if self.mode=='C'else self.core.GPUReadLong(base,6)
            if progress>=item['destination_end']:break
        else:raise AssertionError(('Asset stream bound',item,hex(progress)))
        self.transport_VBI(s);assert self.device.read(0xbd848,4)==progress
        data=self.device.ram()[item['destination_start']:item['destination_end']];item['sha256']=hashlib.sha256(data).hexdigest();self.asset_disc.completions.append(dict(bytes=item['bytes'],progress_address=0xbd848,progress_value=progress,transport='sourceVBI_reading_actualBIOS304E',source_write_end_inclusive=progress+3));self.asset_disc.pending=None
    def handoff_event(self,s):
        self.pump_asset_transfer(s);return super().handoff_event(s)
    def handoff(self,s):
        self.pump_asset_transfer(s);return super().handoff(s)
