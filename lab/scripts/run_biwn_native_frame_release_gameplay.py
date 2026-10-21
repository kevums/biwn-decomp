"""Fresh native-emulator gameplay pair with a read-only observer for new1AE88code."""
import argparse,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save,make_probe

def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group();group.add_argument('--deck-controls',action='store_true');group.add_argument('--mail-roundtrip',action='store_true');parser.add_argument('--shared-selector-repairs',action='store_true');args=parser.parse_args();frames=3000 if args.mail_roundtrip else 2600 if args.deck_controls else 1600
    build_path=ROOT/'verification/native-frame-release-disc-build-current.json';build=json.loads(build_path.read_text());assert build['status']=='terminal_native_frame_release_disc_built_entry_verified_pending_gameplay'
    assert sha(build['derived_disc'])==build['derived_disc_sha256'];parent=json.loads(Path(build['parent_build']).read_text());assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
    out=ROOT/'verification/native-frame-release-gameplay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    source=ROOT/'scripts/native_gameplay_observer.c';text=source.read_text();start=build['frame_release_entry'];stop=build['resident_address']+build['linked_component_bytes']
    marker='static unsigned candidate,errors;';assert text.count(marker)==1
    text=text.replace(marker,marker+'\nstatic uint64_t frame_ref_entries,frame_ref_old_steps,frame_ref_native_entries,frame_ref_native_steps,frame_ref_returns,frame_ref_nonnegative,frame_ref_ids[32];\nstatic char first_frame_ref_RAM_path[4096];')
    marker='    ram=memory;read_cpu=reader;candidate=(unsigned)selected;';assert text.count(marker)==1
    text=text.replace(marker,marker+'\n    snprintf(first_frame_ref_RAM_path,sizeof(first_frame_ref_RAM_path),"%s.frame-reference-first-RAM.bin",path);')
    marker='    steps++;';assert text.count(marker)==1
    extra=f'''
    if(pc==0x1ae88){{
        struct cpu incoming;read_cpu(&incoming);uint32_t id=rd16(incoming.r[15]+4);
        if(frame_ref_entries<32)frame_ref_ids[frame_ref_entries]=id;
        if(id<0x8000)frame_ref_nonnegative++;
        frame_ref_entries++;emit(pc);
        if(frame_ref_entries==1){{FILE *capture=fopen(first_frame_ref_RAM_path,"wb");
            if(!capture)errors++;else{{if(fwrite(ram,1,0x200000,capture)!=0x200000)errors++;if(fclose(capture))errors++;}}}}
    }}
    if(pc>0x1ae88&&pc<0x1aeda)frame_ref_old_steps++;
    if(pc=={start}u)frame_ref_native_entries++;
    if(pc>={start}u&&pc<{stop}u)frame_ref_native_steps++;
    if(pc=={start+46}u)frame_ref_returns++;
'''
    text=text.replace(marker,marker+extra)
    marker='    array(file,"boundary_entries",boundary_entries,4);fputs("}\\n",file);';assert text.count(marker)==1
    text=text.replace(marker,'''    array(file,"boundary_entries",boundary_entries,4);
    fprintf(file,",\\"frame_reference_entries\\":%llu,\\"frame_reference_old_body_steps\\":%llu,\\"frame_reference_native_entries\\":%llu,\\"frame_reference_native_steps\\":%llu,\\"frame_reference_native_returns\\":%llu,\\"frame_reference_nonnegative_ID_entries\\":%llu",
        (unsigned long long)frame_ref_entries,(unsigned long long)frame_ref_old_steps,(unsigned long long)frame_ref_native_entries,(unsigned long long)frame_ref_native_steps,(unsigned long long)frame_ref_returns,(unsigned long long)frame_ref_nonnegative);
    array(file,"frame_reference_first32_ID_words",frame_ref_ids,frame_ref_entries<32?(unsigned)frame_ref_entries:32);
    fputs("}\\n",file);''')
    observer=out/'frame-reference-observer.c';observer.write_text(text);library=out/'libframe-reference-observer.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'observer-compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0
    control_disc=Path(parent['derived_disc']);candidate_disc=Path(build['derived_disc']);shared_repair=None
    if args.shared_selector_repairs:
        from extract_biwn_stage import swap16
        recipe_path=ROOT/'verification/interactive-preview-recipe.json';recipe=json.loads(recipe_path.read_text());command=recipe['candidate'];overlay_path=Path(command[command.index('--experimental-code-overlay')+1]);overlay=json.loads(overlay_path.read_text());repairs=[row for row in overlay['patches']if int(row['address'],16)in [0x464a6,0x10ac2]]
        assert len(repairs)==2 and sum(len(bytes.fromhex(row['original']))for row in repairs)==38
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);offset=json.loads((session/'nextstage-mapping.json').read_text())['payload_raw_cdi_offset'];copies=[]
        for label,path in [('control',control_disc),('candidate',candidate_disc)]:
            copy=out/(label+'-shared-selector-repaired.cdi');shutil.copyfile(path,copy);intervals=[]
            with copy.open('r+b')as stream:
                for row in repairs:
                    before=bytes.fromhex(row['original']);after=bytes.fromhex(row['replacement']);at=offset+int(row['address'],16)-0x4000;assert len(before)==len(after);stream.seek(at);assert stream.read(len(before))==swap16(before);stream.seek(at);stream.write(swap16(after));intervals.append((at,at+len(before)))
                stream.flush();os.fsync(stream.fileno())
            position=changed=0
            with path.open('rb')as left,copy.open('rb')as right:
                while True:
                    a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                    if not a:break
                    if a!=b:
                        for i,(x,y)in enumerate(zip(a,b)):
                            if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changed+=1
                    position+=len(a)
            copies.append(dict(lane=label,parent=str(path),parent_sha256=sha(path),copy=str(copy),copy_sha256=sha(copy),actual_changed_bytes=changed))
        control_disc=Path(copies[0]['copy']);candidate_disc=Path(copies[1]['copy']);shared_repair=dict(repairs=repairs,overlay=str(overlay_path),overlay_sha256=sha(overlay_path),recipe_sha256=sha(recipe_path),declared_bytes=38,discs=copies,host_guest_RAM_writes=0,scope='Existing selector/count restoration applied identically to both separate CDI copies; not untouched-original behavior.');save(out/'shared-selector-repairs.json',shared_repair)
    original_probe=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';probe=out/'probe.py';probe.write_text(make_probe(original_probe,library,control_disc,Path(build['component'])));compile(probe.read_text(),str(probe),'exec')
    windows=[dict(start_frame=600,stop_frame=1601,buttons=['U','C'])]
    if args.deck_controls:windows += [dict(start_frame=1630,stop_frame=1640,buttons=['1']),dict(start_frame=1660,stop_frame=1670,buttons=['B','C']),dict(start_frame=1800,stop_frame=2000,buttons=['OPTION']),dict(start_frame=2100,stop_frame=2104,buttons=['0'])]
    if args.mail_roundtrip:windows += [dict(start_frame=1630,stop_frame=1640,buttons=['1']),dict(start_frame=1660,stop_frame=1670,buttons=['B','C']),dict(start_frame=1750,stop_frame=1760,buttons=['4']),dict(start_frame=1850,stop_frame=1860,buttons=['A']),dict(start_frame=1950,stop_frame=1960,buttons=['C']),dict(start_frame=2050,stop_frame=2060,buttons=['C']),dict(start_frame=2150,stop_frame=2160,buttons=['0'])]
    inputs=out/'controller-input.json';save(inputs,dict(windows=windows))
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames=frames,deck_controls=args.deck_controls,mail_roundtrip=args.mail_roundtrip,build_proof=str(build_path),build_proof_sha256=sha(build_path),commands=[],checkpoint_restores=0,host_guest_RAM_writes=0,new_training=False,default_promoted=False,whole_game_complete=False,
       source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',source,observer,library,probe,original_probe,inputs,core]},scope='Two freshHLEboot native-emulator lanes of repaired parent versus appended native1AE88disc with identical Up+C input. Observer returns0 and performs no guest writes or ownership. Finite game behavior may differ with native instruction timing; unit-equivalence does not promise per-frame equality. No source CPU/GPU/DSP owners, physical console, full-game or performance proof.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-frame-release-gameplay-current.json',state)
    state['shared_selector_repairs']=shared_repair
    mark();children=[]
    try:
        for lane,disc in [('control',str(control_disc)),('candidate',str(candidate_disc))]:
            command=[sys.executable,'-u',str(probe),'--boot','hle','--frames',str(frames),'--core',str(core),'--disc',disc,'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_fresh_native_frame_release_pair';mark();print('PIDs',[child.pid for _,child,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        observations={lane:json.loads((out/lane/'gameplay-observation.json').read_text())for lane,_,_ in children};reports={lane:json.loads((out/lane/'report.json').read_text())for lane,_,_ in children}
        assert all(len(report['frames'])==frames for report in reports.values());assert not any(o['errors']or o['copy_errors']for o in observations.values())
        current=observations['candidate'];control=observations['control'];assert current['entry_copies']>=1 and current['frame_reference_old_body_steps']==0
        reached=current['frame_reference_native_entries']>0
        if reached:assert current['frame_reference_native_entries']==current['frame_reference_entries']and 0<=current['frame_reference_native_entries']-current['frame_reference_native_returns']<=1
        fields=['video_sha256','raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','navigation']
        differences={k:sum(a.get(k)!=b.get(k)for a,b in zip(reports['candidate']['frames'],reports['control']['frames']))for k in fields}
        pcm_equal=sha(out/'candidate/frontend-PCM.s16le')==sha(out/'control/frontend-PCM.s16le')
        state.update(status='terminal_native_frame_release_gameplay_reached_pending_review'if reached else'terminal_native_frame_release_gameplay_not_reached',observations=observations,frame_differences=differences,PCM_equal=pcm_equal,frame_reference_native_reached=reached,report_sha256={lane:sha(out/lane/'report.json')for lane in reports},control_old_body_exercised=control['frame_reference_old_body_steps']>0);mark();print(json.dumps({k:state[k]for k in ['status','frame_differences','PCM_equal','frame_reference_native_reached']}),flush=True)
    except BaseException as error:state.update(status='terminal_native_frame_release_gameplay_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
