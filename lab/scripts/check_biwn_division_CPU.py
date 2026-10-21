"""Pinned native CPU versus fixed C division entries, including real zero traps."""
import argparse,capstone,ctypes as c,json,random
from datetime import datetime,timezone
from pathlib import Path
from check_local_GPU_wait_C import Bus,R8,R16,R32,W16,W32,CALL
from check_biwn_scheduler import Native,CPU,cpu_dict
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def inventory(candidate):
    atlas=Path(candidate['instruction_RAM_source']).read_bytes()
    decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    rows=[]
    for key in candidate['selected_case_sources']:
        pc=int(key,16);ins=next(decoder.disasm(atlas[pc:pc+24],pc,count=1),None)
        if ins and ins.mnemonic in ['divu.w','divs.w']:
            word=int.from_bytes(ins.bytes[:2],'big');src=ins.op_str.split(',')[0]
            if src.startswith('d'):kind='register';value=int(src[1:])
            elif src.startswith('#'):kind='immediate';value=int.from_bytes(ins.bytes[2:4],'big')
            else:assert ins.size==6 and word&63==57;kind='absolute';value=int.from_bytes(ins.bytes[2:6],'big')
            rows.append(dict(pc=pc,bytes=ins.bytes.hex(),size=ins.size,signed=ins.mnemonic=='divs.w',destination=(word>>9)&7,operand_kind=kind,operand=value,assembly=ins.mnemonic+' '+ins.op_str))
    assert len(rows)==28
    return atlas,sorted(rows,key=lambda row:row['pc'])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path)
    parser.add_argument('--cost',type=Path,default=ROOT/'verification/main-static-cycle-cost-experimental-candidate.json')
    parser.add_argument('--zero-only',action='store_true')
    args=parser.parse_args()
    bp=ROOT/'verification/native-formatter-C-bridge-current.json';bridge=json.loads(bp.read_text())
    cp=args.candidate or Path(bridge['CPU_candidate']);candidate=json.loads(cp.read_text());atlas,entries=inventory(candidate)
    library=c.CDLL(candidate['library']);fn=getattr(library,candidate['function'])
    fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),c.c_void_p,c.c_void_p,c.c_void_p];fn.restype=c.c_int
    cost=json.loads(args.cost.read_text());costlib=c.CDLL(cost['library']);cycles_fn=costlib.biwn_native_cycle_cost
    cycles_fn.argtypes=[c.c_uint16,c.POINTER(CPU),c.c_void_p];cycles_fn.restype=c.c_int
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    out=ROOT/'verification/CPU-division-native-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());save(out/'entries.json',entries);print(out,flush=True)
    n=Native(diagnostic_core=core);l=n.lib;fixture=bytearray(atlas);fixture[20:24]=(0x190000).to_bytes(4,'big');fixture[0x190000:0x190002]=bytes.fromhex('4e73')
    for at in [0x1d0000-8,0x1e0000-8]:fixture[at:at+8]=b'\xa5'*8
    n.device.seed(bytes(fixture),0);image=bytearray(fixture);accesses=[];callback_errors=[]
    def reader(width):
        def cb(_,a,p):
            if a>0x200000-width:callback_errors.append(('read',a,width));return 1
            p[0]=int.from_bytes(image[a:a+width],'big');accesses.append(['r',a,width,p[0]]);return 0
        return cb
    def writer(width):
        def cb(_,a,v):
            if a>0x200000-width:callback_errors.append(('write',a,width));return 1
            image[a:a+width]=int(v).to_bytes(width,'big');accesses.append(['w',a,width,v]);return 0
        return cb
    callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4))]
    bus=Bus(*callbacks,CALL(),None,0);rng=random.Random(0xD1E0E5C4);rows=[];mismatches=[]
    pairs=[(0,0),(0,1),(1,1),(0x7fff,1),(0x8000,1),(0xffff,1),(0x10000,1),(0x7fffffff,2),(0x80000000,0xffff),(0x80000000,0x8000),(0xffffffff,0xffff),(0xffff8000,1),(0x12345678,0x7fff),(0xfffeffff,0x8000)]
    try:
        for entry in entries:
            if args.zero_only and entry['operand_kind']=='immediate':continue
            values=[(0x12345678,0)] if args.zero_only else pairs
            for dividend,divisor in values:
                if entry['operand_kind']=='immediate':divisor=entry['operand']
                masks=range(8) if divisor==0 else [0]
                for ipl in masks:
                    for mode in [0,0x2000]:
                        for flags in range(32):
                            image[:]=fixture
                            # Undo all native stores from the previous single instruction.
                            for at in [0x1d0000-8,0x1e0000-8]:
                                n.device.direct(at,4,int.from_bytes(fixture[at:at+4],'big'));n.device.direct(at+4,4,int.from_bytes(fixture[at+4:at+8],'big'))
                            regs=[rng.getrandbits(32) for _ in range(15)]+[0x1d0000]
                            regs[entry['destination']]=dividend
                            if entry['operand_kind']=='register':regs[entry['operand']]=(regs[entry['operand']]&0xffff0000)|divisor
                            elif entry['operand_kind']=='absolute':
                                at=entry['operand'];image[at:at+2]=divisor.to_bytes(2,'big');n.device.direct(at,2,divisor)
                            else:
                                # Restore the other absolute divisor bytes, which are
                                # data in both the immutable atlas and this fixture.
                                pass
                            for absolute in [0x49d24,0x49d26]:
                                if entry['operand_kind']!='absolute' or absolute!=entry['operand']:
                                    n.device.direct(absolute,2,int.from_bytes(fixture[absolute:absolute+2],'big'))
                            sr=mode|(ipl<<8)|flags
                            l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1e0000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1c0000);l.m68k_set_reg(17,sr)
                            for i,value in enumerate(regs):l.m68k_set_reg(i,value)
                            l.m68k_set_reg(16,entry['pc'])
                            before=CPU();before.registers[:]=regs;before.pc=entry['pc'];before.sr=sr;before.usp=n.prefix[16] if mode else regs[15];before.ssp=regs[15] if mode else n.prefix[17]
                            actual=CPU.from_buffer_copy(bytes(before));accesses.clear();callback_errors.clear()
                            buffer=(c.c_uint8*len(image)).from_buffer(image)
                            predicted_cycles=cycles_fn(int(entry['bytes'][:4],16),c.byref(before),buffer)
                            status=fn(c.byref(bus),c.byref(actual),None,None,None)
                            native_cycles=l.m68k_execute(1)
                            expected=CPU();expected.registers[:]=[l.m68k_get_reg(None,i) for i in range(16)];expected.pc=l.m68k_get_reg(None,16);expected.sr=l.m68k_get_reg(None,17);expected.usp=n.prefix[16] if expected.sr&0x2000 else expected.registers[15];expected.ssp=expected.registers[15] if expected.sr&0x2000 else n.prefix[17]
                            native_ram=n.device.ram()
                            state_equal=cpu_dict(actual)==cpu_dict(expected);RAM_equal=native_ram==bytes(image)
                            matched=status in [0,11] and state_equal and RAM_equal and predicted_cycles==native_cycles and not callback_errors
                            rows.append(dict(pc=hex(entry['pc']),sr=sr,dividend=dividend,divisor=divisor,status=status,CPU_equal=state_equal,RAM_equal=RAM_equal,predicted_cycles=predicted_cycles,native_cycles=native_cycles,matched=matched))
                            if not matched and len(mismatches)<12:mismatches.append(dict(**rows[-1],before=cpu_dict(before),expected=cpu_dict(expected),actual=cpu_dict(actual),C_accesses=list(accesses)))
            print(hex(entry['pc']),'cases',len(rows),'failed',sum(not row['matched'] for row in rows),flush=True)
    finally:n.close()
    save(out/'cases.json',rows);save(out/'first-mismatches.json',mismatches)
    proof=dict(status='terminal_division_CPU_native_pass' if all(row['matched'] for row in rows) else 'terminal_division_CPU_native_rejected',directory=str(out),
        cases=len(rows),failed_cases=sum(not row['matched'] for row in rows),zero_divisor_cases=sum(row['divisor']==0 for row in rows),
        CPU_mismatches=sum(not row['CPU_equal'] for row in rows),RAM_mismatches=sum(not row['RAM_equal'] for row in rows),cost_mismatches=sum(row['predicted_cycles']!=row['native_cycles'] for row in rows),
        zero_only=args.zero_only,CPU_candidate=str(cp),cost_candidate=str(args.cost),
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',cp,Path(candidate['library']),Path(candidate['instruction_RAM_source']),args.cost,Path(cost['library']),core]},
        scope='28 fixed division addresses; controlled valid-RAM operands and trap stack/vector, both modes/allCCR, allIPL on zero cases; fullCPU/2MBRAM and pinned emulator instruction charge. No arbitrary busfaults/aliasing, asynchronous IRQs or physical timing.',new_training=False,default_promoted=False)
    save(out/'protocol.json',proof);save(ROOT/'verification/CPU-division-native-check-current.json',proof)
    print(json.dumps({k:proof[k]for k in ['status','cases','failed_cases','zero_divisor_cases','CPU_mismatches','RAM_mismatches','cost_mismatches']}),flush=True)

if __name__=='__main__':main()
