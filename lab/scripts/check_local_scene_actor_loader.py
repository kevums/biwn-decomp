"""Check local-authored complete actor loader against original M68000 code."""
import ctypes as c
import hashlib
import json
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scene_loading as original
ROOT=Path(__file__).resolve().parents[1]

def main():
    author=json.loads((ROOT/'verification/local-scene-actor-author-current.json').read_text())
    out=Path(author['directory']);source=out/'biwn_local_scene_actor_loader.c'
    restoration=ROOT/'projects/black-ice-white-noise/restoration'
    command=['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)]
    inspection=subprocess.run(command,capture_output=True,text=True)
    (out/'syntax.log').write_text(inspection.stderr)
    assert inspection.returncode==0,inspection.stderr
    tree=json.loads(inspection.stdout)
    functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(c['kind']=='CompoundStmt'for c in n.get('inner',[]))]
    assert sum(f['name']=='biwn_scene_loading'for f in functions)==1
    assert all(f['name']=='biwn_scene_loading'or f.get('storageClass')=='static'for f in functions)
    assert not any(n['kind']in {'VarDecl','FileScopeAsmDecl'}for n in tree['inner'])
    names={f['name']for f in functions}
    def visit(n):
        assert n['kind']not in {'GCCAsmStmt','MSAsmStmt'}
        assert n.get('castKind')not in {'IntegralToPointer','PointerToIntegral'}
        if n.get('castKind')=='BitCast':
            # stddef NULL is ((void *)0), implicitly converted for comparison.
            null=n['inner'][0]
            while null['kind']=='ParenExpr':null=null['inner'][0]
            assert null.get('castKind')=='NullToPointer'
        if n['kind']=='CallExpr':
            target=n['inner'][0]
            while target['kind']in {'ImplicitCastExpr','ParenExpr'}:target=target['inner'][0]
            assert (target['kind']=='MemberExpr'and target['name']in {'read16','read32','write16','write32','call'})or (target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
        for child in n.get('inner',[]):visit(child)
    for fn in functions:visit(fn)
    library=out/'liblocal-scene-actors.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    fn=original.bind(c.CDLL(str(library)))
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    cases=[v for v in original.cases()if v['entry']==0x20aa0]
    coverage=set();rows=[];guards=[]
    for ordinal,case in enumerate(cases):
        a=original.Script(snapshot,case);b=original.Script(snapshot,case)
        value,steps=original.original(a,case,coverage);status,actual=original.translated(fn,b,case)
        if status or value!=actual or a.trace!=b.trace or a.memory!=b.memory:
            original.save(out/'mismatch.json',dict(case=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=b.errors))
            raise AssertionError(out/'mismatch.json')
        rows.append(dict(case=ordinal,parameters=case,full_D0=value,original_steps=steps,trace=b.trace))
    base=cases[0]
    for missing in [1,2,3,4,5]:
        s=original.Script(snapshot,base);status,value=original.translated(fn,s,base,missing=missing)
        assert status==1 and value==0xa55aa55a and not s.trace
        guards.append(dict(missing=missing,status=status))
    for kwargs in [dict(null_bus=True),dict(null_out=True)]:
        s=original.Script(snapshot,base);status,value=original.translated(fn,s,base,**kwargs)
        assert status==1 and value==0xa55aa55a and not s.trace;guards.append(kwargs)
    bad={**base,'entry':0x20b2a};s=original.Script(snapshot,bad)
    status,value=original.translated(fn,s,bad);assert status==1 and value==0xa55aa55a and not s.trace
    for row in rows:
        if any(event[0]=='call'for event in row['trace']):
            s=original.Script(snapshot,row['parameters']);s.fail_call=0x13ae0
            status,value=original.translated(fn,s,row['parameters'])
            assert status==3 and value==0xa55aa55a;guards.append(dict(dependency_failure=True,prior_effects_retained=True));break
    for case in cases:
        s=original.Script(snapshot,case);status,value=original.translated(fn,s,case,budget=0)
        if status==4:
            assert value==0xa55aa55a;guards.append(dict(work_limit=True));break
    original.save(out/'fixtures.json',rows)
    report=dict(status='local_complete_scene_actor_loader_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),original_addresses_exercised=len(coverage),host_guards=guards,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_body_edited=False,role_seconds=sum(r['seconds']for r in author['drafts']),full_prompts_and_responses=str(out/'prompts-and-responses.txt'),same_weights_correlated=True,new_training=False,full_route_runtime_promoted=False,native_Chat_verified=False,scope='Complete20AA0 body versus original M68000 on256 finite RAM fixtures: fullD0, ordered bus accesses/helper args and complete externalRAM match. Nested13AE0 is an explicit helper script; private stack/CCR/other registers and full-game integration excluded.')
    original.save(out/'report.json',report);original.save(ROOT/'verification/local-scene-actor-loader-checks-current.json',report)
    print(json.dumps({k:v for k,v in report.items()if not isinstance(v,(dict,list))}))

if __name__=='__main__':main()
