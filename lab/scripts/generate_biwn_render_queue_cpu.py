"""Fixed fullCPU blocks for render loop, queue consumer/reset and sprite mailbox."""
import hashlib,json
from pathlib import Path
import generate_biwn_resource_cpu as resource
base=resource.base;ROOT=base.ROOT
def emit(row):
    op,_,tail=row['assembly'].partition(' ');kind=op.split('.')[0]
    if kind=='bset':
        bit,dest=base.split(tail);assert op=='bset.b';n=base.number(bit);assert 0<=n<8
        return '  case '+hex(row['address'])+'u: /* '+row['assembly']+' */\n   '+resource.load(dest,1)+f's.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((v&(1u<<{n}))?0:4u));v|=1u<<{n};'+resource.store(dest,1)+f's.cpu.pc={hex(row["address"]+row["size"])}u;break;'
    return resource.emit(row).replace('BIWN_RESOURCE_CPU','BIWN_RENDER_QUEUE_CPU')
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'live-render-queue-fullCPU-workmap.json').read_text());image=(session/'nextstage-68000-candidate.bin').read_bytes();ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(image).hexdigest()==mapping['stage_sha256'];rows=sum([f['instructions']for f in mapping['functions']],[]);assert len(rows)==78
    for r in rows:assert ram[r['address']:r['address']+r['size']].hex()==r['bytes']==image[r['address']-0x4000:r['address']-0x4000+r['size']].hex()
    prefix=base.PREFIX.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_render_queue_cpu.py').replace('biwn_input_dispatch_cpu','biwn_render_queue_cpu').replace('biwn_dispatch_cpu_status','biwn_render_queue_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_RENDER_QUEUE_CPU')
    prefix=prefix.replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];').replace('||(state->sr&0x2000u)','')
    suffix=base.SUFFIX.replace('biwn_input_dispatch_cpu','biwn_render_queue_cpu').replace('biwn_dispatch_cpu_status','biwn_render_queue_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_RENDER_QUEUE_CPU')
    header='''#ifndef BIWN_RENDER_QUEUE_CPU_H
#define BIWN_RENDER_QUEUE_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_render_queue_cpu_status {BIWN_RENDER_QUEUE_CPU_OK=0,
 BIWN_RENDER_QUEUE_CPU_BAD_ARGUMENT=1,BIWN_RENDER_QUEUE_CPU_BUS_ERROR=2,
 BIWN_RENDER_QUEUE_CPU_SERVICE_ERROR=3,BIWN_RENDER_QUEUE_CPU_WORK_LIMIT=4,
 BIWN_RENDER_QUEUE_CPU_BAD_RETURN=5,BIWN_RENDER_QUEUE_CPU_YIELDED=6,
 BIWN_RENDER_QUEUE_CPU_BAD_PC=7};
/* Fixed source CPU effects for17DC2renderloop,EA20reset,EA28consumer,
 * E2B8spriteCPUmailbox,E098GPUwait. FullCPU/internal-PC/sourceframes.
 * body stops at outerRTS, call consumesRTS. Renderloop is unbounded and
 * should use stop_on_yield1, leaving DF60 and its return frame intact.
 * Helper providers execute bodies up toRTS. GPU/device behavior and
 * scene17E0E/overlay181F8 are explicit dependencies; no full-game claim.
 * No runtime CPU instruction decode or original CPU/GPU execution. */
enum biwn_render_queue_cpu_status biwn_render_queue_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_render_queue_cpu_status biwn_render_queue_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
    source=ROOT/'projects/black-ice-white-noise/restoration';text=prefix+'\n'.join(emit(r)for r in rows)+'\n'+suffix;(source/'biwn_render_queue_cpu.c').write_text(text);(source/'biwn_render_queue_cpu.h').write_text(header)
    manifest={'status':'generated_unverified','instructions':78,'instructions_decoded':rows,'stage_sha256':mapping['stage_sha256'],'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_render_queue_cpu.c','biwn_render_queue_cpu.h']},'whole_game_complete':False};(session/'render-queue-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
