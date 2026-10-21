"""Compare trace-free preview execution with the verified traced mail route."""
import argparse
import hashlib
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path
from biwn_live_window import framebuffer_ppm

ROOT = Path(__file__).resolve().parents[1]


def saved_PNG_RGB(path, width, height):
    png = path.read_bytes()
    assert png[:8] == b'\x89PNG\r\n\x1a\n'
    offset, compressed = 8, b''
    while offset < len(png):
        size = int.from_bytes(png[offset:offset+4], 'big')
        kind, data = png[offset+4:offset+8], png[offset+8:offset+8+size]
        offset += size+12
        if kind == b'IHDR':
            w, h, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data)
            assert (w,h,depth,color,compression,filtering,interlace) == (width,height,8,2,0,0,0)
        if kind == b'IDAT':compressed += data
    pixels = zlib.decompress(compressed)
    stride = width*3+1
    assert len(pixels) == height*stride
    # The checked frontend PNG writer uses PNG filter0 for every row.
    assert all(pixels[y*stride] == 0 for y in range(height))
    return b''.join(pixels[y*stride+1:(y+1)*stride] for y in range(height))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--C-run', type=Path, required=True)
    args = parser.parse_args()
    receipt = ROOT/'verification/C-space-mail-roundtrip-comparison-current.json'
    proof = json.loads(receipt.read_text())
    assert proof['status'] == 'CPU_GPU_frame_comparison_pass' and all(proof['checks'].values())
    reference, current = Path(proof['C_run']), args.C_run.resolve()
    a, b = [json.loads((path/'report.json').read_text()) for path in [reference, current]]
    checks = dict(candidate_completed=b['status']=='completed_component_uncompared',
        frame_CPU_RAM_video_audio=a['frames']==b['frames'],
        no_original_CPU=b['original_CPU_instructions']==0,
        no_rejected_CPU=b['rejected_CPU_instructions']==0,
        trace_files_absent=not(current/'CPU-before-instructions.bin').exists() and not(current/'retired-instruction-costs.bin').exists(),
        trace_disabled_recorded=b['instruction_trace_recorded'] is False)
    for name in ['warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']:
        checks[name] = hashlib.sha256((reference/name).read_bytes()).digest() == hashlib.sha256((current/name).read_bytes()).digest()
    v = b['video']
    ppm = framebuffer_ppm((current/'final-video.bin').read_bytes(), v['width'], v['height'], v['pitch'])
    checks['PPM_pixels_match_verified_PNG'] = ppm.split(b'\n',3)[3] == saved_PNG_RGB(reference/'final-frame.png', v['width'], v['height'])
    assert all(checks.values()), checks
    result = dict(status='source_preview_trace_off_and_pixel_conversion_verified',
        recorded_at=datetime.now(timezone.utc).isoformat(), frames=len(b['frames']),
        CPU_instructions=b['owned_CPU_instructions'], checks=checks, current=str(current),
        verified_comparison=str(receipt),
        scope='Same200frame scripted mail route, CPU disk traces disabled only. All frameCPU/RAM/video/audio and final machine/PCM match tracedC; final preview PPM matches independently decoded checked PNG. No live keyboard/window interaction verified; originalDSP/IRQ/HLE/devices remain.')
    (ROOT/'verification/interactive-preview-backend-current.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':main()
