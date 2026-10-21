"""Selection block plus real drawing: original instructions vs connected C.

Supplied game-memory input words; no physical polling, world loop or timing.
Both paths share the pinned emulator blitter and synchronous mailbox model.
"""
import argparse, ctypes as c, hashlib, json, random
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
ROOT=frame.ROOT; SP=frame.SP; REGS=frame.REGS
END=0x1a254
def save(p,v): p.write_text(json.dumps(v,indent=2)+'\n')

def original(device,ram,incoming):
    device.seed(ram,0)
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(ram))
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_A7,SP)
    in_formatter=False;steps=[];draws=[]
    def code(engine,address,size,_):
        nonlocal in_formatter
        if address==0x1b45a:in_formatter=True
        if address==0x1b838:in_formatter=False
        if address==0x1b786:draws.append(address)
        assert (0x1a1f0<=address<END or 0x1b718<=address<0x1b780 or 0x1b786<=address<0x1bc78 or 0x14776<=address<0x14caa or 0xe098<=address<0xe0a6 or 0xe2b8<=address<0xe2f4 or 0xe540<=address<0xe588 or (in_formatter and(0x1b160<=address<0x1b478 or 0xe61c<=address<0xe68c))),hex(address)
        steps.append(address)
    def read(engine,access,address,size,value,_):
        if in_formatter or SP-0x1000<=address<SP+8 or 0x14800<=address<0x14842:return
        engine.mem_write(address,device.read(address,size).to_bytes(size,'big'))
    def write(engine,access,address,size,value,_):
        if SP-0x1000<=address<SP+8:return
        value &= (1<<(size*8))-1
        if in_formatter:
            assert size==1 and 0x15b7a0<=address<0x15b7aa
            device.direct(address,size,value);return
        if size==2:
            assert address in [0x49d54,0x49d56]
            assert device.lib.lab_device_write16(None,address,value)==0
        else:
            assert size==4
            device.write(address,value)
    device.lib.lab_device_write16.argtypes=[c.c_void_p,c.c_uint32,c.c_uint16]
    device.lib.lab_device_write16.restype=c.c_int
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x1a1f0,END,count=250000,timeout=3_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==END and cpu.reg_read(UC_M68K_REG_A7)==SP
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i]
    return device.ram(),[t for t in device.trace if t[0]<2],device.registers(),{'CPU_instructions':len(steps),'redraw_calls':len(draws),'device':device.stats()}

def rebuilt(device,ram,incoming,input_word):
    device.seed(ram,1)
    registers=(c.c_uint32*3)(incoming[0],incoming[1],incoming[8])
    assert device.lib.lab_device_input_step(input_word,registers)==0
    output=device.ram();trace=[t for t in device.trace if t[0]<2]
    # The exported host API supplies the input word before entering the block.
    assert trace.pop(0)==(1,0x49bac,4,input_word)
    stats=device.stats()
    assert stats['GPUExec1_calls']==0 and stats['original_GPU_sprite_decodes']==0 and not stats['game_frames_executed'] and not stats['device_error']
    return output,trace,device.registers(),stats

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(snapshot).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    image=(s/'nextstage-68000-candidate.bin').read_bytes()
    for a,b in [(0x1a1f0,END),(0x1b718,0x1b780)]:assert snapshot[a:b]==image[a-0x4000:b-0x4000]
    out=ROOT/'verification/biwn-inventory-interaction'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    library=ROOT/'tools/libbiwn-inventory-interaction.dylib';rng=random.Random(0x1a1f0)
    bits=[19,7,3,18,6,2,17,5,1,4] # analyst digit order1..9,0, not hardware mapping
    sequences=[]
    for start in range(10):
        sequences.append({'name':'digit_cycle_priority_and_no_input','start':start,'inputs':[0]+[1<<b for b in bits]+[1<<9,0xe02fe,0x80000000,0,1<<9]})
        sequences.append({'name':'cycle_full_wrap','start':start,'inputs':[1<<9]*12+[0]})
        sequences.append({'name':'cycle_plus_digit1_priority','start':start,'inputs':[(1<<9)|(1<<19)]})
    if args.preflight:sequences=sequences[:2]
    rows=[]
    for fast in [1,0]:
        device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',fast,library)
        device.lib.lab_device_input_step.argtypes=[c.c_uint32,c.POINTER(c.c_uint32)];device.lib.lab_device_input_step.restype=c.c_int
        try:
            for seq_index,seq in enumerate(sequences):
                case={'start':seq['start'],'selected':seq['start'],'layout':'real','money':200}
                ram=frame.make_ram(snapshot,case)
                ram=bytearray(frame.rebuilt(device,ram)[0])
                for step,input_word in enumerate(seq['inputs']):
                    save(out/'status.json',{'status':'running','fast':fast,'sequence':seq_index,'step':step})
                    ram[0x49bac:0x49bb0]=input_word.to_bytes(4,'big')
                    incoming=[rng.getrandbits(32)for _ in REGS]
                    a,ta,ra,oa=original(device,ram,incoming)
                    b,tb,rb,ob=rebuilt(device,ram,incoming,input_word)
                    equal=a[:0x15b7a0]==b[:0x15b7a0] and a[0x15b7aa:]==b[0x15b7aa:]
                    if not equal or ta!=tb or ra!=rb:
                        save(out/'mismatch.json',{'fast':fast,'sequence':seq_index,'step':step,'input':hex(input_word),'RAM_match':equal,'original_trace':ta,'C_trace':tb,'original_registers':ra,'C_registers':rb})
                        raise AssertionError(str(out/'mismatch.json'))
                    redraw=bool(input_word&0xe02fe);assert oa['redraw_calls']==int(redraw)
                    assert bool(ob['blit_commands'])==redraw
                    selected=int.from_bytes(b[0x49d54:0x49d56],'big')
                    expected=(int.from_bytes(ram[0x49d54:0x49d56],'big')+1)%10 if input_word&(1<<9) else next((i for i,bit in enumerate(bits)if input_word&(1<<bit)),int.from_bytes(ram[0x49d54:0x49d56],'big'))
                    assert selected==expected
                    if redraw:assert b[0x49d54:0x49d56]==b[0x49d56:0x49d58]
                    digest=hashlib.sha256(b[frame.FRAME_START:frame.FRAME_END]).hexdigest()
                    rows.append({'fast':fast,'sequence':seq_index,'step':step,'input_word':hex(input_word),'selected_internal_slot':selected,'redrawn':redraw,'frame_sha256':digest,'original':oa,'rebuilt':ob,'external_CPU_trace_match':True,'RAM_except_formatter_scratch_match':True,'blitter_registers_match':True})
                    ram=bytearray(b)
                folder=out/('fast'if fast else'accurate')/str(seq_index);folder.mkdir(parents=True)
                (folder/'final-panel.raw16be').write_bytes(ram[frame.FRAME_START:frame.FRAME_END])
        finally:device.close()
    for i in range(len(rows)//2):assert rows[i]['frame_sha256']==rows[i+len(rows)//2]['frame_sha256']
    save(out/'fixtures.json',rows)
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'preflight_passed'if args.preflight else'connected_selection_and_inventory_render_match_original_execution','directory':str(out),
            'steps':len(rows),'sequences':len(sequences)*2,'fast_steps':len(rows)//2,'accurate_steps':len(rows)//2,'redraw_steps':sum(x['redrawn']for x in rows),
            'additional_original_components':0,'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),
            'matched':['Selection block executes original digit helper and complete original inventory/text/sprite CPU routines plus original GPU overlay in oracle; no redraw stub.',
                       'Connected C selection invokes checked native C inventory pipeline, text helpers and sprite decoder. Same emulated blitter on both paths.',
                       'Every external CPU read/write width, address, value and order; whole2MB RAM except10formatter scratchbytes; final blitter registers; exact panel bytes after every step.',
                       'Digit priority, cycle priority, complete wrap, unrelated bits and no-input panel retention; fast/accurate outputs agree.'],
            'limits':['Input is an injected game-memory word, not physical controller polling or main-loop execution.','Selection block1A1F0..1A254 only, not whole1A188 function.','FullCCR/caller-saved ABI and asynchronous timing excluded; mailbox completion synchronous.','Existing pinned emulator blitter; no physical hardware or full game reconstruction.','Original assisted-game snapshot and fixed inventory assets retained.'],
            'game_screen_digit_for_last_slot':'0 (user position10, internal index9)'}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal','exit_code':0})
    if not args.preflight:save(ROOT/'verification/biwn-inventory-interaction-checks.json',report)
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
