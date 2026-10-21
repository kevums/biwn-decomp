"""Record code/stream provenance and run two actual local review roles."""
from collections import Counter
import csv
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import binary_tools
import lab


def save(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    candidate=session/'nextstage-68000-candidate.bin'; image=candidate.read_bytes()
    assert binary_tools.sha(candidate)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    checks=json.loads((ROOT/'verification/biwn-dsp-startup-checks.json').read_text())
    assert checks['completed_CPU_cases']==96 and checks['host_guard_cases']==19
    out=session/('dsp-startup-'+lab.stamp());out.mkdir()
    payload=image[0x7248-0x4000:0x8458-0x4000]
    command_raw=json.loads((session/'emulator-runtime/audio-commands-current.json').read_text())
    command_folder=Path(command_raw['directory'])/'baseline'
    stream=image[0x3bce0-0x4000:0x3bd80-0x4000]
    words=[int.from_bytes(stream[i:i+4],'big') for i in range(0,len(stream),4)]
    rows=list(csv.DictReader((command_folder/'audio-command-frames.csv').open()))
    assert all([int(row[f'ram_{0x3bce0+i*4:06x}'],16) for i in range(40)]==words for row in rows[621:])
    watches=list(csv.DictReader((command_folder/'audio-watch-events.csv').open()))
    gpu=[e for e in watches if e['who']=='3']
    assert len(gpu)==40 and all(e['frame']=='483' for e in gpu)
    assert {int(e['addr'],16):int(e['value'],16) for e in gpu}=={0x3bce0+i*4:value for i,value in enumerate(words)}
    references=[]
    for address in [0xf1badc,0xf1bae0,0xf1bae4,0x3bce0,0x3bd04,0xe942,0xe96c,0xe9ec,0xea08]:
        hits=[];position=0;needle=address.to_bytes(4,'big')
        while (position:=image.find(needle,position))>=0:
            hits.append(hex(position+0x4000));position+=1
        references.append({'value':hex(address),'big_endian32_occurrences':hits})
    decodes=[]
    for start,end in [(0x30,0x148),(0x148,0x1ca),(0x7a8,0x82e),(0x9a2,0x9d8)]:
        ins,decoder=binary_tools.jaguar_instructions(payload[start:end],0xf1b000+start,'dsp')
        decodes.append({'interval':[hex(0xf1b000+start),hex(0xf1b000+end)],'instructions':ins,'decoder':decoder})
    save(out/'DSP-reviewed-decodes.json',decodes)
    raw=json.loads((session/'emulator-runtime/audio-path-current.json').read_text())
    observations=[]
    wanted=['f1b7a8','f1b7d0','f1b9a2','f1b9be','f1b81c']
    for run in raw['runs']:
        directory=Path(run['directory']); ram=(directory/'dsp-frames.bin').read_bytes()
        counters={hex(a):dict(Counter(hex(int.from_bytes(ram[i*8192+a-0xf1b000:i*8192+a-0xf1b000+4],'big')) for i in range(621,900))) for a in [0xf1bb04,0xf1bb08,0xf1bb0c]}
        windows=[];counts=Counter()
        for row in csv.reader((directory/'dsp-history.csv').open()):
            if int(row[0])<622:continue
            pcs=row[2:];counts.update(p for p in pcs if p in wanted)
            if 'f1b9a2' in pcs:
                index=pcs.index('f1b9a2');start=next((i for i,p in enumerate(pcs[:index]) if p=='f1b7a8'),max(0,index-50))
                windows.append({'frame':int(row[0]),'chronological_PC_window':pcs[start:index+21]})
        assert all(counts[p]>0 for p in wanted)
        latest=ram[-8192:]
        assert latest[0x10:0xadc]==payload[0x10:0xadc]
        assert int.from_bytes(latest[0xcfc:0xd00],'big')==0xf1b9a2
        observations.append({'name':run['name'],'sampled_frames':[622,900],'sampled_state_values':counters,
                             'PC_occurrences_in_last1024_postframe_windows':dict(counts),'sequence_handler_windows':windows,
                             'DSP_bytes_10_to_ADC_match_original_payload':True,
                             'vector_padding_8_to_10_initial':payload[8:16].hex(),'vector_padding_8_to_10_frame900':latest[8:16].hex()})
    # Exact unsigned arithmetic for the observed handler's r6 transformations.
    command=words[10]; assert command==0x7fffff01
    shifted=(command<<4)&0xffffffff
    signed=shifted if shifted<0x80000000 else shifted-0x100000000
    offset=(signed>>12)<<3
    assert offset==-8 and (command>>28)&1 and command&15==1
    selected=0x3bce0+32
    pointer=words[8];after_command=pointer+8;target=after_command+offset
    assert pointer==target==0x3bd04 and words[9]==0
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'coordinator_reviewed_initial_stream_loop_and_CPU_startup',
            'directory':str(out),'candidate_sha256':binary_tools.sha(candidate),'CPU_comparison':checks,
            'initial_stream':{'address':'0x3bce0','bytes':len(stream),'sha256':__import__('hashlib').sha256(stream).hexdigest(),
                              'word_values':{hex(0x3bce0+i*4):hex(value) for i,value in enumerate(words)},
                              'GPU_stream_population_at483':{'records':40,'values_match_candidate':True,'recorded_PCs':['0xf03112','0xf0311c']},
                              'all279_game_phase_postframe_stream_samples_match_candidate':True},
            'DSP_command2_static_path':{'copy_source':'0x3bd10','copy_destination':'0xf1be00','copy_bytes':8,'source_bytes':'0000000000000000',
                                        'stored_at_F1BB0C':'0x3bd04','argument0_selected_pointer_address':hex(selected),'stored_at_F1BB08':hex(pointer),
                                        'source':'Original DSP bytes F1B0A4..F1B0F8; static interpretation cross-checked against captured DSP state. Not standalone DSP equivalence.'},
            'observed_sequence_handler':{'input_timestamp_address':'0x3bd04','timestamp':0,'control_word_address':'0x3bd08','control_word':hex(command),
                                         'dispatch_top3bits':command>>29,'dispatch_table_entry':'0xf1bcfc','dispatch_target':'0xf1b9a2',
                                         'low_nibble':command&15,'bit28':(command>>28)&1,'signed_relative_offset_bytes':offset,
                                         'pointer_after_command':hex(after_command),'branch_target_pointer':hex(target),'reloaded_counter':0,
                                         'executed_branch':'F1B9AA→F1B9B6; no decrement atF1B9AE..F1B9B4. Returns throughF1B81C with counter0 and pointer3BD04.',
                                         'interpretation':'Observed initial stream repeatedly follows this control loop rather than requesting a voice in the sampled handler windows. Counter0 alone is not proof that timer/sequencer execution stopped.'},
            'observations':observations,'literal_scan':references,
            'limits':['Last1024PC windows are sampled, not a complete execution log or event frequency measurement.',
                      'Literal-value scans include data and miss indirect/computed/short-address references; absence of literalE9EC references does not prove it unused.',
                      'Runtime vector padding8..F differs from original and must not be linearly treated as unchanged code.',
                      'No hardware timing decision, core fix, missing-audio-assets conclusion, exhaustive gameplay test or reconstructed-game validation.'],
            'next_step':'Find alternate stream selection/updates or game actions that replace the initial loop; continue reconstructing original event/voice dispatch with explicit CPU/DSP checks.'}
    save(out/'report.json',report);save(ROOT/'verification/biwn-dsp-startup-review.json',report)
    task=('Return a JSON object only, under180words, with keys copy_count_actual, zero_length_copy_count, mailbox_clear_condition, stream_loop_observation, limits, next_test. Use only supplied evidence. Actual CPU table length4624 copies1156longwords. Zero length copies65536 because of ASR/SUBQ/16bitDBRA. Mailbox requires exactlyzero. Initial stream control7fffff01 takes relative-minus8 branch to3BD04 and reloads counter0; observed handler PCs show execution. Never equate counter0 with stopped timer. Do not infer no sound assets or correct hardware timing. Reviewer must identify errors in analyst using an extra errors key, then supply a corrected object; do not merely copy.')
    evidence={'CPU_summary':{k:checks[k] for k in ['actual_payload','completed_CPU_cases','host_guard_cases','matched','excluded']},
              'initial_stream':report['initial_stream'],'observed_sequence_handler':report['observed_sequence_handler'],
              'PC_occurrences':[{'name':o['name'],'counts':o['PC_occurrences_in_last1024_postframe_windows']} for o in observations],
              'limits':report['limits'],'next_step':report['next_step']}
    run=ROOT/'runs'/(lab.stamp()+'-game-dsp-startup-review');run.mkdir()
    save(run/'protocol.json',{'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'model':lab.CONFIG['models']['advertising'],
                              'native_chat_history':False,'same_weights_correlated':True})
    previous=[]
    with (ROOT/'runs/.inference.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':previous}),640)
            result['word_count']=len(result['text'].split());save(run/(role+'.json'),result)
            with (run/'prompts-and-responses.txt').open('a') as stream:
                stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            previous.append({'role':role,'text':result['text'],'word_count':result['word_count']})
            print(role,result['seconds'],result['word_count'],flush=True)
    local={'recorded_at':datetime.now(timezone.utc).isoformat(),'directory':str(run),'status':'completed_pending_coordinator_review','roles':previous}
    save(run/'status.json',local);save(ROOT/'verification/biwn-dsp-startup-local-review.json',local)
    print(run,flush=True)


if __name__=='__main__':main()
