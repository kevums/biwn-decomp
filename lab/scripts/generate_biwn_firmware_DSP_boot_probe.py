"""Extend guarded DSP with its observed-ROM failure constant for a diagnostic."""
import hashlib,json
from pathlib import Path
import generate_biwn_firmware_DSP_auth as auth
ROOT=auth.ROOT
rename=lambda s:s.replace('biwn_firmware_DSP_auth','biwn_firmware_DSP_boot_probe').replace('BIWN_FIRMWARE_DSP_AUTH','BIWN_FIRMWARE_DSP_BOOT_PROBE')

def main():
    source=ROOT/'projects/black-ice-white-noise/restoration'
    origin=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T033530.239174Z'
    incoming=(origin/'DSP-at-CPU-wait.bin').read_bytes();raw=incoming[0x560:0x566];assert raw.hex()=='980456781234'
    import generate_biwn_entry_setup_cpu as entry
    extra=entry.loader.base.binary_tools.jaguar_instructions(raw,0xf1b560,'dsp')[0][0]
    body=rename((source/'biwn_firmware_DSP_auth.c').read_text())
    assert 'case 0xf1b560u:'not in body
    body=body.replace('  case 0xf1b566u:',rename(auth.emit(extra))+'\n  case 0xf1b566u:',1)
    header=rename((source/'biwn_firmware_DSP_auth.h').read_text())
    a=header.index('/* Fixed');b=header.index('enum biwn_firmware_DSP_boot_probe_status biwn_firmware_DSP_boot_probe_step',a)
    header=header[:a]+'''/* Diagnostic extension: original guarded DSP decryption/ROM check plus
 * exact source F1B560 MOVEI12345678 failure path. MAME-style DSP-only ROM
 * header view may be supplied by the diagnostic caller; it is NOT proved
 * hardware behavior. No source success/failure result injection, host
 * decrypted-code copy, original DSP execution or runtime opcode decoder.
 * This module alone proves no authentic disc boot or complete game. */
'''+header[b:]
    names=['biwn_firmware_DSP_boot_probe.c','biwn_firmware_DSP_boot_probe.h'];(source/names[0]).write_text(body);(source/names[1]).write_text(header)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'firmware-DSP-auth-generation.json').read_text())
    report=dict(status='generated_unverified_diagnostic',instructions=463,instructions_decoded=sorted(mapping['instructions_decoded']+[extra],key=lambda r:r['address']),source_initial_DSP_origin=str(origin),extra_source_instruction=extra,source_instruction_bytes_hostpatched=False,hardware_ROM_view_verified=False,source_sha256={name:hashlib.sha256((source/name).read_bytes()).hexdigest()for name in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),implementation_authorship='coordinator',whole_game_complete=False)
    (session/'firmware-DSP-boot-probe-generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='instructions_decoded'}))

if __name__=='__main__':main()
