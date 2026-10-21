"""Lossless RGB animations from checked C CRY16 frames, nominal source times.

Run using the bundled workspace Python/Pillow runtime. Pinned CRY lookup
tables define RGB conversion; no physical display calibration or game audio.
"""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sha=lambda data:hashlib.sha256(data).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text());directory=Path(proof['directory']);assert json.loads((directory/'status.json').read_text())['status']=='terminal_pass'
    rows=json.loads((directory/'frames.json').read_text());assert len(rows)==763
    table_path=ROOT/'tools/pinned-CRY-color-tables.json';assert sha(table_path.read_bytes())=='a20c8fedd516b611d546f1abe04a0b1f59fdf7a2662556b1306cb5e4da49b181'
    tables=json.loads(table_path.read_text())['tables'];lookup=[]
    for value in range(65536):
        cyan=(value>>12)&15;red=(value>>8)&15;intensity=value&255
        lookup.append(bytes((tables[n][cyan][red]*intensity)>>8 for n in ['redcv','greencv','bluecv']))
    out=ROOT/'verification/BIWN-movie-sequence-export'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);results=[]
    for message in range(58,64):
        source=[r for r in rows if r['message_id']==message];images=[];RGB_sha=[]
        for row in source:
            p=directory/'C-frames'/f'message-{message}-frame-{row["frame"]:03d}.CRY16';data=p.read_bytes();assert len(data)==80640 and sha(data)==row['pixels_sha256']
            rgb=b''.join(lookup[(data[i]<<8)|data[i+1]] for i in range(0,len(data),2));RGB_sha.append(sha(rgb));images.append(Image.frombytes('RGB',(224,180),rgb))
        # Source CTAB time scale600, these sample durations40: nominal15fps.
        # Cumulative rounding yields alternating66/67ms without time drift.
        times=[round((r['source']['time']&0x7fffffff)*1000/600) for r in source]
        assert times==[round(i*1000/15) for i in range(len(source))]
        assert all(r['source']['duration']==40 for r in source)
        final=round(len(source)*1000/15);durations=[b-a for a,b in zip(times,times[1:]+[final])]
        target=ROOT/'verified-previews'/f'C-movie-message-{message}-sequence.webp'
        images[0].save(target,format='WEBP',save_all=True,append_images=images[1:],duration=durations,loop=0,lossless=True,method=4,exact=True)
        with Image.open(target) as reader:
            decoded=[]
            for i in range(reader.n_frames):
                reader.seek(i);rgb=reader.convert('RGB').tobytes();decoded.append(dict(start_ms=reader.info['timestamp'],duration_ms=reader.info['duration'],RGB_sha256=sha(rgb)))
        assert decoded[0]['start_ms']==0 and decoded[-1]['start_ms']+decoded[-1]['duration_ms']==final
        for start,digest in zip(times,RGB_sha):
            found=next(x for x in decoded if x['start_ms']<=start<x['start_ms']+x['duration_ms']);assert found['RGB_sha256']==digest
        result=dict(message_id=message,source_frames=len(source),encoded_frames=len(decoded),duration_ms=final,source_nominal_Hz=15,physical_timing_verified=False,
            width=224,height=180,path=str(target),sha256=sha(target.read_bytes()),bytes=target.stat().st_size,
            decoded_RGB_and_timing_match_all_source_frames=True,lossless_RGB=True,audio_included=False,
            source_RGB_sha256=RGB_sha,encoded_frame_timeline=decoded)
        results.append(result);save(out/'clips.json',results);print(json.dumps({k:result[k] for k in ['message_id','source_frames','encoded_frames','duration_ms','bytes']}),flush=True)
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='six_C_movie_video_previews_exported_and_decode_roundtrip_checked',directory=str(out),clips=results,total_source_frames=763,
        source_report_sha256=sha((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_bytes()),script_sha256=sha(Path(__file__).read_bytes()),
        limits=['Nominal source timescale600/duration40 preview timing, not measured physical playback. Silent lossless RGB conversion using pinned emulator CRY tables; raw CRY/native comparison is primary.',
                'No full movie controller/firmware streaming, audio synchronization or playable game claim.'])
    save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-sequence-export.json',report);print(json.dumps(dict(directory=str(out),clips=6,frames=763)))

if __name__=='__main__':main()
