"""Render matching live host-buffer layout without assuming allocation width."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--stage', choices=['startup', 'world'], default='world')
    parser.add_argument('--mode', choices=['native', 'C'], default='C')
    args = parser.parse_args()
    stem = args.run / (args.mode + '-' + args.stage + '-framebuffer')
    metadata = json.loads(stem.with_suffix('.json').read_text())
    raw = stem.with_suffix('.bin').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == metadata['sha256']
    pitch = metadata['screen_pitch_pixels']
    width, height = metadata['tom_width'], metadata['tom_height']
    assert 0 < width <= pitch and 0 < height <= 512 and pitch * height * 4 <= len(raw), metadata
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            offset = 4 * (y * pitch + x)
            rows.extend(raw[offset:offset + 3][::-1])
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))
    path = stem.with_suffix('.png')
    path.write_bytes(png)
    print(path)


if __name__ == '__main__':
    main()
