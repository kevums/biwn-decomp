"""Exercise queue and lifecycle behavior without opening a physical device."""
import hashlib
import json
from pathlib import Path
from biwn_audio_output import AudioOutput


class FakeStream:
    def __init__(self, **settings): self.settings = settings
    def start(self): pass
    def abort(self): pass
    def close(self): self.closed = True


def main():
    sink = AudioOutput(48000, FakeStream)
    checks = {}
    sink.set_state(suspended=False)
    raw = bytes(range(16))
    sink.submit(raw)
    target = bytearray(8)
    sink.callback(target, 2, None, False)
    assert target == raw[:8]
    sink.callback(target, 2, None, False)
    assert target == raw[8:]
    checks['ordered_PCM_and_partial_blocks'] = True
    sink.callback(target, 2, None, False)
    assert target == bytes(8)
    checks['underflow_zero_fill'] = True
    for name in ('muted', 'suspended'):
        sink.submit(raw)
        sink.set_state(**{name: True})
        sink.callback(target, 2, None, False)
        assert target == bytes(8) and sink.queued == 0
        sink.set_state(**{name: False})
        checks[name+'_discards_pending_audio'] = True
    sink.submit(b'x' * (sink.limit + 40))
    assert sink.queued == sink.limit
    checks['bounded_queue'] = True
    try:
        sink.submit(b'x')
    except ValueError:
        checks['reject_partial_stereo_frame'] = True
    else:
        raise AssertionError('Partial frame accepted')
    sink.close()
    assert sink.stream.closed and not sink.queue and sink.closed
    assert sink.received_bytes == sink.played_bytes + sink.dropped_bytes + sink.queued
    checks['close_and_accounting'] = True
    class FailedStream(FakeStream):
        instance = None
        def __init__(self, **settings):
            super().__init__(**settings)
            FailedStream.instance = self
        def start(self): raise RuntimeError('Unavailable device')
    try:
        AudioOutput(48000, FailedStream)
    except RuntimeError:
        assert FailedStream.instance.closed
        checks['failed_start_closes_device'] = True
    else:
        raise AssertionError('Expected device failure')
    source = Path(__file__).with_name('biwn_audio_output.py')
    result = dict(status='passed', checks=checks, counters=sink.report(),
                  source=str(source.resolve()), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  scope='Injected stream and actual PCM callback assertions; no physical audibility claim.')
    receipt = Path(__file__).resolve().parents[1]/'verification/preview-audio-buffer-checks-current.json'
    receipt.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
