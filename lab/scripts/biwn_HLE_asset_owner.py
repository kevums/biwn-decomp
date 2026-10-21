"""Experimental sole platform HLE asset owner, with source VBI progress.

No normalized-track memcpy, captured674byte phase or direct bd848 completion.
HLE stream ticks are still pumped synchronously at source task handoffs.
"""
import ctypes as c
import hashlib,types
import check_biwn_movie_GPU as GPU


def install(runtime):
    core=runtime.core
    core.JaguarCDHLESetActive.argtypes=[c.c_bool];core.JaguarCDHLESetActive(True)
    core.JaguarCDHLEStreamActive.restype=c.c_bool
    core.JaguarCDHLEStreamDest.restype=core.JaguarCDHLEStreamBytes.restype=c.c_uint32
    core.TOMSetPendingVideoInt.argtypes=[];core.m68k_set_irq2.argtypes=[c.c_uint32]
    VBI=runtime.lib.biwn_vbi_event;VBI.argtypes=[c.POINTER(type(runtime.bus)),c.POINTER(type(runtime.entry_CPU))];VBI.restype=c.c_int
    runtime.HLE_asset_VBIs=[]
    def mirror():
        if runtime.mode!='C':return
        raw=c.create_string_buffer(12000);n=core.GPUStateSave(raw);assert n==4416
        image=GPU.logical(runtime.gpu)+raw.raw[4396:n];assert core.GPUStateLoad(c.create_string_buffer(image))==n
    def adopt_GPU():
        if runtime.mode!='C':return
        raw=c.create_string_buffer(12000);assert core.GPUStateSave(raw)==4416
        changed=GPU.state_from_raw(raw.raw);count=runtime.gpu.instructions
        c.memmove(c.byref(runtime.gpu),c.byref(changed),c.sizeof(changed));runtime.gpu.instructions=count
    def API_body(s):
        mirror();status=core._biwn_HLE_API_body(s);adopt_GPU();return status
    class Disc:
        def __init__(self):self.reset()
        def reset(self):self.pending=None;self.requests=[];self.completions=[];self.stops=0
        def start(self,s):
            assert self.pending is None
            start,end=s.registers[8],s.registers[9];assert start==0x1c0000 and start<end<=0x200000
            item=dict(destination_start=start,destination_end=end,bytes=end-start,
                packed_binary_MSF=s.registers[0],sentinel=s.registers[1],
                transport='platform_HLE_sector_and_sentinel_stream',captured_stream_phase_used=False)
            self.requests.append(item);self.pending=item
        def stop(self):self.stops+=1
    runtime.asset_disc=Disc()
    parent=runtime.startup_provider
    def provider(self,s,target):
        if target==0x303c:self.asset_disc.start(s)
        elif target==0x3042:self.asset_disc.stop()
        else:return parent(s,target)
        # Native executes the ordinary HLE hook once with its RTS; compiled
        # C invokes the same platform ABI body once before its virtual RTS.
        if self.mode=='C':assert API_body(s)==0
    runtime.startup_provider=types.MethodType(provider,runtime)
    old_bios=runtime.bios
    def bios(self,s,target):
        if target==0x304e:
            if self.mode=='C':assert API_body(s)==0
            return
        return old_bios(s,target)
    runtime.bios=types.MethodType(bios,runtime)
    def handoff(self,s):
        completed=None;item=self.asset_disc.pending
        if item:
            assert core.JaguarCDHLEStreamDest()==item['destination_start']
            ticks=0;mirror()
            while core.JaguarCDHLEStreamActive():
                assert ticks<200000,'HLE asset tick bound'
                core.JaguarCDHLEStreamTick();ticks+=1
            adopt_GPU()
            visited=[];progress=0
            for VBI_count in range(1,5):
                expected_PC=s.pc;core.TOMSetPendingVideoInt();
                before_INT1=core.m68k_read_memory_16(0xf000e0)
                if self.mode=='native':
                    core.m68k_set_irq2(2);assert core.m68k_get_reg(None,16)==0xe7d4
                    for _ in range(1000):
                        pc=core.m68k_get_reg(None,16)
                        if pc==expected_PC:break
                        visited.append(hex(pc))
                        assert pc in self.rows,hex(pc);core.m68k_execute(1)
                    else:raise AssertionError('Source HLE progress VBI bound')
                else:
                    core.m68k_set_irq(0);assert VBI(c.byref(self.bus),c.byref(s))==0
                    assert self.body_video(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
                    assert s.pc==expected_PC
                progress=self.device.read(0xbd848,4)
                if progress>=item['destination_end']:break
            if progress<item['destination_end']:
                from pathlib import Path
                import json
                base=self.device.read(0x3074,4)
                (self.out/(self.mode+'-HLE-VBI-debug.json')).write_text(json.dumps(dict(item=item,progress=progress,INT1_before=before_INT1,
                    HLE_stream_ticks=ticks,source_GPU_data_base=hex(base),GPU_data=hex(core.GPUReadLong(base,3)),visited=visited),indent=2)+'\n')
                raise AssertionError((item,progress))
            data=self.device.ram()[item['destination_start']:item['destination_end']]
            item['sha256']=hashlib.sha256(data).hexdigest();item['HLE_stream_ticks']=ticks;item['source_completion_VBIs']=VBI_count
            completed=[dict(bytes=item['bytes'],progress_address=0xbd848,progress_value=progress,
                            completion_by_source_VBI=True,HLE_stream_ticks=ticks)]
            self.asset_disc.completions.extend(completed);self.asset_disc.pending=None
            self.HLE_asset_VBIs.append(dict(CPU=__import__('check_biwn_media_setup_cpu').scheduler.cpu_dict(self.cpu() if self.mode=='native' else s),progress=progress,
                source_completion_VBIs=VBI_count,reference_CPU_steps=len(visited) if self.mode=='native' else None,
                reference_PC_trace=visited if self.mode=='native' else None))
        self.handoffs.append(dict(CPU=__import__('check_biwn_media_setup_cpu').scheduler.cpu_dict(s),context=hex(self.current()),
                                 RAM=hashlib.sha256(self.device.ram()).hexdigest(),hardware=self.hardware(),disc_completed=completed))
    runtime.handoff_event=types.MethodType(handoff,runtime)
