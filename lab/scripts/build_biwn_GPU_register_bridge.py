"""Build isolated GPU bridge using register-only APIs and existing source kernels.

Retains instruction identity fences, counts, bus effects and canonical optional
hash streams. Full RAM snapshots remain available for unknown-instruction logs.
"""
import hashlib,json,os,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    core=json.loads((ROOT/'verification/GPU-register-state-experimental-candidate.json').read_text())
    proof=json.loads((ROOT/'verification/GPU-register-state-current.json').read_text())
    assert proof['status']=='register_state_legacy_suffix_RAM_isolation_and_bank_pointer_match'
    core_path=Path(core['core_path']);assert proof['core_sha256']==core['core_sha256']==hashlib.sha256(core_path.read_bytes()).hexdigest()
    parent=json.loads((ROOT/'verification/C-space-mail-shared-GPU-experimental-candidate.json').read_text())
    path=Path(parent['directory'])/'shared_GPU_bridge.c';source=path.read_text()
    original_sha=hashlib.sha256(source.encode()).hexdigest()
    assert len(parent['ABI_sizes'])==24
    for slot,size in re.findall(r'\[(\d+)\]=\{(\d+),\{',source):assert int(slot)*2+int(size)<=4096
    source=source.replace('#include <stdio.h>','#include <stdio.h>\n#include <dlfcn.h>',1)
    resolver='''
static size_t (*save_registers)(uint8_t*);
static size_t (*load_registers)(const uint8_t*);
static void *core_handle;
static int resolve_register_APIs(void)
{
    Dl_info info;
    uint8_t full[4416],suffix[320];
    if(!dladdr((void*)H.save,&info)||!info.dli_fname)return 1;
    if(strcmp(info.dli_fname,CORE_PATH))return 1;
    core_handle=dlopen(info.dli_fname,RTLD_LAZY|RTLD_NOLOAD);
    if(!core_handle)return 1;
    save_registers=(size_t(*)(uint8_t*))dlsym(core_handle,"BIWNGPUStateSaveRegisters");
    load_registers=(size_t(*)(const uint8_t*))dlsym(core_handle,"BIWNGPUStateLoadRegisters");
    if(!save_registers||!load_registers)return 1;
    if(H.save(full)!=4416||save_registers(suffix)!=320||memcmp(full+4096,suffix,320))return 1;
    return 0;
}
static size_t save_fast(uint8_t *p){return save_registers(p+4096)==320?4416:0;}
static size_t load_fast(const uint8_t *p){return load_registers(p+4096)==320?4416:0;}
'''.replace('CORE_PATH',json.dumps(str(core_path)))
    marker='static uint32_t get32('
    assert source.count(marker)==1;source=source.replace(marker,resolver+'\n'+marker,1)
    assert source.count('memcpy(p,s->local_RAM,4096);')==1
    source=source.replace('memcpy(p,s->local_RAM,4096);','')
    # Six full-state kernels carry all metadata themselves;18partial-state
    # wrappers refresh the unmodeled fields after bus callbacks.
    assert source.count('H.save(raw_after)')==18
    source=source.replace('H.save(raw_after)','save_fast(raw_after)')
    prefix,owner=source.split('int biwn_fast_GPU_owner(',1)
    assert owner.count('H.save(raw)')==1 and owner.count('H.load(raw)')==1
    owner=owner.replace('H.save(raw)','save_fast(raw)').replace('H.load(raw)','load_fast(raw)')
    owner=owner.replace('uint32_t count,operand;','uint32_t count,operand,delay_operand;')
    marker='slot=(pc-0xf03000u)/2;';assert owner.count(marker)==1
    owner=owner.replace(marker,marker+'delay_operand=slot+1<2048?((uint32_t)((uint8_t*)H.RAM())[slot*2+2]<<8)|((uint8_t*)H.RAM())[slot*2+3]:0;')
    owner=owner.replace('matches(0,slot,raw,opcode)','matches(0,slot,(const uint8_t*)H.RAM(),opcode)')
    owner=owner.replace('matches(k,slot,raw,opcode)','matches(k,slot,(const uint8_t*)H.RAM(),opcode)')
    marker='operand=((uint32_t)raw[slot*2+2]<<8)|raw[slot*2+3];';assert owner.count(marker)==1
    owner=owner.replace(marker,'operand=delay_operand;')
    assert owner.count('CC_SHA256(raw,4396,hash);')==2
    owner=owner.replace('CC_SHA256(raw,4396,hash);','memcpy(raw,H.RAM(),4096);CC_SHA256(raw,4396,hash);')
    marker='H=*h;mode=m;memset(&S,0,sizeof(S));';assert owner.count(marker)==1
    owner=owner.replace(marker,'H=*h;mode=m;if(resolve_register_APIs())return 3;memset(&S,0,sizeof(S));')
    source=prefix+'int biwn_fast_GPU_owner('+owner
    # The unknown-capture path retains the actual full legacy snapshot.
    unknown=source.split('static int uncovered(',1)[1].split('static const struct identity*maps',1)[0]
    assert 'H.save(raw)'in unknown and 'save_fast(raw)'not in unknown
    out=ROOT/'verification/GPU-register-bridge-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    target=out/'register_GPU_bridge.c';target.write_text(source);library=out/'libregister-GPU-bridge.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(target),parent['kernel_library'],'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr)
    assert built.returncode==0,str(out/'compiler.log')
    report=dict(parent,status='compiled_register_bridge_unverified',directory=str(out),library=str(library),
                original_bridge=parent['library'],source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                parent_bridge_source_sha256=original_sha,required_core_path=str(core_path),required_core_sha256=core['core_sha256'],
                GPU_register_state_proof=str(ROOT/'verification/GPU-register-state-current.json'),
                GPU_register_API_bytes=320,shared_local_RAM=True,RAM_copy_in_frame_only_path=False,
                optional_hashes_capture_RAM=True,unknown_capture_retains_full_legacy_state=True,
                additional_guest_instruction_batching=False,existing_delay_pair_protocol=True,identity_fences_retained=True,new_training=False,
                accepted_defaults_changed=False,whole_game_complete=False,
                scope='Same24sourcekernels and exact per-instruction owner/counter/timing protocol. Snapshot suffix uses the diagnostic320byte API; shared4096byteGPUlocalRAM is not copied in the normal frame-only path. Source-byte fences read live RAM; delayed-branch decoder operand is captured before execution. Optional full-state hashes and unknown logs still include allRAM. Compiled only; game equivalence, full hash streams and performance unverified.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/GPU-register-bridge-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)

if __name__=='__main__':main()
