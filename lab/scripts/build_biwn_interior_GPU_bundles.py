"""Isolated instruction bundles for three source indoor GPU overlays."""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import generate_biwn_gpu_geometry as base

ROOT=Path(__file__).resolve().parents[1]


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    original=ROOT/'projects/black-ice-white-noise/restoration'
    out=ROOT/'verification/interior-GPU-bundle-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);programs=[]
    for tag in ['6ae0','6da0','6e80']:
        stem='biwn_gpu_interior'+tag;folder=session/('gpu-render-'+tag+'-overlay')
        mapping=json.loads((folder/'initial-linear-decode.json').read_text());rows=mapping['rows']
        payload=(folder/'original-overlay.bin').read_bytes()
        assert hashlib.sha256(payload).hexdigest()==mapping['payload_sha256']
        if tag!='6e80':
            body=(original/(stem+'.c')).read_text();header=(original/(stem+'.h')).read_text()
        else:
            rename=lambda text:text.replace('gpu_geometry','gpu_interior6e80').replace('GPU_GEOMETRY','GPU_INTERIOR6E80')
            header=rename(base.HEADER)
            # No initializer is exposed in this isolated variant.
            header=header.replace('enum biwn_gpu_interior6e80_status biwn_gpu_interior6e80_init(struct biwn_gpu_interior6e80_state *,uint32_t,const uint8_t *);','')
            prefix=rename(base.PREFIX)
            prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith(('static uint32_t sx16(', 'static uint32_t sar(', 'static void divide(', 'static int matrix(')))+'\n'
            cases=[]
            for row in rows:
                word=int(row['bytes'][:4],16);op,m,n=word>>10,(word>>5)&31,word&31
                if op==37:
                    code=f'case {hex(row["address"])}u: /* {row["assembly"]} */ s.registers[0][{n}]=s.registers[1][{m}];s.pc={hex(row["address"]+row["size"])}u;break;'
                else:code=rename(base.emit(row))
                cases.append(code)
            body=prefix+'''#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_interior6e80_status)status;}while(0)
enum biwn_gpu_interior6e80_status biwn_gpu_interior6e80_run(struct biwn_gpu_interior6e80_bus*bus,struct biwn_gpu_interior6e80_state*state,uint32_t budget){struct biwn_gpu_interior6e80_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
'''+ '\n'.join(cases)+'''
default:return BIWN_GPU_INTERIOR6E80_BAD_PC;}if(delayed){if(pending)return BIWN_GPU_INTERIOR6E80_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_GPU_INTERIOR6E80_WORK_LIMIT;}
'''
        assert body.count('while(budget--)')==1
        body=body.replace(stem+'_run(',stem+'_bundle_run(')
        body=body.replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
        end='return BIWN_GPU_INTERIOR'+tag.upper()+'_WORK_LIMIT;}'
        assert body.count(end)==1
        body=body.replace(end,'*state=s;return BIWN_GPU_INTERIOR'+tag.upper()+'_OK;}')
        # Preserve source division-control writes in the same state used
        # by the DIV primitive and expose them to the shared device model.
        needle='if(a==0xf02104u){s->matrix_control=v;return 0;}'
        assert needle in body
        body=body.replace(needle,'if(a==0xf0211cu){s->division_control=v;return bus->write32(bus->context,a,v)?2:0;}'+needle)
        (out/(stem+'.c')).write_text(body);(out/(stem+'.h')).write_text(header)
        library=out/('libinterior'+tag+'-bundle.dylib')
        cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(stem+'.c')),'-o',str(library)]
        result=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
        (out/(tag+'-compiler.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        programs.append(dict(name='interior'+tag,stem=stem,function=stem+'_bundle_run',kind='interior',library=str(library),
            instructions_decoded=rows,source_sha256=hashlib.sha256(body.encode()).hexdigest(),payload_sha256=hashlib.sha256(payload).hexdigest()))
    report=dict(status='compiled_unverified',directory=str(out),programs=programs,coordinator_authored=True,new_training=False,whole_game_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/interior-GPU-bundle-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':main()
