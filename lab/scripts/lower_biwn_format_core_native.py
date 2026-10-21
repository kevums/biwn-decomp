"""Pinned formatter/core wrapper lowering; static C, explicit public call frames."""
import capstone,hashlib,json,re
from pathlib import Path
from lower_biwn_format_number_native import HELPERS as NUMBER_HELPERS
ROOT=Path(__file__).resolve().parents[1];N=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
HELPERS=NUMBER_HELPERS.split('static void np_unsigned',1)[0].replace('#include "format-number-native.h"','#include "format-core-native.h"')
HELPERS=HELPERS.replace('static inline void np_push(uint32_t *r,uint32_t v){r[15]-=4;PW32(r[15],v);}',
 'static inline void np_push_width(uint32_t *r,uint32_t v,unsigned width){r[15]-=width;if(width==2)PW16(r[15],v);else PW32(r[15],v);}')
HELPERS+='''
static inline uint32_t sx8(uint8_t v){return(uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static void np_shift(uint32_t *r,unsigned index,unsigned bits,unsigned n,int left,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v=r[index]&mask;unsigned c=0,ov=0,i;
 for(i=0;i<n;i++){if(left){uint32_t old=v;c=(v&sign)!=0;v=(v<<1)&mask;ov|=((old^v)&sign)!=0;}else{c=v&1u;v=(v>>1)|(v&sign);}}
 np_put(r,index,bits/8,v);
 uint32_t f=(v?0u:4u)|(v&sign?8u:0u)|(c?(n?17u:1u):0u)|(ov?2u:0u);
 if(!n)live&=~16u;
 r[16]=(r[16]&~live)|(f&live);
}
'''
RANGES=[(0x1b29c,0x1b45a,'core'),(0x1b45a,0x1b478,'variadic')]
CALLEES={0x1b160:'pad',0x1b1a8:'string',0x1b212:'number',0x1b29c:'core'}
def generate():
 raw=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
 source=ROOT/'projects/black-ice-white-noise/restoration/biwn_formatter_cpu.c';text=source.read_text()
 cases={int(m[1],16):(m[2],m[3])for m in re.finditer(r'  case 0x([0-9a-f]+)u: /\* (.*?) \*/\n([\s\S]*?)(?=  case |  default:)',text)}
 md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
 lines=[HELPERS];routines=[]
 for start,stop,name in RANGES:
  instructions=list(md.disasm(raw[start:stop],start));assert instructions[-1].address+instructions[-1].size==stop
  facts=[]
  for ins in instructions:
   assembly=(ins.mnemonic+' '+ins.op_str).strip();assert cases[ins.address][0].strip()==assembly
   op=ins.mnemonic.split('.')[0];uses=0;defines=0;successors=[ins.address+ins.size]
   if op in ['move','moveq','tst','clr','cmp','cmpi','ext']:defines=15
   elif op in ['add','addi','addq','sub','subq','neg','asl']:defines=31
   elif op=='bra':successors=[int(ins.op_str[1:],16)]
   elif op in ['bne','beq','ble','bgt','bhi','bge']:
    uses={'bne':4,'beq':4,'ble':14,'bgt':14,'bhi':5,'bge':10}[op];successors=[int(ins.op_str[1:],16),ins.address+ins.size]
   elif op=='jsr':uses=31;defines=31
   elif op=='rts':uses=31;successors=[]
   else:assert op in ['movem','movea','lea','adda','pea','link','unlk'],assembly
   facts.append(dict(pc=ins.address,size=ins.size,bytes=ins.bytes.hex(),assembly=assembly,uses=uses,defines=defines,successors=successors))
  live={f['pc']:0 for f in facts};changed=True
  while changed:
   changed=False
   for f in reversed(facts):
    after=0
    for pc in f['successors']:assert pc in live;after|=live[pc]
    before=f['uses']|(after&~f['defines'])
    if before!=live[f['pc']]:live[f['pc']]=before;changed=True
  locals='v,u'if any(re.search(r'\bu\b',cases[f['pc']][1])for f in facts)else'v'
  lines.extend([f'void biwn_native_format_{name}_body(uint32_t *r){{',f' uint32_t {locals};',f' goto L_{start:x};'])
  for f in facts:
   pc=f['pc'];op=f['assembly'].split('.')[0].split(' ')[0];after=0
   for target in f['successors']:after|=live[target]
   mask=after&f['defines'];f['computed_flags']=mask;f['live_in']=live[pc]
   lines.append(f'L_{pc:x}: /* {f["assembly"]}; CCR mask {mask} */')
   if op=='rts':lines.append(' return;');continue
   if op=='jsr':
    target=int(f['assembly'].split('$')[1].split('.')[0],16);callee=CALLEES[target]
    lines.extend([f' np_push_width(r,0x{pc+f["size"]:x}u,4);',f' biwn_native_format_{callee}_body(r);',' (void)PR32(r[15]);r[15]+=4;',f' goto L_{pc+f["size"]:x};']);continue
   body=cases[pc][1].replace('s.cpu.registers','r').replace('s.cpu.sr','r[16]')
   body=re.sub(r'CHECK\(read_value\(&s,(.*?),([124]),&([vu])\)\);',lambda m:f'{m[3]}=PR{int(m[2])*8}({m[1]});',body)
   body=re.sub(r'CHECK\(write_value\(&s,(.*?),([124]),([vu])\)\);',lambda m:f'PW{int(m[2])*8}({m[1]},{m[3]});',body)
   body=re.sub(r'CHECK\(push\(&s,(.*?),([24])\)\);',lambda m:f'np_push_width(r,{m[1]},{m[2]});',body)
   body=body.replace('bank(&s);','').replace('pop(&s,4);','r[15]+=4;').replace('put(&s,','np_put(r,')
   body=re.sub(r'nz\(&s,([^,]+),(8|16|32)\);',lambda m:f'np_logic(r,{m[1]},{m[2]},{mask}u);',body)
   body=re.sub(r'alu\(&s,([^;]+?)\)',lambda m:f'np_alu(r,{m[1]},{mask}u)',body)
   body=re.sub(r'shift\(&s,([^;]+?)\);',lambda m:f'np_shift(r,{m[1]},{mask}u);',body)
   body=re.sub(r's.cpu.pc=(.*?)\?0x([0-9a-f]+)u:0x([0-9a-f]+)u;break;',lambda m:f'if({m[1]}){{goto L_{m[2]};}}\n   goto L_{m[3]};',body)
   body=re.sub(r's.cpu.pc=0x([0-9a-f]+)u;break;',lambda m:f'goto L_{m[1]};',body)
   assert not any(x in body for x in ['CHECK','s.cpu','&s','break;','read_value','write_value']),body
   lines.append(body.rstrip())
  lines.append('}');routines.append(dict(name=name,start=start,stop=stop,instructions=len(facts),rows=facts,range_sha256=hashlib.sha256(raw[start:stop]).hexdigest()))
 return '\n'.join(lines)+'\n',dict(status='native_core_and_variadic_lowering_pending_CPU_validation',routines=routines,recovered_host_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_origin='coordinator_pinned_instruction_semantics_with_CCR_liveness',scope='Static C labels/branches and direct native C helper bodies with original public call pushes/RTS reads. No runtime decoder or original helper execution. Valid finite format strings and argument pointers; no arbitrary faults,aliasing,IRQ or physical proof.')
if __name__=='__main__':
 code,proof=generate();(N/'format-core-native.c').write_text(code);(ROOT/'verification/native-format-core-lowering-current.json').write_text(json.dumps(proof,indent=2)+'\n');print([(r['name'],r['instructions'])for r in proof['routines']])
