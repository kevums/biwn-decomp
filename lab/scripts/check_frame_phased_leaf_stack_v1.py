"""All-path SP analysis of the four actual linked leaf C phases, not helpers."""
from datetime import datetime,timezone
from pathlib import Path
import re
import subprocess
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    bp=V/'frame-acquire-phased-disc-build-v1-current.json';b=read(bp)
    elf=Path(b['directory'])/'frame-build/native.elf';symbols=b['frame_phased_symbols']
    text=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-d','--insn-width=16',str(elf)],text=True)
    instructions={}
    for line in text.splitlines():
        fields=line.split('\t')
        if len(fields)<3 or not re.fullmatch(r'\s*[0-9a-f]+:',fields[0]):continue
        address=int(fields[0].strip()[:-1],16);raw=bytes.fromhex(fields[1]);assembly=fields[2].strip();parts=assembly.split(None,1)
        if not parts:continue
        instructions[address]=(raw,parts[0],parts[1]if len(parts)>1 else'')
    names=['biwn_frame_phased_start','biwn_frame_phased_after_first_divs','biwn_frame_phased_after_group_divs','biwn_frame_phased_after_load']
    ends=[symbols[names[1]],symbols[names[2]],b['frame_phased_early_address']+b['frame_phased_early_bytes'],b['frame_phased_tail_address']+b['frame_phased_tail_bytes']]
    results=[]
    for name,end in zip(names,ends):
        start=symbols[name];seen={};pending=[(start,0)];maximum=0;returns=[]
        while pending:
            pc,depth=pending.pop()
            if pc in seen:
                assert seen[pc]==depth,('Inconsistent SP at control-flow join',name,hex(pc),seen[pc],depth)
                continue
            assert start<=pc<end,(name,hex(pc));seen[pc]=depth;raw,mn,operand=instructions[pc];change=0
            assert mn not in ['jsr','bsr','bsrs','bsrw','bsrl','jmp','linkw','linkl','unlk'],(name,hex(pc),mn)
            if mn in ['subql','addql'] and operand.endswith(',%sp'):
                value=int(operand.split(',')[0][1:]);change=value if mn=='subql'else-value
            elif mn=='moveml' and ('%sp@-'in operand or'%sp@+'in operand):
                count=int.from_bytes(raw[2:4],'big').bit_count();change=count*4*(1 if'%sp@-'in operand else-1)
            elif mn in ['movel','movew'] and ('%sp@-'in operand or'%sp@+'in operand):
                change=(4 if mn=='movel'else 2)*(1 if'%sp@-'in operand else-1)
            elif operand.endswith(',%sp'):
                raise AssertionError(('Unsupported SP write',name,hex(pc),mn,operand))
            after=depth+change;assert after>=0,(name,hex(pc),after);maximum=max(maximum,depth,after)
            if mn=='rts':assert depth==0,(name,'Unbalanced return',depth);returns.append(pc);continue
            next_pc=pc+len(raw)
            branch=re.fullmatch(r'b(ra|eq|ne|ge|lt|gt|le|hi|ls|cc|cs|pl|mi|vc|vs)[swl]?',mn)
            if branch:
                target=int(operand.split()[0],16);pending.append((target,after))
                if branch.group(1)!='ra':pending.append((next_pc,after))
            elif mn.startswith('db'):
                target=int(operand.split(',')[-1].split()[0],16);pending.extend([(target,after),(next_pc,after)])
            else:pending.append((next_pc,after))
        assert returns and len(seen)==sum(start<=pc<end for pc in instructions),(name,'Unreachable/unanalysed instructions')
        results.append(dict(name=name,start=start,end=end,instructions=len(seen),maximum_leaf_stack_bytes=maximum,returns=returns,all_control_flow_joins_SP_consistent=True,no_calls_or_dynamic_stack_allocation=True))
    assert [r['maximum_leaf_stack_bytes']for r in results]==[36,36,4,28]
    out=V/'frame-phased-leaf-stack-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/'disassembly.txt').write_text(text);save(out/'phases.json',results)
    proof=dict(status='terminal_actual_linked_leaf_C_phase_all_path_stack_bound184_bytes_excluding_helpers_IRQ',directory=str(out),phases=results,original_public_frame_bytes=44,transient_context_bytes=96,C_argument_and_JSR_bytes=8,maximum_leaf_stack_bytes=36,maximum_wrapper_C_phase_depth=184,DIVS_or_loader_stack_not_included=True,global_caller_helper_IRQ_bound_proven=False,all_possible_terminating_or_looping_C_phase_paths_SP_bounded=True,new_predictions=0,new_training=False,scope='CFG analysis visits every linked C instruction, requires one consistent SP depth per join/loop, no calls/dynamic SP writes, and balanced returns. This bounds only the four leaf C phases plus fixed44+96+8wrapper accounting. Loader/actual scheduler/nested calls/interrupts and all callers remain separate. It does not establish a whole-game stack bound or original-source timing.',source_sha256={str(p):sha(p)for p in [Path(__file__),bp,elf,out/'disassembly.txt',out/'phases.json']})
    save(out/'review.json',proof);save(V/'frame-phased-leaf-stack-v1-current.json',proof);print(proof['status'],flush=True)


if __name__=='__main__':main()
