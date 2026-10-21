"""Outdoor source scene setup with real RTXT initialization and disc blocks."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import random
import subprocess
import struct
import ctypes as c
import check_biwn_scene_stream as scene

ROOT=scene.ROOT
sha=scene.sha
save=scene.save


class Runtime(scene.Runtime):
    """Explicit pinned-core expansion-hole reads, never fabricated RAM.

    Some supplied windows overflow the original 50-word texture queue into
    actor pointers. Keep this behavior visible; an unmapped read is not a
    valid actor record or successful restoration fix.
    """
    def __init__(self,library):
        super().__init__(library)
        self.core.m68k_read_memory_16.argtypes=[c.c_uint32]
        self.core.m68k_read_memory_16.restype=c.c_uint32

    def native(self,ram,case):
        self.native_hole_reads=[];self.queue_overruns=[];self.pending_hole=None
        try:result=super().native(ram,case)
        except Exception:
            if self.failure:
                self.failure['texture_queue_overruns']=self.queue_overruns
                self.failure['unmapped_actor_reads']=self.native_hole_reads
            raise
        result[2]['unmapped_actor_reads']=self.native_hole_reads
        result[2]['texture_queue_overruns']=self.queue_overruns
        return result

    def before_step(self,pc,case):
        if pc==0x20bbc:
            index=self.core.m68k_get_reg(None,0)
            if index>=100:
                source=(self.core.m68k_get_reg(None,8)+4)&0xffffff
                self.queue_overruns.append(dict(index=index//2,destination=hex((0x15ec7c+index)&0xffffff),value=self.core.m68k_read_memory_16(source)))
        if pc==0x20ac4:
            address=self.core.m68k_get_reg(None,10)&0xffffff
            if 0x200000<=address<=0x7ffffe:self.pending_hole=address

    def after_step(self,pc,case):
        super().after_step(pc,case)
        if self.pending_hole is not None:
            self.native_hole_reads.append(dict(address=hex(self.pending_hole),width=2,value=self.core.m68k_get_reg(None,4)&65535))
            self.pending_hole=None

    def translated(self,ram,case,**overrides):
        strict=self.device.r16;reads=[]
        def read16(context,address,out):
            if 0x200000<=address<=0x7ffffe:
                out[0]=self.core.m68k_read_memory_16(address)
                reads.append(dict(address=hex(address),width=2,value=out[0]));return 0
            return strict(context,address,out)
        self.device.r16=scene.world.R16(read16)
        try:
            result=super().translated(ram,case,**overrides)
            result[2]['unmapped_actor_reads']=reads
            return result
        finally:self.device.r16=strict


def compare(runtime,ram,case,out,label):
    fault=None
    try:left,expected,original=runtime.native(ram,case)
    except AssertionError:
        diagnostic=getattr(runtime,'failure',None)
        if not diagnostic or not hasattr(runtime,'failure_RAM'):raise
        left=runtime.failure_RAM;stack=diagnostic['registers'][15];raw=left[stack:stack+14]
        ssw,address,opcode,sr,pc=struct.unpack('>HIHHI',raw);last=int(diagnostic['recent_PCs'][-1],16)
        # Validate the actual14byte address-error frame, not merely handler400.
        if not(diagnostic['registers'][16]==scene.native.get(left,12)and address&1 and opcode==scene.native.get(left,last,2)and last+2<=pc<=last+12):raise
        fault=dict(kind='original_M68000_address_error',fault_address=hex(address),faulting_instruction=hex(last),frame_PC=hex(pc),SSW=hex(ssw),SR=hex(sr),exception_frame=raw.hex(),handler_PC=diagnostic['PC'])
        expected=None;original={k:diagnostic[k]for k in['entries','calls','created_tasks','disc_requests','disc_completions','disc_stops','hardware','device']};original['decoded_sprites']=diagnostic['sprites']
        original['unmapped_actor_reads']=runtime.native_hole_reads;original['texture_queue_overruns']=runtime.queue_overruns
    mailboxes=[runtime.core.GPUReadLong(a,0)for a in[0xf03200,0xf03204,0xf0320c,0xf03210,0xf03214]]
    right,value,rebuilt=runtime.translated(ram,case)
    C_mailboxes=[runtime.core.GPUReadLong(a,0)for a in[0xf03200,0xf03204,0xf0320c,0xf03210,0xf03214]]
    original['GPU_mailboxes']=mailboxes;rebuilt['GPU_mailboxes']=C_mailboxes
    return_matches=(value==expected and rebuilt['status']==0)if fault is None else(value==0xa55aa55a and rebuilt['status']in[2,3])
    matched=scene.native.masked(left)==scene.native.masked(right)and return_matches and not rebuilt['errors']and all(original[k]==rebuilt[k]for k in['calls','disc_requests','disc_completions','disc_stops','hardware','GPU_mailboxes','unmapped_actor_reads'])
    if not matched:
        (out/(label+'-native-RAM.bin')).write_bytes(left)
        (out/(label+'-C-RAM.bin')).write_bytes(right)
        save(out/(label+'-mismatch.json'),dict(case=case,original_D0=expected,C_D0=value,original_fault=fault,original=original,C=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(scene.native.masked(left),scene.native.masked(right)))if a!=b][:40]));raise AssertionError(str(out/(label+'-mismatch.json')))
    original['fault']=fault
    if fault:
        observed=rebuilt['alignment_fault'];address=int(fault['fault_address'],16)
        assert observed['width']in[2,4]and observed['logical_address']==address and observed['physical_address']==address&0xffffff
        assert bool(observed['is_write'])==(not bool(int(fault['SSW'],16)&0x10))
    assert not rebuilt['device']['device_error']and not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['original_GPU_sprite_decodes']and not rebuilt['device']['game_frames_executed']
    return left,right,value,original,rebuilt


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--limit',type=int);parser.add_argument('--start',type=int,default=0);args=parser.parse_args()
    assert args.start>=0 and(not args.start or args.limit),'A partial offset requires an explicit preflight limit'
    catalogue=json.loads((ROOT/'verification/outdoor-scene-catalog-current.json').read_text());windows=json.loads((Path(catalogue['directory'])/'windows.json').read_text());records=json.loads((Path(catalogue['directory'])/'records.json').read_text())
    out=ROOT/'verification/outdoor-scene-stream'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'liboutdoor-scene-stream.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/name)for name in scene.SOURCES],'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=Runtime(library);snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes();assert sha(snapshot)==catalogue['resident_flag_RAM_sha256']
    prefix=runtime.disc.use_previous_track_prefix()
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0];address=int(patch['address'],16);old=bytes.fromhex(patch['original']);new=bytes.fromhex(patch['replacement']);assert snapshot[address:address+len(old)]==old
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());buffer=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(buffer)==diagnosis['buffer_sha256'];witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buffer)
    ram=bytearray(snapshot);ram[address:address+len(old)]=new;ram[0x47b80:0x47b84]=bytes(4)
    rng=random.Random(0x20002262);rows=[];texture_init=None
    try:
        init_case=dict(entry=0x1aa40,mode=1,word_scan=1,incoming=[rng.getrandbits(32)for _ in scene.world.REGS],external_D0=0xc001d00d)
        prepared,C_prepared,d0,original,rebuilt=compare(runtime,bytes(ram),init_case,out,'texture-init')
        assert scene.native.get(prepared,0x15b530,2)==1 and scene.native.get(prepared,0x15b532,2)==15
        manifest=runtime.disc.manifest;size=0x1e000;payload=C_prepared[0x1134a0:0x1134a0+size]
        assert sha(payload)==manifest['textures']['payload_sha256']
        texture_init=dict(full_D0=d0,original=original,rebuilt=rebuilt,RTXT_bytes=size,RTXT_sha256=sha(payload),reserved_slots=15)
        save(out/'texture-init.json',texture_init)
        get=scene.native.get;X=get(prepared,0x49c50);Z=get(prepared,0x49c56);sx=((X-1)>>10)-2;row=((0xbc01-Z)>>10)+2;column=sx//5;remainder=sx%5
        merchant=next(window for window in windows if(window['top_row'],window['column'],window['remainder'])==(row,column,remainder));merchant={**merchant,'X':X,'Z':Z,'exact_merchant_coordinates':True}
        vectors=[merchant]+windows
        if args.start:
            assert args.start<len(vectors);vectors=vectors[args.start:]
            for _ in range(args.start*len(scene.world.REGS)):rng.getrandbits(32)
        if args.limit:assert args.limit>0;vectors=vectors[:args.limit]
        for ordinal,window in enumerate(vectors):
            ram=bytearray(prepared);ram[0x49c50:0x49c54]=window['X'].to_bytes(4,'big');ram[0x49c56:0x49c5a]=window['Z'].to_bytes(4,'big')
            case=dict(mode=1,word_scan=1,incoming=[rng.getrandbits(32)for _ in scene.world.REGS],external_D0=0xc001d00d)
            save(out/'status.json',dict(status='running',pid=os.getpid(),completed_cases=len(rows),requested_cases=len(vectors),ordinal=ordinal,window=window))
            left,right,value,original,rebuilt=compare(runtime,bytes(ram),case,out,str(ordinal))
            if not original['fault']:
                assert get(right,0x49c60,2)==1 and get(right,0x47b80,2)==0 and get(right,0x49c8c,2)==12
                assert original['entries']['0x20b2a']==25 and original['entries']['0x20c16']==1 and original['entries']['0x102c4']>=1
            expected_actors=[actor for index in window['record_indices']for segment in records[index]['segments'][window['remainder']:window['remainder']+5]for actor in segment['actors']]
            if not original['fault']:assert original['entries'].get('0x13ae0',0)==len(expected_actors)
            expected_sprites=sum(a['source_factory_path']=='static_decode'for a in expected_actors)
            assert rebuilt['device']['C_sprite_decodes']==original['device']['original_GPU_sprite_decodes']
            if not original['fault']:assert rebuilt['device']['C_sprite_decodes']==expected_sprites
            decoded=[]
            for sprite in original['decoded_sprites']:
                a=sprite['destination'];size=sprite['width']*sprite['height']*2;assert left[a-16:a+size]==right[a-16:a+size]
                decoded.append(dict(**sprite,pixel_sha256=sha(right[a:a+size])))
            # Check all relocated room bytes even if a room happens to lie in
            # a private-stack exclusion; retain pointer tag bits as data.
            room_rows=[]
            for i in range(25):
                pointer=get(right,0x49bb4+i*4);physical=pointer&0xffffff
                assert left[physical:physical+540]==right[physical:physical+540]
                room_rows.append(dict(pointer=hex(pointer),physical=hex(physical),sha256=sha(right[physical:physical+540])))
            rows.append(dict(ordinal=ordinal+args.start,window=window,outcome='native_address_error_and_matching_C_host_stop'if original['fault']else'completed_setup_match',full_D0=value if not original['fault']else None,C_output_untouched_on_fault=bool(original['fault']),original=original,rebuilt=rebuilt,room_buffers_checked=room_rows,actor_placements=len(expected_actors),decoded_sprite_payloads_checked=decoded,created_task_records_checked=scene.check_task_records(left,right,original),full_public_RAM_and_checked_devices_match=True))
            with(out/'cases.jsonl').open('a')as f:f.write(json.dumps(rows[-1])+'\n')
    except Exception as error:
        if hasattr(runtime,'failure_RAM'):(out/'native-failure-RAM.bin').write_bytes(runtime.failure_RAM)
        save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),error=repr(error),native_diagnostic=getattr(runtime,'failure',None)));raise
    finally:runtime.close()
    report=dict(status='readable_outdoor_scene_stream_matches_native_all_bounded_windows'if not args.limit else'readable_outdoor_scene_stream_selected_preflight_pass',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),catalogued_bounded_windows=len(windows),zero_length_boundary_windows_not_executed=catalogue['windows_containing_zero_length_segments'],texture_initialization=texture_init,loaded_room_instances=len(rows)*25,actor_placement_instances=sum(row['actor_placements']for row in rows),C_sprite_decodes=sum(row['rebuilt']['device']['C_sprite_decodes']for row in rows),created_task_records_checked=sum(len(row['created_task_records_checked'])for row in rows),room_pointer_tags_preserved=True,physical_address_bits=24,source_sha256={n:sha((source/n).read_bytes())for n in scene.SOURCES+[n.replace('.c','.h')for n in scene.SOURCES]},script_sha256=sha(Path(__file__).read_bytes()),native_helper_sha256=sha((ROOT/'scripts/check_biwn_scene_stream.py').read_bytes()),normalized_disc_sha256=runtime.disc.manifest['normalized_track_sha256'],stream_witness=witness,new_training=False,native_Chat_verified=False,default_promoted=False,scope='Original1AA40textureinit and readableC load full122880byte RTXT andreserve15slots. Each20F78mode1call loads actual5discrows, parses/relocates25rooms, fixes textures, computes geometry and actor records/tasks/decoded pixels. OriginalCPU/GPU andC compare fullD0/publicRAM, externalcalls/disc events/7blitterregs; all25room540bytebuffers andnewtaskrecords checked explicitly outside private-stack mask. Frozen merchant RAM/TOC/heap/flag/assets; supplied coordinates, wordscan and672streamphase. Highbytetagged pointers preserved; addresses decoded24bits. BIOS303C/3042/DF60completion andGPUack remain synchronous adapters. No live scheduling/interrupts, task execution, fullCPU/GPUABI/cycles, physicaltiming, naturalentryforeachwindow, worldrendering/standalone/fullgame proof. Bounds catalogue excludes windows containing zero-length boundarysegments; those remain visible andunexecuted, not successful scene claims.')
    report['previous_track_prefix']=prefix
    report['completed_setup_cases']=sum(row['outcome']=='completed_setup_match'for row in rows)
    report['original_address_error_cases']=len(rows)-report['completed_setup_cases']
    report['loaded_room_instances']=sum(row['original']['entries'].get('0x20b2a',0)for row in rows)
    report['catalogue_actor_placements_in_windows']=report.pop('actor_placement_instances')
    report['actor_placement_calls_observed']=sum(row['original']['entries'].get('0x13ae0',0)for row in rows)
    report['address_error_windows']=[dict(window=row['window'],original_fault=row['original']['fault'],C_fault=row['rebuilt']['alignment_fault'])for row in rows if row['original']['fault']]
    report['CPU_exception_frame_emulated_in_C']=False
    report['original_queue_overrun_cases']=sum(bool(row['original']['texture_queue_overruns'])for row in rows)
    report['original_unmapped_actor_read_cases']=sum(bool(row['original']['unmapped_actor_reads'])for row in rows)
    report['queue_overrun_windows']=[dict(window=row['window'],writes=row['original']['texture_queue_overruns'],unmapped_actor_reads=row['original']['unmapped_actor_reads'])for row in rows if row['original']['texture_queue_overruns']]
    report['pinned_bus_core_sha256']=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes())
    report['scope']+=' Original texture queue writes beyond50words are recorded, including self-overwriting the queue count and corrupting actor pointers. Expansion-hole word reads use the pinned core CPU bus on the C lane, and values/order compare against original20AC4reads; no CPU instructions run for that adapter. Such matching returns do not establish valid scene data, natural gameplay reachability or a restoration fix. No RAM mirroring/padding or queue capacity repair is invented.'
    if report['original_address_error_cases']:
        report['status']='outdoor_window_completion_and_original_address_fault_outcomes_match_C'if not args.limit else'outdoor_selected_completion_and_address_fault_outcomes_checked'
        report['scope']+=' Original CPU address-error cases are retained separately from successful setup. C stops at the same logical/physical access with matching read/write direction, prior public RAM and device effects and untouched output. Its host error does not emulate CPU exception frames/handler execution; faulted windows are not successful loading claims.'
    report['source_CDI_negative_offset_requests']=sum(request['normalized_track_offset']<0 for row in rows for request in row['rebuilt']['disc_requests'])
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    save(ROOT/'verification'/('outdoor-scene-stream-preflight-current.json'if args.limit else'outdoor-scene-stream-current.json'),report)
    print(json.dumps({k:report[k]for k in ['status','cases','loaded_room_instances','C_sprite_decodes','created_task_records_checked','directory']}),flush=True)


if __name__=='__main__':main()
