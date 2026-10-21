"""Opt-in queue restoration against a narrowly patched original CPU oracle.

The oracle changes only four absolute queue-storage operands. Count, loops,
actors, loading and GPU programs still execute source instructions. Queue
storage is compared explicitly; only its two declared work areas are masked.
"""
import argparse
import ctypes as c
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import random
import subprocess
import check_biwn_outdoor_scene_stream as outdoor
import check_biwn_scene_render_pipeline as rendering

scene=outdoor.scene;ROOT=scene.ROOT;sha=scene.sha;save=scene.save
QUEUE=0x1f0000;CAPACITY=128
PATCHES={0x20ba2:0x15ec7c,0x20c26:0x15ec7c,0x20d3e:0x15ec7c,0x20d8c:0x15ec7c}


def normalized(raw):
    ram=bytearray(raw);ram[0x15ec7c:0x15ece0]=bytes(100);ram[QUEUE:QUEUE+CAPACITY*2]=bytes(CAPACITY*2);return bytes(ram)


class Runtime(outdoor.Runtime):
    def __init__(self,library):
        super().__init__(library)
        self.repaired=self.lib.biwn_scene_stream_repaired_queue
        self.repaired.argtypes=self.stream_fault.argtypes+[c.POINTER(c.c_uint16),c.c_uint32,c.POINTER(c.c_uint32)]
        self.repaired.restype=c.c_int
        self.normal_stream=self.stream_fault

    def before_step(self,pc,case):
        if pc==0x20bbc:
            offset=self.core.m68k_get_reg(None,0);base=self.core.m68k_get_reg(None,9)&0xffffff
            assert base==QUEUE
            source=(self.core.m68k_get_reg(None,8)+4)&0xffffff
            self.native_queue_writes.append(dict(index=offset//2,value=self.core.m68k_read_memory_16(source),address=hex(base+offset)))
            assert offset//2<CAPACITY
        else:super().before_step(pc,case)

    def native(self,ram,case):
        self.native_queue_writes=[]
        try:
            raw,d0,result=super().native(ram,case)
            self.last_native_raw=raw
            return normalized(raw),d0,result
        except Exception:
            if hasattr(self,'failure_RAM'):
                self.last_native_raw=self.failure_RAM;self.failure_RAM=normalized(self.failure_RAM)
            raise

    def translated(self,ram,case,repair=True,capacity=CAPACITY,null_ids=False,**overrides):
        if not repair:return super().translated(ram,case,**overrides)
        storage=(c.c_uint16*(CAPACITY+2))(*([0xdada]*(CAPACITY+2)));ids=c.cast(c.byref(storage,2),c.POINTER(c.c_uint16));peak=c.c_uint32(0)
        def run(*args):return self.repaired(*args,None if null_ids else ids,capacity,c.byref(peak))
        self.stream_fault=run
        try:
            raw,d0,result=super().translated(ram,case,**overrides)
            assert storage[0]==storage[-1]==0xdada
            self.last_C_raw=raw;self.queue_peak=peak.value;self.queue_ids=list(ids[:peak.value])
            result['queue_peak']=peak.value
            return normalized(raw),d0,result
        finally:self.stream_fault=self.normal_stream


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--all-windows',action='store_true');opt=ap.parse_args()
    out=ROOT/'verification/scene-queue-restoration'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=scene.SOURCES+rendering.EXTRA;library=out/'libscene-queue-restoration.dylib'
    source_hashes={n:sha((source/n).read_bytes())for n in names}
    snapshot_dir=out/'source-snapshot';snapshot_dir.mkdir()
    for name in names+[name.replace('.c','.h')for name in names]:(snapshot_dir/name).write_bytes((source/name).read_bytes())
    script_bytes=Path(__file__).read_bytes();(snapshot_dir/Path(__file__).name).write_bytes(script_bytes);script_hash=sha(script_bytes)
    for helper in[Path(scene.__file__),Path(outdoor.__file__),Path(rendering.__file__)]:
        (snapshot_dir/helper.name).write_bytes(helper.read_bytes())
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/n)for n in names],'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    catalogue=json.loads((ROOT/'verification/outdoor-scene-catalog-current.json').read_text());records=json.loads((Path(catalogue['directory'])/'records.json').read_text());windows=json.loads((Path(catalogue['directory'])/'windows.json').read_text())
    def metadata(window):
        segments=[segment for index in window['record_indices']for segment in records[index]['segments'][window['remainder']:window['remainder']+5]]
        return [value for segment in segments for value in segment['texture_ids']],[actor for segment in segments for actor in segment['actors']]
    hazards=[window for window in windows if len(metadata(window)[0])>50]
    assert len(hazards)==51 and max(len(metadata(w)[0])for w in hazards)==61
    nominal=[windows[i]for i in[0,64,128,256,512,1024,1536,2048]if len(metadata(windows[i])[0])<=50]
    # Diagnose the previously crashing scene first; no success by skipping it.
    failing=next(w for w in hazards if(w['top_row'],w['column'],w['remainder'])==(27,1,4))
    vectors=[failing]+[w for w in hazards if w!=failing]+nominal
    if opt.all_windows:vectors=[failing]+[w for w in windows if w!=failing]
    runtime=Runtime(library);snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes();assert sha(snapshot)==catalogue['resident_flag_RAM_sha256']
    prefix=runtime.disc.use_previous_track_prefix();scan=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0];a=int(scan['address'],16);old=bytes.fromhex(scan['original']);new=bytes.fromhex(scan['replacement']);assert snapshot[a:a+len(old)]==old
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());buffer=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(buffer)==diagnosis['buffer_sha256'];witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buffer)
    initial=bytearray(snapshot);initial[a:a+len(old)]=new;initial[0x47b80:0x47b84]=bytes(4)
    patches=[]
    for a,expected in PATCHES.items():
        assert scene.native.get(initial,a)==expected
        initial[a:a+4]=QUEUE.to_bytes(4,'big');patches.append(dict(address=hex(a),original=hex(expected),replacement=hex(QUEUE)))
    save(out/'oracle-patches.json',dict(queue_address=hex(QUEUE),capacity=CAPACITY,patches=patches,scope='Storage-address relocation only; source algorithms, loop/count and all actor/texture/GPU instructions otherwise retained. This is a restoration oracle, not unmodified game execution.'))
    rng=random.Random(0x15ec7c1f0000);incoming=lambda:[rng.getrandbits(32)for _ in scene.world.REGS]
    case=dict(entry=0x1aa40,mode=1,word_scan=1,incoming=incoming(),external_D0=0xc001d00d)
    prepared,C_prepared,d0,original,rebuilt=outdoor.compare(runtime,bytes(initial),case,out,'textures')
    if opt.all_windows:
        X=scene.native.get(prepared,0x49c50);Z=scene.native.get(prepared,0x49c56);sx=((X-1)>>10)-2;row=((0xbc01-Z)>>10)+2
        merchant=next(w for w in windows if(w['top_row'],w['column'],w['remainder'])==(row,sx//5,sx%5))
        vectors.append({**merchant,'X':X,'Z':Z,'exact_merchant_coordinates':True})
    if opt.limit:vectors=vectors[:opt.limit]
    rows=[];render_inputs=[]
    try:
        for i,window in enumerate(vectors):
            save(out/'status.json',dict(status='running',pid=os.getpid(),case=i,completed_cases=len(rows),total=len(vectors),window=window))
            ram=bytearray(prepared);ram[0x49c50:0x49c54]=window['X'].to_bytes(4,'big');ram[0x49c56:0x49c5a]=window['Z'].to_bytes(4,'big')
            case=dict(mode=1,word_scan=1,incoming=incoming(),external_D0=0xc001d00d)
            left,right,d0,original,rebuilt=outdoor.compare(runtime,bytes(ram),case,out,str(i))
            ids,actors=metadata(window);observed=[event['value']for event in runtime.native_queue_writes]
            assert observed==ids==runtime.queue_ids and runtime.queue_peak==len(ids),(i,len(ids),observed,runtime.queue_ids)
            assert runtime.last_native_raw[QUEUE:QUEUE+len(ids)*2]==b''.join(v.to_bytes(2,'big')for v in ids)
            assert runtime.last_C_raw[0x15ec7c:0x15ec7c+min(50,len(ids))*2]==b''.join(v.to_bytes(2,'big')for v in ids[:50])
            assert not original['texture_queue_overruns']and not original['unmapped_actor_reads']
            if not original['fault']:
                assert original['entries'].get('0x13ae0',0)==len(actors)
                assert scene.native.get(right,0x15ece0,2)==scene.native.get(right,0x15ed46,2)==scene.native.get(right,0x15edac,2)==0
            row=dict(window=window,outcome='matched_relocated_queue_oracle_address_error'if original['fault']else'matched_relocated_queue_oracle_return',expected_actor_placements=len(actors),actual_actor_calls=original['entries'].get('0x13ae0',0),ordered_texture_ids=ids,queue_peak=runtime.queue_peak,source_ram_actor_pointer11=hex(scene.native.get(right,0x15ed0e)),full_D0=d0,original=original,rebuilt=rebuilt,task_records=scene.check_task_records(left,right,original),public_RAM_except_explicit_queue_workspaces_matches=True)
            rows.append(row)
            with(out/'cases.jsonl').open('a')as stream:stream.write(json.dumps(row)+'\n')
            if not original['fault']and (window==failing or len(ids)==61 or len(actors)>=7)and len(render_inputs)<5:render_inputs.append((window,runtime.last_C_raw))
        guards=[]
        ram=bytearray(prepared);ram[0x49c50:0x49c54]=failing['X'].to_bytes(4,'big');ram[0x49c56:0x49c5a]=failing['Z'].to_bytes(4,'big')
        case=dict(mode=1,word_scan=1,incoming=incoming(),external_D0=0xc001d00d)
        for capacity in[0,49,50,32768]:
            result,value,details=runtime.translated(bytes(ram),case,capacity=capacity)
            if capacity==50:
                assert details['status']in[3,5]and details['queue_peak']==50
                assert scene.native.get(result,0x15ece0,2)==50
                assert scene.native.get(result,0x15ed0e)&0xffff0000!=0
            else:assert details['status']==1 and scene.native.masked(result)==scene.native.masked(normalized(bytes(ram)))
            assert value==0xa55aa55a;guards.append(dict(capacity=capacity,status=details['status'],queue_peak=details['queue_peak']))
        for label,changes in [('null_workspace',dict(null_ids=True)),('nonempty_pending_queue',{})]:
            initial_guard=bytearray(ram)
            if label=='nonempty_pending_queue':initial_guard[0x15ece0:0x15ece2]=(1).to_bytes(2,'big')
            result,value,details=runtime.translated(bytes(initial_guard),case,**changes)
            assert details['status']==1 and value==0xa55aa55a and details['queue_peak']==0
            assert scene.native.masked(result)==scene.native.masked(normalized(bytes(initial_guard)))
            guards.append(dict(case=label,status=details['status'],queue_peak=details['queue_peak']))
    except Exception as error:
        if hasattr(runtime,'last_native_raw'):(out/'native-RAM.bin').write_bytes(runtime.last_native_raw)
        if hasattr(runtime,'last_C_raw'):(out/'C-RAM.bin').write_bytes(runtime.last_C_raw)
        save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),error=repr(error)));raise
    finally:runtime.close()
    save(out/'render-inputs.json',[dict(window=w,RAM_sha256=sha(ram))for w,ram in render_inputs])
    for i,(window,ram)in enumerate(render_inputs):(out/f'render-input-{i}.bin').write_bytes(ram)
    for name,expected in source_hashes.items():assert sha((source/name).read_bytes())==expected,'C source changed during run: '+name
    report=dict(status='explicit_texture_queue_restoration_matches_relocated_native_oracle',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),overflow_windows=sum(len(row['ordered_texture_ids'])>50 for row in rows),nominal_windows=sum(len(row['ordered_texture_ids'])<=50 for row in rows),returned_cases=sum(row['original']['fault']is None for row in rows),separate_original_actor_position_address_errors=sum(row['original']['fault']is not None for row in rows),maximum_pending_ids=max(row['queue_peak']for row in rows),guards=guards,oracle_patches=patches,source_sha256=source_hashes,script_sha256=script_hash,source_snapshot=str(snapshot_dir),stream_witness=witness,prefix=prefix,default_promoted=False,original_program_equivalence_on_overflow=False,scope='Opt-in Cqueue uses caller128wordstorage beyond the original50wordarea; nativeCPUoracle relocates only4queuebase operands to1F0000. AllorderedIDs explicitlymatch catalogue/nativewrites/Cworkspace; fullD0/public2MBRAM except twoqueueworkareas, actorpointers/records/tasks, discandcheckedGPU/blitterstate match. No deduplication or ID/order/count changes. Original APIs retain overflowbehavior. Static actor70 indoor-position lookup faults mayremain separately matched, not repaired here. FrozenmerchantRAM/suppliedwindows/wordscan672/synchronousdevices; no naturalreachability/liveactors/fullgame/standalone/defaultpromotionproof.')
    report['requested_scope']='all_bounded_windows_plus_merchant'if opt.all_windows else'all_overflow_windows_plus_selected_nominal'
    report['all_bounded_windows_checked']=bool(opt.all_windows and not opt.limit)
    report['zero_length_boundary_windows_not_executed']=catalogue['windows_containing_zero_length_segments']
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    current='scene-queue-restoration-preflight-current.json'if opt.limit else'scene-queue-restoration-full-current.json'if opt.all_windows else'scene-queue-restoration-current.json'
    save(ROOT/'verification'/current,report);print(json.dumps({k:report[k]for k in ['status','directory','cases','overflow_windows','returned_cases','separate_original_actor_position_address_errors','maximum_pending_ids']}),flush=True)


if __name__=='__main__':main()
