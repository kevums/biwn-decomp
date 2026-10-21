"""Execute intervening source task CPU bodies from a single initial state.

No later task CPU/RAM snapshots are transplanted. Recorded MMIO inputs,
OP writes, IRQ delivery points and CD_poll's two firmware outputs remain
declared providers. This is a deterministic CPU host integration check,
not an independently clocked device runtime or live preview installation.
"""
import ctypes as c
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import check_biwn_coordinate_flow as flow
import check_biwn_scheduler as scheduler
from check_biwn_coordinate_yield import Ticket
from check_biwn_natural_coordinate_scheduler import ROOT, DTYPE, cpu_record, sha, save

world=scheduler.cleanup.world
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(scheduler.CPU),c.c_uint32)


class Machine:
    def __init__(self, ram, bus):
        self.ram=bytearray(ram);self.bus_rows=bus;self.expected=[];self.used=0
        self.trace=[];self.errors=[];self.index=None;self.checked=True
        self.MMIO_reads=0;self.MMIO_writes=0
        def operation(kind,width,address,value=None):
            expected=None
            if self.checked:
                assert self.used<len(self.expected),('extra',self.index,kind,width,hex(address))
                expected=self.expected[self.used];self.used+=1
                assert expected[:3]==[kind,width,address],('access',self.index,expected,[kind,width,address])
            if kind=='r':
                if address+width<=len(self.ram):value=int.from_bytes(self.ram[address:address+width],'big')
                else:
                    assert expected is not None,('unprovided MMIO',hex(address))
                    value=expected[3];self.MMIO_reads+=1
            elif address+width<=len(self.ram):self.ram[address:address+width]=value.to_bytes(width,'big')
            else:self.MMIO_writes+=1
            event=[kind,width,address,value]
            if expected is not None:assert event==expected,('value',self.index,expected,event)
            self.trace.append(event);return value
        def reader(width):
            def callback(_,address,value):
                try:value[0]=operation('r',width,address);return 0
                except BaseException as error:self.errors.append(repr(error));return 1
            return callback
        def writer(width):
            def callback(_,address,value):
                try:operation('w',width,address,value);return 0
                except BaseException as error:self.errors.append(repr(error));return 1
            return callback
        self.callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL()]
        self.bus=world.Bus(*self.callbacks,None,0);self.write8=W8(writer(1))
    def start(self,index):
        self.index=index;self.expected=self.bus_rows.get(index,[]);self.used=0;self.checked=True
    def finish(self):
        assert self.used==len(self.expected),(self.index,'unconsumed',self.expected[self.used:])
        assert not self.errors,self.errors
    def owner(self):return int.from_bytes(self.ram[0xc0920:0xc0924],'big')


def main():
    out=ROOT/'verification/coordinate-task-execution'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    bus_path=ROOT/'verification/coordinate-task-bus-current.json';captured_path=ROOT/'verification/natural-coordinate-scheduler-current.json';bridge_path=ROOT/'verification/coordinate-yield-current.json'
    bus_proof=json.loads(bus_path.read_text());captured=json.loads(captured_path.read_text());bridge=json.loads(bridge_path.read_text())
    assert bus_proof['status']=='terminal_inert_bus_capture'
    assert sha(bus_path.parent.parent/'scripts/check_biwn_coordinate_task_execution.py')==sha(Path(__file__))
    folder=Path(bus_proof['directory']);captures=Path(captured['directory'])/'captures'
    assert sha(folder/'CPU-bus.txt')==bus_proof['bus_sha256']and sha(folder/'native-events.txt')==bus_proof['events_sha256']
    assert sha(bridge['library'])==bridge['library_sha256']
    transitions=json.loads((captures.parent/'transitions.json').read_text());first,last=bus_proof['first'],bus_proof['last'];selected=transitions[0]['last']
    trace=np.memmap(folder/'observed/CPU-before-instructions.bin',mode='r',dtype=DTYPE)
    cpu=scheduler.make_cpu(cpu_record(trace[first]));ram=(captures/f'{first}.ram').read_bytes()
    bus_rows={}
    for line in(folder/'CPU-bus.txt').read_text().splitlines():
        index,kind,width,address,value=line.split();bus_rows.setdefault(int(index),[]).append([kind,int(width),int(address),int(value)])
    events={}
    for line in(folder/'native-events.txt').read_text().splitlines():
        row=list(map(int,line.split()));events.setdefault(row[0],[]).append(row[1:])
    machine=Machine(ram,bus_rows)
    library=c.CDLL(bridge['library']);begin,poll=library.biwn_coordinate_yield_begin,library.biwn_coordinate_yield_poll
    begin.argtypes=[c.POINTER(world.Bus),c.POINTER(Ticket),c.POINTER(flow.Request),c.POINTER(scheduler.CPU),c.c_uint32];begin.restype=c.c_int
    poll.argtypes=[c.POINTER(world.Bus),c.POINTER(Ticket),c.POINTER(scheduler.CPU),c.POINTER(flow.Completion)];poll.restype=c.c_int
    runtime=json.loads((ROOT/'verification/unified-restore-runtime-candidate.json').read_text());source_config=json.loads(Path(runtime['CPU_candidate']).read_text())
    source_lib=c.CDLL(source_config['library']);step=getattr(source_lib,source_config['function'])
    step.argtypes=[c.POINTER(world.Bus),c.POINTER(scheduler.CPU),W8,SERVICE,c.c_void_p];step.restype=c.c_int
    dependencies={path:sha(path)for path in [source_config['library'],bridge['library'],str(ROOT/'projects/black-ice-white-noise/restoration/biwn_cpu_irq_entry.c')]}
    irq_lib=out/'libirq.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(ROOT/'projects/black-ice-white-noise/restoration/biwn_cpu_irq_entry.c'),'-o',str(irq_lib)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    irq=c.CDLL(str(irq_lib)).biwn_cpu_irq_entry;irq.argtypes=[c.POINTER(world.Bus),c.POINTER(scheduler.CPU),c.c_uint,c.c_uint,c.POINTER(scheduler.CPU)];irq.restype=c.c_int
    def external(_,bus,cpu_ptr,target):machine.errors.append('Unexpected source helper '+hex(target));return 1
    service=SERVICE(external)
    request=flow.Request(0x18200002,1,7,0xdf60,0,0,0,cpu.registers[0]);ticket=Ticket()
    state=dict(status='running',pid=os.getpid(),directory=str(out),bus_proof=str(bus_path),captured_scheduler_proof=str(captured_path),
               bridge_proof=str(bridge_path),first=first,last=last,compile_command=command,
               input_dependencies_sha256=dependencies,whole_game_complete=False,live_frame_installation=False)
    def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/coordinate-task-execution-active.json',state)
    checkpoint()
    try:
        # Bridge validates return/owner with two additional host reads. The
        # scheduler's game data access sequence must match the original span.
        machine.checked=False
        assert begin(c.byref(machine.bus),c.byref(ticket),c.byref(request),c.byref(cpu),1024)==0
        expected=[row for index in range(first,selected)for row in bus_rows.get(index,[])]
        assert machine.trace[2:]==expected,('initial_scheduler_bus',machine.trace[2:],expected)
        task_steps=0;handoffs=[];previous_owner=int.from_bytes(ram[0xc0920:0xc0924],'big')
        current_object,pending_long=None,None;op_writes=[];irq_entries=[];firmware=[];CPU_locations=set()
        def asynchronous(index):
            nonlocal current_object,pending_long
            for event in events.get(index,[]):
                sequence,frame,halfline,kind,who,pc,address,value=event
                if kind==6:current_object=(address,value)
                if kind!=12:continue
                assert who in (6,8),('unhandled nonCPU writer',who)
                if who==6:continue  # Already computed by game/IRQ source C.
                assert current_object is not None and current_object[1]==0
                base=current_object[0];assert base%8==0 and base+16<=len(machine.ram)
                if address==base:
                    assert pending_long is None;pending_long=(address,value);continue
                assert address==base+4 and pending_long is not None and pending_long[0]==base
                p0=int.from_bytes(machine.ram[base:base+8],'big');p1=int.from_bytes(machine.ram[base+8:base+16],'big');height=(p0&0xffc000)>>14
                assert p0&7==0 and height>0
                data=((p0&0xfffff80000000000)>>40)+((p1&0xffc0000)>>15)
                predicted=((p0&~0xfffff80000ffc000)|((height-1)<<14)|(data<<40))&0xffffffffffffffff
                actual=(pending_long[1]<<32)|value;assert predicted==actual,('OP formula',index,hex(base))
                machine.ram[base:base+8]=actual.to_bytes(8,'big');op_writes.append(dict(index=index,address=base,before=p0,after=actual));pending_long=None
        for index in range(first+1,selected):asynchronous(index)
        for index in range(selected,last+1):
            asynchronous(index)
            expected_cpu=scheduler.make_cpu(cpu_record(trace[index]))
            if cpu.pc==0x304e:
                # Explicit existing firmware/CD_poll ABI provider. Only A0/A1
                # may be supplied; no task-state or RAM snapshot is installed.
                firmware.append(dict(index=index,target='0x304e',A0=expected_cpu.registers[8],A1=expected_cpu.registers[9]))
                cpu.registers[8]=expected_cpu.registers[8];cpu.registers[9]=expected_cpu.registers[9]
            if cpu.pc!=expected_cpu.pc and expected_cpu.pc==0xe7d4:
                output=scheduler.CPU();machine.checked=False;start=len(machine.trace)
                assert irq(c.byref(machine.bus),c.byref(cpu),2,64,c.byref(output))==0
                irq_entries.append(dict(index=index,interrupted_PC=hex(cpu.pc),level=2,resolved_vector=64,computed_bus=machine.trace[start:]))
                cpu=output
            assert scheduler.cpu_dict(cpu)==scheduler.cpu_dict(expected_cpu),('CPU',index,scheduler.cpu_dict(cpu),scheduler.cpu_dict(expected_cpu))
            owner=machine.owner()
            if owner!=previous_owner:
                handoffs.append(dict(index=index,owner=owner,PC=hex(cpu.pc)));previous_owner=owner
            machine.checked=False;completion=flow.Completion(999,998,997,-996);unchanged=bytes(completion)
            status=poll(c.byref(machine.bus),c.byref(ticket),c.byref(cpu),c.byref(completion))
            if index==last:
                assert status==1 and completion.context==request.context and completion.sequence==request.sequence and completion.value==cpu.registers[0]
                assert machine.ram==(captures/f'{last}.ram').read_bytes(),'Final entireRAM differs'
                break
            assert status==0 and bytes(completion)==unchanged
            machine.start(index);CPU_locations.add(cpu.pc)
            status=step(c.byref(machine.bus),c.byref(cpu),machine.write8,service,None)
            assert status in (0,6,10,11),('source_step',index,status,machine.errors)
            machine.finish();task_steps+=1
        assert pending_long is None
        assert len(irq_entries)==5 and len(handoffs)==18
        save(out/'handoffs.json',handoffs);save(out/'OP-writes.json',op_writes);save(out/'IRQ-entries.json',irq_entries);save(out/'firmware-provider.json',firmware)
        state.update(status='terminal_intervening_task_CPU_execution_matches',source_CPU_steps=task_steps,
                     source_CPU_locations=len(CPU_locations),computed_handoffs=len(handoffs),computed_IRQ_entries=len(irq_entries),
                     supplied_OP_formula_checked_writebacks=len(op_writes),supplied_MMIO_reads=machine.MMIO_reads,
                     acknowledged_MMIO_writes=machine.MMIO_writes,firmware_ABI_results_supplied=len(firmware),
                     full_CPU_every_retired_boundary_matches=True,final_entire_RAM_matches=True,
                     original_CPU_instructions_executed=0,intermediate_task_CPU_snapshots_installed=0,intermediate_task_RAM_snapshots_installed=0,
                     request_completes_only_for_owner=True,source_CPU_library=source_config['library'],source_CPU_function=source_config['function'],
                     limitations=['One actual captured initial CPU/RAM state. MMIO values, OP effects and IRQ delivery indices are supplied, not independently scheduled devices.',
                                  'CD_poll supplies only its two A0/A1 firmware ABI outputs; this provider remains.',
                                  'Initial readable scheduler dispatch replaces22instruction boundaries; other task code runs instruction-compatible C. No cycle-clock equivalence or high-level frame-runtime promotion.',
                                  'The broader logical flow/20F78scene-stream integration and standalone native game remain incomplete.'])
        checkpoint();save(ROOT/'verification/coordinate-task-execution-current.json',state)
        print(json.dumps({key:state[key]for key in ['status','directory','source_CPU_steps','computed_handoffs','computed_IRQ_entries','supplied_OP_formula_checked_writebacks','firmware_ABI_results_supplied']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));checkpoint();raise


if __name__=='__main__':main()
