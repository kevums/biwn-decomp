"""Experimental direct one-instruction C startup, retaining periodic timing."""
import ctypes as c,types
import check_biwn_media_setup_cpu as media

def install(runtime):
    fn=runtime.lib.biwn_source_CPU_step
    fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),type(runtime.callbacks[5]),type(runtime.service),c.c_void_p];fn.restype=c.c_int
    count=runtime.lib.biwn_instruction_observer_count;count.restype=c.c_uint64
    runtime.single_step_count=0
    def platform_RTS(s):
        s.pc=runtime.read(s.registers[15],4);s.registers[15]+=4
        if s.sr&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
    def step(self,s):
        self.C_CPU=s;pc=s.pc
        if pc==0xddd8:self.clock_tick();self.clock_ticks+=1
        if hasattr(self,'sample_pending_CPU_IRQ')and self.sample_pending_CPU_IRQ(s):return
        before=count()
        if pc in [0x303c,0x3042,0x4088]:self.startup_provider(s,pc);platform_RTS(s)
        elif pc==0x304e:self.bios(s,pc);platform_RTS(s)
        else:
            status=fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None)
            if status not in [0,6]:
                import json
                (self.out/'single-step-failure.json').write_text(json.dumps(dict(PC=hex(pc),status=status,CPU=media.scheduler.cpu_dict(s),errors=self.errors),indent=2)+'\n')
                self.finish_startup_instruction_probe()
                raise AssertionError(('single source instruction',hex(pc),status,self.errors))
            assert count()==before+1,('single instruction observer count',hex(pc),before,count())
        assert not self.errors,self.errors
        self.single_step_count+=1
        if pc in [0xdf6a,0xdf8a]or(pc==0xde5a and s.pc not in [0xdf66,0xdf86]):self.handoff_event(s)
        command=self.core.GPUReadLong(0xf03204,6)
        if command==0x4b00:self.pending_render=None;self.run_render_request(command)
        elif command==0x4320:self.pending_movement=False;self.run_movement_request()
    runtime.startup_single_step=types.MethodType(step,runtime)
