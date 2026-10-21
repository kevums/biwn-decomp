"""Small fixture adapter to run the stream-caller cases on the pinned core.

Only instruction-boundary callbacks are observed. CPU data-bus callbacks are
not available here; the primary Unicorn test separately checks their order.
"""
import ctypes as c
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *

REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
      UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
      UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
      UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
MAPPING={reg:i for i,reg in enumerate(REGS)}
MAPPING.update({UC_M68K_REG_PC:16,UC_M68K_REG_SR:17})


class NativeCPU:
    def __init__(self,native):
        self.native=native;self.device=native.device;self.core=native.lib
        self.core.m68k_pulse_reset();self.core.m68k_set_irq(0)
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32
        self.hooks=[];self.blitter_command_instructions=0;self.executed=0

    def ctl_set_cpu_model(self,model):
        assert model==UC_CPU_M68K_M68000

    def mem_map(self,address,size):
        assert(address,size)in[(0,0x200000),(0xf02000,0x2000)]

    def mem_write(self,address,data):
        assert 0<=address and address+len(data)<=0x200000
        c.memmove(self.device.pointer+address,bytes(data),len(data))

    def mem_read(self,address,size):
        assert 0<=address and address+size<=0x200000
        return c.string_at(self.device.pointer+address,size)

    def reg_read(self,register):return self.core.m68k_get_reg(None,MAPPING[register])
    def reg_write(self,register,value):self.core.m68k_set_reg(MAPPING[register],value)

    def hook_add(self,kind,callback):
        if kind==UC_HOOK_CODE:self.hooks.append(callback)
        return len(self.hooks)

    def emu_start(self,begin,end,count,timeout):
        self.core.m68k_set_reg(16,begin)
        for _ in range(count):
            pc=self.core.m68k_get_reg(None,16)
            if pc==end:return
            for callback in self.hooks:callback(self,pc,2,None)
            instruction=self.mem_read(pc,6)
            opcode=int.from_bytes(instruction[:2],'big')
            if opcode&0xfff0==0x23c0 and instruction[2:]==bytes.fromhex('00f02238'):
                self.blitter_command_instructions+=1
            self.core.m68k_execute(1);self.executed+=1
            if self.core.GPUReadLong(0xf03204,0)==0x4320:
                # Shared synchronous GPU device contract, same as the primary
                # fixture. Native CPU blitter writes execute in the core itself.
                self.device.write(0xf03204,0x4320)
        raise AssertionError('Pinned native CPU exceeded the fixture instruction bound')
