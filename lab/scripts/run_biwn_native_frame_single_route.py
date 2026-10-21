"""Fresh scene route for native1AE56 with read-only ABI/cache monitoring."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

WATCH=r'''
static int32_t (*next_owner)(uint32_t);
void set_next_owner(void *fn){next_owner=(int32_t(*)(uint32_t))fn;}
static uint64_t single_entries,single_native_entries,single_returns,single_old_steps;
static uint64_t single_nonnegative,single_expected_decrements,single_zero_refs,single_no_matches;
static uint64_t single_monitor_errors,single_native_steps;
static unsigned pending;
static struct cpu incoming;
static uint8_t expected_cache[144];
static uint32_t expected_d0,expected_d1,min_SP;
static uint32_t entry_task,max_private_depth,user_min_headroom=0xffffffffu;
static uint64_t user_stack_observations,user_stack_outside;
static uint16_t expected_sr;
static void watch_single(uint32_t pc){
    if(pc==0x1ae56){
        if(pending)single_monitor_errors++;
        pending=1;read_cpu(&incoming);min_SP=incoming.r[15];entry_task=rd32(0xc0920);single_entries++;emit(pc);
        uint32_t id=rd16(incoming.r[15]+4);if(id<0x8000)single_nonnegative++;
        memcpy(expected_cache,ram+0x15b4a0,144);
        unsigned index;
        for(index=0;index<36;index++){
            if(rd16(0x15b4a0+index*4)==id){
                uint32_t refs=rd16(0x15b4a2+index*4);
                if(refs){uint16_t v=(uint16_t)(refs-1);expected_cache[index*4+2]=(uint8_t)(v>>8);expected_cache[index*4+3]=(uint8_t)v;single_expected_decrements++;}
                else single_zero_refs++;
                break;
            }
        }
        if(index==36)single_no_matches++;
        expected_d0=index==36?140:index*4;
        expected_d1=(incoming.r[1]&0xffff0000u)|index;
        expected_sr=(uint16_t)((incoming.sr&0xffe0u)|(incoming.r[2]==0?4:0)|((incoming.r[2]&0x80000000u)?8:0));
    }
    if(pc>0x1ae56&&pc<0x1ae88)single_old_steps++;
    if(pc==SINGLE_ENTRY)single_native_entries++;
    if((pc>=SINGLE_START&&pc<SINGLE_END)||pc==0x1ae86){
        struct cpu current;read_cpu(&current);if(pc>=SINGLE_START&&pc<SINGLE_END)single_native_steps++;
        if(current.r[15]<min_SP)min_SP=current.r[15];
        if(pending&&!(current.sr&0x2000u)){
            uint32_t task=rd32(0xc0920),sp=current.r[15];user_stack_observations++;
            if(task!=entry_task||!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)user_stack_outside++;
            else if(sp-task-38u<user_min_headroom)user_min_headroom=sp-task-38u;
        }
        if(pc==SINGLE_RETURN||pc==0x1ae86){
            single_returns++;
            if(incoming.r[15]-min_SP>max_private_depth)max_private_depth=incoming.r[15]-min_SP;
            if(!pending||current.r[0]!=expected_d0||current.r[1]!=expected_d1||current.r[8]!=0x15b4a0||current.sr!=expected_sr)single_monitor_errors++;
            for(unsigned i=2;i<16;i++)if(i!=8&&current.r[i]!=incoming.r[i])single_monitor_errors++;
            if(rd32(incoming.r[15]-4)!=incoming.r[2]||memcmp(expected_cache,ram+0x15b4a0,144))single_monitor_errors++;
            pending=0;
        }
    }
}
'''
REPORT=r'''
    fprintf(file,",\"single_entries\":%llu,\"single_native_entries\":%llu,\"single_returns\":%llu,\"single_old_steps\":%llu,\"single_nonnegative_ID_entries\":%llu,\"single_expected_reference_decrements\":%llu,\"single_zero_reference_matches\":%llu,\"single_no_matches\":%llu,\"single_monitor_errors\":%llu,\"single_native_steps\":%llu,\"single_pending\":%u",
        (unsigned long long)single_entries,(unsigned long long)single_native_entries,(unsigned long long)single_returns,(unsigned long long)single_old_steps,(unsigned long long)single_nonnegative,(unsigned long long)single_expected_decrements,(unsigned long long)single_zero_refs,(unsigned long long)single_no_matches,(unsigned long long)single_monitor_errors,(unsigned long long)single_native_steps,pending);
    fprintf(file,",\"single_user_stack_observations\":%llu,\"single_user_stack_outside\":%llu,\"single_user_min_headroom\":%u,\"single_max_private_depth\":%u",
        (unsigned long long)user_stack_observations,(unsigned long long)user_stack_outside,user_min_headroom,max_private_depth);
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--same-layout-control',action='store_true');args=parser.parse_args()
    bp=ROOT/'verification/native-frame-single-disc-build-current.json';build=json.loads(bp.read_text());assert build['status']=='terminal_native_frame_single_disc_built_entry_verified_pending_gameplay';assert sha(build['derived_disc'])==build['derived_disc_sha256']
    parent_path=ROOT/'verification/external-DSP-combined-route-current.json';parent=json.loads(parent_path.read_text());assert parent['status']=='terminal_initial_entry_external_DSP_combined_merchant_equal';assert json.loads(Path(build['parent_build']).read_text())['derived_disc']==parent['command'][parent['command'].index('--disc')+1]
    template=Path(parent['directory'])/'probe.py';assert sha(template)==parent['source_sha256'][str(template)]
    out=ROOT/'verification/native-frame-single-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    disc=Path(build['derived_disc']);control_delta=None
    if args.same_layout_control:
        from extract_biwn_stage import swap16
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);offset=json.loads((session/'nextstage-mapping.json').read_text())['payload_raw_cdi_offset']+0x1ae56-0x4000
        patches=json.loads(Path(build['patch_manifest']).read_text())['delta_patches'];row=next(row for row in patches if int(row['address'],16)==0x1ae56);before=bytes.fromhex(row['replacement']);after=bytes.fromhex(row['original']);assert len(before)==len(after)==6
        disc=out/'BIWN-native-single-same-layout-original-entry-control.cdi';shutil.copyfile(build['derived_disc'],disc)
        with disc.open('r+b')as stream:stream.seek(offset);assert stream.read(6)==swap16(before);stream.seek(offset);stream.write(swap16(after));stream.flush();os.fsync(stream.fileno())
        position=changes=0
        with Path(build['derived_disc']).open('rb')as left,disc.open('rb')as right:
            while True:
                a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                if not a:break
                if a!=b:
                    for i,(x,y)in enumerate(zip(a,b)):
                        if x!=y:assert offset<=position+i<offset+6;changes+=1
                position+=len(a)
        control_delta=dict(address='0x1ae56',before=before.hex(),after=after.hex(),actual_changed_bytes=changes,source=str(build['derived_disc']),source_sha256=build['derived_disc_sha256'],control=str(disc),control_sha256=sha(disc));save(out/'control-six-byte-delta.json',control_delta)
    source=ROOT/'scripts/native_gameplay_observer.c';text=source.read_text();watched=WATCH.replace('SINGLE_ENTRY',hex(build['frame_single_entry'])+'u').replace('SINGLE_START',hex(build['payload_start'])+'u').replace('SINGLE_END',hex(build['resident_address']+build['linked_component_bytes'])+'u').replace('SINGLE_RETURN',hex(build['frame_single_entry']+46)+'u')
    marker='int32_t observe(uint32_t pc) {';assert text.count(marker)==1;text=text.replace(marker,watched+'\n'+marker)
    marker='    steps++;';assert text.count(marker)==1;text=text.replace(marker,marker+'\n    watch_single(pc);')
    marker='    return 0;\n}\nstatic void array';assert text.count(marker)==1;text=text.replace(marker,'    int32_t result=next_owner?next_owner(pc):0;if(result)errors++;return result;\n}\nstatic void array')
    marker='    array(file,"rng_entries",rng_entries,8);';assert text.count(marker)==1;text=text.replace(marker,REPORT+'\n'+marker)
    observer=out/'single-reference-observer.c';observer.write_text(text);library=out/'libsingle-reference-observer.dylib';compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'observer-build.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    text=template.read_text();marker="        rom = c.c_void_p.in_dll(core, 'jaguarMainROM').value";assert text.count(marker)==1
    install=f'''        assert args.CPU_mode=='reference'
        observer=c.CDLL({str(library)!r})
        observer_payload=c.create_string_buffer(Path({build['component']!r}).read_bytes())
        observer.begin_observe.argtypes=[c.c_void_p,c.c_void_p,c.c_int,c.c_void_p,c.c_uint32,c.c_char_p];observer.begin_observe.restype=c.c_int
        assert observer.begin_observe(ram_pointer,c.cast(core.BIWNReadCPUState,c.c_void_p),1,observer_payload,len(observer_payload.raw)-1,str(out/'gameplay-events.bin').encode())==0
        observer.set_next_owner.argtypes=[c.c_void_p];observer.set_next_owner(c.cast(owner,c.c_void_p))
        WATCH_OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32);watch_owner=WATCH_OWNER(('observe',observer));core.BIWNSetCPUExecOwner.argtypes=[WATCH_OWNER,c.c_int];core.BIWNSetCPUExecOwner(watch_owner,0)
        observer.set_frame.argtypes=[c.c_uint32]
'''
    text=text.replace(marker,install+marker);marker='            current_frame = i+1';assert text.count(marker)==1;text=text.replace(marker,marker+'\n            observer.set_frame(current_frame)')
    marker="        report['C_processor_backends']=finish_processors()";at=text.rindex(marker)
    finish="        observer.finish_observe.argtypes=[c.c_char_p];observer.finish_observe.restype=c.c_int\n        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0\n        report['native_compiled_game_C_execution']=True\n"
    text=text[:at]+finish+text[at:]
    old="report['C_CPU_backend']['scope']='SourceCPUfromHLEpreparedinitialPC,not gatedat4000; no originalCPUopcodefallback duringthe testedframes. SourceGPU/DSP/IRQ selection+entry; platformHLE,devices,blitter/OP,IRQlines+ACK/commit/prefetch/emulatorcostservices retained.'";assert text.count(old)==1;text=text.replace(old,"report['C_CPU_backend']['scope']='Retained native emulator CPU/GPU/DSP/IRQ execute the derived disc,including compiled native68000routine1AE56. No host source-instruction processor replacements; read-only observer chains the original reference callback.'")
    probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    command=list(parent['command']);command[2]=str(probe);command[command.index('--CPU-mode')+1]='reference';command[command.index('--disc')+1]=str(disc);command[command.index('--output')+1]=str(out/'candidate')
    state=dict(status='running_fresh_native_frame_single_merchant_route',pid=os.getpid(),directory=str(out),command=command,build_proof=str(bp),build_proof_sha256=sha(bp),native_reference_reused=True,reference=parent['reference'],checkpoint_restores=0,host_guest_RAM_writes=0,frame_single_entry=build['frame_single_entry'],new_training=False,default_promoted=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',observer,library,probe,template,Path(parent['reference'])/'report.json',Path(parent['reference'])/'frontend-PCM.s16le']},scope='Fresh derived native68000disc through the full adaptive merchant/media/outdoor route. Original emulator processors/platform retained. Read-only observer chains unchanged reference callback and checks live1AE56caller registers/CCR/cache at compiled returns. No source CPU/GPU/DSPowners,guest writes or savestate restore. Exact old per-frame equality is measured,not assumed across compiled-code timing/layout changes.')
    state.update(same_layout_control=args.same_layout_control,control_delta=control_delta,stack_model='Existing source task context header38bytes,allocation0x404;measure usermode accesses only,with current task read atC0920. Original and compiled returns monitored separately.')
    pointer=ROOT/'verification'/('native-frame-single-layout-control-current.json'if args.same_layout_control else'native-frame-single-route-current.json')
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark()
    try:
        with(out/'candidate.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
        state['exit_code']=code;assert code==0,'Native scene route failed; retain exact child outputs'
        report=json.loads((out/'candidate/report.json').read_text());control=json.loads((Path(parent['reference'])/'report.json').read_text());observed=json.loads((out/'candidate/gameplay-observation.json').read_text());assert not observed['errors']and not observed['copy_errors']and not report['C_CPU_backend']['stats']['errors']
        last=report['frames'][-1];returned=last['player_mode_word']==1 and last['floor_word']==0 and last['navigation']['outdoor_hold']>=120
        fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256','navigation'];different={key:sum(a[key]!=b[key]for a,b in zip(report['frames'],control['frames']))for key in fields};PCM_equal=sha(out/'candidate/frontend-PCM.s16le')==sha(Path(parent['reference'])/'frontend-PCM.s16le')
        reached=observed['single_native_entries']>0
        body_ownership=observed['single_native_entries']==0 and observed['single_old_steps']>0 if args.same_layout_control else reached and observed['single_entries']==observed['single_native_entries']and observed['single_old_steps']==0
        monitor_pass=body_ownership and observed['single_entries']==observed['single_returns']and observed['single_monitor_errors']==observed['single_pending']==observed['single_user_stack_outside']==0 and observed['single_user_stack_observations']>0
        state.update(status='terminal_native_frame_single_route_pending_review',frames=len(report['frames']),reference_frames=len(control['frames']),compared_prefix_frames=min(len(report['frames']),len(control['frames'])),frame_differences=different,PCM_equal=PCM_equal,nonzero_audio_samples=report['audio']['nonzero_samples'],returned_outdoors=returned,native_single_reached=reached,live_monitor_pass=monitor_pass,observations=observed,report_sha256=sha(out/'candidate/report.json'));mark();print(json.dumps({k:state[k]for k in ['status','frames','frame_differences','PCM_equal','returned_outdoors','native_single_reached','live_monitor_pass']}),flush=True)
    except BaseException as error:state.update(status='terminal_native_frame_single_route_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
