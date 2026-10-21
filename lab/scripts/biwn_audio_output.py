"""Bounded, nonblocking stereo PCM output for the experimental preview.

The sink consumes frontend samples only. It does not pace or modify emulation.
Slow emulation produces silence between available blocks, rather than an
unbounded delayed soundtrack. Pause/mute discard pending sound immediately.
"""
from collections import deque
import ctypes
import threading


def core_audio_rate(core):
    class Geometry(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint) for name in
                    ('base_width', 'base_height', 'max_width', 'max_height')] + [('aspect_ratio', ctypes.c_float)]
    class Timing(ctypes.Structure):
        _fields_ = [('fps', ctypes.c_double), ('sample_rate', ctypes.c_double)]
    class AVInfo(ctypes.Structure):
        _fields_ = [('geometry', Geometry), ('timing', Timing)]
    core.retro_get_system_av_info.argtypes = [ctypes.POINTER(AVInfo)]
    info = AVInfo()
    core.retro_get_system_av_info(ctypes.byref(info))
    rate = info.timing.sample_rate
    if not 8000 <= rate <= 192000:
        raise ValueError(f'Invalid core sample rate: {rate}')
    return rate


class AudioOutput:
    def __init__(self, sample_rate, stream_factory=None):
        if stream_factory is None:
            import sounddevice
            stream_factory = sounddevice.RawOutputStream
        self.sample_rate = sample_rate
        self.limit = max(4, int(sample_rate * .15) * 4)
        self.queue = deque()
        self.queued = 0
        self.lock = threading.Lock()
        self.suspended = True
        self.muted = False
        self.closed = False
        self.received_bytes = self.played_bytes = self.dropped_bytes = 0
        self.silence_bytes = self.status_events = 0
        self.stream = stream_factory(samplerate=sample_rate, channels=2,
                                     dtype='int16', blocksize=0, latency='low',
                                     callback=self.callback)
        try:
            self.stream.start()
        except Exception:
            self.stream.close()
            raise

    def set_state(self, *, suspended=None, muted=None):
        with self.lock:
            if suspended is not None:
                self.suspended = suspended
            if muted is not None:
                self.muted = muted
            if self.suspended or self.muted:
                self.dropped_bytes += self.queued
                self.queue.clear()
                self.queued = 0

    def submit(self, raw):
        if len(raw) % 4:
            raise ValueError('Stereo int16 PCM must contain complete frames')
        with self.lock:
            self.received_bytes += len(raw)
            if self.closed or self.suspended or self.muted:
                self.dropped_bytes += len(raw)
                return
            if len(raw) > self.limit:
                self.dropped_bytes += len(raw) - self.limit
                raw = raw[-self.limit:]
            while self.queue and self.queued + len(raw) > self.limit:
                self.dropped_bytes += len(self.queue[0])
                self.queued -= len(self.queue.popleft())
            if raw:
                self.queue.append(bytes(raw))
                self.queued += len(raw)

    def callback(self, outdata, frames, timing, status):
        target = memoryview(outdata).cast('B')
        target[:] = bytes(len(target))
        position = 0
        with self.lock:
            self.status_events += bool(status)
            if not (self.closed or self.suspended or self.muted):
                while self.queue and position < len(target):
                    block = self.queue.popleft()
                    count = min(len(block), len(target) - position)
                    target[position:position+count] = block[:count]
                    position += count
                    self.queued -= count
                    if count < len(block):
                        self.queue.appendleft(block[count:])
            self.played_bytes += position
            self.silence_bytes += len(target) - position

    def report(self):
        with self.lock:
            return dict(sample_rate=self.sample_rate, received_frames=self.received_bytes//4,
                        delivered_frames=self.played_bytes//4, dropped_frames=self.dropped_bytes//4,
                        silence_frames=self.silence_bytes//4, queued_frames=self.queued//4,
                        device_status_events=self.status_events, muted=self.muted,
                        suspended=self.suspended, closed=self.closed,
                        physical_audibility_verified=False)

    def close(self):
        with self.lock:
            self.closed = True
            self.dropped_bytes += self.queued
            self.queue.clear()
            self.queued = 0
        try:
            self.stream.abort()
        finally:
            self.stream.close()
