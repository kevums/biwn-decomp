"""Execute resident BIOS3000 in subsequent source GPU reload callers."""
import ctypes as c
from check_biwn_media_setup_cpu import world_cpu
class BIOSReloadMixin:
    def __init__(self,*args,**kwargs):
        self.reload_bios_active=False;self.reload_bios_calls=[]
        super().__init__(*args,**kwargs);parent=self.service
        def service(_,bus,cpu,target):
            if target==0x3000 and self.actual_reload_scope():
                self.record_reload(cpu.contents)
                self.reload_bios_active=True
                try:return self.bios_setup_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
                finally:self.reload_bios_active=False
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def reset(self,*args,**kwargs):
        result=super().reset(*args,**kwargs);self.reload_bios_active=False;self.reload_bios_calls=[];return result
    def actual_reload_scope(self):return self.full_running and not self.entry_active
    def record_reload(self,s):
        self.reload_bios_calls.append(dict(target='0x3000',D0=s.registers[0],A0=s.registers[8],A1=s.registers[9],return_PC=hex(self.device.read(s.registers[15],4)),implementation='actual_resident_BIOS_CPU_reload'))
    def native_reload_call(self):
        s=self.cpu();ret=self.device.read(s.registers[15],4);self.record_reload(s);self.reload_bios_active=True
        try:
            for _ in range(100000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==ret:return
                assert pc in self.rows,hex(pc)
                self.core.m68k_execute(1)
            raise AssertionError('Resident BIOS reload bound')
        finally:self.reload_bios_active=False
    def read(self,a,w):
        if self.mode=='C' and self.reload_bios_active and a==0xf02100 and w==4:
            s=self.gpu;s.flags=(s.flags&~7)|s.z|(s.c<<1)|(s.n<<2);v=s.flags&0xffffc1ff
            self.observe(0,a,w,v);return v
        return super().read(a,w)
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode=='C' and self.reload_bios_active and a==0xf02100 and w==4:
            s=self.gpu;s.flags=(v&~8)|((v&8)&s.flags);s.z=v&1;s.c=(v>>1)&1;s.n=(v>>2)&1;s.bank=0 if s.flags&8 else bool(v&0x4000)
