"""Run the lab PC observer and relate sampled addresses to the static export."""
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import extract_biwn_stage as stage


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    core = root / 'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    binary = root / 'tools/biwn-runtime-pc-probe'
    image = root / 'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios = root / 'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    before = {str(p):stage.cdi_layout.sha(p) for p in [core, binary, image, bios]}
    if before[str(image)] != stage.IMAGE_SHA:
        raise ValueError('Preserved CDI changed')
    captured = (session / 'nextstage-68000-candidate.bin').read_bytes()
    if stage.digest(captured) != stage.STAGE_SHA:
        raise ValueError('Static candidate changed')
    manifest = json.loads((session / 'nextstage-divu-export/manifest.json').read_text())
    entries = {int(f['address'],16): f for f in manifest['functions']}
    instructions = {int(i['address'],16): i for i in manifest['instructions']}
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = session / 'emulator-runtime' / ('pc-observer-' + stamp)
    inputs = output / 'inputs'
    inputs.mkdir(parents=True)
    (inputs / image.name).symlink_to(image)
    (inputs / 'jaguarcd_bios.bin').symlink_to(bios)
    env = os.environ.copy()
    env.update(VJ_EXPECT_BUILD='unknown', VJ_HARNESS_LOG_INFO='1')
    runs=[]
    events=['360:up:90','480:left:45','570:a:10','630:up:90']
    for name,mode,presses in [('bios','bios',[]),('hle','hle',[]),('hle-input','hle',events)]:
        cwd=output/name;cwd.mkdir()
        command=[str(binary),str(core),str(inputs/image.name),'--frames','900','--system-dir',str(inputs),
                 '--option','virtualjaguar_cd_boot_mode='+mode,
                 '--option','virtualjaguar_usefastblitter=enabled',
                 '--option','virtualjaguar_crash_detect=enabled']
        if mode=='bios':command.append('--bios')
        for event in presses:command+=['--press',event]
        run={'name':name,'command':command,'cwd':str(cwd),'started_at':datetime.now(timezone.utc).isoformat(),'input_events':presses}
        start=time.monotonic()
        with (cwd/'run.log').open('w') as log:
            process=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            run.update(pid=process.pid,status='running')
            (cwd/'status.json').write_text(json.dumps(run,indent=2)+'\n')
            print(name,process.pid,flush=True)
            try:process.wait(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);process.wait()
                run['wall_budget_expired']=True
        run.update(status='terminal',exit_code=process.returncode,seconds=round(time.monotonic()-start,3))
        (cwd/'status.json').write_text(json.dumps(run,indent=2)+'\n')
        if process.returncode!=0:raise ValueError('Observer did not finish: '+str(cwd))
        with (cwd/'observed_pcs.csv').open() as stream:rows=list(csv.DictReader(stream))
        with (cwd/'frame_pcs.csv').open() as stream:frames=list(csv.DictReader(stream))
        if len(frames)!=900:raise ValueError('Incomplete frame observations')
        valid=[];hits=[]
        for row in rows:
            pc=int(row['pc'],16)
            offset=pc-0x4000
            if captured[offset:offset+16].hex()!=row['first_post_frame_bytes']:continue
            valid.append(pc)
            if pc in entries:
                hits.append({'address':hex(pc),'analyst_or_automatic_name':entries[pc]['name'],
                             'first_frame':int(row['first_frame']),'last_frame':int(row['last_frame']),
                             'first_post_frame_bytes':row['first_post_frame_bytes'],
                             'post_frame_bytes_changed':bool(int(row['post_frame_bytes_changed']))})
        run.update(frames_observed=len(frames),distinct_game_range_PCs=len(rows),
                   PCs_with_first_post_frame_bytes_matching_candidate=len(valid),
                   matching_decoded_instruction_addresses=sum(pc in instructions for pc in valid),
                   static_function_entry_addresses_observed=hits,final_frame_PCs=frames[-1],
                   artifact_sha256={p.name:stage.cdi_layout.sha(p) for p in [cwd/'observed_pcs.csv',cwd/'frame_pcs.csv',cwd/'run.log']})
        (cwd/'status.json').write_text(json.dumps(run,indent=2)+'\n')
        runs.append(run)
        print(name,'terminal',len(hits),'static entries sampled',flush=True)
    after={str(p):stage.cdi_layout.sha(p) for p in [core,binary,image,bios]}
    if after!=before:raise ValueError('Observer input/core changed')
    report={'time':datetime.now(timezone.utc).isoformat(),'runs':runs,'input_and_binary_hashes':after,
            'inputs_and_core_unchanged':True,'captured_bytes_per_PC':16,'observer_source_sha256':stage.cdi_layout.sha(root/'scripts/biwn_runtime_pc_probe.c'),
            'stage_sha256':stage.STAGE_SHA,
            'scope':'Each frame samples only the most recent1024CPU PCs. Matching entry addresses support execution at those addresses; they do not prove inferred function boundaries, names, complete coverage or correctness. Compared RAM bytes are observed after the frame, not at each execution. BIOS is assisted; original emulator game, not reconstructed C, was executed.'}
    path=output/'observations.json';path.write_text(json.dumps(report,indent=2)+'\n')
    (session/'emulator-runtime/pc-observer-summary.json').write_text(json.dumps({'source_report':str(path),**report},indent=2)+'\n')
    print(path,flush=True)


if __name__=='__main__':main()
