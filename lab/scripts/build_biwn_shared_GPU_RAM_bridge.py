"""Isolated GPU bridge experiment with live local-RAM pointers.

Retain the same source kernels, bus callbacks, state save/load and byte fences.
Clone headers/sources rather than changing any accepted kernel or default.
"""
import argparse, ctypes as c, hashlib, json, os, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_movie_GPU as GPU
from biwn_renderer_bundle import State, GeometryState
from biwn_material_bundle import PartialState

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-candidate',type=Path);parser.add_argument('--candidate-output',type=Path);args=parser.parse_args()
    assert not args.base_candidate or args.candidate_output
    old=json.loads((args.base_candidate or ROOT/'verification/fast-GPU-bridge-candidate.json').read_text())
    out=ROOT/'verification/shared-GPU-RAM-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    src=out/'kernel-source';src.mkdir(parents=True)
    kernels=[];headers={};provenance={}
    for p in old['programs']:
        parent=Path(p['library']).parent
        for header in parent.glob('*.h'):
            text=header.read_text()
            if header.name in headers:
                assert headers[header.name]==text, ('Conflicting kernel header',header.name)
            headers[header.name]=text
        original=parent/(p['stem']+'.c')
        text=original.read_text()
        provenance[str(original)]=hashlib.sha256(text.encode()).hexdigest()
        if p['name']=='geometry':
            needle='if(!s)return 1;memset(s,0,sizeof(*s));'
            assert needle in text
            text=text.replace(needle,'if(!s||!s->local_RAM)return 1;{uint8_t*p=s->local_RAM;memset(s,0,sizeof(*s));s->local_RAM=p;}')
        target=src/original.name;target.write_text(text);kernels.append(target)
    for name,text in headers.items():
        text=re.sub(r'uint8_t\s+local_RAM\s*\[\s*4096\s*\]', 'uint8_t *local_RAM',text)
        (src/name).write_text(text)
    for p in old['programs']:
        if 'local_RAM' in headers[p['stem']+'.h']:
            assert 'uint8_t *local_RAM' in (src/(p['stem']+'.h')).read_text()
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    kernel_lib=out/'libshared-GPU-kernels.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(x)for x in kernels],'-o',str(kernel_lib)]
    result=subprocess.run(command,capture_output=True,text=True,env=env)
    (out/'kernel-compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    source=(Path(old['directory'])/'fast_GPU_bridge.c').read_text()
    for p in old['programs']:
        old_header=Path(p['library']).parent/(p['stem']+'.h')
        source=source.replace(str(old_header),str(src/old_header.name))
    assert 'uint8_t local_RAM[4096];' in source
    source=source.replace('uint8_t local_RAM[4096];','uint8_t *local_RAM;')
    source=source.replace('memcpy(s->local_RAM,p,4096);','s->local_RAM=H.RAM();')
    source=source.replace('memcpy(t.local_RAM,s->local_RAM,sizeof(t.local_RAM));','t.local_RAM=s->local_RAM;')
    source=source.replace('memcpy(s->local_RAM,t.local_RAM,sizeof(t.local_RAM));','s->local_RAM=t.local_RAM;')
    source=source.replace('memcpy(H.RAM(),p,4096);H.write32(a,v,6);memcpy(p,H.RAM(),4096);',
        'if(p!=H.RAM())memcpy(H.RAM(),p,4096);H.write32(a,v,6);if(p!=H.RAM())memcpy(p,H.RAM(),4096);')
    assert 'memcpy(t.local_RAM' not in source and 'memcpy(s->local_RAM' not in source
    source+='\nsize_t biwn_shared_GPU_kernel_size(unsigned k){switch(k){'
    for i,p in enumerate(old['programs']):source+=f'case {i}:return sizeof(struct {p["stem"]}_state);'
    source+='default:return 0;}}\n'
    path=out/'shared_GPU_bridge.c';path.write_text(source)
    library=out/'libshared-GPU-bridge.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(path),str(kernel_lib),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env=env)
    (out/'bridge-compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    loaded=c.CDLL(str(library));loaded.biwn_shared_GPU_kernel_size.argtypes=[c.c_uint];loaded.biwn_shared_GPU_kernel_size.restype=c.c_size_t
    sizes=[]
    for i,p in enumerate(old['programs']):
        typ=GeometryState if p['name']=='geometry'or p['kind']=='interior'else PartialState if p['kind']in ['material','consumer','setup']and p['name']not in ['sprite']else GPU.State if p['name']in ['OP','movement','sprite']or p['kind']in ['movie','movie_exit','firstboot']else State
        shared=type('Shared_'+str(i),(c.Structure,),{'_fields_':[(name,c.c_void_p if name=='local_RAM'else field)for name,field in typ._fields_]})
        size=loaded.biwn_shared_GPU_kernel_size(i)
        assert size==c.sizeof(shared),(p['name'],size,c.sizeof(shared))
        sizes.append(dict(name=p['name'],C_size=size,expected_size=c.sizeof(shared)))
    report=dict(status='compiled_unverified',directory=str(out),library=str(library),
        kernel_library=str(kernel_lib),source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        original_bridge=old['library'],source_provenance=provenance,ABI_sizes=sizes,
        shared_local_RAM=True,capture_unknown=old.get('capture_unknown',False),accepted_defaults_changed=False,new_training=False,whole_game_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (args.candidate_output or ROOT/'verification/shared-GPU-RAM-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':main()
