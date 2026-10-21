"""API/error contracts and separate IRQ/padding diagnostics for the DSP program."""
import ctypes as c
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_dsp_media_audio as base


def main():
    root=base.ROOT;primary=json.loads((root/'verification/biwn-dsp-media-audio-checks.json').read_text())
    session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'media-dsp-e840/C-generation.json').read_text())
    runtime=base.Runtime(Path(primary['directory'])/'libdsp-media-audio.dylib',mapping)
    ram=(root/'render-assets/biwn-inventory-baseline.bin').read_bytes();guards=[];diagnostics=[]
    try:
        initial=runtime.load(ram,0,0x0481db08)
        boot,ready=runtime.original_segment(set());ready_raw=runtime.raw()
        for option in ['null_bus','null_state','missing_read8','missing_read32','missing_write32','bad_Z','bad_C','bad_N','bank1','data_PC','stopped']:
            state=base.State.from_buffer_copy(bytes(initial));callbacks=list(runtime.callbacks)
            if option.startswith('missing_'):callbacks[['missing_read8','missing_read32','missing_write32'].index(option)]=[base.R8,base.R32,base.W32][['missing_read8','missing_read32','missing_write32'].index(option)]()
            if option.startswith('bad_'):setattr(state,option[-1].lower(),2)
            if option=='bank1':state.flags|=0x4000
            if option=='data_PC':state.pc=0xf1b138
            if option=='stopped':state.control&=~1
            bus=base.Bus(*callbacks,None);before=bytes(state)
            status=runtime.step(None if option=='null_bus' else c.byref(bus),None if option=='null_state' else c.byref(state))
            expected=3 if option=='data_PC' else 6 if option=='stopped' else 1
            assert status==expected and bytes(state)==before,(option,status)
            guards.append(dict(option=option,status=status))
        for name,entry,index,callback in [('read8',0xf1b0d4,0,base.R8(lambda *_:1)),
                ('read32',0xf1b022,1,base.R32(lambda *_:1)),('write32',0xf1b0d8,2,base.W32(lambda *_:1))]:
            state=base.State.from_buffer_copy(bytes(ready));state.pc=entry
            state.registers[0][0]=0x1a0000;state.registers[0][4]=0x1a0000;state.registers[0][10]=0xf1a148
            callbacks=list(runtime.callbacks);callbacks[index]=callback;bus=base.Bus(*callbacks,None);before=bytes(state)
            status=runtime.step(c.byref(bus),c.byref(state));assert status==2 and bytes(state)==before,(name,status)
            guards.append(dict(failure=name,status=status,guard_internal_entry=hex(entry)))
        for budget in [0,1]:
            state=base.State.from_buffer_copy(bytes(initial));before=bytes(state)
            status=runtime.run(c.byref(runtime.bus),c.byref(state),budget)
            assert status==(1 if budget==0 else 4) and bytes(state)==before
            guards.append(dict(run_budget=budget,status=status))
        # Work-limit error keeps prior peripheral effects while preserving CPU.
        state=base.State.from_buffer_copy(bytes(ready));state.pc=0xf1b0d8;state.registers[0][0]=0x5a00;state.registers[0][10]=0xf1a148
        before=bytes(state);runtime.writes=[];status=runtime.run(c.byref(runtime.bus),c.byref(state),1)
        assert status==4 and bytes(state)==before and runtime.writes==[[0xf1a148,0x5a00]]
        guards.append(dict(run_budget_after_external_store=1,status=status,prior_external_store_retained=True))
        assert runtime.interrupt(None)==1;guards.append(dict(null_interrupt_state=True,status=1))
        state=base.State.from_buffer_copy(bytes(ready));state.registers[0][31]=0;before=bytes(state)
        assert runtime.interrupt(c.byref(state))==1 and bytes(state)==before
        guards.append(dict(invalid_private_IRQ_stack=True,status=1))
        # IRQs with disabled mask, masked handler and stopped engine: compare
        # the exact architecture transition, without executing DSP instructions.
        runtime.core.DSPStateLoad.argtypes=[c.c_void_p];runtime.core.DSPStateLoad.restype=c.c_size_t
        for mode in ['disabled','masked','stopped']:
            state=base.State.from_buffer_copy(bytes(ready));raw=bytearray(ready_raw)
            if mode=='disabled':state.flags&=~0x20
            elif mode=='masked':state.flags|=8
            else:state.control&=~1
            raw[:8496]=base.logical(state);buffer=c.create_string_buffer(bytes(raw));assert runtime.core.DSPStateLoad(buffer)==len(raw)
            count=runtime.counter.value;runtime.core.DSPSetIRQLine(1,1);expected=runtime.raw()[:8496]
            assert runtime.interrupt(c.byref(state))==0 and base.logical(state)==expected and runtime.counter.value==count
            diagnostics.append(dict(IRQ_condition=mode,logical_state_match=True,original_DSP_instructions_executed=0))
        # Forced NOP entries characterize the padding but do not increase the
        # natural source-caller instruction coverage recorded by the primary test.
        missing=primary['unexercised_instructions'];assert missing==['0xf1b01a','0xf1b130','0xf1b132','0xf1b134','0xf1b136']
        for address in missing:
            state=base.State.from_buffer_copy(bytes(ready));state.pc=int(address,16);raw=bytearray(ready_raw);raw[:8496]=base.logical(state)
            buffer=c.create_string_buffer(bytes(raw));runtime.core.DSPStateLoad(buffer)
            runtime.core.DSPExec(1);expected=runtime.raw()[:8496]
            assert runtime.step(c.byref(runtime.bus),c.byref(state))==0 and base.logical(state)==expected
            diagnostics.append(dict(forced_padding_entry=address,logical_state_match=True,normal_coverage_unchanged=True))
        # Exercise the public bounded-run API, not just the step path.
        state=runtime.load(ram,0,0x0481db08);runtime.C_segment(state,boot,0,'guard-ready',Path(primary['directory']))
        check=runtime.load(ram,0,0x0481db08);count=runtime.counter.value
        assert runtime.run(c.byref(runtime.bus),c.byref(check),10000)==0 and base.logical(check)==base.logical(state) and runtime.counter.value==count
        diagnostics.append(dict(public_run_boot_to_idle_matches=True,original_DSP_instructions_on_C_side=0))
        record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='DSP_media_audio_host_guards_and_separate_IRQ_padding_diagnostics_pass',
            host_guards=len(guards),guards=guards,diagnostics=diagnostics,source_sha256=mapping['source_sha256'],
            test_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),primary_report=str(root/'verification/biwn-dsp-media-audio-checks.json'),
            normal_source_caller_coverage_unchanged=True,normal_coverage=[113,118],
            limits='Internal failure/padding/IRQ conditions are separate diagnostics, not natural game-flow coverage. No timing/global DSP/physical hardware or complete game-audio proof.')
        (root/'verification/biwn-dsp-media-audio-guards.json').write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(dict(host_guards=len(guards),separate_diagnostics=len(diagnostics),normal_coverage=[113,118])))
    finally:runtime.media.oracle.close()


if __name__=='__main__':main()
