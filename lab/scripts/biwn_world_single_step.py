"""One source instruction per C world dispatch; timing installed separately."""
import ctypes as c,types
import check_biwn_media_setup_cpu as media

def install(runtime):
    fn=runtime.lib.biwn_source_CPU_step;fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),type(runtime.callbacks[5]),type(runtime.service),c.c_void_p];fn.restype=c.c_int
    count=runtime.lib.biwn_instruction_observer_count;count.restype=c.c_uint64
    def step(self,s):
        self.C_CPU=s;pc=s.pc
        if pc==0xe4c0:self.begin_poll()
        if pc in [0x304e,0x303c,0x3042,0x4088]:
            if pc==0x304e:self.bios(s,pc)
            else:self.startup_provider(s,pc)
            s.pc=self.read(s.registers[15],4);s.registers[15]+=4
            if s.sr&0x2000:s.ssp=s.registers[15]
            else:s.usp=s.registers[15]
            return
        before=count();status=fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None)
        assert status in [0,6]and count()==before+1 and not self.errors,('world source step',hex(pc),status,self.errors)
        if pc==0xe53a:self.end_poll()
        command=self.core.GPUReadLong(0xf03204,6)
        if command==0x4320:self.pending_movement=False;self.run_movement_request()
        elif command in [0x4b00,0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:self.pending_render=None;self.run_render_request(command)
    runtime.world_single_step=types.MethodType(step,runtime)
