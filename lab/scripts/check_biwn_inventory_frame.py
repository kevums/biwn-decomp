"""Reconstructed C inventory image vs original CPU/GPU and saved game buffer.

Both paths use the SAME pinned emulator blitter. This tests restored game
code and integration, not an independently reconstructed hardware backend.
"""
import argparse,ctypes as c,hashlib,json,random,sys,time
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_inventory_draw as draw
ROOT=draw.stage.ROOT;SP=draw.SP;STOP=draw.STOP;REGS=draw.REGS
FRAME_START,FRAME_END=0xb5130,0xbd830
OBSERVER=c.CFUNCTYPE(None,c.c_uint,c.c_uint,c.c_uint32,c.c_uint32)
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

class Device:
    def __init__(self,core,bios,fast,library=None):
        self.lib=c.CDLL(str(library or ROOT/'tools/libbiwn-inventory-device.dylib'))
        self.lib.lab_device_open.argtypes=[c.c_char_p,c.c_char_p,c.c_int];self.lib.lab_device_open.restype=c.c_int
        self.lib.lab_device_seed.argtypes=[c.c_void_p,c.c_uint32,c.c_int];self.lib.lab_device_seed.restype=c.c_int
        self.lib.lab_device_ram.restype=c.c_void_p
        for width,typ in [(8,c.c_uint8),(16,c.c_uint16),(32,c.c_uint32)]:
            fn=getattr(self.lib,'lab_device_read'+str(width));fn.argtypes=[c.c_void_p,c.c_uint32,c.POINTER(typ)];fn.restype=c.c_int
        self.lib.lab_device_write32.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];self.lib.lab_device_write32.restype=c.c_int
        self.lib.lab_device_stat.argtypes=[c.c_uint];self.lib.lab_device_stat.restype=c.c_uint32
        self.lib.lab_device_run_C.argtypes=[c.c_uint32];self.lib.lab_device_run_C.restype=c.c_int
        self.lib.lab_device_observe.argtypes=[OBSERVER]
        assert self.lib.lab_device_open(str(core).encode(),str(bios).encode(),fast)==0
        self.trace=[]
        def observe(kind,width,address,value):self.trace.append((kind,address,width,value))
        self.observer=OBSERVER(observe);self.lib.lab_device_observe(self.observer)
    def seed(self,ram,C_decoder):
        self.trace=[];buffer=c.create_string_buffer(bytes(ram));assert self.lib.lab_device_seed(buffer,len(ram),C_decoder)==0;self.pointer=self.lib.lab_device_ram()
    def read(self,address,width):
        typ={1:c.c_uint8,2:c.c_uint16,4:c.c_uint32}[width];out=typ();assert getattr(self.lib,'lab_device_read'+str(width*8))(None,address,c.byref(out))==0,hex(address);return out.value
    def write(self,address,value):assert self.lib.lab_device_write32(None,address,value)==0,hex(address)
    def direct(self,address,width,value):c.memmove(self.pointer+address,value.to_bytes(width,'big'),width)
    def ram(self):return c.string_at(self.pointer,0x200000)
    def stats(self):return {name:self.lib.lab_device_stat(i)for i,name in enumerate(['GPUExec1_calls','C_sprite_decodes','original_GPU_sprite_decodes','blit_commands','game_frames_executed','device_error'])}
    def registers(self):return [self.read(0xf02200+i,4)for i in range(0,0xa0,4)]
    def close(self):self.lib.lab_device_close()

def original(device,ram,incoming):
    device.seed(ram,0);cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(ram));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_A7,SP);in_formatter=False;steps=[];scratch=[]
    def code(engine,address,size,_):
        nonlocal in_formatter
        if address==0x1b45a:in_formatter=True
        if address==0x1b838:in_formatter=False
        assert (0x1b786<=address<0x1bc78 or 0x14776<=address<0x14caa or 0xe098<=address<0xe0a6 or 0xe2b8<=address<0xe2f4 or 0xe540<=address<0xe588 or (in_formatter and(0x1b160<=address<0x1b478 or 0xe61c<=address<0xe68c))),hex(address)
        steps.append(address)
    def read(engine,access,address,size,value,_):
        if in_formatter or SP-0x1000<=address<SP+8 or 0x14800<=address<0x14842:return
        engine.mem_write(address,device.read(address,size).to_bytes(size,'big'))
    def write(engine,access,address,size,value,_):
        if SP-0x1000<=address<SP+8:return
        if in_formatter:
            assert size==1 and 0x15b7a0<=address<0x15b7aa;device.direct(address,size,value);scratch.append((address,size,value));return
        assert size==4;device.write(address,value&0xffffffff)
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x1b786,STOP,count=250000,timeout=3_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i]
    out=device.ram();trace=[t for t in device.trace if t[0]<2];stats=device.stats();registers=device.registers()
    return out,trace,registers,{'CPU_instructions':len(steps),'formatter_scratch_excluded':scratch,'callee_saved_registers_and_RTS_stack_checked':True,'device':stats}

def rebuilt(device,ram):
    device.seed(ram,1);assert device.lib.lab_device_run_C(100000)==0
    out=device.ram();trace=[t for t in device.trace if t[0]<2];stats=device.stats();registers=device.registers()
    assert stats['GPUExec1_calls']==0 and stats['original_GPU_sprite_decodes']==0 and not stats['game_frames_executed']and not stats['device_error']
    return out,trace,registers,stats

def make_ram(snapshot,case):
    ram=bytearray(snapshot)
    def put(a,w,v):ram[a:a+w]=v.to_bytes(w,'big')
    put(0x49d1e,4,case['money']);put(0x49d54,2,case['start']);put(0x49d56,2,case['selected'])
    ids={'real':[65,36,41,70,0,0,0,0,0,0],'empty':[0]*10,'full':[65,36,41,70,65,36,41,70,65,36]}[case['layout']]
    for i,value in enumerate(ids):put(0x49d2c+i*2,2,value)
    ram[FRAME_START:FRAME_END]=bytes([case.get('poison',0xa5)])*(FRAME_END-FRAME_START)
    ram[0x10a67c:0x10c688]=b'\x5a'*(0x10c688-0x10a67c)
    return ram

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);capture=s/'emulator-runtime/gpu-stack-test-20261013T021159.664820Z/initialized/main-ram-frame-900.bin';snapshot=capture.read_bytes();assert len(snapshot)==0x200000
    image=(s/'nextstage-68000-candidate.bin').read_bytes();assert draw.stage.digest(image)==draw.stage.STAGE_SHA
    for a,b in [(0x1b786,0x1bc78),(0x14776,0x14caa),(0xe2b8,0xe2f4),(0xe098,0xe0a6),(0x4b00,0x4d68),(0x1b160,0x1b478),(0xe61c,0xe68c),(0xe540,0xe588)]:assert snapshot[a:b]==image[a-0x4000:b-0x4000],hex(a)
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib';assert draw.binary_tools.sha(core)=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    out=ROOT/'verification/biwn-inventory-frame'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'protocol.json',{'capture':str(capture),'capture_sha256':draw.binary_tools.sha(capture),'core_sha256':draw.binary_tools.sha(core),'bridge_sha256':draw.binary_tools.sha(ROOT/'tools/libbiwn-inventory-device.dylib'),'scope':'OriginalCPU+GPUoverlays vs compiledgameC with samepinnedemulatorblitter; synchronousmodeledmailbox. No full-game/hardware equivalence.'})
    money=[0,200,0xffffffff,0x80000000,0x7fffffff,123456789,0xffed2979];cases=[]
    for start in range(10):
        for selected in range(10):
            for layout in ['empty','real','full']:cases.append({'start':start,'selected':selected,'layout':layout,'money':money[len(cases)%7]})
    if options.limit:cases=cases[:options.limit]
    rng=random.Random(0xb5130);rows=[];fast_images={};actual_reviews=[]
    for fast in [1,0]:
        device=Device(core,s/'emulator-runtime/inventory-draw-20261013T045440.167975Z/inputs',fast)
        try:
            subset=cases if fast else[case for case in cases if case['start']==case['selected']]
            for i,case in enumerate(subset):
                folder=out/('fast'if fast else'accurate')/f'case-{i:03d}';folder.mkdir(parents=True);save(out/'status.json',{'status':'running','engine':'fast'if fast else'accurate','case':i,'parameters':case})
                ram=make_ram(snapshot,case);a,trace_a,regs_a,observed=original(device,ram,[rng.getrandbits(32)for _ in REGS]);b,trace_b,regs_b,stats=rebuilt(device,ram)
                equal_ram=a[:0x15b7a0]==b[:0x15b7a0]and a[0x15b7aa:]==b[0x15b7aa:]
                if not equal_ram or trace_a!=trace_b or regs_a!=regs_b:
                    (folder/'original-output-ram.bin').write_bytes(a);(folder/'C-output-ram.bin').write_bytes(b);save(folder/'mismatch.json',{'case':case,'CPU_trace':trace_a,'C_trace':trace_b,'original_blitter_registers':regs_a,'C_blitter_registers':regs_b,'original':observed,'rebuilt':stats});raise AssertionError(str(folder/'mismatch.json'))
                frame=b[FRAME_START:FRAME_END];digest=hashlib.sha256(frame).hexdigest();key=json.dumps(case,sort_keys=True)
                if fast:fast_images[key]=digest
                else:assert fast_images[key]==digest,'Fast/accurate frame differs'
                (folder/'C-inventory-96x180.raw16be').write_bytes(frame);save(folder/'CPU-trace.json',trace_b)
                rows.append({'engine':'fast'if fast else'accurate','parameters':case,'directory':str(folder),'frame_sha256':digest,'frame_bytes':len(frame),'whole_RAM_except_formatter_scratch_match':True,'CPU_external_trace_match':True,'final_blitter_registers_match':True,'original':observed,'rebuilt':stats})
            for poison in [0,0x5a,0xa5,0xff]:
                case={'start':0,'selected':0,'layout':'real','money':200,'poison':poison};ram=make_ram(snapshot,case);b,_,_,stats=rebuilt(device,ram);frame=b[FRAME_START:FRAME_END];assert frame==snapshot[FRAME_START:FRAME_END]
                actual_reviews.append({'engine':'fast'if fast else'accurate','poison':poison,'matches_saved_original_game_inventory_buffer':True,'frame_sha256':hashlib.sha256(frame).hexdigest(),'changed_frame_bytes_from_poison':sum(x!=poison for x in frame),'rebuilt':stats})
                (out/('rebuilt-fast.raw16be'if fast else'rebuilt-accurate.raw16be')).write_bytes(frame)
        finally:device.close()
    save(out/'fixtures.json',rows);save(out/'actual-capture-comparison.json',actual_reviews)
    if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out),'actual_capture_matches':len(actual_reviews)}),flush=True);return
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'reconstructed_inventory_buffer_matches_original_code_and_saved_game_capture','directory':str(out),'stage_sha256':draw.stage.STAGE_SHA,'additional_original_components':0,'fast_cases':sum(x['engine']=='fast'for x in rows),'accurate_cases':sum(x['engine']=='accurate'for x in rows),'actual_capture_poison_checks':len(actual_reviews),'frame_dimensions':[96,180],'frame_bytes':34560,'frame_interval':'[0xb5130,0xbd830)','frame_sha256':actual_reviews[0]['frame_sha256'],'capture':str(capture),'capture_sha256':draw.binary_tools.sha(capture),'core_sha256':draw.binary_tools.sha(core),'bridge_sha256':draw.binary_tools.sha(ROOT/'tools/libbiwn-inventory-device.dylib'),
        'rebuilt_original_CPU_instructions_executed':0,'rebuilt_original_GPU_instructions_executed':0,'rebuilt_game_frames_executed':0,'standalone_GPU_decoder_linked_into_backend':True,
        'matched':['300fast and30accurate blitter cases compare originalCPU+GPUroutines vs compiledgameC: externalCPUbus traces, whole2MBRAM except formatter10scratchbytes, finalblitterregisters and exactinventorypixels.','All30shared fast/accurate frames match.','EightC-onlyrenders withfourpoisons underbothengines exactlymatch originalgame RAMframe900inventorybuffer, proving output is regenerated.','Rebuiltpath runs compiledCPU/gamehelpers and Csprite decoder with no originalCPU/GPUexecution and no completegameframeexecution.'],
        'excluded':['Blitter hardware is the existing pinned emulator library, not independently reconstructed or physicalhardware.','Synchronousmodelledmailbox; dispatcher copy/ack/idle scheduling, interrupts and concurrentCPU/GPU/DSP timing are not reproduced.','Internal96x180inventorybuffer only, not a complete320x240gameviewport or whole rebuilt game.','Privateformatterstack and10scratchbytes excluded; fullCCR/caller-savedregisterABI outside scope.','Originalcapture came from assistedBIOS with prioroneGPUstackintervention. No unmodifiedBIOS/physicalCDproof.','RGBdisplay interpretation separate from bit-exact16bitbuffer comparison.']}
    save(out/'report.json',report);save(ROOT/'verification/biwn-inventory-frame-checks.json',report);save(out/'status.json',{'status':'terminal','exit_code':0});print(json.dumps(report),flush=True)

if __name__=='__main__':main()
