"""Link the new typed-CCR string body into the same resident layout/ABI."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def main():
    parent_path=ROOT/'verification/native-format-optimization-builds/20261018T160621.790163Z/O2-lean/bundle.json'
    parent=json.loads(parent_path.read_text());assert sha(parent['binary'])==parent['binary_sha256']
    for path,digest in parent['source_sha256'].items():assert sha(path)==digest,path
    prep_path=ROOT/'verification/native-string-ccr-preparation-current.json';prep=json.loads(prep_path.read_text())
    assert sha(prep['source'])==prep['source_sha256']
    old_make=Path(parent['directory'])/'Makefile';text=old_make.read_text();assert text.count(parent['string_source'])==1
    out=ROOT/'verification/native-string-ccr-bundle'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    makefile=out/'Makefile';makefile.write_text(text.replace(parent['string_source'],prep['source']))
    build=out/'build';cmd=['make','-f',str(makefile),'format-bundle','BUILD='+str(build)]
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    result=subprocess.run(cmd,cwd=native,capture_output=True,text=True);(out/'make.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    binary=build/'native-format-bundle.bin';elf=binary.with_suffix('.elf');payload=binary.read_bytes();assert len(payload)<=parent['reserved_bytes']
    symbols={}
    for line in subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'--defined-only',str(elf)],text=True).splitlines():
        fields=line.split()
        if len(fields)==3:symbols[fields[2]]=int(fields[0],16)
    assert symbols['biwn_native_heap_start']==parent['heap_start']
    unchanged_prefix=parent['symbols']['biwn_native_format_string']-parent['base']
    previous=Path(parent['binary']).read_bytes();expected_prefix=bytearray(previous[:unchanged_prefix]);relocations=[]
    old_mul=parent['symbols']['__mulsi3'];new_mul=symbols['__mulsi3']
    assert previous[old_mul-parent['base']:]==payload[new_mul-parent['base']:],'Runtime multiply implementation changed'
    # libgcc is linked after the shortened string body. Only actual aligned
    # JSR abs.l operands targeting that unchanged routine may move in prefix.
    pattern=b'\x4e\xb9'+old_mul.to_bytes(4,'big')
    for i in range(0,len(expected_prefix)-5,2):
        if previous[i:i+6]==pattern:
            expected_prefix[i+2:i+6]=new_mul.to_bytes(4,'big')
            relocations.append(dict(JSR_PC=parent['base']+i,symbol='__mulsi3',old_target=old_mul,new_target=new_mul))
    assert payload[:unchanged_prefix]==bytes(expected_prefix)
    assert all(symbols[k]==v for k,v in parent['symbols'].items()if v<parent['symbols']['biwn_native_format_string'])
    proof={**parent,'status':'CCR_liveness_string_linked_pending_exact_bundle_checks','pid':os.getpid(),'directory':str(out),
        'binary':str(binary),'binary_sha256':sha(binary),'ELF':str(elf),'symbols':symbols,'binary_bytes':len(payload),
        'padding_bytes':parent['reserved_bytes']-len(payload),'parent_bundle_proof':str(parent_path),'parent_bundle_sha256':sha(parent_path),
        'string_source':prep['source'],'string_authorship':'Coordinator typed-IR compiler with per-bit CCR liveness; not model output.',
        'source_C_changed':True,'prefix_bytes_equal_after_verified_JSR_relocation':unchanged_prefix,
        'verified_prefix_relocations':relocations,'runtime_multiply_bytes_unchanged':True,
        'disc_built':False,'default_promoted':False,'new_training':False,'whole_game_complete':False,
        'source_sha256':{str(p):sha(p)for p in [Path(__file__),parent_path,old_make,makefile,prep_path,Path(prep['source']),ROOT/'scripts/lower_m68k_facts_to_C_v3.py',*build.glob('*.o'),binary,elf]}}
    save(out/'bundle.json',proof);save(ROOT/'verification/native-string-ccr-bundle-current.json',proof)
    print(json.dumps({k:proof[k]for k in ['status','directory','binary_bytes','reserved_bytes','prefix_bytes_equal_after_verified_JSR_relocation','verified_prefix_relocations']}))


if __name__=='__main__':main()
