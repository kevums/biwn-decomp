"""Source game180000 prefix/actual BIOS/bootGPU/marker FIFO to natural4000."""
import ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_ROM_install_scheduled_startup as original
import check_biwn_full_video_cpu_gpu as video
from biwn_game_firstboot_runtime import GameFirstbootMixin
ROOT=original.ROOT;save=original.save;sha=original.sha
class Runtime(GameFirstbootMixin,original.Runtime):pass
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);previous=json.loads((ROOT/'verification/ROM-install-movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json').read_text());out=ROOT/'verification/BIWN-game-firstboot-to-stage'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration'
    names=list(previous['source_sha256'])+['biwn_game_firstboot_cpu.c','biwn_game_firstboot_GPU.c','biwn_gpu_cd_marker_ISR.c','biwn_bios_marker_setup_cpu.c'];lib=out/'libfirstboot-stage.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);
    if build.returncode:save(out/'status.json',dict(status='terminal_compile_failed',error=build.stderr));raise AssertionError(build.stderr)
    rows=[]
    for p in session.glob('*-fullCPU-generation.json'):rows+=json.loads(p.read_text()).get('instructions_decoded',[])
    mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];ram=bytearray(0x200000);boot=(session/'boot-payload-68000-candidate.bin').read_bytes();ram[0x180000:0x180000+len(boot)]=boot;assert ram[0x4000:0x100000]==bytes(1032192)
    disc=original.base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';Runtime.entry_rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded'];runtime=Runtime(lib,rows,*[m['instructions_decoded']for m in mappings],disc=disc,out=out,frame_directory=frames);runtime.entry_coverage=set();results=[]
    try:
        for case in range(2):
            states={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',case=case,mode=mode));cpu,snapshot=runtime.firstboot_to_stage(bytes(ram),case,mode);states[mode]=snapshot;save(out/f'case-{case}-{mode}.json',snapshot);(out/f'case-{case}-{mode}-RAM.bin').write_bytes(runtime.device.ram());(out/f'case-{case}-{mode}-GPU.bin').write_bytes(video.gpu_state(runtime.core)[0][:4396]if mode=='native'else video.logical(runtime.gpu))
            if states['native']!=states['C']:
                save(out/'mismatch.json',dict(native=states['native'],C=states['C']));raise AssertionError(str(out/'mismatch.json'))
            assert (out/f'case-{case}-native-RAM.bin').read_bytes()==(out/f'case-{case}-C-RAM.bin').read_bytes()
            assert states['C']['marker_request']==dict(D0=0x023217,D1=0x53545542,D2=0,A0=0x4000,A1=0x100000)
            results.append(dict(case=case,CPU=states['C']['CPU'],controller_ticks=states['C']['controller_ticks'],GPU_IRQs=states['C']['GPU_IRQs'],stage_sha256=sha(runtime.device.ram()[0x4000:0x100000]),full_snapshot_RAM_match=True));save(out/'cases.json',results)
        selected=runtime.firstboot_rows;report=dict(status='source_game180000_actual_BIOS_GPU_marker_stream_to4000_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_CPU_instruction_coverage=[len(selected&runtime.fb_CPU_coverage),len(selected)],stage_sha256=results[0]['stage_sha256'],initial_game_stage_hostloaded=False,initial60000byte_boot_stub_supplied=True,natural_CPU_jump_to4000=True,full_firmware_boot_verified=False,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),whole_game_complete=False,limits=['Supplied pinned60000byte BIOS-loaded game boot payload, userBIOSROM and initial CPU/GPU/DSP/device seed includingGPU R31. Actual ROM resident copy precedes declared host-invoked3048/3006/305A firmware TOC prelude. This is not preceding/authenticated/complete firmware boot.', 'Source180000 video/500long GPU copy/mode3/3060 marker setup selects TOCtrack2/minus6frames, reads STUB16long marker stream into4000..100000, polls strictlypastend, stopsI2S/GPU and naturally JMP4000. Explicit controller ticks per source poll and fixedVCOUNT4/synchronousGPU work remain timing providers; no CPU/GPU reset or payload copy during loader.','GPU init/poll/markerIRQ/shutdown and all reached BIOS CPU code run as fixed C on C path. CompleteCPU/privateRAM/logicalGPU-DSP/controller baseline+9byte extension/peripherals/events/trace counts match. Other boot/caller/data/region/timing variants and later game entry integration remain unverified.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/game-firstboot-to-stage-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256']}))
    except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error),errors=runtime.errors[-5:]));raise
    finally:runtime.core.CDIntfCloseImage();runtime.oracle.close();disc.close()
if __name__=='__main__':main()
