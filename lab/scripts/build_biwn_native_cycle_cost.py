"""Generate cost-only C from pinned metadata; no CPU instruction execution."""
import hashlib,json,os,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
    meta=Path(json.loads((ROOT/'verification/CPU-cycle-metadata-current.json').read_text())['metadata']);data=json.loads(meta.read_text());out=ROOT/'verification/native-cycle-cost-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    kinds=['CONST','Bcc','DBcc','Scc','BCLR','MVMLE','MVMEL','ASR','ASL','LSR','LSL','ROR','ROL','ROXR','ROXL','MULU','MULS','DIVU','DIVS'];rows=[]
    for info in data['opcodes']:
        h=data['handlers'].get(str(info['handler']));base=extra=kind=0
        if h:
            if h['constant_cycles']is not None:kind=1;base=h['constant_cycles']
            else:
                name=h['name'];kind=kinds.index(name)+1
                if name=='BCLR':base=min(map(int,h['returns']));extra=max(map(int,h['returns']))
                elif name not in ['Bcc','DBcc','Scc']:base=int(re.search(r'\(\s*(\d+)\+retcycles',h['returns'][-1]).group(1))
        rows.append('{'+','.join(str(x)for x in [kind,base,extra,info['condition'],info['size'],info['smode'],info['sreg'],info['dreg']])+'},')
    source='''#include <stdint.h>
struct cpu {uint32_t registers[16],pc,usp,ssp;uint16_t sr;};
struct model {int16_t kind,base,extra,cc,size,smode,sreg,dreg;};
static const struct model models[65536]={'''+''.join(rows)+'''};
static int condition(unsigned cc,unsigned sr){int z=(sr&4)!=0,n=(sr&8)!=0,v=(sr&2)!=0,c=(sr&1)!=0;switch(cc){case 0:return 1;case 1:return 0;case 2:return !c&&!z;case 3:return c||z;case 4:return !c;case 5:return c;case 6:return !z;case 7:return z;case 8:return !v;case 9:return v;case 10:return !n;case 11:return n;case 12:return n==v;case 13:return n!=v;case 14:return !z&&n==v;default:return z||n!=v;}}
static int32_t sx8(uint32_t v){return(int32_t)(v&127)-(int32_t)(v&128);}static int32_t sx16(uint32_t v){return(int32_t)(v&32767)-(int32_t)(v&32768);}
static unsigned bits(uint32_t v){unsigned n=0;while(v){n+=v&1;v>>=1;}return n;}
static int read(const uint8_t*RAM,uint32_t a,unsigned w,uint32_t*v){unsigned i;if(!w||w>4||a>0x200000u-w)return 1;*v=0;for(i=0;i<w;i++)*v=(*v<<8)|RAM[a+i];return 0;}
static int operand(const struct model*m,const struct cpu*s,const uint8_t*RAM,unsigned w,uint32_t*v){uint32_t a=0,x=0,index,ext=s->pc+2,reg=(unsigned)m->sreg;switch(m->smode){case 0:*v=s->registers[reg]&(w==4?0xffffffffu:(1u<<(w*8))-1);return 0;case 1:*v=s->registers[8+reg]&(w==4?0xffffffffu:(1u<<(w*8))-1);return 0;case 2:case 3:a=s->registers[8+reg];break;case 4:a=s->registers[8+reg]-(w==1&&reg==7?2:w);break;case 5:if(read(RAM,ext,2,&x))return 1;a=s->registers[8+reg]+(uint32_t)sx16(x);break;case 6:case 10:if(read(RAM,ext,2,&x))return 1;index=s->registers[(x>>12)&15];if(!(x&0x800))index=(uint32_t)sx16(index);a=(m->smode==6?s->registers[8+reg]:ext)+(uint32_t)sx8(x)+index;break;case 7:if(read(RAM,ext,2,&x))return 1;a=(uint32_t)sx16(x);break;case 8:if(read(RAM,ext,4,&a))return 1;break;case 9:if(read(RAM,ext,2,&x))return 1;a=ext+(uint32_t)sx16(x);break;case 11:return read(RAM,ext,w,v);case 12:case 13:case 14:case 15:*v=reg;return 0;default:return 1;}a&=0xffffff;if(a>=0x200000)return 1;return read(RAM,a,w,v);}
static int divu(uint32_t a,uint32_t b){unsigned i;int cycles=38;uint32_t h=b<<16;if((a>>16)>=b)return 6;for(i=0;i<15;i++){uint32_t t=a;a<<=1;if(t&0x80000000u)a-=h;else{cycles+=2;if(a>=h){a-=h;cycles--;}}}return cycles*2-4;}
static int divs(uint32_t value,uint32_t divisor){int32_t a=(int32_t)value,b=sx16(divisor);uint32_t aa,bb,q;unsigned i;int cycles;if(a==(-2147483647-1))return -1;aa=(uint32_t)(a<0?-a:a);bb=(uint32_t)(b<0?-b:b);cycles=6+(a<0);if((aa>>16)>=bb)return(cycles+2)*2-4;q=aa/bb;cycles+=55;if(b>=0)cycles+=a>=0?-1:1;for(i=0;i<15;i++){cycles+=(q&0x8000)==0;q<<=1;}return cycles*2-4;}
int biwn_native_cycle_cost(uint16_t op,const struct cpu*s,const uint8_t*RAM){const struct model*m=&models[op];uint32_t x,count;int e;switch(m->kind){case 1:return m->base;case 2:return condition(m->cc,s->sr)?10:((op&255)==0||(op&255)==255?12:8);case 3:return condition(m->cc,s->sr)?12:((s->registers[op&7]&65535)==0?14:10);case 4:return condition(m->cc,s->sr)?6:4;case 5:if(operand(m,s,RAM,4,&x))return -1;return(x&31)<16?m->base:m->extra;case 6:case 7:if(read(RAM,s->pc+2,2,&x))return -1;return m->base+(int)bits(x)*(m->size==2?8:4);case 8:case 9:case 10:case 11:case 12:case 13:case 14:case 15:count=(op&32)?s->registers[(op>>9)&7]&63:((op>>9)&7);if(!(op&32)&&!count)count=8;return m->base+2*(int)count;case 16:if(operand(m,s,RAM,2,&x))return -1;return m->base+2*(int)bits(x);case 17:if(operand(m,s,RAM,2,&x))return -1;x=(uint32_t)sx16(x)<<1;count=0;while(x){count+=(x&3)==1||(x&3)==2;x>>=1;}return m->base+2*(int)count;case 18:case 19:if(operand(m,s,RAM,2,&x)||!x)return -1;e=m->kind==18?divu(s->registers[m->dreg],x):divs(s->registers[m->dreg],x);return e<0?-1:m->base+e;default:return -1;}}
'''
    path=out/'native_cycle_cost.c';path.write_text(source);lib=out/'libnative-cycle-cost.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(path),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    report=dict(status='compiled_unverified_cost_only',directory=str(out),library=str(lib),metadata=str(meta),metadata_sha256=hashlib.sha256(meta.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(source.encode()).hexdigest(),original_CPU_execution=False,new_training=False,coordinator_authored=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/native-cycle-cost-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
