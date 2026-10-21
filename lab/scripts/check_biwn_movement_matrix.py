"""GPU4320 preserved execution vs native high-level C; no core changes/frames."""
import argparse,ctypes as c,hashlib,json,random,sys
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_inventory_frame as frame
import check_biwn_sprite_decode as sprite
ROOT=frame.ROOT
R16=sprite.R16;W16=sprite.W16
class Bus(c.Structure):_fields_=[('read16',R16),('write16',W16),('context',c.c_void_p),('read_budget',c.c_uint32)]
class Result(c.Structure):_fields_=[('matrix_and_translation',c.c_uint32*12),('raw_products',c.c_uint32*3),('final_pointer',c.c_uint32)]
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def result_dict(result):return {'matrix_and_translation':list(result.matrix_and_translation),'raw_products':list(result.raw_products),'final_pointer':result.final_pointer}

def host(fn,memory,args,budget=12,missing=None):
    def read(_,a,v):
        try:v[0]=memory.read(a,2);return 0
        except Exception as error:memory.errors.append(str(error));return 1
    def write(_,a,v):
        try:memory.write(a,2,v);return 0
        except Exception as error:memory.errors.append(str(error));return 1
    r=R16(read)if missing!=0 else R16();w=W16(write)if missing!=1 else W16()
    bus=Bus(r,w,None,budget);output=Result();c.memset(c.byref(output),0xa5,c.sizeof(output));before=bytes(output)
    status=fn(c.byref(bus),*args,c.byref(output))
    return status,bus.read_budget,bytes(output)==before

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'gpu-movement-overlay/mapping.json').read_text())
    decoded=json.loads((session/'gpu-movement-overlay/original-code-decode.json').read_text())['instructions'];opcodes={x['address']:int(x['bytes'][:4],16)>>10 for x in decoded}
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(snapshot).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    assert hashlib.sha256(snapshot[0x4328:0x4720]).hexdigest()==mapping['sha256']
    out=ROOT/'verification/biwn-movement-matrix'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    cases=[{'kind':'actual_snapshot_arguments','params':[0x49ccc,0,snapshot[0x49cba],0,int.from_bytes(snapshot[0x49cc4:0x49cc8],'big')]}]
    for axis in range(3):
        for angle in range(256):
            p=[0x49ccc,0,0,0,[0,1,0xffff,0x8000,0x7fff][angle%5]];p[axis+1]=angle
            cases.append({'kind':'exhaustive_low_byte_single_axis','axis':axis,'angle':angle,'params':p})
    rng=random.Random(0x4320)
    for i in range(256):
        cases.append({'kind':'mixed_angles_and_full_width_inputs','params':[rng.choice([0x49ccc,0x110000,0x120002]),*[0 if rng.randrange(4)==0 else rng.getrandbits(32)for _ in range(3)],rng.choice([0x10000,0xffff0000,rng.getrandbits(32)])]})
    if args.limit:cases=cases[:args.limit]
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-movement-device.dylib')
    lib=device.lib;lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0
    lib.lab_movement_original.argtypes=[c.c_uint32]*6;lib.lab_movement_original.restype=c.c_int
    lib.lab_movement_C.argtypes=[c.c_uint32]*5+[c.POINTER(Result),c.c_uint32];lib.lab_movement_C.restype=c.c_int
    lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    lib.lab_movement_register.argtypes=[c.c_uint,c.c_uint];lib.lab_movement_register.restype=c.c_uint32
    lib.lab_movement_history.argtypes=[c.POINTER(c.c_uint32)];lib.lab_movement_history.restype=c.c_int
    lib.lab_movement_steps.restype=c.c_uint32
    rows=[];coverage=set();direct_coverage=set();delay_coverage=set()
    try:
        for i,case in enumerate(cases):
            save(out/'status.json',{'status':'running','case':i});ram=bytearray(snapshot);p=case['params'];base=p[0]
            if i:
                ram[base:base+32]=rng.randbytes(32)
                for j in range(3):ram[base+18+j*2:base+20+j*2]=rng.choice([0,1,0xffff,0x7fff,0x8000,rng.randrange(65536)]).to_bytes(2,'big')
            device.seed(ram,0);assert lib.lab_movement_original(*p,rng.getrandbits(32))==0
            original=device.ram();original_registers=[lib.lab_movement_register(0,j)for j in range(32)];alternate=[lib.lab_movement_register(1,j)for j in [0,1,3]]
            original_steps=lib.lab_movement_steps();events=[]
            for index in range(lib.lab_movement_event_count()):
                ev=(c.c_uint32*5)();assert lib.lab_movement_event(index,ev)==0
                if ev[0]not in [11,12]:continue
                assert ev[1]==3;pc=ev[2]-2;opcode=opcodes[pc];width={40:2,46:2}[opcode]
                events.append(('r'if ev[0]==11 else'w',ev[3],width,ev[4]))
            history=(c.c_uint32*1024)();count=lib.lab_movement_history(history);direct_coverage.update(history[:count]);coverage.update(history[:count])
            for pc in history[:count]:
                if opcodes.get(pc)in [52,53]:delay_coverage.add(pc+2);coverage.add(pc+2)
            assert len(events)==36 and all(event[3]==0 for event in events if event[0]=='r')
            device.seed(ram,1);output=Result();status=lib.lab_movement_C(*p,c.byref(output),12);rebuilt=device.ram()
            predicted=[('r'if kind==4 else'w',address,width,value)for kind,address,width,value in device.trace]
            assert all(kind in [4,5]for kind,_,_,_ in device.trace)
            match_shape=[x[:3]for x in events]==[x[:3]for x in predicted]
            match_writes=[x for x in events if x[0]=='w']==[x for x in predicted if x[0]=='w']
            result=result_dict(output);match_regs=result['matrix_and_translation']==original_registers[9:21] and result['raw_products']==alternate and result['final_pointer']==original_registers[0]
            if status or original!=rebuilt or not match_shape or not match_writes or not match_regs:
                save(out/'mismatch.json',{'case':case,'C_status':status,'C_result':result,'original_matrix_registers':original_registers[9:21],'original_products':alternate,'original_pointer':original_registers[0],'original_trace':events,'C_trace':predicted,'RAM_differences':[[j,original[j],rebuilt[j]]for j in range(len(original))if original[j]!=rebuilt[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
            assert not device.stats()['GPUExec1_calls'] and not device.stats()['game_frames_executed']
            assert rebuilt[base+24:base+26]==ram[base+24:base+26]
            rows.append({'case':case,'initial_matrix32_bytes':bytes(ram[base:base+32]).hex(),'output_matrix32_bytes':rebuilt[base:base+32].hex(),'C_result':result,'original_GPUExec1_calls':original_steps,'external_bus_shape_and_write_values_match':True,'whole2MB_RAM_match':True,'key_registers_match':True,'original_trace':events,'C_trace':predicted,'RAM_sha256':hashlib.sha256(rebuilt).hexdigest()})
    finally:device.close()
    save(out/'fixtures.json',rows)
    if args.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}),flush=True);return
    fn=lib.biwn_movement_matrix;fn.argtypes=[c.POINTER(Bus)]+[c.c_uint32]*5+[c.POINTER(Result)];fn.restype=c.c_int
    guards=[];params=cases[0]['params'];base=params[0]
    assert fn(None,*params,c.byref(Result()))==1 and fn(c.byref(Bus()),*params,None)==1;guards.extend([{'null_bus':True,'status':1},{'null_output':True,'status':1}])
    for missing in [0,1]:
        mem=sprite.Memory(snapshot);status,_,unchanged=host(fn,mem,params,missing=missing);assert status==1 and unchanged and not mem.trace;guards.append({'missing_callback':missing,'status':1})
    for budget in [0,5,11]:
        mem=sprite.Memory(snapshot);status,remaining,unchanged=host(fn,mem,params,budget);assert status==2 and remaining==0 and unchanged and len([t for t in mem.trace if t[0]=='w'])==9
        guards.append({'read_budget':budget,'status':2,'prior_identity_stores_retained':9})
    for read,write in [((base+4,2),None),(None,(base,2)),(None,(base+26,2))]:
        mem=sprite.Memory(snapshot);mem.fail_read=read;mem.fail_write=write;status,_,unchanged=host(fn,mem,params);assert status==3 and unchanged
        guards.append({'failed_read':read,'failed_write':write,'status':3,'partial_trace':mem.trace})
    save(out/'guards.json',guards)
    covered=[row for row in decoded if row['address']in coverage]
    save(out/'coverage.json',{'covered':len(covered),'total':len(decoded),'missing':[row for row in decoded if row['address']not in coverage],'observed_PCs':sorted(coverage)})
    assert len(covered)==len(decoded),'OriginalGPU instruction coverage incomplete'
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'original_GPU_movement_overlay_matches_high_level_C','directory':str(out),'GPU_cases':len(rows),'single_axis_angle_cases':768,'mixed_cases':256,'actual_snapshot_argument_cases':1,'host_guard_cases':len(guards),'GPU_instructions_covered':len(covered),'GPU_code_instructions':len(decoded),'direct_PC_instruction_count':sum(row['address']in direct_coverage for row in decoded),'mandatory_delay_instruction_count':sum(row['address']in delay_coverage and row['address']not in direct_coverage for row in decoded),'coverage_method':'Pinned PC history omits directly executed branch delay slots; these are derived from executed JUMP/JR and JTRMpage39 always-executed rule, not claimed as directly recorded PCs.','overlay_bytes':1016,'overlay_sha256':mapping['sha256'],'processor':'GPU','portable_components':1,
            'source_sha256':{name:frame.draw.binary_tools.sha(ROOT/'projects/black-ice-white-noise/restoration'/name)for name in ['biwn_movement_matrix.c','biwn_movement_matrix.h']},'core_sha256':frame.draw.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),'bridge_sha256':frame.draw.binary_tools.sha(ROOT/'tools/libbiwn-movement-device.dylib'),
            'matched':['All2MB mainRAM; all external read address/width/order and write values/order; final12matrix/translation registers,three alternate-bank raw products and delay-slot final pointer.','All256low-byte angles on each axis, signed speed limits, zero/truncated speeds, full32bit angle inputs, mixed rotations, poisoned initial matrices, signed/wrapped translation words and preserved gap.','All353GPU code instructions covered by recordedPCs plus mandatory branch delay slots perJTRMpage39; noCPU/DSP/gameframes execute in this isolated oracle.'],
            'limits':['Pinned softwareemulator, not physical hardware or timing; originalwatch readvalues are zero placeholders.','Halfword-aligned mainRAM matrices with fixed original sine table; arbitrary aliasing into GPUcode/mailboxes or asynchronous schedules excluded.','OriginalGPUoverlay copied from preserved header-selected payload; dispatcher scheduling/completion modeled by stopping atF031BE, not reconstructed.','High-level C is not yet connected to the CPU update caller; collision/terrain/scene/entity helpers and full game remain unfinished.','Host errors/read budgets are added behavior; partial RAM effects retained, result struct committed only on success.'],
            'rotation_order':['angle2','angle1','angle3'],'sine_table_entries':65,'fixed_point_fraction_bits':14,'speed_semantics':'signed low16','translation_rounding':'arithmetic right shift14 without rounding bias; rotations add8192 before arithmetic shift14'}
    save(out/'report.json',report);save(ROOT/'verification/biwn-movement-matrix-checks.json',report);save(out/'status.json',{'status':'terminal','exit_code':0});print(json.dumps(report),flush=True)

if __name__=='__main__':main()
