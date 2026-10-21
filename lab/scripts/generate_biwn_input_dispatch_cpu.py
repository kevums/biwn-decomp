"""Source-specific static C recompile of the checked816-instruction dispatcher.

This is a build-time translator for this fixed routine, not a runtime CPU
emulator. Unknown instructions/address forms fail generation. Original CPU
execution, not this generator, supplies the comparison oracle.
"""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import binary_tools
def split(text):
    result=[];start=0;depth=0
    for i,ch in enumerate(text):
        if ch=='(':depth+=1
        elif ch==')':depth-=1
        elif ch==','and not depth:result.append(text[start:i].strip());start=i+1
    result.append(text[start:].strip());return result
def number(text):return int(text.replace('#','').replace('$',''),16)
def register(text):
    match=re.fullmatch(r'([da])([0-7])',text)
    return int(match[2])+(8 if match[1]=='a'else 0)if match else None
def address(text):
    if re.fullmatch(r'\$[0-9a-f]+\.[wl]',text):return hex(number(text[:-2]))+'u'
    m=re.fullmatch(r'(\$[0-9a-f]+)?\((a[0-7]|pc)(?:, ([da][0-7])\.([wl]))?\)',text)
    assert m,text
    prefix,base,index,width=m.groups();base_value=hex(number(prefix))+'u'if base=='pc'else f's.cpu.registers[{register(base)}]'
    if prefix and base!='pc':base_value+='+'+hex(number(prefix))+'u'
    if index:
        value=f's.cpu.registers[{register(index)}]';base_value+='+'+(f'sx16((uint16_t){value})'if width=='w'else value)
    return '('+base_value+')'
def load(text,width,name='v'):
    reg=register(text)
    if reg is not None:return f'{name}=s.cpu.registers[{reg}];'
    if text.startswith('#'):return f'{name}={hex(number(text))}u;'
    assert not text.endswith('+')and not text.startswith('-'),text
    return f'CHECK(read_value(&s,{address(text)},{width},&{name}));'
def store(text,width,name='v'):
    reg=register(text)
    if reg is not None:return f'put(&s,{reg},{width},{name});'
    if text=='-(a7)':return f'CHECK(push(&s,{name},{width}));'
    return f'CHECK(write_value(&s,{address(text)},{width},{name}));'
def emit(row):
    pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=split(tail);base=op.split('.')[0];width={'b':1,'w':2,'l':4}.get(op[-1],4);code=[];terminal=False
    if base=='movem':
        indices=[2,3,4,10,11,12,13]
        if parts[1]=='-(a7)':code=[f'CHECK(push(&s,s.cpu.registers[{i}],4));'for i in reversed(indices)]
        else:
            assert parts[0]=='(a7)+'
            code=[f'CHECK(read_value(&s,s.cpu.registers[15],4,&v));s.cpu.registers[{i}]=v;pop(&s,4);'for i in indices]
    elif base in ['move','movea']:
        code=[load(parts[0],width)]
        if base=='movea':code+=[f's.cpu.registers[{register(parts[1])}]='+('sx16((uint16_t)v)'if width==2 else'v')+';']
        else:code+=[store(parts[1],width),'nz(&s,v,'+str(width*8)+');']
    elif base=='moveq':
        code=[f'v=sx8({hex(number(parts[0])&255)}u);s.cpu.registers[{register(parts[1])}]=v;nz(&s,v,32);']
    elif base=='lea':code=[f's.cpu.registers[{register(parts[1])}]={address(parts[0])};']
    elif base=='pea':code=[f'CHECK(push(&s,{address(parts[0])},4));']
    elif base in ['adda','addq']and register(parts[1])is not None and register(parts[1])>=8:
        code=[load(parts[0],width),f's.cpu.registers[{register(parts[1])}]+='+('sx16((uint16_t)v)'if width==2 else'v')+';bank(&s);']
    elif base in ['add','addq','addi','sub','cmpi','andi']:
        code=[load(parts[0],width),load(parts[1],width,'u')]
        if base=='andi':code+=['v=u&v;','nz(&s,v,'+str(width*8)+');',store(parts[1],width)]
        else:
            code+=[f'v=alu(&s,u,v,{width*8},{int(base in ["sub","cmpi"])},{int(base=="cmpi")});']
            if base!='cmpi':code+=[store(parts[1],width)]
    elif base=='clr':code=['v=0;',store(parts[0],width),f'nz(&s,0,{width*8});']
    elif base=='tst':code=[load(parts[0],width),f'nz(&s,v,{width*8});']
    elif base=='neg':code=[load(parts[0],width),f'v=alu(&s,0,v,{width*8},1,0);',store(parts[0],width)]
    elif base=='btst':code=[load(parts[1],1),f's.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|(v&(1u<<{number(parts[0])})?0:4));']
    elif base=='ext':
        reg=register(parts[0]);code=[f'v='+('sx16((uint16_t)'if width==4 else'sx8((uint8_t)')+f's.cpu.registers[{reg}]);',store(parts[0],width),f'nz(&s,v,{width*8});']
    elif base in ['asl','asr']:
        code=[load(parts[0],4,'u'),f'shift(&s,{register(parts[1])},{width*8},u&63u,{int(base=="asl")});']
    elif base=='swap':
        reg=register(parts[0]);code=[f'v=s.cpu.registers[{reg}];v=(v<<16)|(v>>16);s.cpu.registers[{reg}]=v;nz(&s,v,32);']
    elif base in ['bra','beq','bne','ble','bge','bgt','bhi','bls']:
        conditions={'bra':'1','beq':'(s.cpu.sr&4u)!=0','bne':'(s.cpu.sr&4u)==0','ble':'(s.cpu.sr&4u)||(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u)','bge':'!(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u)','bgt':'!(s.cpu.sr&4u)&&!(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u)','bhi':'!(s.cpu.sr&5u)','bls':'(s.cpu.sr&5u)!=0'}
        code=[f's.cpu.pc=({conditions[base]})?{hex(number(parts[0]))}u:{hex(nxt)}u;break;'];terminal=True
    elif base=='jmp':code=[f's.cpu.pc={address(parts[0])};break;'];terminal=True
    elif base=='jsr':
        target=number(parts[0][:-2]);code=[f'CHECK(push(&s,{hex(nxt)}u,4));s.cpu.pc={hex(target)}u;',f'if(stop_on_yield&&s.cpu.pc==0xdf60u){{*state=s.cpu;return BIWN_DISPATCH_CPU_YIELDED;}}',f'CHECK(invoke(&s,{hex(target)}u,{hex(nxt)}u));break;'];terminal=True
    elif base=='rts':
        code=['if(full_call){CHECK(read_value(&s,s.cpu.registers[15],4,&v));s.cpu.pc=v;pop(&s,4);}*state=s.cpu;return BIWN_DISPATCH_CPU_OK;'];terminal=True
    else:raise ValueError((hex(pc),asm))
    if not terminal:code+=[f's.cpu.pc={hex(nxt)}u;break;']
    return '  case '+hex(pc)+'u: /* '+asm+' */\n   '+'\n   '.join(code)

HEADER='''#ifndef BIWN_INPUT_DISPATCH_CPU_H
#define BIWN_INPUT_DISPATCH_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_dispatch_cpu_status {BIWN_DISPATCH_CPU_OK=0,BIWN_DISPATCH_CPU_BAD_ARGUMENT=1,
 BIWN_DISPATCH_CPU_BUS_ERROR=2,BIWN_DISPATCH_CPU_SERVICE_ERROR=3,
 BIWN_DISPATCH_CPU_WORK_LIMIT=4,BIWN_DISPATCH_CPU_BAD_RETURN=5,
 BIWN_DISPATCH_CPU_YIELDED=6,BIWN_DISPATCH_CPU_BAD_PC=7};
/* Static C blocks for all816checked instructions; no runtime instruction
 * decoding or CPU-core calls. Exact CPU state permits internal continuation.
 * body stops before19F2A RTS; call executes it. stop_on_yield leaves DF60
 * and its real return/private frames for the scheduler, committing CPU.
 * A nested provider may also suspend at DF60: status6 propagates the
 * provider's complete CPU/private frames without popping the input JSR.
 * Other host errors preserve inputCPU and priorRAM effects. Usermode only.
 * Services execute helper bodies up to RTS; their behavior remains explicit. */
enum biwn_dispatch_cpu_status biwn_input_dispatch_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_dispatch_cpu_status biwn_input_dispatch_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
'''
PREFIX='''/* Generated by scripts/generate_biwn_input_dispatch_cpu.py from pinned
 * source instructions. Source-specific static recompilation, not recovered
 * original source. See manifest and original-CPU comparison evidence. */
#include "biwn_input_dispatch_cpu.h"
struct dispatch {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;biwn_input_write8 write8;biwn_world_cpu_service service;void *context;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static void bank(struct dispatch *s){s->cpu.usp=s->cpu.registers[15];}
static void pop(struct dispatch *s,uint32_t n){s->cpu.registers[15]+=n;bank(s);}
static void put(struct dispatch *s,unsigned r,unsigned width,uint32_t v){uint32_t mask=width==4?0xffffffffu:(1u<<(width*8))-1u;s->cpu.registers[r]=(s->cpu.registers[r]&~mask)|(v&mask);if(r==15)bank(s);}
static void nz(struct dispatch *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static uint32_t alu(struct dispatch *s,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,ov;a&=mask;b&=mask;r=(sub?a-b:a+b)&mask;carry=sub?a<b:r<a;ov=sub?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;nz(s,r,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0)|(ov?2u:0));return r;}
static void shift(struct dispatch *s,unsigned r,unsigned bits,unsigned n,int left){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v=s->cpu.registers[r]&mask;unsigned c=0,ov=0,i;
 for(i=0;i<n;i++){if(left){uint32_t old=v;c=(v&sign)!=0;v=(v<<1)&mask;ov|=((old^v)&sign)!=0;}else{c=v&1u;v=(v>>1)|(v&sign);}}
 put(s,r,bits/8,v);nz(s,v,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(n?0x13u:3u))|(c?(n?0x11u:1u):0)|(ov?2u:0));}
static int read_value(struct dispatch *s,uint32_t a,unsigned w,uint32_t *v){uint8_t b;uint16_t h;if(w==1){if(s->bus->read8(s->bus->context,a,&b))return 2;*v=b;}else if(w==2){if(s->bus->read16(s->bus->context,a,&h))return 2;*v=h;}else if(s->bus->read32(s->bus->context,a,v))return 2;return 0;}
static int write_value(struct dispatch *s,uint32_t a,unsigned w,uint32_t v){if(w==1)return s->write8(s->bus->context,a,(uint8_t)v)?2:0;if(w==2)return s->bus->write16(s->bus->context,a,(uint16_t)v)?2:0;return s->bus->write32(s->bus->context,a,v)?2:0;}
static int push(struct dispatch *s,uint32_t v,unsigned w){s->cpu.registers[15]-=w;bank(s);return write_value(s,s->cpu.registers[15],w,v);}
static int invoke(struct dispatch *s,uint32_t target,uint32_t ret){uint32_t sp=s->cpu.registers[15],pc;{int status=s->service(s->context,s->bus,&s->cpu,target);if(status==6&&s->cpu.pc==0xdf60u)return 6;if(status)return 3;}if(s->cpu.registers[15]!=sp)return 5;if(read_value(s,sp,4,&pc))return 2;if(pc!=ret)return 5;pop(s,4);s->cpu.pc=pc;return 0;}
#define CHECK(e) do{int status=(e);if(status){if(status==6)*state=s.cpu;return(enum biwn_dispatch_cpu_status)status;}}while(0)
static enum biwn_dispatch_cpu_status run(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_input_write8 write8,biwn_world_cpu_service service,void *context,uint32_t budget,int stop_on_yield,int full_call)
{
 struct dispatch s;uint32_t v,u;
 if(!bus||!state||!write8||!service||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||(state->sr&0x2000u)||(stop_on_yield!=0&&stop_on_yield!=1))return BIWN_DISPATCH_CPU_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.write8=write8;s.service=service;s.context=context;
 while(budget--){switch(s.cpu.pc){
'''
SUFFIX='''  default:return BIWN_DISPATCH_CPU_BAD_PC;
 }}return BIWN_DISPATCH_CPU_WORK_LIMIT;
}
enum biwn_dispatch_cpu_status biwn_input_dispatch_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,biwn_input_write8 w8,biwn_world_cpu_service svc,void *ctx,uint32_t budget,int yield){return run(bus,cpu,w8,svc,ctx,budget,yield,0);}
enum biwn_dispatch_cpu_status biwn_input_dispatch_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,biwn_input_write8 w8,biwn_world_cpu_service svc,void *ctx,uint32_t budget,int yield){return run(bus,cpu,w8,svc,ctx,budget,yield,1);}
'''
def main():
    folder=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((folder/'input-dispatch-fullCPU-workmap.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();image=(folder/'nextstage-68000-candidate.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest()==mapping['stage_sha256']
    for row in mapping['instructions']:assert snapshot[row['address']:row['address']+row['size']].hex()==row['bytes']
    assert len(mapping['instructions'])==816
    source=ROOT/'projects/black-ice-white-noise/restoration';c_source=PREFIX+'\n'.join(emit(row)for row in mapping['instructions'])+'\n'+SUFFIX
    (source/'biwn_input_dispatch_cpu.h').write_text(HEADER);(source/'biwn_input_dispatch_cpu.c').write_text(c_source)
    manifest={'stage_sha256':mapping['stage_sha256'],'instructions':816,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'workmap_sha256':hashlib.sha256((folder/'input-dispatch-fullCPU-workmap.json').read_bytes()).hexdigest(),'C_sha256':hashlib.sha256(c_source.encode()).hexdigest(),'status':'generated_unverified','scope':'Static source-specific C; no runtime decode/CPU emulator. FullCPU/original-CPU comparison and yield continuation acceptance pending.'}
    (folder/'input-dispatch-fullCPU-generation.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
