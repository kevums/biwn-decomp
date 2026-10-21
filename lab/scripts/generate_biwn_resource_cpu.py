"""Static full-CPU C for resource/memory/copy callers; no runtime decoding."""
import hashlib,json,re
from pathlib import Path
import generate_biwn_input_dispatch_cpu as base
ROOT=base.ROOT
RANGES={0x1b002:0x1b044,0x1af04:0x1b002,0x1545c:0x1557a,0x152a2:0x1545c,0x15200:0x152a2,0x1b044:0x1b154,0xe3e0:0xe4aa}
# A private build-time namespace permits new addressing forms without
# changing the accepted dispatcher generator or its generated C bytes.
ns={'__name__':'resource_codegen_base','__file__':str(Path(base.__file__))}
exec(compile(Path(base.__file__).read_text(),base.__file__,'exec'),ns)
old_load=ns['load'];old_store=ns['store']
def load(text,width,name='v'):
    m=re.fullmatch(r'\((a[0-7])\)\+',text)
    if m:
        reg=base.register(m[1]);step=2 if width==1 and reg==15 else width
        return f'CHECK(read_value(&s,s.cpu.registers[{reg}],{width},&{name}));s.cpu.registers[{reg}]+={step};bank(&s);'
    return old_load(text,width,name)
def store(text,width,name='v'):
    m=re.fullmatch(r'\((a[0-7])\)\+',text)
    if m:
        reg=base.register(m[1]);step=2 if width==1 and reg==15 else width
        return f'CHECK(write_value(&s,s.cpu.registers[{reg}],{width},{name}));s.cpu.registers[{reg}]+={step};bank(&s);'
    return old_store(text,width,name)
ns['load']=load;ns['store']=store
def indices(text):
    result=[]
    for part in text.split('/'):
        ends=part.split('-');first=base.register(ends[0]);last=base.register(ends[-1]);assert first is not None and last is not None;result.extend(range(first,last+1))
    return result
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=base.split(tail);kind=op.split('.')[0];width={'b':1,'w':2,'l':4}.get(op[-1],4);code=None;terminal=False
    if kind=='movem':
        if parts[1]=='-(a7)':code=[f'CHECK(push(&s,s.cpu.registers[{r}],4));'for r in reversed(indices(parts[0]))]
        else:assert parts[0]=='(a7)+';code=[f'CHECK(read_value(&s,s.cpu.registers[15],4,&v));s.cpu.registers[{r}]=v;pop(&s,4);'for r in indices(parts[1])]
    elif kind in ['cmp','cmpa']:
        code=[load(parts[0],width),load(parts[1],4 if kind=='cmpa'else width,'u')]
        if kind=='cmpa'and width==2:code+=['v=sx16((uint16_t)v);']
        code+=[f'(void)alu(&s,u,v,{32 if kind=="cmpa"else width*8},1,1);']
    elif kind in ['subq','suba']:
        reg=base.register(parts[1])
        if reg is not None and reg>=8:code=[load(parts[0],width),f's.cpu.registers[{reg}]-='+('sx16((uint16_t)v)'if width==2 else'v')+';bank(&s);']
        else:code=[load(parts[0],width),load(parts[1],width,'u'),f'v=alu(&s,u,v,{width*8},1,0);',store(parts[1],width)]
    elif kind in ['and','or']:
        code=[load(parts[0],width),load(parts[1],width,'u'),'v=u'+('&'if kind=='and'else'|')+'v;',store(parts[1],width),f'nz(&s,v,{width*8});']
    elif kind=='not':code=[load(parts[0],width),'v=~v;',store(parts[0],width),f'nz(&s,v,{width*8});']
    elif kind=='muls':
        code=[load(parts[0],2),load(parts[1],2,'u'),'v=sx16((uint16_t)v)*sx16((uint16_t)u);',store(parts[1],4),'nz(&s,v,32);']
    elif kind=='dbra':
        r=base.register(parts[0]);code=[f'v=(uint16_t)(s.cpu.registers[{r}]-1u);put(&s,{r},2,v);s.cpu.pc=v!=0xffffu?{hex(base.number(parts[1]))}u:{hex(nxt)}u;break;'];terminal=True
    elif kind in ['bcc','bcs','bpl','bmi','blt']:
        cond={'bcc':'!(s.cpu.sr&1u)','bcs':'(s.cpu.sr&1u)!=0','bpl':'!(s.cpu.sr&8u)','bmi':'(s.cpu.sr&8u)!=0','blt':'(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u)!=0'}[kind]
        code=[f's.cpu.pc=({cond})?{hex(base.number(parts[0]))}u:{hex(nxt)}u;break;'];terminal=True
    if code is None:return ns['emit'](row).replace('BIWN_DISPATCH_CPU','BIWN_RESOURCE_CPU')
    if not terminal:code+=[f's.cpu.pc={hex(nxt)}u;break;']
    return '  case '+hex(pc)+'u: /* '+asm+' */\n   '+'\n   '.join(code)
HEADER='''#ifndef BIWN_RESOURCE_CPU_H
#define BIWN_RESOURCE_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_resource_cpu_status {BIWN_RESOURCE_CPU_OK=0,BIWN_RESOURCE_CPU_BAD_ARGUMENT=1,
 BIWN_RESOURCE_CPU_BUS_ERROR=2,BIWN_RESOURCE_CPU_SERVICE_ERROR=3,
 BIWN_RESOURCE_CPU_WORK_LIMIT=4,BIWN_RESOURCE_CPU_BAD_RETURN=5,
 BIWN_RESOURCE_CPU_YIELDED=6,BIWN_RESOURCE_CPU_BAD_PC=7};
/* Static fullCPU bodies for1B002release,1AF04acquire,1545Cfree,152A2allocate,
 * 15200compact,1B044load andE3E0/E3EEcopy. A helper provider executes nested
 * bodies up toRTS; callers retain all source argument/save frames. body
 * stops atRTS, call executesRTS. InternalPC resume is supported. DF60 yield
 * and DF8C wait return status6 before their wrappers execute, preserving
 * nested frames for actual scheduler yield/wait and later continuation.
 * commits CPU/frames; otherhosterrors retain RAM and unchanged inputCPU.
 * No runtime instructiondecode or originalCPU/GPUcalls. Devices/services
 * are explicit providers; this alone does not prove disk/model lifetimes. */
enum biwn_resource_cpu_status biwn_resource_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_resource_cpu_status biwn_resource_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();old=json.loads((session/'resource-lifetime-fullCPU-workmap.json').read_text());assert hashlib.sha256(image).hexdigest()==old['stage_sha256'];snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    for a,b in RANGES.items():
        assert snapshot[a:b]==image[a-0x4000:b-0x4000];part,_=base.binary_tools.m68k_instructions(snapshot[a:b],a);rows+=part
    assert len(rows)==506
    prefix=base.PREFIX.replace('biwn_input_dispatch_cpu','biwn_resource_cpu').replace('BIWN_DISPATCH_CPU','BIWN_RESOURCE_CPU')
    prefix=prefix.replace('generate_biwn_input_dispatch_cpu.py','generate_biwn_resource_cpu.py')
    prefix=prefix.replace('s->cpu.usp=s->cpu.registers[15];','if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];')
    prefix=prefix.replace('||(state->sr&0x2000u)','')
    prefix=prefix.replace('if(s->service(s->context,s->bus,&s->cpu,target))return 3;','{int status=s->service(s->context,s->bus,&s->cpu,target);if(status==6&&s->cpu.pc==0xdf60u)return 6;if(status)return 3;}')
    prefix=prefix.replace('if(status)return(enum biwn_dispatch_cpu_status)status;','if(status){if(status==6)*state=s.cpu;return(enum biwn_resource_cpu_status)status;}')
    # Enum names also occur in the private function signature/cast.
    prefix=prefix.replace('biwn_dispatch_cpu_status','biwn_resource_cpu_status')
    prefix=prefix.replace('if(status)return(enum biwn_resource_cpu_status)status;','if(status){if(status==6)*state=s.cpu;return(enum biwn_resource_cpu_status)status;}')
    prefix=prefix.replace('status==6&&s->cpu.pc==0xdf60u','status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)')
    suffix=base.SUFFIX.replace('biwn_input_dispatch_cpu','biwn_resource_cpu').replace('biwn_dispatch_cpu_status','biwn_resource_cpu_status').replace('BIWN_DISPATCH_CPU','BIWN_RESOURCE_CPU')
    text=prefix+'\n'.join(emit(row)for row in rows)+'\n'+suffix
    text=text.replace('stop_on_yield&&s.cpu.pc==0xdf60u','stop_on_yield&&(s.cpu.pc==0xdf60u||s.cpu.pc==0xdf8cu)')
    source=ROOT/'projects/black-ice-white-noise/restoration';(source/'biwn_resource_cpu.c').write_text(text);(source/'biwn_resource_cpu.h').write_text(HEADER)
    manifest={'status':'generated_unverified','instructions':len(rows),'ranges':{hex(a):hex(b)for a,b in RANGES.items()},'stage_sha256':old['stage_sha256'],'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'C_sha256':hashlib.sha256(text.encode()).hexdigest(),'instructions_decoded':rows}
    (session/'resource-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k!='instructions_decoded'}))
if __name__=='__main__':main()
