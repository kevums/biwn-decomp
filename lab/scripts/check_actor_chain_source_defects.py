"""Reject real C-chain virtual-stack/geometry-anchor defects after compilation."""
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_actor_chain as f

ROOT=f.ROOT
ND=f.ND


def main():
    gate=f.direct.g.read(ROOT/'verification/native-actor-chain-final-current.json')
    rows=f.direct.g.read(Path(gate['directory'])/'results.json')
    witness=max((row for row in rows if row['group']=='movement'),key=lambda row:row['candidate_depth'])
    case=f.chain.vectors()[witness['index']]
    out=ROOT/'verification/actor-chain-source-defects'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source_move=(ND/'actor-chain-move.c').read_text();source_collision=(ND/'actor-chain-collision.c').read_text()
    variants=[('wrong_virtual_JSR_width',source_move.replace('s->r[15]-=4;','s->r[15]-=2;'),source_collision),('standalone_geometry_anchor_used_inside_movement',source_move,source_collision.replace('s->r[19]==0x13c9au','0'))]
    controls=[];native=f.chain.Native()
    try:
        snapshot,payload,symbols,build=f.prepare(gate)
        a=f.chain.execute(snapshot,case,payload,symbols,False);b=f.chain.execute(snapshot,case,payload,symbols,True)
        assert all(a[k]==b[k]for k in ['ram','registers','trace'])
        assert f.chain.replay(native,snapshot,case,payload,symbols,False,a)==f.chain.replay(native,snapshot,case,payload,symbols,True,b)
        for name,move,collision in variants:
            assert move!=source_move or collision!=source_collision
            variant=out/name;variant.mkdir();mp=variant/'move.c';cp=variant/'collision.c';mp.write_text(move);cp.write_text(collision)
            p=subprocess.run(['make','-f',str(ND/'Makefile.actor-chain-compact'),'actor-chain','BUILD='+str(variant/'build'),'ADDRESS='+hex(gate['code_address']),'MOVE_SOURCE='+str(mp),'COLLISION_SOURCE='+str(cp)],capture_output=True,text=True)
            (variant/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
            binary=variant/'build/actor-chain.bin';elf=variant/'build/actor-chain.elf';nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True)
            names={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
            bad=dict(binary=str(binary),symbols=names,code_address=gate['code_address'])
            snapshot,payload,symbols,build=f.prepare(bad)
            rejection=None
            try:
                result=f.chain.execute(snapshot,case,payload,symbols,True)
            except Exception as error:
                rejection=dict(kind='guest_execution_rejected',exception=type(error).__name__,error=str(error),repr=repr(error))
            else:
                fields=[key for key in ['ram','registers','trace']if a[key]!=result[key]]
                if fields:rejection=dict(kind='original_result_or_ordered_trace_mismatch',fields=fields,original_regs=a['registers'],defective_regs=result['registers'])
                else:
                    an=f.chain.replay(native,snapshot,case,payload,symbols,False,a)
                    bn=f.chain.replay(native,snapshot,case,payload,symbols,True,result)
                    differences=[key for key in an if an[key]!=bn[key]]
                    if differences:rejection=dict(kind='native_CPU_or_ABI_mismatch',fields=differences,original=an,defective=bn)
            assert rejection,name+' was not rejected'
            row=dict(defect=name,rejected=True,fixture_index=witness['index'],rejection=rejection,binary=str(binary),binary_sha256=f.direct.g.sha(binary))
            f.direct.g.save(variant/'witness.json',dict(case=case,**row));controls.append(row)
            print(name,rejection['kind'],flush=True)
    finally:native.close()
    f.direct.g.save(out/'controls.json',controls)
    inputs=[Path(__file__),out/'controls.json',*out.rglob('*.c'),*out.rglob('*.bin'),*out.rglob('*.elf'),*out.rglob('witness.json')]
    state=dict(status='terminal_actor_chain_compiled_source_defects_rejected',directory=str(out),positive_native_original_comparison_pass=True,controls=controls,new_predictions=0,source_sha256={str(p):f.direct.g.sha(p)for p in inputs},scope=__doc__)
    f.direct.g.save(out/'protocol.json',state);f.direct.g.save(ROOT/'verification/actor-chain-source-defects-current.json',state)
    print(state['status'],len(controls))


if __name__=='__main__':main()
