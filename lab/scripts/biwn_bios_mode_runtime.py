"""Actual BIOS3006 with a loaded preserved CDI and source-poll controller ticks."""
import ctypes as c,hashlib
from pathlib import Path
from check_biwn_media_setup_cpu import world_cpu,ROOT
class BIOSModeMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.actual_bios_entries.add(0x3006);self.bios_mode_body=self.lib.biwn_bios_mode_cpu_body;self.bios_mode_body.argtypes=self.entry_body.argtypes;self.bios_mode_body.restype=c.c_int;parent=self.service
        self.core.CDIntfOpenImage.argtypes=[c.c_char_p];self.core.CDIntfOpenImage.restype=c.c_bool;self.core.CDROMInit.argtypes=[];self.core.CDROMReset.argtypes=[];self.core.CDIntfCloseImage.argtypes=[];self.core.BUTCHExec.argtypes=[c.c_uint32];self.core.CDROMStateSave.argtypes=[c.c_void_p];self.core.CDROMStateSave.restype=c.c_size_t
        assert self.core.CDIntfOpenImage(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode());self.core.CDROMInit();self.bios_mode_ticks=0
        def service(_,bus,cpu,target):
            if self.entry_active and target in [0x3006,0x3544]:
                if target==0x3006:self.entry_bios(cpu.contents,target)
                return self.bios_mode_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def reset(self,*args,**kwargs):
        result=super().reset(*args,**kwargs);self.core.CDROMReset();self.bios_mode_ticks=0;return result
    def snapshot(self):
        s=super().snapshot();b=c.create_string_buffer(200000);n=self.core.CDROMStateSave(b);assert 0<n<=len(b);s['hardware']['BUTCH_CDROM_full_state']=dict(size=n,sha256=hashlib.sha256(b.raw[:n]).hexdigest());self.core.CDROMStateExtSave.argtypes=[c.c_void_p];self.core.CDROMStateExtSave.restype=c.c_size_t;e=c.create_string_buffer(16);m=self.core.CDROMStateExtSave(e);assert m==9;s['hardware']['BUTCH_timing_extension']=dict(size=m,sha256=hashlib.sha256(e.raw[:m]).hexdigest());return s
    def tick_BUTCH(self):self.core.BUTCHExec(0);self.bios_mode_ticks+=1
    def before_entry_CPU(self,pc):
        if pc==0x3544:self.tick_BUTCH()
    def read(self,a,w):
        if self.entry_active and self.mode=='C'and a==0xdfff00 and w==4:self.tick_BUTCH()
        return super().read(a,w)
    def entry_bios(self,s,target):
        if target==0x3006:
            self.BIOS_calls.append(dict(target=hex(target),D0=s.registers[0],A0=s.registers[8],A1=s.registers[9],implementation='actual_user_BIOS_mode_DSA_wait_source'))
            return
        return super().entry_bios(s,target)
