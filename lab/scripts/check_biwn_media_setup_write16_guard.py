"""Check the DSP loader's late write16 failure without repeating normal runs."""
import ctypes as c
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as base


def main():
    root=base.ROOT
    report=json.loads((root/'verification/biwn-media-setup-cpu-checks.json').read_text())
    session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'media-setup-fullCPU-generation.json').read_text())
    runtime=base.Runtime(Path(report['directory'])/'libmedia-setup.dylib',mapping['instructions_decoded'])
    initial=base.CPU();initial.registers[:]=[0]*15+[0x1fe000]
    initial.pc=0xe840;initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.sr=0x700
    ram=bytearray((root/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    ram[initial.registers[15]:initial.registers[15]+4]=base.STOP.to_bytes(4,'big');ram=bytes(ram)
    try:
        _,actual,record=runtime.translated(ram,initial,0,fail=('write',2))
        assert record['status']==2 and record['CPU_unchanged'] and bytes(actual)==bytes(initial)
        assert record['ordered_bus_events']>100 # earlier image/MMIO writes remain observable
        data=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='media_setup_late_write16_guard_pass',
            additional_guards=1,primary_guards=report['host_guards'],total_host_guards=report['host_guards']+1,
            primary_report=str(root/'verification/biwn-media-setup-cpu-checks.json'),
            failure=['write',2],result=record,source_sha256=mapping['source_sha256'],
            test_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            normal_source_instruction_coverage_changed=False,limits='Host-error contract only. Earlier source RAM/MMIO writes remain; input CPU is unchanged.')
        (root/'verification/biwn-media-setup-write16-guard.json').write_text(json.dumps(data,indent=2)+'\n')
        print(json.dumps(dict(total_host_guards=data['total_host_guards'],normal_coverage_changed=False)))
    finally:runtime.oracle.close()


if __name__=='__main__':main()
