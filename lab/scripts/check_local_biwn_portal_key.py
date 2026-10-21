"""Compare unedited model-authored value helper with original doorway blocks."""
import ctypes as c
import hashlib
import json
import os
import random
import re
import subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=Path(__file__).resolve().parents[1]


def main():
    protocol=json.loads((ROOT/'verification/local-portal-key-author-current.json').read_text())
    out=Path(protocol['directory']);source=out/'biwn_local_portal_key.c';text=source.read_text()
    # Source was manually inspected; enforce the reviewed dependency surface.
    assert re.findall(r'#include\s*([<"].*?[>"])',text)==['<stdint.h>']
    assert text.count('biwn_local_portal_key(')==1
    assert not re.search(r'\b(?:asm|system|exec|fopen|printf|malloc|free)\b|__attribute__',text)
    inspection=subprocess.run(['clang','-std=c99','-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True)
    assert inspection.returncode==0,inspection.stderr
    tree=json.loads(inspection.stdout)
    assert all(node['kind']in {'TypedefDecl','RecordDecl','FunctionDecl'}for node in tree['inner'])
    functions=[node for node in tree['inner']if node['kind']=='FunctionDecl']
    assert len(functions)==1 and functions[0]['name']=='biwn_local_portal_key'
    assert functions[0]['type']['qualType'].startswith('int (')
    params=[node for node in functions[0]['inner']if node['kind']=='ParmVarDecl']
    assert [node['name']for node in params]==['direction','x','z','min_x','max_x','min_z','max_z','encoded_key','key_out']
    assert [node['type']['qualType']for node in params]==['unsigned int']+['uint16_t']*6+['uint8_t','uint16_t *']
    assert not any(node['kind']=='VarDecl'for node in tree['inner'])
    allowed={'FunctionDecl','ParmVarDecl','CompoundStmt','IfStmt','BinaryOperator',
             'ImplicitCastExpr','DeclRefExpr','IntegerLiteral','ReturnStmt','CStyleCastExpr',
             'DeclStmt','VarDecl','CompoundAssignOperator','UnaryOperator','ParenExpr',
             'ConditionalOperator','SwitchStmt','CaseStmt','DefaultStmt','BreakStmt','ConstantExpr'}
    def inspect(node):
        assert node['kind']in allowed,('Unexpected generated construct',node['kind'])
        assert node.get('castKind')not in {'IntegralToPointer','PointerToIntegral','BitCast'}
        if node['kind']in {'BinaryOperator','CompoundAssignOperator'}and node.get('opcode')in {'+','-','+=','-='}:
            assert not any('*'in child.get('type',{}).get('qualType','')for child in node.get('inner',[])), 'Pointer arithmetic excluded'
        if node['kind']=='UnaryOperator':
            assert node.get('opcode')in {'*','!','~','+','-'}
            if node.get('opcode')=='*':
                child=node['inner'][0]
                while child['kind']in {'ImplicitCastExpr','ParenExpr'}:child=child['inner'][0]
                assert child['kind']=='DeclRefExpr'and child['referencedDecl']['name']=='key_out'
        for child in node.get('inner',[]):inspect(child)
    inspect(functions[0])
    (out/'source-structure-check.json').write_text(json.dumps(dict(status='pure_helper_structure_pass',one_function=True,no_calls_or_loops=True,no_pointer_casts_or_arithmetic=True,only_output_pointer_dereferenced=True),indent=2)+'\n')
    library=out/'libportal-key.dylib';command=['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(library)]
    compilation=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(compilation.stdout+compilation.stderr);assert compilation.returncode==0,compilation.stderr
    fn=c.CDLL(str(library)).biwn_local_portal_key
    fn.argtypes=[c.c_uint]+[c.c_uint16]*6+[c.c_uint8,c.POINTER(c.c_uint16)];fn.restype=c.c_int
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    oracle=media.scheduler.Native(diagnostic_core=core);runtime=media.Runtime.__new__(media.Runtime)
    runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    entries=[0x1048c,0x1049a,0x104a8,0x104b6];rng=random.Random(0x10430)
    fixtures=[];edges=[(0,0),(0,1),(1,0),(63,0),(64,0),(0,64),(0x7fff,0),(0x8000,0),(0xffff,0),(0xffff,0xfffe),(0,0xffff),(65530,65500)]
    for direction in range(4):
        for left,right in edges:
            for encoded in [0,1,15,16,63,127,128,255]:
                values=[0x3333,0x4444,0x5555,0x6666,0x7777,0x8888]
                a,b=[(0,2),(3,0),(5,1),(1,4)][direction];values[a],values[b]=left,right
                fixtures.append((direction,values,encoded))
        fixtures.extend((direction,[rng.getrandbits(16)for _ in range(6)],rng.getrandbits(8))for _ in range(512))
    results=[]
    try:
        for direction,values,encoded in fixtures:
            x,z,min_x,max_x,min_z,max_z=values;memory=bytearray(atlas);object_address,record_address=0x70000,0x71000
            for offset,value in [(6,x),(12,z),(0x4e,min_x),(0x4a,max_x),(0x56,min_z),(0x52,max_z)]:
                memory[object_address+offset:object_address+offset+2]=value.to_bytes(2,'big')
            memory[record_address+[11,13,15,17][direction]]=encoded
            initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(16)]
            initial.registers[8],initial.registers[9]=record_address,object_address
            initial.usp,initial.ssp=0x180800,0x1e0000;initial.sr=rng.randrange(32)|(0x2000 if rng.getrandbits(1)else 0)
            initial.registers[15]=initial.ssp if initial.sr&0x2000 else initial.usp
            initial.pc=entries[direction];runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial)
            for step in range(16):
                if runtime.cpu().pc==0x104d0:break
                runtime.core.m68k_execute(1)
            native=runtime.cpu();assert native.pc==0x104d0,(direction,hex(native.pc))
            key=c.c_uint16(0xcafe);actual=fn(direction,*values,encoded,c.byref(key))
            expected_key=native.registers[0]&0xffff;expected_match=int(bool(native.sr&4))
            assert (key.value,actual)==(expected_key,expected_match),(direction,values,encoded,key.value,actual,expected_key,expected_match)
            results.append(dict(direction=direction,values=values,encoded_key=encoded,key=key.value,match=actual))
    finally:oracle.close()
    for direction in [4,5,0xffff,0xffffffff]:
        key=c.c_uint16(0xcafe);assert fn(direction,0,0,0,0,0,0,0,c.byref(key))==-1 and key.value==0xcafe
    assert fn(0,0,0,0,0,0,0,0,None)==-1
    (out/'original-value-cases.json').write_text(json.dumps(results,indent=2)+'\n')
    report=dict(status='local_portal_value_helper_original_CPU_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),guards=5,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),compiler=command,core=str(core),roles=protocol['results'],raw_JSON_only=protocol['raw_JSON_only'],model_source_edited=False,coordinator_contribution='Observed contract, mechanical fence extraction, ABI binding, synthetic fixtures and original-native-CPU comparison; helper body authored by local model.',new_training=False,same_weights_correlated=True,native_Chat_verified=False,runtime_promoted=False,scope='Four axis paths1048C..104D0: full16bit shifted key and comparison decision match originalCPU. Flags/register effects, timing, fullportal function, natural gameplay and physicalhardware excluded. C uses unsigned storage with defined integer promotions; no negative signed shift.')
    (out/'original-checks.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-portal-key-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['cases'],flush=True)


if __name__=='__main__':main()
