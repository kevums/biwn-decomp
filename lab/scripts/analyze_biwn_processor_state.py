"""Compare post-frame bytes with preserved CPU-copied processor candidates."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(data): return hashlib.sha256(data).hexdigest()

def spans(frames):
    result=[]
    for frame in frames:
        if result and frame == result[-1][1]+1: result[-1][1]=frame
        else: result.append([frame,frame])
    return result

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    source=json.loads((session/'emulator-runtime/processor-state-current.json').read_text())
    directory=Path(source['directory'])
    boot=(session/'boot-payload-68000-candidate.bin').read_bytes()[0x188:0x188+2004]
    helper=(session/'processor-programs/nextstage-helper-gpu-static-relocated.bin').read_bytes()
    main_gpu=(session/'processor-programs/nextstage-main-gpu.bin').read_bytes()
    dsp_candidate=(session/'processor-programs/nextstage-dsp.bin').read_bytes()
    runs=[]
    for mode in ('bios','hle'):
        folder=directory/mode
        with (folder/'processor-state.csv').open() as f: rows=list(csv.DictReader(f))
        gpu=(folder/'gpu-frames.bin').read_bytes(); dsp=(folder/'dsp-frames.bin').read_bytes()
        assert len(rows)==900 and len(gpu)==900*4096 and len(dsp)==900*8192
        boot_matches=[]; helper_matches=[]; best_dsp=None
        for frame in range(1,901):
            g=gpu[(frame-1)*4096:frame*4096]
            d=dsp[(frame-1)*8192:frame*8192]
            # Original CPU writes the 32-bit handshake at F03800 after copying.
            if all(a==b for i,(a,b) in enumerate(zip(boot,g[0x200:0x200+2004]))
                   if not 0x600<=i<0x604): boot_matches.append(frame)
            # Main GPU's separately captured 636-byte load overlaps the first36
            # helper bytes. Its relocated completion word is at F039EC.
            mismatches=[i for i,(a,b) in enumerate(zip(helper,g[0x258:0x258+len(helper)]))
                        if a!=b and i>=36 and not 0xf039ec<=0xf03258+i<0xf039f0]
            if not mismatches: helper_matches.append(frame)
            differences=[{'address':hex(0xf1b000+i),'candidate':f'{a:02x}','observed':f'{b:02x}'}
                         for i,(a,b) in enumerate(zip(dsp_candidate,d)) if a!=b]
            if best_dsp is None or len(differences)<best_dsp['different_bytes']:
                best_dsp={'frame':frame,'different_bytes':len(differences),'differences':differences}
        low_running=[r for r in rows if int(r['gpu_pc'],16)<0x4000 and int(r['gpu_control'],16)&1]
        low_stopped=[r for r in rows if int(r['gpu_pc'],16)<0x4000 and not(int(r['gpu_control'],16)&1)]
        first=int(low_running[0]['frame']) if low_running else None
        details={'mode':mode,'boot_copy_matching_frames_except_handshake':spans(boot_matches),
                 'helper_matching_frames_except_main_overlap_and_completion_word':spans(helper_matches),
                 'helper_bytes_compared_per_frame':len(helper)-36-4,
                 'low_gpu_pc_running_samples':len(low_running),'low_gpu_pc_stopped_samples':len(low_stopped),
                 'first_low_running_sample':low_running[0] if low_running else None,
                 'transition_samples':rows[max(0,first-3):first+1] if first else [],
                 'DSP_closest_full_candidate':best_dsp,
                 'nonzero_i2s_capture_frames':spans([int(r['frame']) for r in rows if int(r['i2s_nonzero_capture_count'])]),
                 'final_audio_pairs':int(rows[-1]['audio_pairs_total']),
                 'final_nonsilent_pairs':int(rows[-1]['audio_nonsilent_total']),
                 'prior_PC_trace_mismatch_frames':next(r for r in source['runs'] if r['mode']==mode)['prior_PC_trace_mismatch_frames']}
        if helper_matches:
            f=helper_matches[0];g=gpu[(f-1)*4096:f*4096]
            details['first_helper_match']={'frame':f,'main_GPU_overlapping_36_bytes_match':g[0x258:0x27c]==main_gpu[0x258:0x27c],
                'completion_word':g[0x9ec:0x9f0].hex(),
                'helper_excluded_ranges':['F03258..F0327B: separately loaded main GPU overlaps helper prefix',
                                          'F039EC..F039EF: completion/handshake word from static relocation report']}
        runs.append(details)
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'source_report':str(directory/'report.json'),
            'runs':runs,'candidate_sha256':{'boot_copied_2004':sha(boot),'helper_static_relocated':sha(helper),
                                           'main_GPU_636':sha(main_gpu),'DSP_4624':sha(dsp_candidate)},
            'findings':['The first low GPU PC sample at BIOS frame431 is stopped by emulator control bit0; low PC alone is not evidence of GPU execution.',
                        'BIOS first sampled low PC with GO bit set is frame439, before CPU boot wait begins at620. Frame438 samples GPU F03010 with control2081. Sub-frame cause is unknown.',
                        'HLE snapshots match2184 helper bytes after the two explicitly documented exclusions. The overlapped36bytes match the separate main GPU source at the first matching frame.',
                        'DSP whole-candidate bytes are not identical; differences are retained rather than masked as a pass.',
                        'HLE has zero nonzero I2S capture frames and zero nonsilent output pairs despite later DSP GO bit set. This does not identify the cause of silence.'],
            'limits':['Post-frame samples, not an instruction-by-instruction trace; byte matching supports loading/patching hypotheses only.',
                      'The emulator core and originals are unchanged. BIOS path remains assisted, not a physical-hardware result.',
                      'framebuffer_hash collection was disabled in this probe. Its zero CSV values are placeholders and must not be interpreted as black video.',
                      'GO bit interpretation is from the pinned emulator implementation, not a new claim of JTRM/hardware conformance.',
                      'Matching prior frame CPU/GPU/DSP PCs is a limited observer-inertness check, not proof that every side effect is unchanged.'],
            'next_probe':'Capture GPU flags/register banks and PC/control write/interrupt ordering within BIOS frames438–439; retain baseline and assisted-path labels.'}
    (directory/'coordinator-review.json').write_text(json.dumps(report,indent=2)+'\n')
    (session/'emulator-runtime/processor-state-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'report':str(session/'emulator-runtime/processor-state-review.json'),
                      'runs':[{k:v for k,v in r.items() if k in ('mode','boot_copy_matching_frames_except_handshake','helper_matching_frames_except_main_overlap_and_completion_word','low_gpu_pc_running_samples','low_gpu_pc_stopped_samples')} for r in runs]},indent=2))

if __name__=='__main__':main()
