"""Compare controlled prefixes at frame and observed RAM-change boundaries."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FIELDS=['actor0_type','actor0_X','actor0_Z','actor0_state','actor1_type','actor1_X','actor1_Z','actor1_state','player_X','player_Z','yaw_byte_49cba','elapsed_ticks_4c24c']
DTYPE=np.dtype({'names':['frame','PC','previous_PC','previous_frame','ordinal','before','after','mode','floor','scene','tick','opcode','valid'],
    'formats':['<u4','<u4','<u4','<u4','<u8',('<u4',(12,)),('<u4',(12,)),'<u4','<u4','<u4','<u4','<u2','<u2'],
    'offsets':[0,4,8,12,16,104,152,200,204,208,212,216,218],'itemsize':224})


def series(array,index):
    result=[]
    for row in array:
        if row['before'][index]==row['after'][index] or row['mode']!=1:continue
        if index<8:
            actor_type_index=0 if index<4 else 4
            if row['after'][actor_type_index]!=64:continue
        result.append(dict(frame=int(row['frame']),value=int(row['after'][index]),
            previous_CPU_PC=hex(int(row['previous_PC'])),next_CPU_PC=hex(int(row['PC'])),
            previous_opcode=hex(int(row['opcode'])),opcode_in_RAM=bool(row['valid']),
            tick=int(row['tick']),ordinal=int(row['ordinal'])))
    return result


def first_difference(left,right,keys):
    for index,(a,b)in enumerate(zip(left,right)):
        if any(a[key]!=b[key]for key in keys):return dict(index=index,reference=a,candidate=b)
    if len(left)!=len(right):return dict(index=min(len(left),len(right)),length_difference=True)
    return None


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--proof',type=Path,default=ROOT/'verification/native-cadence-controls-current.json');args=parser.parse_args()
    proof=json.loads(args.proof.read_text());out=Path(proof['directory'])
    reports={lane:json.loads((out/lane/'report.json').read_text())['frames']for lane in proof['lanes']}
    reference=reports['reference'];frame_fields=['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word','video_sha256']
    arrays={lane:np.memmap(out/lane/'gameplay-events.bin',mode='r',dtype=DTYPE)for lane in reports}
    frame_comparison={}
    for lane,rows in reports.items():
        assert len(rows)==len(reference)==proof['frames']
        different={field:[a['frame']for a,b in zip(reference,rows)if a[field]!=b[field]]for field in frame_fields}
        sampled=[(a,b)for a,b in zip(reference,rows)if'active_actor_snapshot'in a]
        frame_comparison[lane]=dict(different_counts={key:len(value)for key,value in different.items()},
            first_differences={key:(value[0]if value else None)for key,value in different.items()},
            actor_samples=len(sampled),actor_sample_differences=sum(a['active_actor_snapshot']!=b['active_actor_snapshot']for a,b in sampled))
    change_comparison={}
    for index in [1,2,5,6,8,9,10,11]:
        streams={lane:series(array,index)for lane,array in arrays.items()}
        change_comparison[FIELDS[index]]=dict(counts={lane:len(value)for lane,value in streams.items()},comparisons={})
        for lane in ['heap_only','startup_layout','native']:
            left,right=streams['reference'],streams[lane]
            change_comparison[FIELDS[index]]['comparisons'][lane]=dict(
                first_value_or_writer_difference=first_difference(left,right,['value','previous_CPU_PC']),
                first_frame_or_value_difference=first_difference(left,right,['frame','value','previous_CPU_PC']),
                common_prefix_values_equal=all(a['value']==b['value']for a,b in zip(left,right)))
        for lane,stream in streams.items():
            (out/(lane+'-'+FIELDS[index]+'-changes.json')).write_text(json.dumps(stream,indent=2)+'\n')
    result=dict(status='terminal_controlled_cadence_observations_classified_causality_review_pending',
        recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source_proof=str(args.proof),frames=proof['frames'],
        frame_comparison=frame_comparison,change_comparison=change_comparison,
        scope='Same-core fresh four-arm observations. Actor changes filtered to world mode1/type64; player/timestep changes filtered to world mode1. Previous CPU PC is a writer candidate, not a traced bus write; inspect its opcode/operands before attributing a change. Common prefix equality is not full stream equality if lengths differ. No hardware or whole-game claim.')
    (out/'cadence-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    pointer=ROOT/('verification/native-cadence-movement-analysis-current.json'if proof.get('pad_input')!='none'else'verification/native-cadence-analysis-current.json')
    pointer.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(frame_comparison,indent=2))
    for field,row in change_comparison.items():
        print(field,'counts',row['counts'])
        for lane,data in row['comparisons'].items():
            first=data['first_value_or_writer_difference']
            print(lane,'first value/writer difference',first)


if __name__=='__main__':main()
