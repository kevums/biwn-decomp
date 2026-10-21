"""Isolated captured launch, both retained blitter engines and one counterfactual.

This explicitly restores captured RAM/device state in isolated test processes.
It does not alter the live preview, source discs or a continuing gameplay run.
"""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    pp=ROOT/'verification/native-fast-core-blitter-handoff-current.json';parent=json.loads(pp.read_text());capture=Path(parent['directory'])
    assert parent['capture_found']and parent['exit_code']==0
    for p,h in {**parent['source_sha256'],**parent['output_sha256']}.items():assert sha(p)==h,p
    core=Path(parent['command'][parent['command'].index('--core')+1]);symbols={}
    for line in subprocess.check_output(['nm',str(core)],text=True).splitlines():
        fields=line.split()
        if len(fields)==3 and fields[2]in['_GPUStateSave','_BlitterStateLoad','_BlitterStateSave']:symbols[fields[2]]=int(fields[0],16)
    assert len(symbols)==3
    original_ram=(capture/'launch-before-RAM.bin').read_bytes();expected=(capture/'first-corruption-RAM.bin').read_bytes()
    writers=[json.loads(line)for line in(capture/'A2-base-writers.jsonl').read_text().splitlines()]
    gpu_writes=[row for row in writers if row['frame']==1429 and row['phase']==2 and row['previous_PC']==0xf03302]
    assert len(gpu_writes)==1
    target=gpu_writes[0]['after_base'];assert target==0x8b3d0
    out=ROOT/'verification/native-fast-core-corrupt-blit-replay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';source_text=source.read_text();results=[];commands=[]
    for engine in ['fast','reference']:
        lane=out/engine;lane.mkdir();probe=lane/'probe.py'
        text='import sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\n'+source_text
        marker='ROOT = Path(__file__).resolve().parents[1]';assert text.count(marker)==1;text=text.replace(marker,'ROOT = Path('+repr(str(ROOT))+')')
        if engine=='reference':
            marker="b'virtualjaguar_usefastblitter': b'enabled'";assert text.count(marker)==1;text=text.replace(marker,"b'virtualjaguar_usefastblitter': b'disabled'")
        marker="        PC_ring = (c.c_uint32*1024).in_dll(core, 'pcQueue') if args.trace_firmware else None";assert text.count(marker)==1
        replay=f'''
        capture=Path({str(capture)!r})
        before=(capture/'launch-before-RAM.bin').read_bytes()
        GPU=(capture/'launch-before-GPU.bin').read_bytes()
        B=(capture/'launch-before-blitter.bin').read_bytes()
        expected=(capture/'first-corruption-RAM.bin').read_bytes()
        slide=c.cast(core.GPUStateSave,c.c_void_p).value-{symbols['_GPUStateSave']}
        SAVE=c.CFUNCTYPE(c.c_size_t,c.c_void_p)
        bsave=SAVE(slide+{symbols['_BlitterStateSave']});bload=SAVE(slide+{symbols['_BlitterStateLoad']})
        core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
        core.BlitterWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        result=[]
        for name,base in [('captured',0x44168),('counterfactual_GPU_framebuffer',{target})]:
            c.memmove(ram_pointer,before,len(before));g=c.create_string_buffer(GPU);assert core.GPUStateLoad(g)==len(GPU)
            state=bytearray(B);state[0x24:0x28]=base.to_bytes(4,'big');raw=c.create_string_buffer(bytes(state));assert bload(raw)==len(B)
            check=c.create_string_buffer(4096);assert bsave(check)==len(B)and check.raw[:len(B)]==bytes(state)
            # Exact STORE r0,(r3) from the recorded GPU branch delay slot.
            core.BlitterWriteLong(0xf02238,0x41802c01,3)
            after=c.string_at(ram_pointer,0x200000);(out/(name+'-RAM.bin')).write_bytes(after)
            result.append(dict(lane=name,A2_base=hex(base),before_world=before[0x49c50:0x49c60].hex(),after_world=after[0x49c50:0x49c60].hex(),world_changed=before[0x49c50:0x49c60]!=after[0x49c50:0x49c60],whole_RAM_equal_to_captured_after=after==expected,whole_RAM_changed_bytes=sum(a!=b for a,b in zip(before,after)),after_RAM_sha256=hashlib.sha256(after).hexdigest(),device_state_roundtrip=True))
        save(out/'replay.json',dict(engine={engine!r},results=result,options=report['requested_options'],core_sha256=report['core_sha256'],CPU_instructions_executed=0,GPU_instructions_executed=0,physical_equivalence=False,scope='Captured twoMB RAM+GPU+463byteblitter state restored in an isolated test; call exact retained BlitterWriteLong once. Counterfactual changes only A2base,not a deployedgamefix.'))
        return
'''
        text=text.replace(marker,replay+'\n'+marker);compile(text,str(probe),'exec');probe.write_text(text)
        command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','1','--core',str(core),'--no-publish','--output',str(lane/'output')]
        commands.append(command)
        with(lane/'log.txt').open('w')as log:code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode
        assert code==0,(engine,code)
        result=json.loads((lane/'output/replay.json').read_text());results.append(result)
        assert result['results'][0]['world_changed']
        assert not result['results'][1]['world_changed']
    assert results[0]['results'][0]['whole_RAM_equal_to_captured_after']
    same_engines=[a['after_RAM_sha256']==b['after_RAM_sha256']for a,b in zip(results[0]['results'],results[1]['results'])]
    state=dict(status='terminal_captured_formatter_corrupt_blit_replayed',directory=str(out),commands=commands,source_proof=str(pp),source_proof_sha256=sha(pp),results=results,fast_and_reference_RAM_equal=same_engines,captured_fast_whole_RAM_reproduced=True,counterfactual_only_A2_base_changed=True,counterfactual_is_game_fix=False,new_training=False,default_promoted=False,hardware_verified=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),pp,source,core,*capture.glob('launch-before-*.bin'),capture/'first-corruption-RAM.bin']},output_sha256={str(p):sha(p)for p in out.rglob('*')if p.is_file()},scope='One actual renderer launch explains the first captured world overwrite in the pinned emulator. Both engines execute this device fixture; no CPU/GPU instruction or continuing-route fix. Source-vs-emulator cause and robust synchronization repair remain unproven.')
    save(out/'protocol.json',state);save(ROOT/'verification/native-fast-core-corrupt-blit-replay-current.json',state)
    print(json.dumps(dict(status=state['status'],fast_and_reference_RAM_equal=same_engines,results=results),indent=2),flush=True)

if __name__=='__main__':main()
