"""Isolated original input/locomotion fixtures; leaves the live preview alone."""
import ctypes as c
import json
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_A7, UC_M68K_REG_PC, UC_M68K_REG_SR
import check_biwn_input_dispatch as dispatcher
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def main():
    out=ROOT/'verification/BIWN-run-controls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    manifest=ROOT/'verification/CPU-IRQ-selection-core-experimental-candidate.json'
    core_path=Path(json.loads(manifest.read_text())['core_path'])
    core=c.CDLL(str(core_path))
    core.JoystickReadWord.argtypes=[c.c_uint32]
    core.JoystickReadWord.restype=c.c_uint16
    core.JoystickWriteWord.argtypes=[c.c_uint32,c.c_uint16]
    core.JoystickWriteWord.restype=None
    pad=(c.c_uint8*84).in_dll(core,'joypad0Buttons')
    baseline=ROOT/'render-assets/biwn-inventory-baseline.bin'
    snapshot=baseline.read_bytes()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=session/'nextstage-68000-candidate.bin'
    assert snapshot[0xe4c0:0xe540]==image.read_bytes()[0xe4c0-0x4000:0xe540-0x4000]
    assert snapshot[0x191f4:0x19f2c]==image.read_bytes()[0x191f4-0x4000:0x19f2c-0x4000]
    held={};poll_results=[]
    for name,buttons in [('none',[]),('up',[0]),('C',[18]),('up_C',[0,18]),('up_B',[0,17])]:
        core.JoystickInit()
        for i in buttons:pad[i]=1
        cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        cpu.mem_map(0,0x200000)
        cpu.mem_write(0,snapshot)
        cpu.mem_map(0xf14000,0x1000)
        cpu.mem_write(dispatcher.SP,dispatcher.STOP.to_bytes(4,'big'))
        cpu.reg_write(UC_M68K_REG_SR,0x2000)
        cpu.reg_write(UC_M68K_REG_A7,dispatcher.SP)
        accesses=[]
        def write(engine,access,address,width,value,opaque):
            if address==0xf14000:
                assert width==2
                core.JoystickWriteWord(0,value)
                accesses.append(['write',address,width,value])
        def read(engine,access,address,width,value,opaque):
            if address==0xf14000:
                assert width==4
                row=(core.JoystickReadWord(0)<<16)|core.JoystickReadWord(2)
                engine.mem_write(address,row.to_bytes(4,'big'))
                accesses.append(['read',address,width,row])
        cpu.hook_add(UC_HOOK_MEM_WRITE,write)
        cpu.hook_add(UC_HOOK_MEM_READ,read)
        cpu.emu_start(0xe4c0,dispatcher.STOP,count=256,timeout=1000000)
        assert cpu.reg_read(UC_M68K_REG_PC)==dispatcher.STOP
        held[name]=int.from_bytes(cpu.mem_read(0x49ba4,4),'big')
        poll_results.append(dict(buttons=name,original_poll_held=hex(held[name]),accesses=accesses))
    assert held==dict(none=0,up=0x100000,C=0x2000,up_C=0x102000,up_B=0x2100000),held
    # Original dispatcher with explicit helper stubs. The division numerator
    # is observed at the helper boundary; movement in the full game also
    # depends on animation, collision and scheduling.
    seed=dispatcher.cases(snapshot)[0]
    rows=[]
    for state,buttons in [(1,'up'),(5,'up'),(5,'up_C'),(8,'up_C'),(8,'up')]:
        case=dict(seed)
        case.update(state=state,held=held[buttons],kind='run_control',read_queues=[],helper_effects=[])
        case['initial']=list(seed['initial'])+[[0x49cb8,2,state],[0x49ba4,4,held[buttons]],
            [0x49c4e,2,0],[0x49d62,2,0],[0x4c24c,4,10],[0x49cc8,4,0]]
        case['helper_returns']=dict(seed['helper_returns'])
        case['helper_returns'][str(0xe588)]=0
        script=dispatcher.Script(snapshot,case)
        d0,steps=dispatcher.original(script,case,set())
        division=[row[2] for row in script.trace if row[:2]==['call',0xe588]]
        rows.append(dict(initial_state=state,buttons=buttons,
            resulting_state=int.from_bytes(script.memory[0x49cb8:0x49cba],'big'),
            division_arguments=division,original_instructions=steps))
    assert [r['resulting_state'] for r in rows]==[5,5,8,8,5],rows
    assert rows[1]['division_arguments']==[[15728640,300]]
    assert rows[3]['division_arguments']==[[47185920,300]]
    result=dict(status='terminal_original_controller_C_run_state_verified',directory=str(out),
        poll=poll_results,dispatcher=rows,
        preview_mapping=dict(forward='Up',Jaguar_C='c',Shift_mapped=False),
        checked_answer='Hold keyboard C while moving forward with Up. Original input polling maps Jaguar C to held bit0x2000; walking state5 switches to running state8. The established running path uses scale9 versus walking scale3. Animation/state transitions can take an update. This does not establish a universal threefold displacement or FPS increase.',
        scope='Isolated original 68000 input polling against actual pinned emulator joystick matrix, then original dispatcher with declared helper stubs. No live preview manipulation, complete gameplay sprint or physical-controller test.',
        source_sha256={str(p):sha(p) for p in [Path(__file__),manifest,core_path,baseline,image,ROOT/'scripts/biwn_live_window.py',ROOT/'scripts/check_biwn_input_dispatch.py']},
        new_model_code=False,new_training=False,default_promoted=False)
    save(out/'verification.json',result)
    save(ROOT/'verification/BIWN-run-controls-current.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
