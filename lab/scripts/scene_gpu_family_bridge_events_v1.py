"""Read-only GPU CPU boundary records and declared mailbox inputs for nested fixtures.

The fixture supplies device input levels. It never substitutes native CPU bodies
or seeds their CPU state. This does not run the GPU command consumer programs.
"""
import scene_gpu_family_scene_runtime_v2 as gpu

class Events:
    def __init__(self, bridge, runtime, gate, slot):
        self.b, self.r, self.syms, self.slot = bridge, runtime, gate['symbols'], slot
        self.reads, self.writes = gpu.native_sites(__import__('pathlib').Path(gate['payload']).read_bytes(), bridge.CODE)
        self.wait_return = self.wait_row = self.row = None
        self.pending = None
        self.stack = []
        self.write_value = None

    def logical(self, physical):
        b, r = self.b, self.r
        raw = r.device.ram()[self.slot+b.OFFSET+4:self.slot+b.OFFSET+82]
        cpu = b.base.CPU()
        cpu.registers[:] = [int.from_bytes(raw[i:i+4], 'big') for i in range(0,64,4)]
        cpu.pc = int.from_bytes(raw[64:68], 'big')
        cpu.usp = int.from_bytes(raw[68:72], 'big')
        cpu.ssp = int.from_bytes(raw[72:76], 'big')
        cpu.sr = int.from_bytes(raw[76:78], 'big')
        if cpu.sr & 0x2000: cpu.usp = physical.usp
        else: cpu.ssp = physical.ssp
        return cpu

    def record(self, target, cpu):
        row = dict(target=target, actual_body=True, incoming=self.b.base.cd.scheduler.cpu_dict(cpu))
        self.r.calls.append(row)
        return row

    def before(self, physical, native):
        pc, r, syms = physical.pc, self.r, self.syms
        self.write_value = None
        if native:
            if self.wait_return is not None and pc == self.wait_return:
                cpu = self.logical(physical); assert cpu.pc == 0xe0a4
                self.wait_row['return'] = self.b.base.cd.scheduler.cpu_dict(cpu)
                self.wait_return = self.wait_row = None
            if pc == syms['biwn_v30_gpu_begin']:
                cpu = self.logical(physical); assert self.row is None and cpu.pc in gpu.GPU_ENTRIES
                self.row = self.record(cpu.pc, cpu)
            if pc == syms['scene_gpu_wait_body'] and self.row is not None and self.row['target'] != 0xe098:
                cpu = self.logical(physical); assert self.wait_row is None and cpu.pc == 0xe098
                self.wait_return = r.device.read(physical.registers[15], 4)
                assert self.b.CODE <= self.wait_return < self.b.CODE+len(__import__('pathlib').Path(self.b._BUILD['component']).read_bytes())
                self.wait_row = self.record(0xe098, cpu)
            if pc == syms['biwn_v30_gpu_end']:
                cpu = self.logical(physical)
                assert self.row is not None and self.wait_row is None and cpu.pc == gpu.GPU_ENTRIES[self.row['target']]
                self.row['return'] = self.b.base.cd.scheduler.cpu_dict(cpu); self.row = None
            if pc in self.reads:
                address = physical.registers[self.reads[pc]] & 0xffffff
                if address in [0xf03200, 0xf03204]: r.inject(address, 4)
            if pc in self.writes:
                src, dest = self.writes[pc]
                if physical.registers[dest] & 0xffffff == 0xf03204: self.write_value = physical.registers[src]
        # Real original helpers can also run inside a native busy fallback.
        if self.pending == pc:
            self.stack.append(self.record(pc, physical)); self.pending = None
        if pc in gpu.GPU_ENTRIES.values() and self.stack:
            self.stack.pop()['return'] = self.b.base.cd.scheduler.cpu_dict(physical)
        source = r.rows.get(pc)
        if source and source['assembly'].startswith('jsr '):
            target = int(source['assembly'].split('$')[1].split('.')[0], 16)
            self.pending = target if target in gpu.GPU_ENTRIES else None
        if pc == 0xe098: r.inject(0xf03200, 4)
        if pc in gpu.POLL: r.inject(0xf03204, 4)

    def after(self, pc):
        if pc in gpu.WRITES: self.r.command_written(self.r.core.GPUReadLong(0xf03204, 0))
        if self.write_value is not None: self.r.command_written(self.write_value)

    def complete(self):
        assert self.row is None and self.wait_row is None and not self.stack and self.pending is None
