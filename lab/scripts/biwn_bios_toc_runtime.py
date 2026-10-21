"""Actual305A linked to preserved CDI/BUTCH; explicit poll schedule retained."""
import ctypes as c
from check_biwn_media_setup_cpu import world_cpu
class BIOSTOCMixin:
    def __init__(self,*args,**kwargs):
        self.bios_toc_active=False;self.bios_toc_ticks=0
        super().__init__(*args,**kwargs);self.actual_bios_entries.add(0x305a);self.bios_toc_body=self.lib.biwn_bios_toc_cpu_body;self.bios_toc_body.argtypes=self.entry_body.argtypes;self.bios_toc_body.restype=c.c_int;parent=self.service
        def service(_,bus,cpu,target):
            if self.entry_active and target in [0x305a,0x390e]:
                before=self.bios_toc_active;self.bios_toc_active=True
                try:
                    if target==0x305a:self.entry_bios(cpu.contents,target)
                    return self.bios_toc_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
                finally:self.bios_toc_active=before
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def reset(self,*args,**kwargs):
        result=super().reset(*args,**kwargs);self.bios_toc_active=False;self.bios_toc_ticks=0;return result
    def tick_BUTCH(self):
        if self.bios_toc_active:self.core.BUTCHExec(0);self.bios_toc_ticks+=1
        else:super().tick_BUTCH()
    def before_entry_CPU(self,pc):
        if pc in [0x3910,0x392e,0x37e0]:self.tick_BUTCH()
        if pc==0x3904:self.bios_toc_active=False
        return super().before_entry_CPU(pc)
    def entry_bios(self,s,target):
        if target==0x305a:
            self.bios_toc_active=True
            self.BIOS_calls.append(dict(target=hex(target),D0=s.registers[0],A0=s.registers[8],A1=s.registers[9],implementation='actual_user_BIOS_TOC_source'))
            return
        return super().entry_bios(s,target)
