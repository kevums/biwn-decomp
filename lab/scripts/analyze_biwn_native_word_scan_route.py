"""Classify real transitions; include the state before the first return input."""
from pathlib import Path
from datetime import datetime,timezone
import json
from run_biwn_native_fast_gameplay_route import ROOT,save,sha


def main():
    pp=ROOT/'verification/native-word-scan-route-current.json';protocol=json.loads(pp.read_text());out=Path(protocol['directory']);results={}
    for lane in protocol['lanes']:
        path=out/lane/'report.json';report=json.loads(path.read_text());assert sha(path)==protocol['results'][lane]['report_sha256'];rows=report['frames'];return_index=next((i for i,x in enumerate(rows)if(x.get('navigation')or{}).get('return_started')),None)
        changes=[];previous=rows[return_index-1]if return_index is not None and return_index else None
        if return_index is not None:
            for x in rows[return_index:]:
                if previous is not None and x['floor_word']!=previous['floor_word']:changes.append(dict(frame=x['frame'],from_floor=previous['floor_word'],to_floor=x['floor_word'],mode=x['player_mode_word'],scene=x['scene_word']))
                previous=x
        pre=rows[return_index-1]if return_index else None;last=rows[-1];pairs={(x['from_floor'],x['to_floor'])for x in changes};nav=last.get('navigation')or{}
        results[lane]=dict(**protocol['results'][lane]);results[lane].update(return_pre_state=({k:pre[k]for k in ['frame','raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']}if pre else None),observed_floor_transitions=changes,continuous_merchant_to_outdoor=bool(protocol['results'][lane]['merchant_reached']and(2,1)in pairs and(1,0)in pairs and protocol['results'][lane]['completed_outdoor_hold']),source_report_sha256=sha(path),last_outdoor_hold=nav.get('outdoor_hold',0))
        # Diagnose first repaired-original stopping at the portal boundary.
        if lane=='original_repaired':
            transitions=[];prior=None
            for x in rows[return_index or 0:]:
                key=(x['player_mode_word'],x['floor_word'],x['scene_word'])
                if key!=prior:transitions.append(dict(frame=x['frame'],mode=key[0],floor=key[1],scene=key[2],X=x['raw_player_X'],Z=x['raw_player_Z']));prior=key
            results[lane]['post_return_mode_transition_count']=len(transitions);results[lane]['last12mode_transitions']=transitions[-12:]
    result=dict(status='terminal_four_arm_word_scan_routes_semantically_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),source_protocol=str(pp),source_protocol_sha256=sha(pp),directory=str(out),results=results,classifier_correction='First runner required floor2in post-input snapshots, but firstDown can change floor2to1within that same frame. Correct analysis uses the immediately preceding floor2state and observed2→1→0transitions; original falseclassifications retained in protocol.',known_scan_read_limit='Existing repair still permits some reads across the32Kwindow bound; payload/run-end rejection is tested separately.',source_sha256={str(Path(__file__)):sha(__file__)},scope='Four fresh lanes, identical feedback policy. Native repaired completes fullreturn+120outdoorhold. Original repaired reaches outdoor near the finitecutoff, leaving only53holdframes; its120framehold is unproven, not a verified instability or repeated portal oscillation. Unmodified original/native do not complete firstdescent by finitecutoff. No fullgame/hardware/equivalence claim.')
    save(out/'semantic-analysis.json',result);save(ROOT/'verification/native-word-scan-route-analysis-current.json',result)
    for lane,row in results.items():print(lane,'continuous',row['continuous_merchant_to_outdoor'],'transitions',row['observed_floor_transitions'],'end',row['final_fields'],'hold',row['last_outdoor_hold'])
    print('Repaired original lastmode transitions',results['original_repaired']['last12mode_transitions'])
if __name__=='__main__':main()
