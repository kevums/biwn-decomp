"""Review complete ordinary-pad discovery and freeze its actual input schedule."""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--target',type=int,required=True);args=parser.parse_args()
    job_path=ROOT/f'verification/normal-route-{args.target}-navigation-job.json'
    job=json.loads(job_path.read_text());out=Path(job['directory']);path=out/'report.json'
    report=json.loads(path.read_text());frames=report['frames'];change=report['scene_change_frame']
    assert report['status']=='terminal_fresh_libretro_CD_probe' and report['loaded']
    assert not report['source_C_execution'] and not report['captured_state_input'] and not report['host_CPU_or_GPU_register_seed']
    assert report['normal_input_only'] and not report['diagnostic_switches_set']
    assert len(frames)==report['executed_frames']==frames[-1]['frame']
    assert [f['frame']for f in frames]==list(range(1,len(frames)+1))
    assert frames[-1]['scene_word']==args.target and frames[-1]['player_mode_word']==2
    assert frames[-1]['frame']==change+report['stop_after_scene_change_frames']
    windows=[];counts={};ids={'U':4,'D':5,'L':6,'R':7,'A':8,'B':0,'C':1,'OPTION':3,'PAUSE':2}
    for row in frames:
        nav=row.get('navigation');buttons=sorted(nav['buttons'])if nav else[]
        assert not nav or nav['no_guest_memory_writes']
        for button in buttons:counts[str(ids[button])]=counts.get(str(ids[button]),0)+1
        if not buttons:continue
        if windows and windows[-1]['stop_frame']==row['frame']and windows[-1]['buttons']==buttons:
            windows[-1]['stop_frame']+=1
        else:windows.append(dict(start_frame=row['frame'],stop_frame=row['frame']+1,buttons=buttons))
    assert counts==report['pressed_input_samples']
    fixed=ROOT/f'verification/scene{args.target}-global-fixed-input.json'
    schedule=dict(windows=windows,source=str(path),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scope='Frozen actual normal pad inputs; not memory state or reconstructed-C proof.')
    fixed.write_text(json.dumps(schedule,indent=2)+'\n')
    checkpoint=out/f'checkpoint-{change:08d}'/'report.json';cp=json.loads(checkpoint.read_text())
    assert cp['original_processors_only'] and cp['source_frame']==change
    result=dict(status=f'original_normal_pad_scene{args.target}_reached',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),frames=len(frames),scene_change_frame=change,final_scene=args.target,final_player_mode=2,pressed_input_samples=counts,fixed_schedule=str(fixed),fixed_replay_verified=False,checkpoint=str(checkpoint),source_C_execution_verified=False,boot_completion_proven=report['boot_completion_proven'],whole_game_complete=False,scope=f'Fresh HLE boot plus normal controller navigation toscene{args.target}; originalCPU/GPU/DSP/IRQ/HLE/devices. Source probe leaves boot_completion_proven false; observed loaded interior is the claim. No guest writes, full-game or physical-hardware proof.',PNG=str(out/'original-emulator-final-frame.png'))
    (ROOT/f'verification/normal-route-{args.target}-navigation-review.json').write_text(json.dumps(result,indent=2)+'\n')
    job.update(status='terminal_completed_verified_report',review=str(ROOT/f'verification/normal-route-{args.target}-navigation-review.json'))
    job_path.write_text(json.dumps(job,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
