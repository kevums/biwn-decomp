"""Static full CPU rendering-record builder and nested movement submission."""
import hashlib,json
from pathlib import Path
import generate_biwn_resource_cpu as resource
base=resource.base;ROOT=base.ROOT
RANGES={0x170a0:0x17326,0xe220:0xe26c,0xe098:0xe0a6}
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
    rows=[]
    for start,end in RANGES.items():
        assert image[start-0x4000:end-0x4000]==snapshot[start:end]
        decoded,_=base.binary_tools.m68k_instructions(snapshot[start:end],start);rows+=decoded
    prefix=base.PREFIX.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_geometry_records_cpu.py').replace('biwn_input_dispatch_cpu','biwn_geometry_records_cpu').replace('biwn_dispatch_cpu_status','biwn_geometry_records_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_GEOMETRY_RECORDS_CPU')
    prefix=prefix.replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('static uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}\n','')
    suffix=base.SUFFIX.replace('biwn_input_dispatch_cpu','biwn_geometry_records_cpu').replace('biwn_dispatch_cpu_status','biwn_geometry_records_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_GEOMETRY_RECORDS_CPU')
    header='''#ifndef BIWN_GEOMETRY_RECORDS_CPU_H
#define BIWN_GEOMETRY_RECORDS_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_geometry_records_cpu_status {BIWN_GEOMETRY_RECORDS_CPU_OK=0,
 BIWN_GEOMETRY_RECORDS_CPU_BAD_ARGUMENT=1,BIWN_GEOMETRY_RECORDS_CPU_BUS_ERROR=2,
 BIWN_GEOMETRY_RECORDS_CPU_SERVICE_ERROR=3,BIWN_GEOMETRY_RECORDS_CPU_WORK_LIMIT=4,
 BIWN_GEOMETRY_RECORDS_CPU_BAD_RETURN=5,BIWN_GEOMETRY_RECORDS_CPU_YIELDED=6,
 BIWN_GEOMETRY_RECORDS_CPU_BAD_PC=7};
/* Full CPU/source-frame record builder170A0 plus E220/E098 submission.
 * body stops before outer RTS; call consumes it. Both stack banks.
 * Actual E3E0 memory-copy body and GPU4320 math are explicit providers.
 * Builds rendering records from40actors/40static records, without bounds
 * checks absent from source. Use valid finite input/handle/buffer fixtures.
 * No runtime instruction decode/original CPU calls or whole3Dviewport claim. */
enum biwn_geometry_records_cpu_status biwn_geometry_records_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_geometry_records_cpu_status biwn_geometry_records_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
    source=ROOT/'projects/black-ice-white-noise/restoration'
    (source/'biwn_geometry_records_cpu.c').write_text(prefix+'\n'.join(resource.emit(row).replace('BIWN_RESOURCE_CPU','BIWN_GEOMETRY_RECORDS_CPU')for row in rows)+'\n'+suffix)
    (source/'biwn_geometry_records_cpu.h').write_text(header)
    manifest=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,ranges={hex(a):hex(b)for a,b in RANGES.items()},stage_sha256=hashlib.sha256(image).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_geometry_records_cpu.c','biwn_geometry_records_cpu.h']},whole_game_complete=False)
    (session/'geometry-records-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
