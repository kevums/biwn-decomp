"""Original native CPU polling versus C using the existing emulator pad model."""
import ctypes as c,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
import check_biwn_input_poll as poll
import emulated_pad_input as pad
ROOT=poll.ROOT
def main():
 report=json.loads((ROOT/'verification/biwn-input-poll-checks.json').read_text());library=Path(report['directory'])/'libinput.dylib';lib=c.CDLL(str(library));fn=lib.biwn_input_poll;fn.argtypes=[c.POINTER(poll.world.Bus)];fn.restype=c.c_int
 native=scheduler.Native();backend=pad.Backend(native.lib,native.device);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[];mapping={};rng=random.Random(0xf14000)
 sets=[[]]+[[i]for i in range(21)]+[list(range(21))]+[[i for i in range(21)if rng.getrandbits(1)]for _ in range(105)]+[[20],[20],[],[20]]
 sequence_previous=0;sequence=[]
 try:
  for case,buttons in enumerate(sets):
   previous=sequence_previous if case>=128 else 0 if case<=22 else rng.getrandbits(32);ram=bytearray(snapshot);ram[0x49ba4:0x49ba8]=previous.to_bytes(4,'big');ram[poll.SP:poll.SP+4]=poll.STOP.to_bytes(4,'big');native.device.seed(ram,0);backend.set_buttons(buttons)
   native.lib.m68k_pulse_reset();native.lib.m68k_set_irq(0);native.lib.m68k_set_reg(17,0x2000);native.lib.m68k_set_reg(15,poll.SP);incoming=[rng.getrandbits(32)for _ in range(15)]
   for i,value in enumerate(incoming):native.lib.m68k_set_reg(i,value)
   native.lib.m68k_set_reg(16,0xe4c0);raw=[];steps=[]
   for _ in range(100):
    pc=native.lib.m68k_get_reg(None,16)
    if pc==poll.STOP:break
    assert 0xe4c0<=pc<0xe53c;steps.append(pc);native.lib.m68k_execute(1)
    if pc in[0xe4d4,0xe4e8,0xe4fc,0xe512]:raw.append(native.lib.m68k_get_reg(None,0))
   else:raise AssertionError('Native input poll did not return')
   assert all(native.lib.m68k_get_reg(None,i)==value for i,value in enumerate(incoming))and native.lib.m68k_get_reg(None,15)==poll.SP+4
   original=native.device.ram();held=int.from_bytes(original[0x49ba4:0x49ba8],'big');edges=int.from_bytes(original[0x49bac:0x49bb0],'big')
   if len(buttons)==1 and case<=21:mapping[str(buttons[0])]=held;assert held and held&(held-1)==0
   native.device.seed(ram,1);backend.set_buttons(buttons);C_reads=[];C_writes=[]
   def read(_,address,out):
    if address==0xf14000:value=backend.sample();C_reads.append(value)
    else:value=native.device.read(address,4)
    out[0]=value;return 0
   def w16(_,address,value):assert address==0xf14000;C_writes.append(value);backend.select(value);return 0
   def w32(_,address,value):native.device.write(address,value);return 0
   callbacks=[poll.world.R32(read),poll.world.W16(w16),poll.world.W32(w32)];bus=poll.world.Bus(poll.world.R8(),poll.world.R16(),*callbacks,poll.world.CALL(),None,0);assert fn(c.byref(bus))==0
   rebuilt=native.device.ram();assert raw==C_reads and C_writes==[0x810e,0x810d,0x810b,0x8107]and original[:poll.SP-16]==rebuilt[:poll.SP-16]and original[poll.SP+8:]==rebuilt[poll.SP+8:]
   if case>=128:sequence_previous=held;sequence.append({'core_buttons':buttons,'previous':previous,'held':held,'press_edges':edges})
   rows.append({'case':case,'core_button_indices':buttons,'previous':previous,'held':held,'press_edges':edges,'raw_register_reads':raw,'native_CPU_PCs':[hex(x)for x in steps],'RAM_and_raw_values_match':True})
 finally:native.close()
 assert [x['press_edges']for x in sequence]==[0x10000000,0,0,0x10000000]
 assert len(set(mapping.values()))==21;mask=0
 for value in mapping.values():mask|=value
 assert mask==0x32ff22ff
 out=ROOT/'verification/emulated-pad-poll'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n')
 data={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'native_original_and_C_emulated_pad_poll_match','directory':str(out),'native_CPU_cases':len(rows),'press_hold_release_repress_sequence':sequence,'button_to_game_bit':mapping,'button_names_from_pinned_core_header':dict(enumerate(pad.BUTTON_NAMES)),'ordinary_emulated_port0_mask':'0x32ff22ff','raw_MMIO_possible_mask':'0x33ff33ff','core_sha256':scheduler.cleanup.world.select.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),'source_sha256':report['source_sha256'],'scope':'Existing pinned emulator ordinarypad socket0 model, noTeamTap/nonpaddevices. Original CPU function versus C; not independent hardware accuracy or physicalpad proof. No core edits or gameframes.'}
 (ROOT/'verification/emulated-pad-mapping.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'native_CPU_cases':len(rows),'emulated_buttons':len(mapping),'emulated_mask':hex(mask),'mapping':mapping}),flush=True)
if __name__=='__main__':main()
