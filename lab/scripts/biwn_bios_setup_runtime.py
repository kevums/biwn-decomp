"""Use actual resident BIOS3000 within the source E00A CPU loader call."""
import ctypes as c
from check_biwn_media_setup_cpu import world_cpu
import check_biwn_full_video_cpu_gpu as video
class BIOSSetupMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.actual_bios_setup=True;self.bios_setup_body=self.lib.biwn_bios_setup_cpu_body;self.bios_setup_body.argtypes=self.entry_body.argtypes;self.bios_setup_body.restype=c.c_int;parent=self.service
        def service(_,bus,cpu,target):
            if self.entry_active and target==0x3000:
                self.entry_bios(cpu.contents,target)
                return self.bios_setup_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
            return parent(_,bus,cpu,target)
        self.service=world_cpu.SERVICE(service)
    def entry_bios(self,s,target):
        if target==0x3000:
            self.BIOS_calls.append(dict(target=hex(target),D0=s.registers[0],A0=s.registers[8],A1=s.registers[9],implementation='actual_user_BIOS_resident_CPU_source'))
            return
        return super().entry_bios(s,target)
    def read(self,a,w):
        if self.mode=='C'and self.entry_active and a==0xf02100 and w==4:
            s=self.gpu;s.flags=(s.flags&~7)|s.z|(s.c<<1)|(s.n<<2);value=s.flags&0xffffc1ff
            self.observe(0,a,w,value);return value
        return super().read(a,w)
    def run_boot_exit(self,kind):
        raw=video.logical(self.gpu)if self.mode=='C'else video.gpu_state(self.core)[0][:4396]
        (self.out/f'{self.mode}-{kind}-GPU-before.bin').write_bytes(raw)
        result=super().run_boot_exit(kind)
        raw=video.logical(self.gpu)if self.mode=='C'else video.gpu_state(self.core)[0][:4396]
        (self.out/f'{self.mode}-{kind}-GPU-after.bin').write_bytes(raw)
        return result
