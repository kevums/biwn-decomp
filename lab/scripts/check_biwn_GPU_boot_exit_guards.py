"""Host contracts and real captured source GPU IRQ0 frame comparison."""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_boot_exit_AV as joined
import check_biwn_movie_GPU as gpu
from check_biwn_main_GPU_boot import Bus,W16
ROOT=joined.ROOT;save=joined.save;sha=joined.sha

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-boot-exit-AV.json').read_text());lib=c.CDLL(str(Path(proof['directory'])/'libcontroller-AV.dylib'));boot=lib.biwn_gpu_main_boot_run;exit=lib.biwn_gpu_movie_exit_run;event=lib.biwn_gpu_movie_exit_CPU_control5
    for f in [boot,exit]:f.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32];f.restype=c.c_int
    event.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State)];event.restype=c.c_int
    bp=json.loads((ROOT/'verification/BIWN-main-GPU-boot-original.json').read_text());ep=json.loads((ROOT/'verification/BIWN-movie-exit-GPU-original.json').read_text());before_boot=(Path(bp['directory'])/'before-GPU.bin').read_bytes();before_event=(Path(ep['directory'])/'before-GPU.bin').read_bytes();entered=(Path(ep['directory'])/'IRQ-entered-GPU.bin').read_bytes()
    cases=[]
    def check(kind,options,expected):
        state=gpu.state_from_raw(before_boot if kind=='boot' else entered if kind=='exit' else before_event);calls=[]
        def r16(_,a,v):calls.append(['r16',a]);v[0]=0;return int(options.get('fail_read',False))
        def r32(_,a,v):calls.append(['r32',a]);v[0]=0;return int(options.get('fail_read',False))
        def w16(_,a,v):calls.append(['w16',a,v]);return int(options.get('fail_write',False))
        def w32(_,a,v):calls.append(['w32',a,v]);return int(options.get('fail_write',False))
        callbacks=[gpu.R16(r16),gpu.R32(r32),W16(w16),gpu.W32(w32),gpu.OBS()]
        if 'missing' in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        bus=Bus(*callbacks,None)
        if options.get('bad_pc'):state.pc=0
        if options.get('bad_bank'):state.active_bank=1
        if options.get('bad_flag'):state.z=2
        if options.get('masked'):state.flags|=8
        if options.get('disabled'):state.flags&=~0x10
        if options.get('external_stack'):state.registers[0][31]=0x1c0004
        initial=bytes(state);status=(event(None if options.get('null_bus') else c.byref(bus),None if options.get('null_state') else c.byref(state)) if kind=='event' else (boot if kind=='boot' else exit)(None if options.get('null_bus') else c.byref(bus),None if options.get('null_state') else c.byref(state),options.get('budget',100)))
        assert status==expected,(kind,options,status)
        if status:assert bytes(state)==initial
        if options.get('masked') or options.get('disabled'):
            previous=gpu.State.from_buffer_copy(initial);assert state.pc==previous.pc and state.registers[0][31]==previous.registers[0][31] and state.control&0x40
        if kind=='event' and not options:assert gpu.logical(state)==entered[:4396]
        cases.append(dict(kind=kind,options=options,status=status,state_unchanged=bytes(state)==initial,external_calls=calls))
    for kind in ['boot','exit']:
        missing=[0,1,2,3] if kind=='boot' else [1,3]
        for options in [dict(missing=i) for i in missing]+[dict(null_bus=True),dict(null_state=True),dict(budget=0),dict(bad_bank=True),dict(bad_flag=True)]:check(kind,options,1)
        check(kind,dict(bad_pc=True),3);check(kind,dict(budget=1),4);check(kind,dict(fail_write=True),2);check(kind,{},0)
    for options in [dict(null_bus=True),dict(null_state=True),dict(missing=3),dict(bad_bank=True),dict(bad_flag=True)]:check('event',options,1)
    check('event',dict(external_stack=True,fail_write=True),2);check('event',dict(masked=True),0);check('event',dict(disabled=True),0);check('event',{},0)
    out=ROOT/'verification/BIWN-GPU-boot-exit-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='boot_exit_host_contracts_and_real_IRQ0_frame_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),checks=len(cases),cases=cases,real4396byte_GPU_IRQ_event_match=True,source_sha256={n:h for n,h in proof['source_sha256'].items() if n in ['biwn_gpu_main_boot.c','biwn_gpu_movie_exit.c']},scope='Normal kernel successes with no-op peripheral guard bus, typed host errors preserve inputstate (prior external calls retained), masked/disabled IRQ0 latch remains pending, valid event equals capturedoriginal4396bytes. No otherIRQ/bank1/physicaltiming/gameplay proof.')
    save(out/'report.json',report);save(ROOT/'verification/BIWN-GPU-boot-exit-guards.json',report);print(json.dumps(dict(directory=str(out),checks=len(cases),real_IRQ_frame_match=True)))
if __name__=='__main__':main()
