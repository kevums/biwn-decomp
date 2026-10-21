"""Exercise new route cases against the pinned original CPU, not game fixtures."""
import ctypes as c
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--candidate',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--PC',type=lambda value:int(value,0),action='append');parser.add_argument('--exception-events',action='store_true');parser.add_argument('--cost-candidate',type=Path);args=parser.parse_args()
    assert not args.candidate or args.output,'Isolated candidates need a separate proof path'
    candidate=json.loads((args.candidate or ROOT/'verification/scene17-route-CPU-experimental-candidate.json').read_text())
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    oracle=media.scheduler.Native(diagnostic_core=core)
    runtime=media.Runtime.__new__(media.Runtime)
    runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    lib=c.CDLL(candidate['library']);fn=getattr(lib,candidate['function'])
    fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p]
    fn.restype=c.c_int
    atlas=Path(candidate['instruction_RAM_source']).read_bytes()
    results=[];cost=None
    if args.cost_candidate:
        cost_manifest=json.loads(args.cost_candidate.read_text());cost_lib=c.CDLL(cost_manifest['library']);cost=cost_lib.biwn_native_cycle_cost
        cost.argtypes=[c.c_uint16,c.POINTER(media.CPU),c.POINTER(c.c_uint8)];cost.restype=c.c_int
    try:
        rows=[row for row in candidate['new_cases']if not args.PC or row['address']in args.PC]
        assert not args.PC or {row['address']for row in rows}==set(args.PC)
        for row in rows:
            pc=row['address'];assert atlas[pc:pc+row['size']].hex()==row['bytes']
            cases=0;destinations=set()
            for sr in list(range(32))+list(range(0x2000,0x2020)):
                for operand in ([0,1,0x80,0x8001,0xffff]if args.PC else[0,1,0x8001,0xffff]):
                    initial=media.CPU();initial.registers[:]=[12,0xffff,0x8001,0xfffffff9,3,5,12,7]+[0x72000,0x70000,0x71000,0x73000,0x74000,0x75000,0x76000,0x180800]
                    initial.usp,initial.ssp,initial.sr,initial.pc=0x180800,0x1e0000,sr,pc
                    if pc==0x1af60:initial.registers[0]=operand
                    if pc==0x1049e:initial.registers[1]=0x7fff0000|(0x7fff if operand&0x8000 else operand)
                    if pc==0x1047e:initial.registers[2]=2 if operand==0x8001 else operand
                    if pc==0x2190c:initial.registers[5]=4 # word EA must be aligned
                    if pc in [0x10518,0x19f78]:initial.registers[0]=0xa5a50000|operand
                    if pc in [0x1a436,0x1a442]:
                        initial.registers[5 if pc==0x1a436 else 7]=0xa5a50000|operand
                    if pc==0x1a43c:initial.registers[6]=(operand<<16)|operand
                    if pc in [0x13420,0x1479e,0x14976,0x1bcf4,0x1bd60]:initial.registers[0]=0xa5a40000|((operand&1)<<16)|operand
                    if pc==0x1785e:initial.registers[1]=0xa5a50000|operand
                    initial.registers[15]=initial.ssp if sr&0x2000 else initial.usp
                    fixture=bytearray(atlas)
                    opcode=int(row['bytes'][:4],16)
                    exception=opcode==0x4afc or 0x4e40<=opcode<=0x4e4f
                    if exception:
                        assert args.exception_events
                        vector=4 if opcode==0x4afc else 32+(opcode&15)
                        fixture[vector*4:vector*4+4]=(0x1d000).to_bytes(4,'big')
                        fixture[0x1d000:0x1d002]=b'\x4e\x71'
                    if pc in [0x1a42e,0x1a448,0x1a450]:
                        stack=initial.registers[15]
                        fixture[stack+0x2c:stack+0x30]=((operand<<16)|operand).to_bytes(4,'big')
                        fixture[stack+0x30:stack+0x34]=((operand<<16)|(operand^0xffff)).to_bytes(4,'big')
                    # Exercise both zero/nonzero tests and wrapped word ALU
                    # while keeping address-indexed operands inside main RAM.
                    for address in [0x70006,0x7004a,0x7100e,0x71012,0x71014,0x73020]:
                        fixture[address:address+4]=((operand<<16)|operand).to_bytes(4,'big')
                    fixture[0x7100d]=0x81
                    if pc in [0x104a8,0x104ac,0x2190c]:
                        address={0x104a8:0x70052,0x104ac:0x7000c,0x2190c:0x70044}[pc]
                        fixture[address:address+2]=operand.to_bytes(2,'big')
                    if pc==0x104b0:fixture[0x7200f]=operand&255
                    runtime.device.seed(bytes(fixture),0);runtime.seed_cpu(initial);native_cycles=runtime.core.m68k_execute(1)
                    native_cpu,native_ram=runtime.cpu(),runtime.device.ram()
                    if cost:
                        cost_RAM=(c.c_uint8*len(fixture)).from_buffer(fixture)
                        predicted=cost(opcode,c.byref(initial),cost_RAM)
                        assert predicted==native_cycles,(hex(pc),'cycles',predicted,native_cycles)
                    memory=bytearray(fixture)
                    def reader(width):
                        def read(_,address,out):
                            if address+width>len(memory):return 1
                            out[0]=int.from_bytes(memory[address:address+width],'big');return 0
                        return read
                    def writer(width):
                        def write(_,address,value):
                            if address+width>len(memory):return 1
                            memory[address:address+width]=value.to_bytes(width,'big');return 0
                        return write
                    world=media.scheduler.cleanup.world
                    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),media.W8(writer(1))]
                    bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
                    translated=media.CPU.from_buffer_copy(bytes(initial))
                    status=fn(c.byref(bus),c.byref(translated),callbacks[5],media.world_cpu.SERVICE(),None)
                    assert status==(11 if exception else 0),(hex(pc),sr,operand,status)
                    assert media.scheduler.cpu_dict(translated)==media.scheduler.cpu_dict(native_cpu),(hex(pc),sr,operand,media.scheduler.cpu_dict(translated),media.scheduler.cpu_dict(native_cpu))
                    assert bytes(memory)==native_ram,(hex(pc),sr,operand,'RAM differs')
                    destinations.add(translated.pc);cases+=1
            results.append(dict(PC=hex(pc),instruction=row['assembly'],cases=cases,destination_PCs=[hex(x)for x in sorted(destinations)]))
            print(hex(pc),cases,'original/C instruction fixtures passed',flush=True)
    finally:oracle.close()
    report=dict(status='new_route_CPU_instruction_fixtures_pass'if args.candidate else'new_scene17_CPU_instruction_fixtures_pass',recorded_at=datetime.now(timezone.utc).isoformat(),cases=sum(x['cases']for x in results),instructions=results,candidate=candidate['library'],source_sha256=candidate['source_sha256'],core=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),scope='All32CCR combinations in user/supervisor mode with declared register/RAM seeds; fullCPU/register/stackbank/mainRAM match original nativeCPU for each isolated step. Source-specific multiply/subtract cases additionally vary operands. Synthetic instruction fixtures, not natural game states, nested-function semantics, cycle-cost or full-route proof.',whole_game_complete=False,selected_PC_filter=args.PC,source_exception_events=args.exception_events,cycle_costs_compared=bool(cost),cost_candidate=str(args.cost_candidate)if args.cost_candidate else None)
    (args.output or ROOT/'verification/scene17-new-CPU-instruction-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],report['cases'],flush=True)


if __name__=='__main__':main()
