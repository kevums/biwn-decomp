"""Pinned emulator pad backend; no original CPU instruction execution here."""
import ctypes as c,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BUTTON_NAMES=['BUTTON_U','BUTTON_D','BUTTON_L','BUTTON_R','BUTTON_s','BUTTON_7','BUTTON_4','BUTTON_1','BUTTON_0','BUTTON_8','BUTTON_5','BUTTON_2','BUTTON_d','BUTTON_9','BUTTON_6','BUTTON_3','BUTTON_A','BUTTON_B','BUTTON_C','BUTTON_OPTION','BUTTON_PAUSE']
class Backend:
 def __init__(self,core,device,mapping=None):
  self.lib=core;self.device=device;self.mapping=mapping
  self.port0=(c.c_uint8*84).in_dll(core,'joypad0Buttons');self.port1=(c.c_uint8*84).in_dll(core,'joypad1Buttons')
  core.JoystickReset.argtypes=[];core.JoystickSetTeamTap.argtypes=[c.c_int,c.c_bool]
  core.m68k_read_memory_32.argtypes=[c.c_uint32];core.m68k_read_memory_32.restype=c.c_uint32
  core.m68k_write_memory_16.argtypes=[c.c_uint32,c.c_uint32];core.m68k_write_memory_16.restype=None
 def set_buttons(self,buttons):
  self.lib.JoystickReset();self.lib.JoystickSetTeamTap(0,False);self.lib.JoystickSetTeamTap(1,False)
  for i in range(84):self.port0[i]=0;self.port1[i]=0
  for i in buttons:assert 0<=i<21;self.port0[i]=1
 def select(self,value):self.lib.m68k_write_memory_16(0xf14000,value)
 def sample(self):return self.lib.m68k_read_memory_32(0xf14000)
 def start(self,case):
  if self.mapping is None:self.mapping=json.loads((ROOT/'verification/emulated-pad-mapping.json').read_text())['button_to_game_bit']
  self.case=case;self.polls=0;self.samples=[];self.raw_reads=[];self.selects=[];self.set_buttons([])
 def begin_poll(self):
  requested=self.case['poll_inputs'][min(self.polls,len(self.case['poll_inputs'])-1)]&0xffffffff
  buttons=[int(i)for i,bit in self.mapping.items()if requested&bit];self.set_buttons(buttons)
  clock=(self.case['clock']+self.polls)&0xffffffff;self.device.direct(0x778cc,4,clock)
  self.samples.append({'poll':self.polls,'requested_game_bits':requested,'core_button_indices':buttons,'clock':clock});self.polls+=1
 def read_for_C(self):
  value=self.sample();self.raw_reads.append(value);return value
 def write_for_C(self,value):self.selects.append(value);self.select(value)
