"""Compare cost-only predictions with original execution; not timing adoption."""
import ctypes as c
import json,hashlib,collections
from pathlib import Path
from biwn_m68k_cycle_cost import Cost

def install(runtime):
    assert runtime.mode=='native'
    def read(a,w):
        assert 0<=a<=0x200000-w,('cycle metadata memory range',hex(a))
        return int.from_bytes(c.string_at(runtime.device.pointer+a,w),'big')
    model=Cost(read);execute=runtime.core.m68k_execute
    irq=runtime.core.m68k_set_irq2;pending_entry=0;IRQ_entries=[]
    def assert_irq(level):
        nonlocal pending_entry
        before=runtime.cpu();result=irq(level);after=runtime.cpu()
        if before.pc!=after.pc and after.ssp==before.ssp-6:
            # Pinned m68kinterface.c explicitly defers56cycles at entry.
            pending_entry+=56;IRQ_entries.append(dict(level=level,from_PC=hex(before.pc),handler=hex(after.pc),cycles=56))
        return result
    runtime.core.m68k_set_irq2=assert_irq
    counts=collections.Counter();total=0;expected_total=0;unsupported=collections.Counter();mismatches=collections.Counter();examples={};trace=hashlib.sha256();pcs=set()
    def wrapped(budget):
        nonlocal total,expected_total,pending_entry
        assert budget==1,'cycle probe requires instruction boundary'
        state=runtime.cpu();opcode=read(state.pc,2);pcs.add(state.pc)
        try:predicted,name=model.predict(opcode,state);problem=None
        except (ValueError,AssertionError,ImportError)as error:predicted=None;name=model.models[opcode][1]['name']if model.models[opcode][1]else'unsupported';problem=str(error)
        entry=pending_entry;pending_entry=0
        actual=execute(budget);assert actual>0
        if predicted is not None:predicted+=entry
        total+=actual;counts[name]+=1
        trace.update(state.pc.to_bytes(4,'big')+opcode.to_bytes(2,'big')+actual.to_bytes(4,'big'))
        if predicted is None:unsupported[name]+=1
        else:
            expected_total+=predicted
            if actual!=predicted:mismatches[(hex(state.pc),hex(opcode),name,predicted,actual)]+=1
        if (problem or(actual!=predicted))and name not in examples:examples[name]=dict(PC=hex(state.pc),opcode=hex(opcode),actual=actual,predicted=predicted,problem=problem,CPU=__import__('check_biwn_media_setup_cpu').scheduler.cpu_dict(state))
        return actual
    runtime.core.m68k_execute=wrapped
    def report():
        return dict(status='cost_model_comparison_not_global_timing',instructions=sum(counts.values()),unique_PC_count=len(pcs),actual_cycles=total,predicted_supported_cycles=expected_total,
            unsupported=dict(unsupported),IRQ_entries=IRQ_entries,interrupt_entry_cycles=sum(v['cycles']for v in IRQ_entries),pinned_entry_charge_has_accuracy_FIXME=True,mismatches=[dict(PC=k[0],opcode=k[1],family=k[2],predicted=k[3],actual=k[4],count=v)for k,v in mismatches.items()],
            examples=examples,families=dict(counts),reference_trace_sha256=trace.hexdigest(),metadata_sha256=hashlib.sha256(Path(json.loads((runtime.out.parents[1]/'CPU-cycle-metadata-current.json').read_text())['metadata']).read_bytes()).hexdigest(),
            source=__file__,scope='Original CPU execution is reference only. Cost model runs no opcode bodies. Interrupt/exception entry and physical bus stalls need separate accounting; this probe does not adopt a global clock.')
    runtime.cycle_cost_report=report
