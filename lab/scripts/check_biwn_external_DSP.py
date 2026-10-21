"""Native/strict-owner atomic checks from real external-DSP witnesses and controlled variants."""
import argparse,ctypes as c,json,random,struct,hashlib
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from check_biwn_scheduler import Native
from biwn_DSP_music_owner import OWNER,Stats
import biwn_DSP_program_router

def read(p):return json.loads(Path(p).read_text())
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--candidate',type=Path,default=ROOT/'verification/external-DSP-experimental-candidate-current.json');parser.add_argument('--random-cases',type=int,default=0);args=parser.parse_args()
    candidate=read(args.candidate);observed=read(ROOT/'verification/merchant-DSP-transition-observation-current.json')
    identities=read(Path(candidate['directory'])/'external-identities.json');by={r['address']:r for r in identities}
    witnesses=[w for w in observed['observer']['witnesses']if int(w['PC'],16)in by]
    assert len(witnesses)==460
    fixture=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    for row in identities:fixture[row['address']:row['address']+2]=bytes.fromhex(row['bytes'])
    fixture=bytes(fixture)
    out=ROOT/'verification/external-DSP-native-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    cases=[dict(kind='captured',witness=w,raw=Path(w['file']).read_bytes())for w in witnesses]
    rng=random.Random(0xD5F0E);chosen=[0,2,4,0xa,0x22,0x82,0x8a,0x8e,0x92,0x102]
    for i in range(args.random_cases):
        pc=chosen[i%len(chosen)];w=next(w for w in witnesses if int(w['PC'],16)==pc);raw=bytearray(Path(w['file']).read_bytes());variant=i//len(chosen)
        edges=[0,1,0x7fffff,0x800000,0x7fffffff,0x80000000,0xffffffff,0xfffffffe,0x100,0xff000000,0xff0000,0x12345678,0x87654321,0xffffff,0xff800000,0x55555555];bank=(variant//len(edges))%2
        regs=[rng.getrandbits(32)for _ in range(64)]
        word=int(w['opcode'],16);m=(word>>5)&31;n=word&31
        if variant<128:regs[bank*32+m]=edges[variant%len(edges)];regs[bank*32+n]=edges[(variant*7)%len(edges)]
        if pc==2:regs[bank*32+8]=0xf1b800+4*(i%64) # valid local DSP stores, no invented peripheral transactions
        struct.pack_into('=64I',raw,8239,*regs);struct.pack_into('=I',raw,8212,bank<<14);raw[8495]=bank;raw[8236:8239]=bytes([rng.randrange(2),rng.randrange(2),(variant//(len(edges)*2))%2])
        cases.append(dict(kind='controlled_register_variant',witness=w,raw=bytes(raw)))
    native=Native(diagnostic_core=Path(candidate['required_core_path']));core=native.lib
    core.DSPStateSave.argtypes=[c.c_void_p];core.DSPStateSave.restype=c.c_size_t;core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t;core.DSPExec.argtypes=[c.c_int32]
    core.BIWNSetDSPInstructionOwner.argtypes=[OWNER];counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count')
    def raw_state():
        b=c.create_string_buffer(32768);n=core.DSPStateSave(b);assert n==8729;return b.raw[:n]
    owner=biwn_DSP_program_router.install(core,out,args.candidate);callback,library,host,finish=owner
    library.biwn_DSP_external_stats.restype=c.POINTER(Stats)
    rows=[];bad=[]
    try:
        for i,case in enumerate(cases):
            raw=case['raw'];pc=int(case['witness']['PC'],16)
            core.BIWNSetDSPInstructionOwner(OWNER());native.device.seed(fixture,0);assert core.DSPStateLoad(c.create_string_buffer(raw))==len(raw)
            before=counter.value;core.DSPExec(1);retired=(counter.value-before)&0xffffffff;assert retired==1
            expected=raw_state();expected_RAM=hashlib.sha256(native.device.ram()).hexdigest()
            native.device.seed(fixture,0);assert core.DSPStateLoad(c.create_string_buffer(raw))==len(raw)
            assert library.biwn_DSP_router_begin(c.byref(host))==0;core.BIWNSetDSPInstructionOwner(callback)
            core.DSPExec(1);actual=raw_state();counts={k:getattr(core,'BIWNDSP'+k+'InstructionCount')()for k in ['Owned','Original','Rejected']};stats=library.biwn_DSP_external_stats().contents
            RAM_equal=hashlib.sha256(native.device.ram()).hexdigest()==expected_RAM;logical_equal=actual[:8496]==expected[:8496]
            matched=logical_equal and RAM_equal and counts==dict(Owned=1,Original=0,Rejected=0) and stats.errors==stats.uncovered==0
            row=dict(case=i,kind=case['kind'],pc=hex(pc),opcode=case['witness']['opcode'],matched=matched,logical_DSP_equal=logical_equal,RAM_equal=RAM_equal,core_counts=counts,external_errors=stats.errors)
            rows.append(row)
            if not matched and len(bad)<8:
                before_regs=struct.unpack_from('=64I',raw,8239);word=int(case['witness']['opcode'],16);bank=raw[8495];m=(word>>5)&31;n=word&31
                detail=dict(**row,input_RM=hex(before_regs[bank*32+m]),input_RN=hex(before_regs[bank*32+n]),incoming_carry=raw[8238],expected_RN=hex(struct.unpack_from('=I',expected,8239+4*(bank*32+n))[0]),actual_RN=hex(struct.unpack_from('=I',actual,8239+4*(bank*32+n))[0]),logical_difference_offsets=[j for j,(a,b)in enumerate(zip(expected[:8496],actual[:8496]))if a!=b][:24])
                bad.append(detail);(out/f'case-{i}-native.bin').write_bytes(expected);(out/f'case-{i}-C.bin').write_bytes(actual)
        final=finish();save(out/'cases.json',rows);save(out/'first-mismatches.json',bad)
        proof=dict(status='terminal_external_DSP_native_pass'if all(x['matched']for x in rows)else'terminal_external_DSP_native_rejected',directory=str(out),cases=len(rows),captured_cases=460,controlled_variants=args.random_cases,failed_cases=sum(not x['matched']for x in rows),first_mismatches=bad,candidate=str(args.candidate),candidate_sha256=sha(args.candidate),source_original_fallbacks=sum(x['core_counts']['Original']for x in rows),final_case_owner_report=final,
            scope='Atomic original DSP versus fixed C owner using captured full DSP states and controlled main RAM with observed instruction bytes. Full8496logicalDSPbytes and all2MBRAM compared each case; no clocks/concurrentCPU/IRQ or fresh gameplay proof. Controlled variants restrict stores to valid local DSP RAM. Private233byte pipeline tail excluded from equality.',
            source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',args.candidate,Path(candidate['library']),Path(candidate['external_library']),Path(candidate['directory'])/'biwn_external_arithmetic.c',Path(observed['directory'])/'protocol.json']},new_training=False,default_promoted=False)
        save(out/'protocol.json',proof);save(ROOT/'verification/external-DSP-native-check-current.json',proof);print(json.dumps({k:proof[k]for k in ['status','cases','failed_cases','first_mismatches']}),flush=True)
    except BaseException as error:
        save(out/'protocol.json',dict(status='terminal_external_DSP_check_driver_failed',directory=str(out),error=repr(error),candidate=str(args.candidate),semantic_result=False))
        raise
    finally:native.close()

if __name__=='__main__':main()
