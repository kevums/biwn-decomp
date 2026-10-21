"""Isolated OP kernel variant exporting exact last outer/delay operand metadata."""
import json,hashlib,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=json.loads((ROOT/'verification/OP-GPU-slice-current.json').read_text());old=Path(prior['directory'])
    out=ROOT/'verification/OP-GPU-private-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    body=(old/'biwn_gpu_OP_slice.c').read_text();body='static unsigned biwn_OP_last_metadata[3];\n'+body
    for row in prior['instructions_decoded']:
        word=int(row['bytes'][:4],16);needle='case '+hex(row['address'])+'u:';assert body.count(needle)==1
        code=' if(!delayed)biwn_OP_last_metadata[0]='+str(word)+'u;biwn_OP_last_metadata[1]='+str((word>>5)&31)+'u;biwn_OP_last_metadata[2]='+str(word&31)+'u;'
        body=body.replace(needle,needle+code)
    body+='\nvoid biwn_gpu_OP_slice_last_private(unsigned *p){p[0]=biwn_OP_last_metadata[0];p[1]=biwn_OP_last_metadata[1];p[2]=biwn_OP_last_metadata[2];}\n'
    (out/'biwn_gpu_OP_slice.c').write_text(body);(out/'biwn_gpu_OP_slice.h').write_bytes((old/'biwn_gpu_OP_slice.h').read_bytes());library=out/'libGPU-OP-private.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/'biwn_gpu_OP_slice.c'),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    report={**prior,'status':'compiled_pending_OP_private_metadata_comparison','directory':str(out),'library':str(library),'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(body.encode()).hexdigest(),'private_metadata_getter':True,'default_replaced':False}
    (ROOT/'verification/OP-private-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
