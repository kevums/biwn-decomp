"""Compare local ADDX helper with original opcode execution, both inputs/CCR."""
import ctypes as c,json,re,subprocess,random,os,hashlib,argparse
from pathlib import Path
import check_biwn_scheduler as scheduler
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('protocol',type=Path);parser.add_argument('--final-after-thinking',action='store_true');args=parser.parse_args();d=json.loads(args.protocol.read_text());answer=d['results'][0]['answer'];raw_answer=answer
    if args.final_after_thinking:
        assert '</think>'in answer;answer=answer.rsplit('</think>',1)[1]
    blocks=re.findall(r'```(?:c)?\s*\n(.*?)```',answer,re.S);assert len(blocks)==1;code=blocks[0]
    assert re.search(r'static uint32_t biwn_addx_long\(uint16_t \*sr, uint32_t src, uint32_t dst\)',code)
    assert not any(token in code for token in ['#include','system(','asm','__attribute__','extern','[',']'])
    out=args.protocol.parent/'ADDX-code-gate';out.mkdir(exist_ok=True);(out/'candidate.inc').write_text(code)
    source=out/'candidate.c';source.write_text('#include <stdint.h>\n'+code+'\nuint32_t tested_addx(uint16_t *sr,uint32_t src,uint32_t dst){return biwn_addx_long(sr,src,dst);}\n');lib=out/'libaddx.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)];build=subprocess.run(command,text=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    fn=c.CDLL(str(lib)).tested_addx;fn.argtypes=[c.POINTER(c.c_uint16),c.c_uint32,c.c_uint32];fn.restype=c.c_uint32
    core=Path(json.loads((ROOT/'verification/BIWN-CPU-IRQ-state-export-candidate.json').read_text())['core_path']);native=scheduler.Native(diagnostic_core=core);cpu=native.lib;native.device.pointer=native.device.lib.lab_device_ram();native.device.direct(0x10000,2,0xd181);native.device.direct(0x10002,2,0x4e71);cpu.m68k_pulse_reset();cpu.m68k_set_irq(0);cpu.m68k_set_reg(17,0x2700);cpu.m68k_set_reg(15,0x1e0000)
    values=[0,1,2,0x7fffffff,0x80000000,0x80000001,0xfffffffe,0xffffffff];rng=random.Random(0x41444458);cases=[(src,dst,sr|ccr)for src in values for dst in values for sr in [0x2700,0x2300]for ccr in range(32)]+[(rng.getrandbits(32),rng.getrandbits(32),0x2700|rng.randrange(32))for _ in range(65536)]
    failed=0;examples=[]
    try:
        for src,dst,sr in cases:
            cpu.m68k_set_reg(0,dst);cpu.m68k_set_reg(1,src);cpu.m68k_set_reg(17,sr);cpu.m68k_set_reg(16,0x10000);cycles=cpu.m68k_execute(1);assert cycles==8 and cpu.m68k_get_reg(None,16)==0x10002
            expected=cpu.m68k_get_reg(None,0);expected_sr=cpu.m68k_get_reg(None,17);actual_sr=c.c_uint16(sr);actual=fn(c.byref(actual_sr),src,dst)
            if actual!=expected or actual_sr.value!=expected_sr:
                failed+=1
                if len(examples)<16:examples.append(dict(src=src,dst=dst,incoming_SR=sr,expected_result=expected,actual_result=actual,expected_SR=expected_sr,actual_SR=actual_sr.value))
    finally:native.close()
    report=dict(status='pass'if not failed else'rejected_local_ADDX_code',cases=len(cases),failure_count=failed,failures=examples,reference='Original pinned D181 ADDX.L D1,D0 opcode, not mirrored implementation tests',core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(code.encode()).hexdigest(),protocol=str(args.protocol.resolve()),original_CPU_on_reference_only=True,new_training=False,candidate_selection='last final code block after raw thinking delimiter; full response unmodified and format-unready'if args.final_after_thinking else'only response code block',scope='Single ADDX primitive only; game math integration, all helper instructions and full game remain separate gates.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));print(out)

if __name__=='__main__':main()
