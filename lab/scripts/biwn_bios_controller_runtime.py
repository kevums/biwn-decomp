"""Actual BIOS3048 controller setup before disc mode/TOC initialization."""
import ctypes as c
from check_biwn_media_setup_cpu import world_cpu
class BIOSControllerMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.actual_bios_entries={0x3000,0x3048};self.bios_controller_body=self.lib.biwn_bios_controller_cpu_body;self.bios_controller_body.argtypes=self.entry_body.argtypes;self.bios_controller_body.restype=c.c_int;parent=self.service
        def service(_,bus,cpu,target):
            if self.entry_active and target==0x3048:
                self.entry_bios(cpu.contents,target)
                return self.bios_controller_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def entry_bios(self,s,target):
        if target==0x3048:
            self.BIOS_calls.append(dict(target=hex(target),D0=s.registers[0],A0=s.registers[8],A1=s.registers[9],implementation='actual_user_BIOS_controller_CPU_source'))
            return
        return super().entry_bios(s,target)
