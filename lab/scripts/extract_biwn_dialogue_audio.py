"""Bounded, image-specific FILM/CTAB/STAB extraction; no game execution.

The 738-byte phase is inferred from six matching FILM records, not a BIOS
seek witness. The source consumes STAB entries with time=FFFFFFFF as audio
at D8DA..D8E4. Preserve their bytes and boundaries without assuming timing.
"""
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path
import extract_biwn_stage as stage
from check_biwn_68000_slices import make_toc

ROOT = stage.ROOT
def sha(data): return hashlib.sha256(data).hexdigest()
def save(path, data): path.write_text(json.dumps(data, indent=2) + '\n')
def u32(data, offset): return struct.unpack_from('>I', data, offset)[0]

def main():
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    layout = json.loads((session/'cdi-layout.json').read_text())
    records = json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']
    toc = make_toc(layout)
    # Literal D50A..D524 adjustment with the declared-layout TOC fixture.
    desired = 3
    chosen = None
    for offset in range(8, len(toc), 8):
        if toc[offset+4] == 0: desired = (desired+1)&0xffff
        if toc[offset] == (desired&255): chosen = toc[offset]; break
    assert chosen == 4
    path = session/'raw-tracks/track-04-raw.bin'
    raw = path.read_bytes()
    declared = next(t for t in layout['extracted_tracks'] if t['track'] == chosen)
    assert len(raw) == declared['bytes'] and sha(raw) == declared['sha256']
    normalized = stage.swap16(raw)
    out = ROOT/'verification/BIWN-dialogue-audio-extraction'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    results = []
    for record in records:
        index = record['message_id']; offset = int(record['source_long_fields'][1],16)
        film_start = offset+738
        assert normalized[film_start:film_start+4] == b'FILM'
        header_size = u32(normalized, film_start+4)
        assert 72 <= header_size <= 0x10000
        header = normalized[film_start:film_start+header_size]
        assert len(header) == header_size and header[16:20] == b'FDSC'
        assert header[36:40] == b'ADSC' and header[56:60] == b'CTAB'
        count = u32(header,68)
        assert count > 0 and header_size == 72+16*count
        audio = bytearray(); chunks=[]; sample_records=[]; video_count=0
        for cluster in range(count):
            relative, length, time, marker = struct.unpack_from('>4I',header,72+cluster*16)
            cluster_start = film_start+header_size+relative
            payload = normalized[cluster_start:cluster_start+length]
            assert len(payload) == length and payload[:64] == struct.pack('>I',marker)*16
            assert payload[64:68] == b'STAB'
            table_size = u32(payload,68); samples = u32(payload,76)
            assert table_size == 16+16*samples and 64+table_size <= length
            chunk_audio=0
            for sample in range(samples):
                start,size,timestamp,duration=struct.unpack_from('>4I',payload,80+16*sample)
                absolute=cluster_start+64+table_size+start
                assert start+size <= length-64-table_size
                row=dict(cluster=cluster,sample=sample,normalized_track_offset=absolute,bytes=size,time=timestamp,duration=duration)
                if timestamp == 0xffffffff:
                    data=normalized[absolute:absolute+size]
                    assert len(data)==size
                    row.update(audio=True,concatenated_audio_offset=len(audio),sha256=sha(data))
                    if not chunks: (out/f'message-{index}-first-audio.bin').write_bytes(data)
                    audio.extend(data);chunks.append(row);chunk_audio+=1
                else: row['audio']=False;video_count+=1
                sample_records.append(row)
        assert chunks
        target=out/f'message-{index}-audio-bytes.bin';target.write_bytes(audio)
        assert sha(target.read_bytes()) == sha(audio)
        results.append(dict(message_id=index,declared_message_track=3,fixture_resolved_stored_track=chosen,
            message_offset=offset,FILM_normalized_track_offset=film_start,inferred_phase=738,
            header_bytes=header_size,header_sha256=sha(header),SCLK=u32(header,48),DSP_increment=u32(header,52),
            clusters=count,video_samples=video_count,audio_chunks=len(chunks),audio_bytes=len(audio),
            audio_path=str(target),audio_sha256=sha(audio),first_chunk_path=str(out/f'message-{index}-first-audio.bin'),
            audio_chunks_manifest=chunks,sample_records=sample_records))
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='static_dialogue_audio_chunks_extracted',directory=str(out),
        raw_track_sha256=sha(raw),normalized_track_sha256=sha(normalized),script_sha256=sha(Path(__file__).read_bytes()),
        declared_layout_sha256=sha((session/'cdi-layout.json').read_bytes()),TOC_fixture_hex=bytes(toc[:48]).hex(),
        messages=results,audio_bytes=sum(x['audio_bytes'] for x in results),audio_chunks=sum(x['audio_chunks'] for x in results),
        original_game_code_executed=False,C_DSP_execution_verified=False,BIOS_seek_mapping_verified=False,
        movie_streaming_verified=False,whole_game_complete=False,
        limits=['Source-format static extraction only. Track adjustment uses the declared-layout TOC fixture; no physical TOC or 738-byte BIOS seek witness.',
                'Chunk order preserved, but concatenation is not proof of scheduling, queue lifetime, wall-clock duration or in-game playback.'])
    save(out/'report.json',report);save(ROOT/'verification/BIWN-dialogue-audio-extraction.json',report)
    print(json.dumps(dict(directory=str(out),messages=len(results),audio_bytes=report['audio_bytes'],audio_chunks=report['audio_chunks'])))

if __name__=='__main__': main()
