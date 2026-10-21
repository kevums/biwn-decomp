"""Full raw OP GPU boundary and CPU/frame proof under normal scheduling."""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())


def equal(a,b,name):
    left,right=(a/name).read_bytes(),(b/name).read_bytes()
    assert left==right,(name,str(a),str(b))
    return dict(bytes=len(left),sha256=hashlib.sha256(left).hexdigest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-root',type=Path,required=True);args=parser.parse_args()
    folder=args.run_root.resolve();commands=read(folder/'commands.json')
    assert all(row['exit_code']==0 for row in commands)
    runs={}
    for direction in sorted({row['direction']for row in commands}):
        n=folder/(direction+'-trace');c=folder/(direction+'-C')
        native,owned=read(n/'report.json'),read(c/'report.json')
        assert native['status']==owned['status']=='completed_component_uncompared'
        assert native['frames']==owned['frames'] and native['warm_CPU']==owned['warm_CPU']
        assert native['core_sha256']==owned['core_sha256']
        assert native['original_CPU_instructions']==owned['original_CPU_instructions']==0
        assert native['rejected_CPU_instructions']==owned['rejected_CPU_instructions']==0
        assert native['owned_CPU_instructions']==owned['owned_CPU_instructions']
        assert native['fixed_C_instruction_steps']==owned['fixed_C_instruction_steps']
        ns,cs=n/'OP-GPU-slices',c/'OP-GPU-slices';nr,cr=read(ns/'report.json'),read(cs/'report.json')
        assert nr['status']==cr['status']=='completed_uncompared' and not nr['errors'] and not cr['errors']
        assert nr['calls']==cr['calls']>0 and not nr['pending'] and not cr['pending']
        source_instructions=0
        for a,b in zip(nr['records'],cr['records']):
            for key in ['index','cycles','before_PC','after_PC','before_GPU_sha256','after_GPU_sha256']:assert a[key]==b[key],(direction,key,a['index'])
            assert b['original_opcode_delta']==0 and b['C_status']==0
            source_instructions+=b['C_source_instructions']
            for phase in ['before','after']:equal(ns,cs,f'{a["index"]:06d}-{phase}.bin')
        files={name:equal(n,c,name)for name in ['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin']}
        runs[direction]=dict(frames=len(owned['frames']),CPU_owned_instructions=owned['owned_CPU_instructions'],
                             CPU_fixed_C_calls=owned['fixed_C_instruction_steps'],HLE_stub_RTS_count=owned['HLE_stub_RTS_count'],
                             OP_releases=cr['calls'],OP_C_source_instructions=source_instructions,
                             OP_original_GPU_opcodes=0,all_raw_OP_GPU_states_and_CPU_frame_bytes_match=True,
                             all_audio_samples_silent=owned['audio']['nonzero_samples']==0,
                             artifacts=files,sources={'reference':str(n),'C':str(c)})
    out=ROOT/'verification/frame-CPU-OP-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='normal_frame_C_CPU_and_OP_GPU_releases_match_original',directory=str(out),run_root=str(folder),runs=runs,
                original_warm_startup=True,original_regular_GPU_and_DSP=True,new_training=False,coordinator_authored_integration=True,
                whole_game_complete=False,native_Chat_latest_verified=False,
                limits=['CPU-owned window after original600frame startup. Only OP-triggered GPU releases replaced; regular GPU/DSP/IRQ/HLE providers remain.',
                        'Default unit-cost GPU profile; retained CPU prefetch words and OP release ending on branch reject.',
                        'RawGPU microstate and complete serialized machine equality scoped to these runs; physical display/timing, natural audio and standalone C game unfinished.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/frame-CPU-OP-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)


if __name__=='__main__':main()
