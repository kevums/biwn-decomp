"""Source CPU IRQ sampling for C-owned startup after timed prefix events.

Uses pending/enabled TOM state and SR mask; never fabricates a VBI or clears
RAM progress. The handler still executes synchronously at a CPU boundary.
"""
import ctypes as c
import types,struct
import check_biwn_media_setup_cpu as media

def install(runtime):
    core=runtime.core;core.TOMIRQRequestActive.restype=c.c_int
    fn=runtime.lib.biwn_vbi_event;fn.argtypes=[c.POINTER(type(runtime.bus)),c.POINTER(type(runtime.entry_CPU))];fn.restype=c.c_int
    runtime.pending_CPU_IRQ_events=[]
    core.M68KStateSave.argtypes=[c.c_void_p];core.M68KStateSave.restype=c.c_size_t
    def sample(self,s):
        if (s.sr&0x0700)>=0x0200 or not core.TOMIRQRequestActive():return False
        # Pinned148byte M68K save ABI: deferred level wins over old intLevel.
        # TOM's pending latch alone does not reassert an acknowledged line.
        raw=c.create_string_buffer(256);size=core.M68KStateSave(raw);assert size==148,size
        deferred,queued=struct.unpack_from('=ii',raw.raw,140)
        level=queued if deferred else struct.unpack_from('=i',raw.raw,80)[0]
        if level<=((s.sr>>8)&7):return False
        assert level==2,level
        before=media.scheduler.cpu_dict(s);pc=s.pc
        core.m68k_set_irq(0);core.m68k_set_irq2(0)
        assert fn(c.byref(self.bus),c.byref(s))==0
        assert self.body_video(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
        assert s.pc==pc
        self.pending_CPU_IRQ_events.append(dict(CPU_before=before,CPU_after=media.scheduler.cpu_dict(s),source_handler=0xe7d4,IRQ_level=level,no_new_video_event_injected=True))
        return True
    runtime.sample_pending_CPU_IRQ=types.MethodType(sample,runtime)
