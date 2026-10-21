"""Check long-run artifacts and request two actual local scope reviews."""
from collections import Counter
import csv
from datetime import datetime,timezone
import fcntl
import json
from pathlib import Path
import struct
import sys
import zlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,binary_tools


def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def rows(path):
    with path.open() as stream:return list(csv.DictReader(stream))


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    raw=json.loads((session/'emulator-runtime/long-audio-current.json').read_text());directory=Path(raw['directory'])
    expansion=json.loads((session/'long-observed-disassembly-summary.json').read_text())
    repair=json.loads((session/'long-observed-data-repair-summary.json').read_text())
    assert repair['instructions_total']==18306 and repair['long_stable_sampled_PCs_missing_after']==0
    assert raw['inputs_core_original_observer_unchanged'] and raw['preflight900_exact_frame_command_DSP_watch_match']
    observations=[];images=[]
    for run in raw['runs']:
        assert run['status']=='terminal' and run['exit_code']==0 and run['ring_unreadable']==0
        d=Path(run['directory'])
        for name,digest in run['artifact_sha256'].items():assert binary_tools.sha(d/name)==digest
        if run['name']=='preflight900':continue
        commands=rows(d/'audio-command-frames.csv');frames=rows(d/'audio-path-frames.csv');ram=(d/'dsp-frames.bin').read_bytes()
        counters={hex(a):dict(Counter(hex(int.from_bytes(ram[i*8192+a-0xf1b000:i*8192+a-0xf1b000+4],'big'))for i in range(621,9000)))for a in [0xf1bb04,0xf1bb08,0xf1bb0c]}
        ring_nonzero=[i+1 for i in range(621,9000)if any(ram[i*8192+0xb10:i*8192+0xb50])]
        assert not ring_nonzero and not run['command_state_changed_frames'] and not run['game_phase_watch_records']
        assert not run['post621_nonzero_capture_frames'] and run['post621_nonsilent_audio_pairs_delta']==0
        assert all(row=={**commands[621],'frame':row['frame']}for row in commands[621:])
        observations.append({'name':run['name'],'frames':9000,'sampled_game_interval':[622,9000],'sampled_game_frames':8379,
                             'ring_events_consumed':run['ring_events'],'max_events_between_frame_drains':run['max_frame_events'],'unreadable_ring_records':0,
                             'CPU_distinct_sampled_PCs':run['CPU_distinct_sampled_PCs'],'command_state_change_frames':0,'watched_game_phase_writes':0,
                             'post621_nonsilent_audio_pairs_delta':0,'nonzero_output_ring_frames':ring_nonzero,'sampled_DSP_state':counters,
                             'final_frame':frames[-1]})
        for ppm in sorted(d.glob('frame-*.ppm')):
            magic,dim,maximum,pixels=ppm.read_bytes().split(b'\n',3);width,height=map(int,dim.split());assert magic==b'P6'and maximum==b'255'and len(pixels)==width*height*3
            png=ppm.with_suffix('.png');data=png.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
            offset=8;compressed=b''
            while offset<len(data):
                length=struct.unpack('>I',data[offset:offset+4])[0];kind=data[offset+4:offset+8];block=data[offset+8:offset+8+length]
                assert zlib.crc32(kind+block)&0xffffffff==struct.unpack('>I',data[offset+8+length:offset+12+length])[0]
                if kind==b'IDAT':compressed+=block
                offset+=12+length
            decoded=zlib.decompress(compressed);assert len(decoded)==height*(width*3+1)
            assert all(decoded[y*(width*3+1)]==0 for y in range(height))
            recovered=b''.join(decoded[y*(width*3+1)+1:(y+1)*(width*3+1)]for y in range(height));assert recovered==pixels
            images.append({'PPM':str(ppm),'PNG':str(png),'PPM_sha256':binary_tools.sha(ppm),'PNG_sha256':binary_tools.sha(png),'dimensions':[width,height],'PNG_pixels_match_PPM':True})
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'coordinator_reviewed_long_original_game_audio_and_static_expansion',
            'directory':str(directory),'raw_report':str(directory/'report.json'),'observations':observations,
            'supplied_events':raw['protocol']['inputs'],'preflight900_exact_match':True,'pre_input_state_equal_through689':True,
            'difference_counts':{k:len(v)for k,v in raw['input_vs_baseline_difference_frames'].items()},
            'first_difference_frames':{k:(v[0]if v else None)for k,v in raw['input_vs_baseline_difference_frames'].items()},
            'command_difference_frames':len(raw['input_vs_baseline_command_difference_frames']),
            'visual_review':'Coordinator viewed preflight900 and input9000 captures: character/street/HUD remain visible; view/position and inventory panel changed. This does not attribute every supplied button to a game action.',
            'derived_images':images,'static_expansion':{'initial_instructions':18225,'new_instructions':81,'instructions_total':18306,'function_count':206,'new_function_entries':0,
                                                     'instruction_report':str(session/'long-observed-disassembly-summary.json'),'data_repair_report':str(session/'long-observed-data-repair-summary.json'),
                                                     'final_export':str(Path(repair['directory'])/'export'),'stable_sampled_PCs_missing_after':0},
            'checked_portable_C_components':14,
            'conclusion':'Chosen extended original-game input exploration visibly changes scene/inventory and adds observed CPU paths. Watched stream/mailbox state and zero game audio remain unchanged through9000frames. Initial stream is consistent with the earlier control loop. No absence-of-assets or complete-game reconstruction conclusion.',
            'limits':raw['protocol']['limits']+['Input effects carry over between button intervals; this is not an isolated causal test of each button.','First16postframe bytes/PC samples support boundaries, not full execution coverage, original function ABI or C equivalence.','New81Ghidra instruction starts are approximate decompiler evidence; portableC count remains14.'],
            'next_step':'Inspect newly observed UI/game-state paths and original stream-selection references; reconstruct useful routines against original instruction fixtures. Continue broader advertising evaluation.'}
    save(directory/'coordinator-review.json',report);save(ROOT/'verification/biwn-long-audio-review.json',report)
    task=('Return a JSON object only, under160words, with keys frames_each_long_run, framebuffer_difference_frames, stream_changes, new_nonzero_audio, new_static_instruction_starts, checked_C_components, limits, next_step. Preserve9000,8224,0,false,81,14. Separate original game in assisted emulator from a reconstructed build. Do not infer missing assets, every button worked, hardware correctness or full code coverage. Reviewer must identify unsupported claims in analyst using errors key, then correct them; do not claim independent verification.')
    evidence={k:report[k]for k in ['observations','difference_counts','command_difference_frames','visual_review','static_expansion','checked_portable_C_components','conclusion','limits','next_step']}
    out=ROOT/'runs'/(lab.stamp()+'-game-long-audio-review');out.mkdir()
    save(out/'protocol.json',{'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'model':lab.CONFIG['models']['advertising'],'same_weights_correlated':True,'native_chat_history':False})
    previous=[]
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':previous}),640)
            result['word_count']=len(result['text'].split());save(out/(role+'.json'),result)
            with (out/'prompts-and-responses.txt').open('a')as stream:stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            previous.append({'role':role,'text':result['text'],'word_count':result['word_count']});print(role,result['seconds'],result['word_count'],flush=True)
    local={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':previous}
    save(out/'status.json',local);save(ROOT/'verification/biwn-long-audio-local-review.json',local);print(out,flush=True)


if __name__=='__main__':main()
