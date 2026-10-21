"""Decode cycle metadata from the pinned core; never execute CPU opcodes."""
import json,re,subprocess,hashlib,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]

def main():
    core=Path(json.loads((ROOT/'verification/BIWN-GPU-IRQ-forward-candidate.json').read_text())['core_path']).parent
    source=core/'src/m68000'
    out=ROOT/'verification/CPU-cycle-metadata'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    helper=out/'decode.c';helper.write_text('''#include <stdio.h>
#include "readcpu.h"
int main(void){unsigned op;read_table68k();do_merges();for(op=0;op<65536;op++){
struct instr *i=&table68k[op];printf("%u,%ld,%u,%u,%u,%u,%u,%u,%u\\n",op,i->handler,i->mnemo,i->cc,i->size,i->smode,i->sreg,i->dmode,i->dreg);
}free_table68k();return 0;}\n''')
    command=['clang','-std=c99','-O2','-DINLINE=inline','-I',str(source),str(helper),str(source/'readcpu.c'),str(source/'cpudefs.c'),'-o',str(out/'decode')]
    compiled=subprocess.run(command,text=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiled.stdout+compiled.stderr);assert not compiled.returncode,compiled.stderr
    data=subprocess.check_output([str(out/'decode')],text=True);(out/'opcode-metadata.csv').write_text(data)
    opmap=[]
    for line in data.splitlines():
        op,handler,mnemo,cc,size,smode,sreg,dmode,dreg=map(int,line.split(','));assert op==len(opmap)
        opmap.append(dict(handler=op if handler==-1 else handler,mnemo=mnemo,condition=cc,size=size,smode=smode,sreg=sreg,dmode=dmode,dreg=dreg))
    text=(source/'cpuemu.c').read_text();functions={}
    matches=list(re.finditer(r'unsigned long CPUFUNC\(op_([0-9a-f]+)_5\)\(uint32_t opcode\) /\* (.*?) \*/',text))
    for match in matches:
        end=text.find('\nunsigned long CPUFUNC(',match.end());body=text[match.end():end if end>=0 else len(text)]
        returns=re.findall(r'\breturn\s+([^;]+);',body);constant=returns and all(re.fullmatch(r'\d+',v.strip())for v in returns)and len(set(v.strip()for v in returns))==1
        functions[str(int(match.group(1),16))]=dict(name=match.group(2),returns=returns,constant_cycles=int(returns[0])if constant else None,body=body)
    small=(source/'cpustbl.c').read_text();part=small[small.index('op_smalltbl_5'):];supported={int(op)for op in re.findall(r'CPUFUNC\(op_[0-9a-f]+_5\),\s*\d+,\s*(\d+)',part)}
    metadata=dict(opcodes=opmap,handlers=functions,compatible_handler_table='op_smalltbl_5_ff',supported_handlers=sorted(supported),source_directory=str(source),compiler=command,
        source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['readcpu.c','readcpu.h','cpudefs.c','cpuemu.c','cpustbl.c','m68kinterface.c']},
        original_CPU_execution=False,scope='Cycle-cost metadata from pinned emulator, not physical bus or globally scheduled game proof.')
    (out/'metadata.json').write_text(json.dumps(metadata)+'\n');pointer=dict(directory=str(out),metadata=str(out/'metadata.json'),handler_count=len(functions),constant_handler_count=sum(v['constant_cycles']is not None for v in functions.values()),original_CPU_execution=False)
    (ROOT/'verification/CPU-cycle-metadata-current.json').write_text(json.dumps(pointer,indent=2)+'\n');print(pointer)

if __name__=='__main__':main()
