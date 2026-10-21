"""Assemble local source for the exact existing marker repair, then derive CDIs.
Only the18byte declared game fragment changes from each preserved baseline.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
from check_biwn_native_button_digit import ROOT,sha,save
from extract_biwn_stage import swap16,IMAGE_SHA
ADDRESS=0x1b0ee

def main():
    ap=ROOT/'verification/local-native-word-scan-current.json';author=json.loads(ap.read_text());source=Path(author['candidate']);assert sha(source)==author['candidate_sha256']
    text=source.read_text();assert not re.search(r'(?im)^\s*\.(?:byte|word|long|incbin|org)\b',text)
    legacy_path=ROOT/'verification/elevator-word-scan-overlay.json';legacy=json.loads(legacy_path.read_text())['patches'][0]
    baseline_path=ROOT/'verification/native-controller-lean-disc-build-current.json';baseline=json.loads(baseline_path.read_text())
    for p,digest in baseline['source_sha256'].items():assert sha(p)==digest,p
    assert sha(baseline['derived_disc'])==baseline['derived_disc_sha256'] and sha(baseline['original_disc'])==IMAGE_SHA
    out=ROOT/'builds/BIWN-native-word-scan'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),author_proof=str(ap),author_proof_sha256=sha(ap),baseline_proof=str(baseline_path),baseline_proof_sha256=sha(baseline_path),source=str(source),source_sha256=sha(source),raw_local_assembly_unchanged=True,new_training=False,native_Chat=False,whole_game_complete=False,physical_console=False)
    def mark():save(out/'build.json',state);save(ROOT/'verification/native-word-scan-build-active.json',state)
    mark()
    try:
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');linker=out/'marker-word-scan.ld';linker.write_text('ENTRY(biwn_marker_word_scan)\nPROVIDE(biwn_marker_run = 0x1b100);\nPROVIDE(biwn_marker_scan_failure = 0x1b122);\nSECTIONS { .text 0x1b0ee : SUBALIGN(2) { *(.text*) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }\nASSERT(SIZEOF(.text)==18,"Marker repair must remain18bytes")\n')
        commands=[[prefix+'as','-m68000','--register-prefix-optional','-o',str(out/'marker.o'),str(source)],[prefix+'ld','-T',str(linker),'-o',str(out/'marker.elf'),str(out/'marker.o')],[prefix+'objcopy','-O','binary',str(out/'marker.elf'),str(out/'marker.bin')]]
        log=''
        for command in commands:
            p=subprocess.run(command,capture_output=True,text=True);log+=p.stdout+p.stderr;(out/'compile.log').write_text(log);assert p.returncode==0,p.stderr
        symbols={row.split()[-1]:int(row.split()[0],16)for row in subprocess.check_output([prefix+'nm','--defined-only',str(out/'marker.elf')],text=True).splitlines()if len(row.split())==3}
        assert symbols['biwn_marker_word_scan']==ADDRESS and symbols['biwn_marker_run']==0x1b100 and symbols['biwn_marker_scan_failure']==0x1b122
        binary=out/'marker.bin';patch=binary.read_bytes();assert patch.hex()==legacy['replacement'] and len(patch)==18
        (out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-d',str(out/'marker.elf')],text=True))
        native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';shutil.copy2(source,native/'marker-word-scan.S');shutil.copy2(linker,native/'marker-word-scan.ld')
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset']+ADDRESS-0x4000
        images={};expected=bytes.fromhex(legacy['original']);assert len(expected)==len(patch)
        for lane,input_disc,expected_hash in [('original_repaired',baseline['original_disc'],baseline['original_disc_sha256']),('native_repaired',baseline['derived_disc'],baseline['derived_disc_sha256'])]:
            assert sha(input_disc)==expected_hash;disc=out/('BIWN-23-'+lane.replace('_','-')+'-word-scan.cdi');shutil.copyfile(input_disc,disc)
            with disc.open('r+b')as f:
                f.seek(offset);assert f.read(len(patch))==swap16(expected);f.seek(offset);f.write(swap16(patch));f.flush();os.fsync(f.fileno())
            differences=position=0
            with Path(input_disc).open('rb')as left,disc.open('rb')as right:
                while True:
                    a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                    if not a:break
                    if a!=b:
                        for i,(x,y)in enumerate(zip(a,b)):
                            if x!=y:assert offset<=position+i<offset+18;differences+=1
                    position+=len(a)
            assert sha(input_disc)==expected_hash and position==Path(input_disc).stat().st_size
            images[lane]=dict(disc=str(disc),sha256=sha(disc),baseline=input_disc,baseline_sha256=expected_hash,changed_bytes=differences,all_other_bytes_and_metadata_preserved=True)
        # Also save a mainstage representation for isolated CPU checks.
        stage=bytearray(Path(baseline['derived_stage']).read_bytes());assert stage[ADDRESS-0x4000:ADDRESS-0x4000+18]==expected;stage[ADDRESS-0x4000:ADDRESS-0x4000+18]=patch;(out/'mainstage-native-repaired.bin').write_bytes(stage)
        state.update(status='terminal_source_assembled_marker_CDIs_pending_native_checks',images=images,original_fragment=expected.hex(),repaired_fragment=patch.hex(),repair_address=ADDRESS,repair_bytes=18,actual_changed_bytes=sum(a!=b for a,b in zip(expected,patch)),binary=str(binary),binary_sha256=sha(binary),ELF=str(out/'marker.elf'),linked_at=ADDRESS,compile_commands=commands,canonical_source=str(native/'marker-word-scan.S'),canonical_source_sha256=sha(native/'marker-word-scan.S'),linker=str(linker),linker_sha256=sha(linker),legacy_overlay=str(legacy_path),legacy_overlay_sha256=sha(legacy_path),legacy_repair_bytes_equal=True,linker_preflight_fix='First linker aligned text to1B0F0. Explicit1B0EE outputaddress and SUBALIGN(2) now enforce the original word-aligned location; symbols/18bytes checked before any CDIcopy.',assembler_option_note='Local Author used bare uppercase registers despite requested GNU percent syntax. Unchanged source is assembled with documented --register-prefix-optional; no manual source edits.',baseline_native_entries=13,new_complete_function_entries=0,scope='Same existing18byte scan repair now assembled from local-model source and installed on disc before boot. Two derivatives isolate repair on original and native13baselines. Complete marker-run/payload code and other original providers remain; no physical boot/full-game proof and no generally bounds-safe-parser claim.',source_dependencies_sha256={str(p):sha(p)for p in [Path(__file__),source,linker,baseline_path,legacy_path,native/'marker-word-scan.S',native/'marker-word-scan.ld']})
        mark();save(ROOT/'verification/native-word-scan-build-current.json',state);print(state['status'],{k:v['changed_bytes']for k,v in images.items()},flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
