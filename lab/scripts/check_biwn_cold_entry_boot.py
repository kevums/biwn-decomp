"""Actual4000 CPU caller through helpers/GPU/music acknowledgement to DD40.

BIOS ABI/TOC and processor alternation are declared providers. No mailbox
completion script, processor-setup calls or captured initialized CPU supplied.
"""
import ctypes as c,json,os,random,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_boot_exit_AV as source
import check_biwn_full_video_cpu_gpu as video
import check_biwn_dsp_media_audio as dsp
from check_biwn_music_DSP_bootstrap import Bus as MusicBus,W16
ROOT=source.ROOT;media=source.media;save=source.save;sha=source.sha
BIOS={0x3000,0x3048,0x3006,0x305a}
from check_biwn_source_entry_boot import Runtime
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);out=ROOT/'verification/BIWN-cold-source4000-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration'
    prior=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());names=list(prior['source_sha256'])+['biwn_entry_setup_cpu.c','biwn_dsp_music_bootstrap.c'];library=out/'libsource-entry.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup','entry-setup','GPU-boot','geometry-records']];rows=sum((m['instructions_decoded']for m in maps),[]);Runtime.entry_rows=maps[3]['instructions_decoded'];runtime=Runtime(library,rows,*[m['instructions_decoded']for m in maps[:3]]);runtime.entry_coverage=set();layout=json.loads((session/'cdi-layout.json').read_text());runtime.entry_TOC=source.controller.make_toc(layout);stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert sha(stage)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';base=bytearray(0x200000);base[0x4000:0x4000+len(stage)]=stage;base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();results=[]
    try:
        for case in range(2):
            observed={};RAM={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',case=case,mode=mode));observed[mode],checks=runtime.source_entry(bytes(base),case,mode);RAM[mode]=runtime.device.ram();save(out/f'case-{case}-{mode}.json',observed[mode]);(out/f'case-{case}-{mode}-RAM.bin').write_bytes(RAM[mode])
            if observed['native']!=observed['C']or RAM['native']!=RAM['C']:save(out/'mismatch.json',observed);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(case=case,snapshot=observed['C'],checks=checks));save(out/'cases.json',results)
        report=dict(status='source4000_CPU_helpers_GPU_boot_music_command2_to_DD40_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),entry_CPU_coverage=[len(runtime.entry_coverage&runtime.entry_addresses),len(runtime.entry_addresses)],covered_CPU_PC=sorted(runtime.entry_coverage),source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,DSP_mailbox_completion_script=False,initial_processor_setup_calls_supplied=False,source4000_to_DD40_caller_verified_with_declared_providers=True,initial_FrozenRAM_supplied=False,initial_main_RAM_zero_plus_pinned_stage=True,initial_stage_sha256=sha(stage),global_boot_verified=False,whole_game_complete=False,limits=['Zero mainRAM plus pinned source stage, supplied initialCPU/device seed and canonical pre-relocation GPU payload; BIOS3000/3048/3006 preserve-register adapters and305A syntheticTOC from source disc layout, not firmware. DefaultNTSC only.','Actual source4000 caller/DFF4/D340/E6A0/E00A/1557A/17340/E942/E7AA executes continuously toDD40. Native/C completeCPU/bothstackbanks/private2MBRAM/logicalGPU4396/DSP8496/peripherals/BIOSargs andGPU/DSPtraces compare.','Source musicDSP flags init beforeCPUcommand2 and handler beforeCPUmailboxpoll are explicit processor alternation boundaries; actualperiod/interleaving/global clocks/musicmixer/bank1/SSI output/fullsourceDD40startup and game/physicalscanout are not included in this standalone proof.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/cold-source4000-entry-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','covered_CPU_PC','compiler']}))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
