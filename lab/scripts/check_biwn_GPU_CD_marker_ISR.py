"""Controlled source GPU IRQ1 against pinned original GPU and preserved-CDI BUTCH."""
import ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_overlay_AV as overlay
import check_biwn_movie_GPU as gpu
from check_biwn_main_GPU_boot import Bus,W16
ROOT=overlay.ROOT;save=overlay.save;sha=overlay.sha
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'GPU-CD-marker-ISR-C-generation.json').read_text());src=ROOT/'projects/black-ice-white-noise/restoration';out=ROOT/'verification/BIWN-GPU-CD-marker-ISR'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);library=out/'libGPU-CD-ISR.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_gpu_cd_marker_ISR.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    lib=c.CDLL(str(library));run=lib.biwn_gpu_cd_marker_ISR_run;run.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State),c.c_uint32,c.c_uint32];run.restype=c.c_int;event=lib.biwn_gpu_cd_marker_ISR_assert;event.argtypes=[c.POINTER(Bus),c.POINTER(gpu.State)];event.restype=c.c_int
    previous=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())['instructions_decoded']for n in ['movie','video','media-setup']];runtime=overlay.Runtime(Path(previous['directory'])/'libcontroller-AV.dylib',sum(maps,[]),*maps);core=runtime.core;core.GPUSetIRQLine.argtypes=[c.c_int,c.c_int];core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];core.CDIntfOpenImage.argtypes=[c.c_char_p];core.CDIntfOpenImage.restype=c.c_bool;core.CDROMStateSave.argtypes=[c.c_void_p];core.CDROMStateSave.restype=c.c_size_t;core.BUTCHExec.argtypes=[c.c_uint32]
    assert core.CDIntfOpenImage(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode());core.CDROMInit()
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();payload=bytearray(4096);payload[0x50:0x1a0]=bios[0x84a6+0x382:0x84a6+0x4d2];payload[0x10:0x1c]=bytes.fromhex('981e306400f0d3c0e400e400');results=[];coverage=set();rng=random.Random(0xcd15ac)
    def controller(scenario):
        core.CDROMReset()
        for a,w,v in [(0xdfff00,4,0x180000),(0xdfff04,4,0x10000),(0xdfff10,4,1)]:runtime.device.direct(a,w,v) if a<0x200000 else runtime.write(a,w,v)
        if scenario in [1,2]:runtime.write(0xdfff0a,2,0x7001 if scenario==1 else 0x0400)
        if scenario==3:
            for v in [0x1002,0x113a,0x121b]:runtime.write(0xdfff0a,2,v)
        for _ in range(4 if scenario in [1,2]else 80 if scenario==3 else 0):core.BUTCHExec(0)
    def fixture(case,scenario,bank,ended):
        runtime.mode='native';runtime.gpu=None;runtime.reset(baseline,case%3);controller(scenario);c.memmove(core.GPUGetRAM(),bytes(payload),len(payload));raw=bytearray(overlay.video.gpu_state(core)[0]);regs=[rng.getrandbits(32)for _ in range(64)];regs[31]=0xf04000
        flags=0x20|(0x4000 if bank else 0)|(case%8);struct.pack_into('=64I',raw,4139,*regs);struct.pack_into('=I',raw,4096,0xf031ce);struct.pack_into('=I',raw,4112,flags);struct.pack_into('=I',raw,4128,1);raw[4136:4139]=bytes([flags&1,(flags>>2)&1,(flags>>1)&1]);raw[4395]=bank
        for off,v in [(0x50,0x1c0044 if ended else 0x1bfffc),(0x54,0x1c0040),(0x58,0),(0x5c,16 if case&16 else 0),(0x60,0x53545542)]:raw[off:off+4]=v.to_bytes(4,'big')
        assert core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw)
        for a in range(0x1c0000,0x1c0080,4):runtime.device.direct(a,4,0xa5a5a5a5)
        return bytes(raw)
    def hardware(state=None):
        h=runtime.snapshot()['hardware'];h['GPU']=dict(size=4396,sha256=sha(gpu.logical(state)if state is not None else overlay.video.gpu_state(core)[0][:4396]));b=c.create_string_buffer(200000);n=core.CDROMStateSave(b);assert 0<n<=len(b);h['BUTCH_CDROM']=dict(size=n,sha256=sha(b.raw[:n]));core.CDROMStateExtSave.argtypes=[c.c_void_p];core.CDROMStateExtSave.restype=c.c_size_t;e=c.create_string_buffer(16);m=core.CDROMStateExtSave(e);assert m==9;h['BUTCH_timing_extension']=dict(size=m,sha256=sha(e.raw[:m]));return h
    try:
        for case in range(64):
            scenario=case%4;bank=(case//4)%2;ended=(case//8)%2;initial=fixture(case,scenario,bank,ended);initial_RAM=runtime.device.ram();core.GPUSetIRQLine(1,1);entered=overlay.video.gpu_state(core)[0][:4396];entry_RAM=runtime.device.ram();pcs=[];delays=0;code=c.string_at(core.GPUGetRAM(),4096)
            for _ in range(500):
                pc=core.GPUGetPC()
                if pc==0xf031ce:break
                pcs.append(pc);coverage.add(pc);opcode=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');core.GPUExec(1)
                if opcode>>10 in [52,53]and core.GPUGetPC()!=pc+2:delays+=1;coverage.add(pc+2)
            else:raise AssertionError(('Native CD ISR bound',hex(pc)))
            expected=overlay.video.gpu_state(core)[0][:4396];expected_RAM=runtime.device.ram();expected_hw=hardware()
            runtime.reset(initial_RAM,case%3);controller(scenario);assert core.GPUStateLoad(c.create_string_buffer(initial))==len(initial);state=gpu.state_from_raw(initial);trace=[]
            callbacks=[gpu.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),gpu.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(core.GPUWriteWord(a,v,3),0)[1]),gpu.W32(lambda _,a,v:(core.GPUWriteLong(a,v,3),0)[1]),gpu.OBS(lambda _,pc:trace.append(pc))];bus=Bus(*callbacks,None);counter=runtime.gpu_counter.value
            assert event(c.byref(bus),c.byref(state))==0
            assert gpu.logical(state)==entered and runtime.device.ram()==entry_RAM
            status=run(c.byref(bus),c.byref(state),500,0xf031ce)
            if status or gpu.logical(state)!=expected or runtime.device.ram()!=expected_RAM or hardware(state)!=expected_hw or trace!=pcs or state.instructions!=len(pcs)+delays:
                save(out/'mismatch.json',dict(case=case,scenario=scenario,status=status,native_trace=pcs,C_trace=trace,native_hardware=expected_hw,C_hardware=hardware(state),GPU_differences=[i for i,(a,b)in enumerate(zip(gpu.logical(state),expected))if a!=b][:70],RAM_differences=[i for i,(a,b)in enumerate(zip(runtime.device.ram(),expected_RAM))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert runtime.gpu_counter.value==counter
            results.append(dict(case=case,scenario=scenario,bank=bank,ended=ended,IRQ_frame_match=True,GPU_sha256=sha(expected),RAM_sha256=sha(expected_RAM),instructions=state.instructions,full_GPU_RAM_BUTCH_peripherals_trace_match=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};report=dict(status='resident_BIOS_GPU_CD_IRQ1_source_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(selected&coverage),len(selected)],uncovered_PC=sorted(selected-coverage),both_incoming_banks_verified=True,CDROM_timing_extension_compared=True,full_logical_GPU4396_RAM_BUTCH_peripherals_IRQ_frame_PC_trace_and_counts_compared=True,original_GPU_instructions_on_C_path=0,source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,full_transport_verified=False,limits=['Controlled IRQ1 assertion from resident idle. Source3060 marker handler atF03064/baseF03050, fixedD2=0patch pairs; marker-active and inactive descriptors; empty/7001/0400/0100 seek-reply states,within/afterend and bothbanks. Declared controller ticks; no global/physical IRQ scheduling or concurrent/delay-slot event proof.','Preserved CDI provides BUTCH FIFO/replies; manually seeded transfer descriptor and interrupt event. Full payload stream,BIOS CPU caller,otherD2/encrypted handler variants,firmware boot/playability remain unverified.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/GPU-CD-marker-ISR-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler','uncovered_PC']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:core.CDIntfCloseImage();runtime.oracle.close()
if __name__=='__main__':main()
