"""Bound the three fixed actor leaf C phases; helpers and exceptions excluded."""
from datetime import datetime,timezone
from pathlib import Path
import re,subprocess
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def analyze(elf,names,ends,symbols):
    text=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-d','--insn-width=16',str(elf)],text=True)
    instructions={}
    for line in text.splitlines():
        fields=line.split('\t')
        if len(fields)<3 or not re.fullmatch(r'\s*[0-9a-f]+:',fields[0]):continue
        address=int(fields[0].strip()[:-1],16);raw=bytes.fromhex(fields[1]);assembly=fields[2].strip();parts=assembly.split(None,1)
        if not parts:continue
        instructions[address]=(raw,parts[0],parts[1]if len(parts)>1 else'')
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
            if mn=='illegal':continue
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
    return results,text


def main():
    bp=V/'actor-phased-disc-build-v1-current.json';b=read(bp)
    out=V/'actor-phased-leaf-stack-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    results=[];paths=[Path(__file__),bp];bounds={}
    for module,names,public in [('dispatch',['biwn_actor_dispatch_phase'],16),('initialize',['biwn_actor_initialize_start','biwn_actor_initialize_after_placement'],32)]:
        a=b['actor_phased_artifacts'][module];elf=Path(a['ELF']);symbols=a['symbols']
        sections=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-h',str(elf)],text=True)
        row=next(line.split() for line in sections.splitlines() if len(line.split())>2 and line.split()[1]=='.body')
        end=int(row[3],16)+int(row[2],16)
        ends=[symbols[n] for n in names[1:]]+[end]
        rows,text=analyze(elf,names,ends,symbols)
        for r in rows:r['wrapper_C_phase_depth']=public+96+8+r['maximum_leaf_stack_bytes']
        maximum=max(r['wrapper_C_phase_depth']for r in rows);bounds[module]=maximum
        assert maximum == (128 if module == 'dispatch' else 156), (module, maximum)
        results+=rows
        dis=out/(module+'-disassembly.txt');dis.write_text(text);paths += [elf,dis]
    save(out/'phases.json',results);paths.append(out/'phases.json')
    proof=dict(status='terminal_fixed_actor_leaf_C_phase_static_bounds128_and156_excluding_helpers_IRQ',directory=str(out),
        phases=results,maximum_wrapper_C_phase_depth=bounds,C_frames_parked_across_helpers=0,
        all_global_stack_paths_proven=False,helpers_and_exception_handlers_included=False,
        illegal_instruction_trap_is_terminal_for_this_analysis=True,new_predictions=0,new_training=False,
        source_sha256={str(p):sha(p)for p in paths},
        scope='Every linked C-phase instruction is visited by CFG/SP analysis. Joins and loops require consistent SP; normal RTS is balanced. No calls or dynamic SP writes. Illegal-instruction default terminates this analysis; its exception handling, helper/caller stacks, arbitrary IRQ and complete-game bounds are excluded.')
    save(out/'review.json',proof);save(V/'actor-phased-leaf-stack-v1-current.json',proof);print(proof['status'],flush=True)


if __name__=='__main__':main()
