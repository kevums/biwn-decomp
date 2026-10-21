"""Actual ROM resident install before explicitly seeded game4000 entry.

The intervening complete firmware/disc boot remains unimplemented; do not
describe the seeded game entry as a natural firmware continuation.
"""
import ctypes as c
from check_biwn_media_setup_cpu import CPU,ROOT,sha
import check_biwn_media_setup_cpu as media
class ROMResidentInstallMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.resident_install_body=self.lib.biwn_bios_resident_install_cpu_body;self.resident_install_body.argtypes=self.fn.argtypes;self.resident_install_body.restype=c.c_int
        self.user_BIOS=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert sha(self.user_BIOS)=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b'
    def reset(self,ram,seed):
        super().reset(ram,seed)
        if hasattr(self,'prepare_initial_serial_fixture'):self.prepare_initial_serial_fixture()
        assert self.device.ram()[0x3000:0x3e00]==bytes(0xe00),'Resident RAM must start empty'
        c.memmove(self.rom,self.user_BIOS,len(self.user_BIOS))
        s=CPU();s.pc=0x80203e;s.registers[15]=s.ssp=0x1fe000;s.usp=0x180000;s.sr=0x2700
        initial=media.scheduler.cpu_dict(s)
        if self.mode=='native':
            self.seed_cpu(s);steps=0
            for _ in range(10000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0x802054:break
                assert pc in self.rows,hex(pc);self.core.m68k_execute(1);steps+=1
            else:raise AssertionError('Initial ROM copy bound')
            s=self.cpu();assert steps==1908
        else:
            assert self.resident_install_body(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
        assert self.device.ram()[0x3000:0x39ec]==self.user_BIOS[0x84a6:0x8e92]
        assert self.device.ram()[0x39ec:0x3e00]==bytes(0x414)
        self.resident_install_summary=dict(initial_CPU=initial,CPU=media.scheduler.cpu_dict(s),RAM_sha256=sha(self.device.ram()),bytes_copied=2540,ROM_interval=['0x8084a6','0x808e92'],RAM_interval=['0x3000','0x39ec'],RAM_resident_payload_host_copy=False,initial_ROM_supplied=True,complete_firmware_to_game_CPU_continuation=False)
    def source_entry(self,*args,**kwargs):
        result,checks=super().source_entry(*args,**kwargs);result['firmware_resident_install']=self.resident_install_summary
        return result,checks
