"""Compute scoped audio observations, then request actual local analysis/review."""
from collections import Counter
import csv
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
import binary_tools


def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    raw=json.loads((session/'emulator-runtime/audio-path-current.json').read_text())
    folder=Path(raw['directory'])
    observations=[]
    for run in raw['runs']:
        d=Path(run['directory'])
        frames=list(csv.DictReader((d/'audio-path-frames.csv').open()))
        data=(d/'dsp-frames.bin').read_bytes()
        counts=Counter();values=Counter();writers=Counter();control=[];audio_records=0
        for event in csv.DictReader((d/'audio-watch-events.csv').open()):
            addr=int(event['addr'],16)
            if addr<0xf1a148:
                control.append(event)
            if int(event['frame'])<622 or addr not in (0xf1a148,0xf1a14a,0xf1a14c,0xf1a14e):continue
            assert event['type']=='12'
            audio_records+=1;counts[event['addr']]+=1;values[event['value']]+=1
            writers[(event['who'],event['pc'])]+=1
        latest=data[-8192:]
        row={'name':run['name'],'frames':900,'game_phase_interval':[622,900],
             'prior_CPU_GPU_DSP_samples_match_all_900':not run['baseline_mismatch_frames'],
             'post622_output_register_write_records':audio_records,
             'post622_records_by_address':dict(counts), 'post622_record_values':dict(values),
             'post622_record_writer_PC':[{'who':who,'recorded_pc':pc,'records':n} for (who,pc),n in writers.items()],
             'post622_nonzero_output_or_capture_frames':[int(f['frame']) for f in frames[621:] if int(f['left'],16) or int(f['right'],16) or int(f['i2s_nonzero_capture_count'])],
             'post622_output_ring_nonzero_frames':[i+1 for i in range(621,900) if any(data[i*8192+0xb10:i*8192+0xb50])],
             'frame900_mixer_gain':hex(int.from_bytes(latest[0xb00:0xb04],'big')),
             'frame900_dispatch_table_minus4':hex(int.from_bytes(latest[0xb50:0xb54],'big')),
             'frame900_dispatch_table_zero':hex(int.from_bytes(latest[0xb54:0xb58],'big')),
             'frame900_observed_dispatch_words':[{'address':hex(a),'word':hex(int.from_bytes(latest[a-0xf1b000:a-0xf1b000+4],'big'))} for a in (0xf1bd10,0xf1bd60,0xf1bdb0,0xf1be00)],
             'final_frame':frames[-1], 'control_write_records':control,
             'ring_unreadable':run['ring_unreadable']}
        assert audio_records and set(values)=={'00000000'}
        assert not row['post622_nonzero_output_or_capture_frames']
        assert not row['post622_output_ring_nonzero_frames']
        observations.append(row)
    decodes=[]
    first=Path(raw['runs'][0]['directory'])
    latest=(first/'dsp-frames.bin').read_bytes()[-8192:]
    for address,length in [(0xf1b1ca,86),(0xf1b77a,46)]:
        instructions,decoder=binary_tools.jaguar_instructions(latest[address-0xf1b000:address-0xf1b000+length],address,'dsp')
        decodes.append({'address':hex(address),'instructions':instructions,'decoder':decoder})
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'coordinator_reviewed_zero_output_path',
            'raw_report':str(folder/'report.json'),'directory':str(folder),'observations':observations,
            'instructions':decodes,'inputs_and_core_unchanged':raw['inputs_and_core_unchanged'],
            'conclusion':'Game DSP executes and issues zero-valued writes to both output words while output ring is zero in every sampled frame622..900. This narrows investigation to mixer/command/input state rather than only downstream resampling. It does not prove a root cause, missing game content, audible quality, or hardware correctness.',
            'interpretation':'At frame900 dispatch words -4,-4,-4,0 select skip targetF1B1DC three times and finish targetF1B1E2. Accumulators start at0 atF1B1CC/1CE; this observed empty work path is consistent with zero mixer output. No general voice-count or command-format conclusion.',
            'caveats':raw['protocol']['limits']+[
                'DSP trace record PCs are advanced: writes recorded atF1B790/F1B79A correspond to store instructionsF1B78E/F1B798; each32bit write yields two16bit bus records. Do not count those as independent stereo sample pairs.',
                'Only observed622..900game-phase interval compared; BIOS startup previously had nonsilent output.',
                'The two final DSP snapshots differ atF1B00B; do not claim whole code/RAM byte identity.',
                'Exploratory linear decode atF1B1C0 started inside MOVEI immediate; retained original file but discard that row. Reviewed decode uses observedF1B1CA boundary.'],
            'next_step':'Trace CPU writes to DSP command mailboxF1BADC..F1BAE7 and mainRAM stream3BCE0..3BD7F while testing game buttons; distinguish absence of requested sounds from failed command consumption.'}
    save(folder/'coordinator-review.json',report)
    save(ROOT/'verification/biwn-audio-path-review.json',report)
    task=('In under160words, analyze this measured zero-output DSP path. Distinguish records from complete sample pairs, static interpretation from observed execution, and running DSP from stalled output generation. Do not claim a root cause or missing audio assets. Identify a bounded next experiment for the CPU command mailbox/stream. No core fixes or new guest-state writes. Reviewer must identify unsupported assertions in the prior draft; do not merely copy it.')
    out=ROOT/'runs'/f'{lab.stamp()}-game-audio-path-review';out.mkdir()
    evidence={k:v for k,v in report.items() if k!='instructions'}
    # Keep only game-phase facts and concise initialization controls in prompt.
    for row in evidence['observations']:
        row['control_write_records']=[e for e in row['control_write_records'] if int(e['frame'])>=620]
    evidence['instructions']=decodes
    save(out/'protocol.json',{'task':task,'source_evidence':evidence,'roles':['analyst','reviewer'],'model':lab.CONFIG['models']['advertising'],'same_weights_correlated':True,'native_chat_history':False})
    previous=[]
    with (ROOT/'runs/.inference.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'source_evidence':evidence,'previous_drafts':previous}),640)
            result['word_count']=len(result['text'].split())
            save(out/(role+'.json'),result)
            with (out/'prompts-and-responses.txt').open('a') as stream:
                stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            previous.append({'role':role,'text':result['text'],'word_count':result['word_count']})
            print(role,result['seconds'],result['word_count'],flush=True)
    save(ROOT/'verification/biwn-audio-local-review.json',{'directory':str(out),'status':'completed_pending_coordinator_review','roles':previous})
    print(out,flush=True)


if __name__=='__main__':main()
