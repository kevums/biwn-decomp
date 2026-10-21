"""Compare fast backend with retained four-arm movement observations."""
from datetime import datetime,timezone
import json
from pathlib import Path
import numpy as np
from analyze_biwn_native_cadence import DTYPE,FIELDS,series,first_difference
from run_biwn_native_gameplay_route import ROOT,save,sha
from analyze_biwn_native_gameplay_route import comparison


def main():
    path=ROOT/'verification/native-fast-movement-prefix-current.json';p=json.loads(path.read_text());out=Path(p['directory'])
    prior=json.loads(Path(p['prior_control_proof']).read_text());control=Path(prior['directory'])
    rows={lane:json.loads((control/lane/'report.json').read_text())['frames']for lane in prior['lanes']}
    rows['fast']=json.loads((out/'fast/report.json').read_text())['frames']
    arrays={lane:np.memmap(control/lane/'gameplay-events.bin',mode='r',dtype=DTYPE)for lane in prior['lanes']}
    arrays['fast']=np.memmap(out/'fast/gameplay-events.bin',mode='r',dtype=DTYPE)
    changes={}
    for index in [1,2,5,6,8,9,10,11]:
        streams={lane:series(a,index)for lane,a in arrays.items()};ref=streams['reference']
        changes[FIELDS[index]]=dict(counts={lane:len(s)for lane,s in streams.items()},comparisons={lane:dict(first_value_or_writer_difference=first_difference(ref,s,['value','previous_CPU_PC']),first_frame_or_value_difference=first_difference(ref,s,['frame','value','previous_CPU_PC']))for lane,s in streams.items()if lane!='reference'})
    result=dict(status='terminal_fast_movement_prefix_differences_classified',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source_proof=str(path),source_proof_sha256=sha(path),frame_comparison={lane:comparison(rows['reference'],v)for lane,v in rows.items()},change_comparison=changes,
        source_sha256={str(Path(__file__)):sha(__file__),str(ROOT/'scripts/analyze_biwn_native_cadence.py'):sha(ROOT/'scripts/analyze_biwn_native_cadence.py'),str(ROOT/'scripts/analyze_biwn_native_gameplay_route.py'):sha(ROOT/'scripts/analyze_biwn_native_gameplay_route.py')},
        scope='Fast fresh660frame prefix vs previous immutable same-core/pad four-arm observations; RAM changes with previous-PC writer candidates. No full-route or hardware claim; changed-value counts are not all update counts.')
    save(out/'movement-analysis.json',result);save(ROOT/'verification/native-fast-movement-analysis-current.json',result)
    print(json.dumps(result['frame_comparison']['fast'],indent=2));print('Fast yaw',changes['yaw_byte_49cba']['comparisons']['fast']);print('Fast actor0X',changes['actor0_X']['comparisons']['fast'])


if __name__=='__main__':main()
