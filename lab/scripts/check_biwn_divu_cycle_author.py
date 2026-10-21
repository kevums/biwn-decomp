"""Compare local model arithmetic code with pinned C timing helpers."""
import ast,ctypes as c,hashlib,json,re,random,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def extract_function(text,name):
    start=text.index(name);start=text.rfind('\n',0,start)+1;brace=text.index('{',start);depth=1;i=brace+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('protocol',type=Path);args=parser.parse_args();protocol=json.loads(args.protocol.read_text());out=args.protocol.parent/'cycle-code-gate';out.mkdir(exist_ok=True)
    meta=json.loads(Path(json.loads((ROOT/'verification/CPU-cycle-metadata-current.json').read_text())['metadata']).read_text());source=Path(meta['source_directory'])/'cpuextra.c';text=source.read_text()
    code='/* Cost helpers copied from GPLv3-or-later pinned UAE/Virtual Jaguar cpuextra.c; no CPU instruction bodies. */\n#include <stdint.h>\n#include <stdlib.h>\n#define INLINE inline\n'+ '\n'.join(extract_function(text,n)for n in ['getDivu68kCycles_2','getDivu68kCycles(','getDivs68kCycles_2','getDivs68kCycles('])
    ref=out/'reference.c';ref.write_text(code);lib=out/'libcycles.dylib';command=['clang','-std=c99','-O2','-dynamiclib',str(ref),'-o',str(lib)]
    result=subprocess.run(command,text=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(result.stdout+result.stderr);assert not result.returncode,result.stderr
    dll=c.CDLL(str(lib));fn=dll.getDivu68kCycles;fn.argtypes=[c.c_uint32,c.c_uint16];fn.restype=c.c_int
    answer=protocol['results'][0]['answer'];blocks=re.findall(r'```(?:python)?\s*\n(.*?)```',answer,re.S);assert len(blocks)==1
    candidate=blocks[0];(out/'candidate.py').write_text(candidate);tree=ast.parse(candidate)
    assert len(tree.body)==1 and isinstance(tree.body[0],ast.FunctionDef)and tree.body[0].name=='divu_cycles'
    assert not any(isinstance(n,(ast.Import,ast.ImportFrom,ast.Attribute,ast.Global,ast.Nonlocal,ast.Lambda,ast.With,ast.ClassDef))for n in ast.walk(tree))
    assert all(isinstance(n.func,ast.Name)and n.func.id in ['range','int','abs']for n in ast.walk(tree)if isinstance(n,ast.Call))
    namespace={'__builtins__':{'range':range,'int':int,'abs':abs}};exec(compile(tree,str(out/'candidate.py'),'exec'),namespace);local=namespace['divu_cycles']
    dividends=[0,1,0x7fff,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff];divisors=[0,1,2,3,0x7fff,0x8000,0xffff]
    rng=random.Random(0x4249574e);cases=[(a,b)for a in dividends for b in divisors]+[(rng.getrandbits(32),rng.getrandbits(16))for _ in range(100000)]
    failures=[]
    for a,b in cases:
        expected,actual=fn(a,b),local(a,b)
        if actual!=expected:failures.append(dict(dividend=a,divisor=b,expected=expected,actual=actual))
    report=dict(status='pass'if not failures else'rejected_local_code',cases=len(cases),failure_count=len(failures),failures=failures[:20],protocol=str(args.protocol),compiler=command,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
        original_CPU_opcode_execution=False,scope='Arithmetic timing helper equivalence only. Cost-model instruction integration and global timing remain separate gates.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));print(out)

if __name__=='__main__':main()
