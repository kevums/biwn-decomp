"""Keep serialized active USP/SSP coherent after every accepted C instruction.

No instruction/register/RAM/cycle semantics are replaced. This normalizes
the active stack-bank field to A7; the inactive bank remains untouched.
"""
import json,subprocess,shutil,os
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def main():
    pp=ROOT/'verification/doorway-C-runtime-build-current.json';prior=json.loads(pp.read_text())
    assert prior['status']=='terminal_doorway_C_compiled_pending_checks'
    cp=Path(prior['CPU_candidate']);candidate=json.loads(cp.read_text())
    out=ROOT/'verification/doorway-C-bank-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    source=out/'bank-coherent-CPU.c'
    old_fn=candidate['function'];new_fn='biwn_doorway_bank_coherent_step'
    source.write_text('#include "biwn_input_dispatch_cpu.h"\n'
        'extern int '+old_fn+'(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);\n'
        'int '+new_fn+'(struct biwn_world_bus*b,struct biwn_task_cpu*s,biwn_input_write8 w,biwn_world_cpu_service service,void*context){\n'
        'int status='+old_fn+'(b,s,w,service,context);\n'
        'if(s&&(status==0||status==6||status==10||status==11)){if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];}\n'
        'return status;}\n')
    library=out/'libgeometry-bank-coherent-CPU.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(source),candidate['library'],'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    new=dict(candidate,library=str(library),function=new_fn,directory=str(out),unwrapped_CPU_library=candidate['library'],
             generated_instruction_source_sha256=candidate['source_sha256'],source_sha256=sha(source),
             active_bank_normalization='After accepted status0/6/10/11 only, active USP/SSP equals A7;inactive bank andallotherstate untouched.')
    newp=out/'CPU-bank-coherent-candidate.json';save(newp,new)
    listing=Path(prior['directory'])/'new-instructions.json';shutil.copy2(listing,out/listing.name)
    proof=dict(status='terminal_doorway_bank_C_compiled_pending_checks',directory=str(out),CPU_candidate=str(newp),
               parent_build=str(pp),parent_build_sha256=sha(pp),build_proof=prior['build_proof'],build_proof_sha256=prior['build_proof_sha256'],
               static_instruction_starts=prior['static_instruction_starts'],new_training=False,default_promoted=False,whole_game_complete=False,
               source_sha256={str(p):sha(p) for p in [out/'runner-as-run.py',pp,cp,Path(candidate['library']),source,library,newp,listing,out/listing.name]})
    save(out/'protocol.json',proof);save(ROOT/'verification/doorway-C-bank-build-current.json',proof)
    print(proof['status'],flush=True)


if __name__=='__main__':main()
