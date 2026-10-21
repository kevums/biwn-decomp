"""Source constructor->loader suspension->idle->completion->full continuation."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
from biwn_disc_backend import Disc
ROOT=media.ROOT;save=media.save;sha=media.sha;SP=0x1f8000;SSP=0x1ff000;STOP=0x190000
MAIN=0xc2128;IDLE=0xc5928


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preserve-source-descriptor',action='store_true',help='Keep the original scene1 tag and asset ID from the frozen source image.')
    parser.add_argument('--experimental-mode3-count13',action='store_true',help='Separate restoration hypothesis: preserve scene1 descriptor and change only the mode3 count word from16 to13 in test RAM.')
    parser.add_argument('--experimental-request13',action='store_true',help='Diagnostic adapter only: replace the source selector acquisition argument16 with13 at helper entry; no source promotion.')
    parser.add_argument('--experimental-selector13',action='store_true',help='Use separate explicit guest-code selector*13/count13 overlay on both native and C paths; no argument adapter.')
    parser.add_argument('--all-mode3-assets',action='store_true',help='With selector13 only: controlled repeated selection of source descriptors for all19 observed mode3 marker groups; retained machine and actual scheduler.')
    options=parser.parse_args()
    assert not options.all_mode3_assets or options.experimental_selector13
    assert not options.experimental_selector13 or not(options.experimental_mode3_count13 or options.experimental_request13)
    preserve_descriptor=options.preserve_source_descriptor or options.experimental_mode3_count13 or options.experimental_request13 or options.experimental_selector13
    observe_retry=preserve_descriptor and not (options.experimental_selector13 or (options.experimental_mode3_count13 and options.experimental_request13))
    proof_name=('scene-selector13-all-assets-experiment' if options.all_mode3_assets else
                'scene-constructor-selector13-restoration-experiment' if options.experimental_selector13 else
                'scene-constructor-count13-request13-experiment' if options.experimental_mode3_count13 and options.experimental_request13 else
                'scene-constructor-request13-experiment' if options.experimental_request13 else
                'scene-constructor-count13-experiment' if options.experimental_mode3_count13 else
                'scene-constructor-source-descriptor-scheduler' if preserve_descriptor else 'scene-constructor-scheduler')
    out=ROOT/'verification'/proof_name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    files=[restore/('experimental/selector13/biwn_scene_constructor_cpu.c' if options.experimental_selector13 else 'experimental/biwn_scene_constructor_cpu.c'),*[restore/name for name in
        ['biwn_interior_loading_cpu.c','biwn_resource_cpu.c','biwn_cd_cpu.c','biwn_scheduler.c',
         'biwn_task_loops.c','biwn_media_setup_cpu.c']]]
    library=out/'libconstructor-scheduler.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restore),
        *map(str,files),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert not compiled.returncode,compiled.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    generations=dict(constructor=json.loads((ROOT/('verification/scene-constructor-selector13-generation-current.json' if options.experimental_selector13 else 'verification/scene-constructor-CPU-generation-current.json')).read_text()),
        interior=json.loads((session/'interior-loading-fullCPU-generation.json').read_text()),
        resource=json.loads((session/'resource-fullCPU-generation.json').read_text()),
        cd=json.loads((session/'cd-wrapper-fullCPU-generation.json').read_text()),
        media=json.loads((session/'media-setup-fullCPU-generation.json').read_text()))
    rows={name:record['instructions_decoded']for name,record in generations.items()}
    sets={name:{row['address']for row in instructions}for name,instructions in rows.items()}
    atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    if options.experimental_selector13:
        assert sha(atlas)==generations['constructor']['original_atlas_sha256']
        atlas=(restore/'experimental/selector13/patched-test-RAM.bin').read_bytes()
        assert sha(atlas)==generations['constructor']['patched_atlas_sha256']
    for instructions in rows.values():
        for row in instructions:assert atlas[row['address']:row['address']+row['size']].hex()==row['bytes']
    runtime=media.Runtime(library,sum(rows.values(),[]));phases={};results=[];rng=random.Random(0x10990df60)
    world=media.scheduler.cleanup.world
    def read(width):
        def callback(_,address,value):value[0]=runtime.read(address,width);return 0
        return callback
    def write(width):
        def callback(_,address,value):runtime.write(address,width,value);return 0
        return callback
    callbacks=[world.R8(read(1)),world.R16(read(2)),world.R32(read(4)),world.W16(write(2)),world.W32(write(4)),media.W8(write(1))]
    bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
    def body(name):
        fn=getattr(runtime.lib,name);fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;return fn
    functions=dict(constructor=body('biwn_scene_constructor_cpu_body'),interior=body('biwn_interior_loading_cpu_body'),
                   resource=body('biwn_resource_cpu_body'),cd=body('biwn_cd_cpu_body'),media=body('biwn_media_setup_cpu_body'))
    yielding=runtime.lib.biwn_scheduler_yield;yielding.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];yielding.restype=c.c_int
    idle_step=runtime.lib.biwn_task_loop_step;idle_step.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_void_p,c.c_void_p,c.c_uint32];idle_step.restype=c.c_int
    vectors=[(index,delay)for index in ([0]if options.all_mode3_assets else [0,1,15])for delay in [1,2,4]]
    descriptors={}
    # First source record for each observed C000..C012 marker group. Limit
    # this catalog to matched assets, not every potentially decoded record.
    for descriptor in range(62):
        address=0x3d822+146*descriptor
        tag=int.from_bytes(atlas[address:address+2],'big');asset=int.from_bytes(atlas[address+2:address+4],'big')
        if tag==0 and asset<19:descriptors.setdefault(asset,descriptor)
    if options.all_mode3_assets:assert set(descriptors)==set(range(19))
    try:
        for case,(index,delay) in enumerate(vectors):
            ram=bytearray(atlas);scene=0x3d822+146
            def put(a,width,value):ram[a:a+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
            if not preserve_descriptor:
                put(scene,2,0);put(scene+2,2,0)
            if options.experimental_mode3_count13:
                assert int.from_bytes(ram[0x464a6:0x464a8],'big')==16
                put(0x464a6,2,13)
            put(0x400e4,2,index);put(0x47b80,2,0);put(0x47b82,2,0)
            put(SP,4,STOP);put(0x80,4,0xde08);put(0xc0920,4,MAIN)
            for context,other,pc,sp in [(MAIN,IDLE,0x10990,SP),(IDLE,MAIN,0xf360,IDLE+0x400)]:
                for offset,width,value in [(0,4,other),(4,4,other),(8,4,pc),(12,4,sp),(16,4,pc),
                                           (20,2,0),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(context+offset,width,value)
            initial=media.CPU();initial.registers[:15]=[rng.getrandbits(32)for _ in range(15)]
            initial.registers[15]=SP;initial.pc=0x10990;initial.usp=SP;initial.ssp=SSP;initial.sr=[0,0x10,0x13][case if options.all_mode3_assets else case//3]
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',case=case,mode=mode,completion_switch=delay))
                runtime.reset(bytes(ram),0);disc=Disc();cpu=media.CPU.from_buffer_copy(bytes(initial));errors=[];native_trace=[];bios=[];asset_payloads=[];loader_yield_entries=0
                def service(_,passed,state,target):
                    if target==0x1ac68 and options.experimental_request13:
                        address=state.contents.registers[15]+4
                        assert runtime.device.read(address,2)==16
                        runtime.device.direct(address,2,13)
                    for name in ['constructor','interior','resource','cd','media']:
                        if target in sets[name]:return functions[name](passed,state,callbacks[5],service_cb,None,100000,1)
                    if target==0x303c:
                        args=[state.contents.registers[i]for i in [8,9,0]];bios.append([target,args]);disc.start(*args);return 0
                    if target==0x3042:bios.append([target,[]]);disc.stop();return 0
                    errors.append(hex(target));return 1
                service_cb=media.world_cpu.SERVICE(service)
                if mode=='native':runtime.seed_cpu(cpu)
                def native_until(predicate):
                    nonlocal loader_yield_entries
                    for _ in range(150000):
                        pc=runtime.cpu().pc
                        if predicate(pc):return runtime.cpu()
                        native_trace.append(pc)
                        if pc==0xdf60 and runtime.device.read(0xc0920,4)==MAIN:loader_yield_entries+=1
                        if pc==0x1ac68 and options.experimental_request13:
                            address=runtime.cpu().registers[15]+4
                            assert runtime.device.read(address,2)==16
                            runtime.device.direct(address,2,13)
                        if pc in [0x303c,0x3042]:
                            state=runtime.cpu()
                            if pc==0x303c:
                                args=[state.registers[i]for i in [8,9,0]];bios.append([pc,args]);disc.start(*args)
                            else:bios.append([pc,[]]);disc.stop()
                            old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
                        else:runtime.core.m68k_execute(1)
                    raise AssertionError(('Native continuation limit',hex(pc)))
                def c_until(predicate):
                    nonlocal cpu
                    for _ in range(32):
                        if predicate(cpu.pc):return
                        name=next((name for name in sets if cpu.pc in sets[name]),None);assert name,hex(cpu.pc)
                        status=functions[name](c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,100000,1)
                        assert status in [0,6]and not errors,(name,status,hex(cpu.pc),errors)
                        if status==0:
                            assert runtime.rows[cpu.pc]['assembly']=='rts',hex(cpu.pc)
                            cpu.pc=runtime.device.read(cpu.registers[15],4);cpu.registers[15]+=4;cpu.usp=cpu.registers[15]
                    raise AssertionError('C continuation limit')
                def mark(name):
                    record=dict(CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),
                        hardware=runtime.snapshot()['hardware'],current_context=hex(runtime.device.read(0xc0920,4)),
                        disc_requests=list(disc.requests),disc_completions=list(disc.completions),bios=list(bios))
                    phases.setdefault(str(case)+'-'+name,{})[mode]=record;save(out/(str(case)+'-'+mode+'-'+name+'.json'),record)
                if mode=='native':cpu=native_until(lambda pc:pc==0xdf60)
                else:c_until(lambda pc:pc==0xdf60)
                assert cpu.pc==0xdf60 and disc.pending is not None;mark('nested_loader_suspended')
                if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE)
                else:
                    assert yielding(c.byref(bus),c.byref(cpu),128)==0
                    if cpu.pc==0xf366:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0
                    assert cpu.pc==0xf360
                mark('idle_selected')
                for deferred in range(1,delay):
                    # Idle yields back without supplying progress; original loader must suspend again.
                    if mode=='native':cpu=native_until(lambda pc:pc==0x1b0da)
                    else:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1b0da
                    mark('deferred_'+str(deferred)+'_loader_resumed')
                    if mode=='native':cpu=native_until(lambda pc:pc==0xdf60)
                    else:c_until(lambda pc:pc==0xdf60)
                    assert runtime.device.read(0xbd848,4)==0 and disc.pending is not None
                    mark('deferred_'+str(deferred)+'_loader_resuspended')
                    if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE)
                    else:
                        assert yielding(c.byref(bus),c.byref(cpu),128)==0
                        if cpu.pc==0xf366:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0
                        assert cpu.pc==0xf360
                    mark('deferred_'+str(deferred)+'_idle_selected')
                disc.tick(lambda a,data:c.memmove(runtime.device.pointer+a,data,len(data)),lambda a,value:runtime.device.direct(a,4,value))
                mark('completion_after_switch')
                if mode=='native':cpu=native_until(lambda pc:pc==0x1b0da)
                else:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1b0da
                mark('nested_loader_resumed')
                if observe_retry:
                    # Observe repeated *source* reads rather than treating a
                    # second suspension as a completed constructor or a hang.
                    for retry in range(3):
                        if mode=='native':cpu=native_until(lambda pc:pc in [STOP,0xdf60])
                        else:c_until(lambda pc:pc in [STOP,0xdf60])
                        assert cpu.pc==0xdf60 and disc.pending is not None,('Expected bounded source retry',hex(cpu.pc))
                        mark('retry_'+str(retry)+'_loader_suspended')
                        if retry==2:break
                        if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE)
                        else:
                            assert yielding(c.byref(bus),c.byref(cpu),128)==0
                            if cpu.pc==0xf366:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0
                            assert cpu.pc==0xf360
                        mark('retry_'+str(retry)+'_idle_selected')
                        disc.tick(lambda a,data:c.memmove(runtime.device.pointer+a,data,len(data)),lambda a,value:runtime.device.direct(a,4,value))
                        mark('retry_'+str(retry)+'_completion_after_switch')
                        if mode=='native':cpu=native_until(lambda pc:pc==0x1b0da)
                        else:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1b0da
                        mark('retry_'+str(retry)+'_loader_resumed')
                    assert not errors
                else:
                    if mode=='native':cpu=native_until(lambda pc:pc==STOP)
                    else:c_until(lambda pc:pc==STOP)
                    assert cpu.pc==STOP and cpu.registers[15]==SP+4 and not errors;mark('constructor_returned')
                if options.experimental_selector13:
                    assert runtime.device.read(0x403d8,2)==13,'Saved selector ID must agree with source acquisition/cache ID'
                    selected=runtime.device.read(0x403da,2)
                    assert runtime.device.read(0x15b4a0+selected*4,2)==13,('Selected cache record must carry acquired ID13',selected,[runtime.device.read(0x15b4a0+i*4,2)for i in range(36)])
                    def supplied_call(entry,argument,prefix='controlled'):
                        # Controlled caller frame for a separate lifetime test.
                        # Keep machine/RAM/devices/CPU registers; no reset, no
                        # original CPU on C side. Not a natural game caller.
                        nonlocal cpu
                        runtime.device.direct(SP,4,STOP);runtime.device.direct(SP+4,2,argument)
                        cpu.registers[15]=SP;cpu.usp=SP;cpu.pc=entry
                        if mode=='native':
                            runtime.core.m68k_set_reg(15,SP);runtime.core.m68k_set_reg(16,entry)
                        for transfer in range(4):
                            if mode=='native':cpu=native_until(lambda pc:pc in [STOP,0xdf60])
                            else:c_until(lambda pc:pc in [STOP,0xdf60])
                            if cpu.pc==STOP:break
                            assert options.all_mode3_assets and cpu.pc==0xdf60 and disc.pending is not None
                            mark(prefix+'_loader_suspended_'+str(transfer))
                            if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE)
                            else:
                                assert yielding(c.byref(bus),c.byref(cpu),128)==0
                                if cpu.pc==0xf366:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0
                                assert cpu.pc==0xf360
                            mark(prefix+'_idle_selected_'+str(transfer))
                            for deferred in range(1,delay):
                                if mode=='native':cpu=native_until(lambda pc:pc==0x1b0da)
                                else:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1b0da
                                mark(prefix+'_deferred_'+str(deferred)+'_loader_resumed')
                                if mode=='native':cpu=native_until(lambda pc:pc==0xdf60)
                                else:c_until(lambda pc:pc==0xdf60)
                                assert disc.pending is not None and runtime.device.read(0xbd848,4)==0
                                mark(prefix+'_deferred_'+str(deferred)+'_loader_resuspended')
                                if mode=='native':cpu=native_until(lambda pc:pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE)
                                else:
                                    assert yielding(c.byref(bus),c.byref(cpu),128)==0
                                    if cpu.pc==0xf366:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0
                                    assert cpu.pc==0xf360
                                mark(prefix+'_deferred_'+str(deferred)+'_idle_selected')
                            disc.tick(lambda a,data:c.memmove(runtime.device.pointer+a,data,len(data)),lambda a,value:runtime.device.direct(a,4,value))
                            mark(prefix+'_completion_after_switch_'+str(transfer))
                            if mode=='native':cpu=native_until(lambda pc:pc==0x1b0da)
                            else:assert idle_step(c.byref(bus),c.byref(cpu),None,None,128)==0 and cpu.pc==0x1b0da
                            mark(prefix+'_loader_resumed_'+str(transfer))
                        else:raise AssertionError(('Unexpected repeated read in source-selector candidate',entry,argument))
                        assert cpu.pc==STOP and cpu.registers[15]==SP+4
                    supplied_call(0x10a6a,1)
                    assert len(disc.requests)==1 and disc.pending is None,'Reselect must reuse loaded cache'
                    assert runtime.device.read(0x403d8,2)==13
                    selected=runtime.device.read(0x403da,2)
                    assert all(runtime.device.read(0x15b4a2+(selected+i)*4,2)==1 for i in range(13))
                    mark('controlled_reselection_returned')
                    if options.all_mode3_assets:
                        for ordinal,asset in enumerate([1,0,*range(2,19),1,0,18]):
                            supplied_call(0x10a6a,descriptors[asset],prefix='asset_'+str(ordinal))
                            assert runtime.device.read(0x403d8,2)==asset*13
                            selected=runtime.device.read(0x403da,2)
                            assert all(runtime.device.read(0x15b4a0+(selected+i)*4,2)==asset*13+i and runtime.device.read(0x15b4a2+(selected+i)*4,2)==1 for i in range(13))
                            address=runtime.device.read(0x4674c+selected*8,4)
                            marker=disc.data.find((0xc000+asset).to_bytes(4,'big')*16);assert marker>=0
                            payload=disc.data[marker+64:marker+64+106496]
                            assert c.string_at(runtime.device.pointer+address,106496)==payload
                            expected_pointers={0x23f7c:address,0x24068:address+32768,0x24070:address+32768,0x24078:address+65536,0x24080:address+65536,0x24088:address+98304,0x24090:address+98304}
                            assert all(runtime.device.read(a,4)==value for a,value in expected_pointers.items())
                            render_input=out/f'case-{case}-asset-{ordinal}-{mode}-render-input.bin'
                            if case==0:render_input.write_bytes(runtime.device.ram())
                            asset_payloads.append(dict(ordinal=ordinal,asset=asset,descriptor=descriptors[asset],cache_index=selected,pointer=hex(address),payload_sha256=sha(payload),requests_so_far=len(disc.requests),source_plane_pointers=expected_pointers,render_input_RAM_sha256=sha(runtime.device.ram()) if case==0 else None))
                            mark('asset_'+str(ordinal)+'_selector_returned')
                    requests_before_release=len(disc.requests)
                    supplied_call(0x1ae88,runtime.device.read(0x403d8,2))
                    assert len(disc.requests)==requests_before_release and disc.pending is None
                    assert all(runtime.device.read(0x15b4a2+(selected+i)*4,2)==0 for i in range(13))
                    mark('controlled_release_returned')
                final=runtime.device.ram();(out/(str(case)+'-'+mode+'-final-RAM.bin')).write_bytes(final)
                results.append(dict(case=case,index=index,completion_switch=delay,mode=mode,CPU=media.scheduler.cpu_dict(cpu),
                    RAM_sha256=sha(final),payload_sha256=sha(final[0x1134a0:0x1334a0]),
                    requests=disc.requests,completions=disc.completions,BIOS_calls=bios,
                    asset_payloads=asset_payloads,source_loader_yields_observed=loader_yield_entries,global_yield_entries_observed=native_trace.count(0xdf60),source_scheduler_switches_observed=native_trace.count(0xde08),
                    original_CPU_instructions=len(native_trace)if mode=='native'else 0,
                    original_visited_addresses=sorted(set(native_trace))if mode=='native'else[]))
        for name,record in phases.items():assert record['native']==record['C'],('Phase mismatch',name)
        for case in range(len(vectors)):assert(out/f'{case}-native-final-RAM.bin').read_bytes()==(out/f'{case}-C-final-RAM.bin').read_bytes()
        for case in range(len(vectors)):
            left=next(x for x in results if x['case']==case and x['mode']=='native');right=next(x for x in results if x['case']==case and x['mode']=='C');assert left['asset_payloads']==right['asset_payloads']
        report=dict(status=('experimental_selector13_all19_assets_native_C_match' if options.all_mode3_assets else
                           'experimental_selector13_constructor_returns_native_C_match' if options.experimental_selector13 else
                           'experimental_count13_request13_constructor_returns_native_C_match' if options.experimental_mode3_count13 and options.experimental_request13 else
                           'experimental_constructor_bounded_retry_native_C_match' if observe_retry and (options.experimental_mode3_count13 or options.experimental_request13) else
                           'source_descriptor_constructor_bounded_retry_native_C_match' if observe_retry else
                           'constructor_nested_loader_actual_scheduler_native_C_match'),recorded_at=datetime.now(timezone.utc).isoformat(),
            directory=str(out),cases=len(vectors),phases=phases,results=results,source_sha256={p.name:sha(p.read_bytes())for p in files},test_script_sha256=sha(Path(__file__).read_bytes()),
            original_CPU_instructions_on_C_path=0,source_loader_yields=48 if observe_retry else 21,
            source_scheduler_switches=78 if observe_retry else 42,completion_switch_values=[1,2,4],
            scripted_game_helper_targets=[],BIOS_adapters=['0x303c','0x3042'],completion_delivery='External disc tick only after actual idle selection',
            source_scene_descriptor_preserved=preserve_descriptor,
            scene_descriptor_tag=int.from_bytes(ram[scene:scene+2],'big'),
            scene_descriptor_asset=int.from_bytes(ram[scene+2:scene+4],'big'),
            constructor_return_verified=not observe_retry,
            completed_disc_requests_per_case=3 if observe_retry else 1,
            terminal_pending_disc_request=observe_retry,
            experimental_source_data_patch=([dict(address='0x464a6',width=2,original=16,experimental=13)] if options.experimental_mode3_count13 else []),
            experimental_argument_adapter=([dict(target='0x1ac68',source_selector_argument=16,externally_substituted_argument=13)] if options.experimental_request13 else []),
            experimental_guest_code_overlay=generations['constructor'].get('patches',[]) if options.experimental_selector13 else [],
            saved_selector_ID_matches_acquired_cache_ID_verified=options.experimental_selector13,
            controlled_cache_reselection_and_release_verified=options.experimental_selector13,
            all19_mode3_assets_controlled_lifecycle_verified=options.all_mode3_assets,
            source_descriptors=descriptors if options.all_mode3_assets else {},
            original_image_modified=False,runtime_default_promoted=False,
            new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,
            scope='Source fullCPU constructor/selector/cache/slot/insert/device/loader/copy/CD wrappers and real scheduler yield/idle/resume. '
                  'AllCPU registers/SR/USP/SSP,completeRAM/privateframes,checkedhardware,BIOS args and actual disc events compare at initial/completion/return phases and all deferred resumption/suspension switches. '
                  'Controlled two-context ring,'+('unchanged source scene1descriptor,' if preserve_descriptor else 'scene1tag0/asset0,')+'index0/1/15,completion deferred1/2/4switches,'+('experimental mode3 count13 data word,' if options.experimental_mode3_count13 or options.experimental_selector13 else 'original frozenmode tables,')+'BIOSpreserving adapters,674bytephase '
                  'and external file bytes/progress remain inputs. '+('Separate selector*13 guest-code/count13 overlay; saved selector ID and acquired cache ID13 agree. Controlled additional selector/release calls reuse the cache without a new disc request and check thirteen references1->0, with no machine reset. These host-supplied caller frames are not natural game calls. Not original-image equivalence or author-intent proof; rendering consistency and broader cache lifetime remain unverified. ' if options.experimental_selector13 else 'Experimental source data or acquisition-argument modification, not original-image equivalence or author-intent proof; source selector and its saved ID remain16, so cache release/render consistency is unverified. ' if options.experimental_mode3_count13 or options.experimental_request13 else 'Originalmode3oversizedcopy retained. ')+'Globaldevices/interrupt/timing, '
                  'ordinary boot/natural gameplay and whole-game completeness unverified.'+
                  (' Scene1 asset1 repeatedly requests the same stream under the declared inputs; three completions and three subsequent loader suspensions compared per case. This proves bounded original/C retry behavior, not constructor return or a repair.' if observe_retry else '')+
                  (' All19 observed mode3 marker groups selected through their unchanged source descriptors,plus cache reuses/evictions/revisits,using controlled caller frames. Exact106496bytepayloads,source plane pointers,and13references per selection checked. Source loader/scheduler provide each actual suspension/resume; no memory/device reset between selections. Renderer execution,other descriptor branches,naturalcaller/wholegame unverified.' if options.all_mode3_assets else ''))
        if options.all_mode3_assets:
            report['source_loader_yields']=sum(x['source_loader_yields_observed']for x in results if x['mode']=='native')
            report['source_scheduler_switches']=sum(x['source_scheduler_switches_observed']for x in results if x['mode']=='native')
            report['completed_disc_requests_per_case']=[len(x['completions'])for x in results if x['mode']=='native']
            report['render_input_capture_case']=0
            report['render_input_capture_scope']='Native/C RAM snapshots after supplied selector calls,source loaded bytes/cache/plane pointers. CPU/MMIO/GPU reset/provider fixtures still explicit; not uninterrupted loading-to-rendering or natural-gameplay proof.'
            report['scope']=report['scope'].replace('index0/1/15,','index0,')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'))
        save(ROOT/'verification'/(proof_name+'-current.json'),report);print(report['status'],flush=True)
    except Exception as error:save(out/'failure.json',dict(error=repr(error),phases=phases));raise
    finally:runtime.oracle.close()


if __name__=='__main__':main()
