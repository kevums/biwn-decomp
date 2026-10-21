"""Source-specific straight-line C lowering with CCR liveness, no CPU dispatch."""
import capstone,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];N=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
START=0x1b212;STOP=0x1b29c
HELPERS=r'''
#include "format-number-native.h"
#include "m68k-fact-helpers-v2.h"
static inline uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static inline void np_put(uint32_t *r,unsigned i,unsigned width,uint32_t v){
 uint32_t mask=width==4?0xffffffffu:(1u<<(width*8))-1u;
 r[i]=(r[i]&~mask)|(v&mask);
}
static inline void np_logic(uint32_t *r,uint32_t v,unsigned bits,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),f;
 v&=mask;f=(v?0u:4u)|(v&sign?8u:0u);r[16]=(r[16]&~live)|(f&live);
}
static inline uint32_t np_alu(uint32_t *r,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v,f;
 a&=mask;b&=mask;v=(sub?a-b:a+b)&mask;
 f=((sub?a<b:v<a)?(cmp?1u:17u):0u)|
  ((sub?((a^b)&(a^v)&sign):((~(a^b))&(a^v)&sign))?2u:0u)|(v?0u:4u)|(v&sign?8u:0u);
 r[16]=(r[16]&~live)|(f&live);return v;
}
static inline void np_push(uint32_t *r,uint32_t v){r[15]-=4;PW32(r[15],v);}
static void np_unsigned(uint32_t *r,int remainder){
 uint32_t sp=r[15];int fault=remainder?biwn_native_unsigned_remainder_body(r):biwn_native_unsigned_divide_body(r);
 if(fault){
  if(remainder)r[15]=sp-12;
  biwn_native_semantic_divide_zero(r);
  mf_move32(r,3,r[9]);mf_move32(r,2,r[8]);
  if(remainder){(void)PR32(r[15]);r[15]+=12;mf_move32(r,0,r[1]);}
 }
 /* Complete the helper's original outer RTS public read/pop. */
 (void)PR32(r[15]);r[15]+=4;
}
'''
def generate():
 image=ROOT/'render-assets/biwn-inventory-baseline.bin';raw=image.read_bytes();assert hashlib.sha256(raw).hexdigest()=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
 source=ROOT/'projects/black-ice-white-noise/restoration/biwn_formatter_cpu.c';text=source.read_text()
 md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
 ins=list(md.disasm(raw[START:STOP],START));cases={int(m[1],16):(m[2],m[3]) for m in re.finditer(r'  case 0x([0-9a-f]+)u: /\* (.*?) \*/\n([\s\S]*?)(?=  case |  default:)',text)}
 facts=[]
 for i in ins:
  assembly=(i.mnemonic+' '+i.op_str).strip();old,body=cases[i.address];assert old.strip()==assembly,(hex(i.address),old,assembly)
  op=i.mnemonic.split('.')[0];uses=0;defines=0;successors=[i.address+i.size]
  if op in ['move','tst','clr','cmp']:defines=15
  elif op in ['subq','addq']:defines=0 if i.op_str.endswith(', a7') else 31
  elif op in ['bne','beq','ble','bgt']:
   uses=4 if op in ['bne','beq'] else 14;target=int(i.op_str[1:],16);successors=[target,i.address+i.size]
  elif op=='jsr':uses=31;defines=31
  elif op=='rts':uses=31;successors=[]
  else:assert op in ['movem','movea','lea'],assembly
  facts.append(dict(pc=i.address,assembly=assembly,bytes=i.bytes.hex(),size=i.size,uses=uses,defines=defines,successors=successors))
 bypc={f['pc']:f for f in facts};live={f['pc']:0 for f in facts}
 changed=True
 while changed:
  changed=False
  for f in reversed(facts):
   after=0
   for pc in f['successors']:assert pc in bypc;after|=live[pc]
   before=f['uses']|(after&~f['defines'])
   if before!=live[f['pc']]:live[f['pc']]=before;changed=True
 lines=[HELPERS,'/* Deterministic lowering of pinned recovered instruction semantics; not model C. */','void biwn_native_format_number_body(uint32_t *r){',' uint32_t v,u;',' goto L_1b212;']
 for f in facts:
  pc=f['pc'];op=f['assembly'].split('.')[0].split(' ')[0];after=0
  for target in f['successors']:after|=live[target]
  mask=after&f['defines'];f['live_in']=live[pc];f['computed_flags']=mask
  lines.append(f'L_{pc:x}: /* {f["assembly"]}; CCR mask {mask} */')
  if op=='rts':lines.append(' return;');continue
  if op=='jsr':
   target=int(f['assembly'].split('$')[1].split('.')[0],16);assert target in [0xe61c,0xe67c]
   lines.extend([f' np_push(r,0x{pc+f["size"]:x}u);',f' np_unsigned(r,{int(target==0xe67c)});',f' goto L_{pc+f["size"]:x};']);continue
  body=cases[pc][1]
  body=body.replace('s.cpu.registers','r').replace('s.cpu.sr','r[16]')
  body=re.sub(r'CHECK\(read_value\(&s,(.*?),([124]),&([vu])\)\);',lambda m:f'{m[3]}=PR{int(m[2])*8}({m[1]});',body)
  body=re.sub(r'CHECK\(write_value\(&s,(.*?),([124]),([vu])\)\);',lambda m:f'PW{int(m[2])*8}({m[1]},{m[3]});',body)
  body=re.sub(r'CHECK\(push\(&s,(.*?),4\)\);',lambda m:f'np_push(r,{m[1]});',body)
  body=body.replace('bank(&s);','').replace('pop(&s,4);','r[15]+=4;').replace('put(&s,','np_put(r,')
  body=re.sub(r'nz\(&s,([^,]+),(8|16|32)\);',lambda m:f'np_logic(r,{m[1]},{m[2]},{mask}u);',body)
  body=re.sub(r'alu\(&s,([^;]+?)\)',lambda m:f'np_alu(r,{m[1]},{mask}u)',body)
  body=re.sub(r's.cpu.pc=(.*?)\?0x([0-9a-f]+)u:0x([0-9a-f]+)u;break;',lambda m:f'if({m[1]}){{goto L_{m[2]};}}\n   goto L_{m[3]};',body)
  body=re.sub(r's.cpu.pc=0x([0-9a-f]+)u;break;',lambda m:f'goto L_{m[1]};',body)
  assert not any(x in body for x in ['CHECK','s.cpu','&s','break;','read_value','write_value']),body
  lines.append(body.rstrip())
 lines.append('}');return '\n'.join(lines)+'\n',dict(status='native_number_lowering_pending_CPU_validation',start=START,stop=STOP,original_instructions=len(facts),rows=facts,recovered_host_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),range_sha256=hashlib.sha256(raw[START:STOP]).hexdigest(),source_origin='coordinator_source_specific_C_semantics_lowering_with_CCR_liveness',scope='Straight labels/branches, volatile guest accesses and native C math callees. No runtime CPU dispatch. External arithmetic calls make all CCR bits live at entry for declared zero-fault context observation; no other arbitrary exception/IRQ equivalence claimed.')
if __name__=='__main__':
 code,proof=generate();(N/'format-number-native.c').write_text(code);(ROOT/'verification/native-format-number-lowering-current.json').write_text(json.dumps(proof,indent=2)+'\n');print(len(proof['rows']),'instructions',sum(bool(f['computed_flags']) for f in proof['rows']),'CCR sites')
