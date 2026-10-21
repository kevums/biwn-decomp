"""Isolated helper compiler/ABI experiments. Existing source/defaults untouched."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
    bp=ROOT/'verification/native-format-bundle-current.json';base=json.loads(bp.read_text());assert sha(base['binary'])==base['binary_sha256']
    source_makefile=Path(base['directory'])/'Makefile';text=source_makefile.read_text();native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    assert text.count('$(CROSS)gcc $(CFLAGS) -I. -Wall -Wextra -Werror -c $< -o $@')==2
    out=ROOT/'verification/native-format-optimization-builds'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[]
    for kind,optimization,lean in [('O2','O2',False),('O3','O3',False),('O2-lean','O2',True)]:
        directory=out/kind;directory.mkdir();makefile=directory/'Makefile'
        candidate=text.replace('$(CROSS)gcc $(CFLAGS) -I. -Wall -Wextra -Werror -c $< -o $@','$(CROSS)gcc $(filter-out -Os -O2 -O3,$(CFLAGS)) -'+optimization+' -I. -Wall -Wextra -Werror -c $< -o $@')
        inputs=[bp,source_makefile,Path(base['pad_source']),Path(base['string_source'])]
        if lean:
            # C compiler ABI preserves the registers not mentioned below.
            # r0/r1/r2/r8/r9/r10/r15/r16 retain their original semantic offsets.
            # Full original CPU/public-save tests must validate this hypothesis.
            for name,areg in [('pad','a1'),('string','a2')]:
                source=native/f'format-{name}-shim.S';asm=source.read_text()
                assert asm.count('movem.l %d0-%d7/%a0-%a6,(%sp)')==1 and asm.count('movem.l (%sp),%d0-%d7/%a0-%a6')==1
                asm=asm.replace('movem.l %d0-%d7/%a0-%a6,(%sp)',f'movem.l %d0-%d2,(%sp)\nmovem.l %a0-%{areg},32(%sp)')
                asm=asm.replace('movem.l (%sp),%d0-%d7/%a0-%a6',f'movem.l (%sp),%d0-%d2\nmovem.l 32(%sp),%a0-%{areg}')
                path=directory/f'format-{name}-lean-shim.S';path.write_text('/* Experimental compiler-ABI-aware shim; coordinator-authored, not model output. */\n'+asm)
                marker=f'$(BUILD)/format-{name}-shim.o: format-{name}-shim.S';assert candidate.count(marker)==1
                candidate=candidate.replace(marker,f'$(BUILD)/format-{name}-shim.o: {path}')
                inputs+=[source,path]
        makefile.write_text(candidate);build=directory/'build';command=['make','-f',str(makefile),'format-bundle','BUILD='+str(build)]
        p=subprocess.run(command,cwd=native,capture_output=True,text=True);(directory/'make.log').write_text(p.stdout+p.stderr)
        row=dict(kind=kind,status='build_failed'if p.returncode else'linked_pending_semantic_and_cost_checks',command=command,exit_code=p.returncode,directory=str(directory),optimization=optimization,lean_abi_shim=lean,default_promoted=False,disc_built=False)
        if p.returncode==0:
            binary=build/'native-format-bundle.bin';elf=binary.with_suffix('.elf');payload=binary.read_bytes();assert len(payload)<=base['reserved_bytes']
            symbols={}
            for line in subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'--defined-only',str(elf)],text=True).splitlines():
                fields=line.split()
                if len(fields)==3:symbols[fields[2]]=int(fields[0],16)
            assert symbols['biwn_native_heap_start']==base['heap_start']
            proof={**base,'status':'experimental_optimization_linked_pending_full_checks','directory':str(directory),'binary':str(binary),'binary_sha256':sha(binary),'ELF':str(elf),'symbols':symbols,
                   'binary_bytes':len(payload),'padding_bytes':base['reserved_bytes']-len(payload),'parent_bundle_proof':str(bp),'parent_bundle_sha256':sha(bp),'optimization':optimization,'lean_abi_shim':lean,
                   'source_sha256':{str(p):sha(p)for p in [Path(__file__),makefile,*inputs,*build.glob('*.o'),binary,elf]},'disc_built':False,'default_promoted':False}
            proof_path=directory/'bundle.json';save(proof_path,proof);row.update(bundle_proof=str(proof_path),binary_sha256=sha(binary),binary_bytes=len(payload))
        save(directory/'build-status.json',row);rows.append(row);print(kind,row['status'],row.get('binary_bytes'),flush=True)
    report=dict(status='terminal_three_isolated_helper_optimization_build_attempts',directory=str(out),base_bundle=str(bp),base_bundle_sha256=sha(bp),candidates=rows,source_C_changed=False,new_training=False,LLM_calls=0,whole_game_complete=False)
    save(out/'builds.json',report);save(ROOT/'verification/native-format-optimization-builds-current.json',report)
if __name__=='__main__':main()
