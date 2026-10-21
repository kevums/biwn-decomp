"""Compare local semantic C against original DSP and independent compression."""
import ctypes as c,json,os,random,struct,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_scheduler as scheduler
import check_biwn_TOC_compression as reference
ROOT=scheduler.ROOT
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    model=ROOT/'verification/TOC-checksum-local-code/20261015T091703.486405Z/repair-1'
    code=model/'candidate.c';text=code.read_text();assert text.startswith('#include')and '```'not in text
    out=ROOT/'verification/BIWN-TOC-local-C'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    lib=out/'checksum.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(code),'-o',str(lib)]
    build=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert build.returncode==0
    fn=c.CDLL(str(lib)).biwn_firmware_TOC_checksum;fn.argtypes=[c.POINTER(c.c_uint8),c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];fn.restype=c.c_int
    source=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T083153.831713Z/fourth-DSP-command';incoming=(source/'DSP-after-CPU.bin').read_bytes();ram=(source/'RAM-after-CPU.bin').read_bytes()
    constants=[]
    for group in range(4):constants.extend(struct.unpack_from('>16I',incoming,0x3fc+76*group+12))
    assert constants==reference.K;K=(c.c_uint32*64)(*constants)
    rng=random.Random(0x50df4);cases=[('source_TOC',incoming[0x800:0xc00]),('zero',bytes(1024)),('all_ff',bytes([255])*1024),('byte_ramp',bytes(range(256))*4)]
    cases.extend((f'single_byte_{offset}',incoming[0x800:0x800+offset]+bytes([incoming[0x800+offset]^128])+incoming[0x801+offset:0xc00])for offset in [0,7,8,12,47,48,63,64,255,511,767,1023])
    cases.extend((f'random_{i}',rng.randbytes(1024))for i in range(8));assert len(cases)==24
    run=scheduler.Native();core=run.lib;core.DSPStateLoad.argtypes=[c.c_void_p];core.DSPStateLoad.restype=c.c_size_t;core.DSPStateSave.argtypes=[c.c_void_p];core.DSPStateSave.restype=c.c_size_t
    core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];core.DSPReadLong.restype=c.c_uint32;core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.DSPExec.argtypes=[c.c_int32];core.DSPGetPC.restype=c.c_uint32
    counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count');buffer=c.create_string_buffer(12000);rows=[]
    try:
        for label,data in cases:
            inp=(c.c_uint8*1024).from_buffer_copy(data);result=(c.c_uint32*4)();assert fn(inp,K,result)==0
            C=struct.pack('>4I',*result);independent,blocks=reference.compress(data);assert C==independent,(label,'independent mismatch')
            run.device.seed(ram,0);state=bytearray(incoming);state[0x800:0xc00]=data;assert core.DSPStateLoad(c.create_string_buffer(bytes(state)))==8729;CPU_before=bytes(run.prefix);start=counter.value;native_blocks=[]
            for i in range(200000):
                if i and core.DSPReadLong(0xf1b020,0)&0x80000000:break
                if label=='source_TOC' and core.DSPGetPC()==0xf1b238:
                    assert core.DSPStateSave(buffer)==8729;raw=buffer.raw;values=struct.unpack_from('=64I',raw,8239);assert raw[8495]==1;native_blocks.append(struct.pack('>4I',*values[48:52]).hex())
                core.DSPExec(1)
            else:raise AssertionError('native command budget exceeded')
            command_count=(counter.value-start)&0xffffffff
            core.DSPWriteLong(0xf1b3f8,0xffffffff,6);core.DSPWriteLong(0xf1a114,5,6);start=counter.value
            for i in range(1000):
                if i and not core.DSPReadLong(0xf1b3f8,0)&0x80000000 and not core.DSPReadLong(0xf1a100,0)&8:break
                core.DSPExec(1)
            else:raise AssertionError('native IRQ did not return')
            native=run.device.ram()[0xfb1b0:0xfb1c0];assert native==C,(label,native.hex(),C.hex());assert bytes(run.prefix)==CPU_before
            if label=='source_TOC':assert native_blocks==blocks and len(blocks)==16;save(out/'source-block-checkpoints.json',dict(native=native_blocks,independent=blocks))
            rows.append(dict(case=label,TOC_sha256=hashlib.sha256(data).hexdigest(),digest=C.hex(),original_DSP_command_instructions=command_count,original_DSP_IRQ_instructions=(counter.value-start)&0xffffffff,CPU_register_prefix_unchanged=True))
        guards=[]
        for name,inp,table in [('null_TOC',None,K),('null_constants',(c.c_uint8*1024)(),None)]:
            sent=(c.c_uint32*4)(1,2,3,4);assert fn(inp,table,sent)==1 and list(sent)==[1,2,3,4];guards.append(name)
        assert fn((c.c_uint8*1024)(),K,None)==1;guards.append('null_out')
        report=dict(status='local_semantic_C_matches_original_DSP_and_independent_compression',directory=str(out),candidate_source=str(code),candidate_sha256=hashlib.sha256(code.read_bytes()).hexdigest(),compiler=command,cases=rows,cases_count=24,null_guards=guards,baseline_block_checkpoints=16,source_round_constants_verified=64,authorship='Local Restorer emitted repair1 from coordinator-supplied verified semantics; coordinator compiled/tested it. No coordinator edits to the repaired C body.',scope='1024byte checksum output only. Captured DSP/RAM boundary, synthetic TOC variants and supplied CPU IRQ; SSI/all clocks held. No full DSP register/IRQ/PC state replacement or live firmware C integration, no hardware/whole boot proof.',whole_boot=False,new_weight_training=False,raw_model_prompt_and_response=str(model/'request-and-response.json'))
        save(out/'report.json',report);save(ROOT/'verification/BIWN-TOC-local-C-current.json',report)
        print(json.dumps(dict(directory=str(out),cases=24,baseline_block_checkpoints=16,guards=3,status=report['status'])),flush=True)
    finally:run.close()

if __name__=='__main__':main()
