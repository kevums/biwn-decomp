"""Experimental incremental HLE CD delivery at source system-clock events.

This uses a supplied clock quantum, not CPU cycle-derived global scheduling.
The native/C game VBI observes partial transfer progress on each pulse.
"""
import ctypes as c
import hashlib
import types
import check_biwn_media_setup_cpu as media
import check_biwn_movie_GPU as GPU


def install(runtime, clock_us):
    import biwn_HLE_asset_owner
    biwn_HLE_asset_owner.install(runtime)
    core = runtime.core
    core.JaguarGetHalflinePeriodUs.restype = c.c_double
    period = core.JaguarGetHalflinePeriodUs()
    assert 0 < period < 100 and clock_us > period
    VBI = runtime.lib.biwn_vbi_event
    runtime.HLE_asset_clock_events = []
    runtime.HLE_asset_clock_us = 0.0
    fraction = 0.0
    pending_ticks = 0
    pending_vbis = 0
    reference_steps = 0
    reference_trace = []
    source_clock = runtime.clock_tick

    def mirror():
        if runtime.mode != 'C':
            return
        raw = c.create_string_buffer(12000)
        assert core.GPUStateSave(raw) == 4416
        image = GPU.logical(runtime.gpu) + raw.raw[4396:4416]
        assert core.GPUStateLoad(c.create_string_buffer(image)) == 4416

    def adopt():
        if runtime.mode != 'C':
            return
        raw = c.create_string_buffer(12000)
        assert core.GPUStateSave(raw) == 4416
        changed = GPU.state_from_raw(raw.raw)
        count = runtime.gpu.instructions
        c.memmove(c.byref(runtime.gpu), c.byref(changed), c.sizeof(changed))
        runtime.gpu.instructions = count

    def clock(self):
        nonlocal fraction, pending_ticks, pending_vbis, reference_steps, reference_trace
        self.HLE_asset_clock_us += clock_us
        fraction += clock_us
        ticks_due = int(fraction / period)
        fraction -= ticks_due * period
        item = self.asset_disc.pending
        if item:
            if 'first_clock_us' not in item:
                item['first_clock_us'] = self.HLE_asset_clock_us
            assert core.JaguarCDHLEStreamDest() == item['destination_start']
            status_base = self.device.read(0x3074, 4)
            before = core.GPUReadLong(status_base, 3)
            mirror()
            advanced = 0
            for _ in range(ticks_due):
                if not core.JaguarCDHLEStreamActive():
                    break
                core.JaguarCDHLEStreamTick()
                advanced += 1
            adopt()
            pending_ticks += advanced
            s = self.cpu() if self.mode == 'native' else self.C_CPU
            expected_pc = s.pc
            core.TOMSetPendingVideoInt()
            visited = []
            if self.mode == 'native':
                core.m68k_set_irq2(2)
                assert core.m68k_get_reg(None, 16) == 0xe7d4
                for _ in range(1000):
                    pc = core.m68k_get_reg(None, 16)
                    if pc == expected_pc:
                        break
                    visited.append(hex(pc))
                    assert pc in self.rows, hex(pc)
                    core.m68k_execute(1)
                else:
                    raise AssertionError('incremental CD source VBI bound')
            else:
                core.m68k_set_irq(0)
                assert VBI(c.byref(self.bus), c.byref(s)) == 0
                assert self.body_video(c.byref(self.bus), c.byref(s), self.callbacks[5], self.service, None, 10000, 0) == 0
                assert s.pc == expected_pc
            pending_vbis += 1
            reference_steps += len(visited)
            reference_trace.extend(visited)
            progress = self.device.read(0xbd848, 4)
            active = bool(core.JaguarCDHLEStreamActive())
            self.HLE_asset_clock_events.append(dict(
                clock_us=self.HLE_asset_clock_us, asset_index=len(self.asset_disc.requests)-1,
                requested_ticks=ticks_due, advanced_ticks=advanced,
                stream_request_bytes=core.JaguarCDHLEStreamBytes(),
                GPU_write_pointer_before=before, GPU_write_pointer_after=core.GPUReadLong(status_base,3),
                stream_active=active, source_progress=progress,
                CPU=media.scheduler.cpu_dict(self.cpu() if self.mode=='native' else s),
                RAM_sha256=hashlib.sha256(self.device.ram()).hexdigest()))
            if not active and progress >= item['destination_end']:
                data = self.device.ram()[item['destination_start']:item['destination_end']]
                item.update(sha256=hashlib.sha256(data).hexdigest(), HLE_stream_ticks=pending_ticks,
                            source_completion_VBIs=pending_vbis, last_clock_us=self.HLE_asset_clock_us)
                self.asset_disc.completions.append(dict(bytes=item['bytes'], progress_address=0xbd848,
                    progress_value=progress, completion_by_source_VBI=True, HLE_stream_ticks=pending_ticks))
                self.HLE_asset_VBIs.append(dict(CPU=media.scheduler.cpu_dict(self.cpu() if self.mode=='native' else s),
                    progress=progress, source_completion_VBIs=pending_vbis,
                    reference_CPU_steps=reference_steps if self.mode=='native' else None,
                    reference_PC_trace=reference_trace if self.mode=='native' else None))
                self.asset_disc.pending = None
                pending_ticks = pending_vbis = reference_steps = 0
                reference_trace = []
        source_clock()

    def handoff(self, s):
        # A context switch observes in-flight data; it cannot finish a read.
        self.handoffs.append(dict(CPU=media.scheduler.cpu_dict(s), context=hex(self.current()),
            RAM=hashlib.sha256(self.device.ram()).hexdigest(), hardware=self.hardware(), disc_completed=None))

    runtime.clock_tick = types.MethodType(clock, runtime)
    runtime.handoff_event = types.MethodType(handoff, runtime)
