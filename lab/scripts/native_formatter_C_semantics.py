"""Build-time additions for fixed instructions in the native formatter image.

These emit explicit C statements; no runtime instruction decoder is introduced.
Generated code is experimental until checked against the pinned native CPU.
"""
import re
import generate_biwn_atomic_startup_math as math
base=math.base
resource=math.movie.loader.resource

def emit(row):
 pc=row['address'];nxt=pc+row['size'];asm=row['assembly'];op,_,tail=asm.partition(' ');parts=base.split(tail);kind=op.split('.')[0];width={'b':1,'w':2,'l':4}.get(op[-1],4);code=[];terminal=False
 def load(x,w=width,name='v'):return resource.load(x,w,name)
 def store(x,w=width,name='v'):return resource.store(x,w,name)
 def privilege():
  return ('if(!(s.cpu.sr&0x2000u)){v=s.cpu.sr;s.cpu.usp=s.cpu.registers[15];s.cpu.sr|=0x2000u;s.cpu.registers[15]=s.cpu.ssp;CHECK(push(&s,s.cpu.pc,4));CHECK(push(&s,v,2));s.cpu.ssp=s.cpu.registers[15];CHECK(read_value(&s,0x20u,4,&v));s.cpu.pc=v;*state=s.cpu;return 11;}')
 if kind=='movem':
  assert width==4 and not any(x.endswith('+')or x.startswith('-')for x in parts)
  source_list=base.register(parts[0].split('/')[0].split('-')[0])is not None
  registers=resource.indices(parts[0]if source_list else parts[1]);address=base.address(parts[1]if source_list else parts[0]);items=['{uint32_t at='+address+';']
  for index,r in enumerate(registers):
   if source_list:items.append(f'CHECK(write_value(&s,at+{index*4}u,4,s.cpu.registers[{r}]));')
   else:items.append(f'CHECK(read_value(&s,at+{index*4}u,4,&v));s.cpu.registers[{r}]=v;')
  if not source_list and 15 in registers:items.append('bank(&s);')
  code=items+['}']
 elif kind=='move'and('sr'in parts or'ccr'in parts):
  if parts[0]=='sr':code=['v=s.cpu.sr;',store(parts[1],2)]
  elif parts[1]=='ccr':code=[load(parts[0],2),'s.cpu.sr=(uint16_t)((s.cpu.sr&0xffe0u)|(v&0x1fu));']
  elif parts[1]=='sr':code=[privilege(),load(parts[0],2),'s.cpu.ssp=s.cpu.registers[15];s.cpu.sr=(uint16_t)(v&0x271fu);if(!(s.cpu.sr&0x2000u))s.cpu.registers[15]=s.cpu.usp;']
  else:raise ValueError(asm)
 elif kind=='move'and'usp'in parts:
  code=[privilege()]
  if parts[0]=='usp':code.append(f's.cpu.registers[{base.register(parts[1])}]=s.cpu.usp;bank(&s);')
  else:code.append(f's.cpu.usp=s.cpu.registers[{base.register(parts[0])}];')
 elif kind=='move'and re.fullmatch(r'-\(a[0-7]\)',parts[1]):
  r=base.register(parts[1][2:4]);step=2 if width==1 and r==15 else width
  code=[load(parts[0]),f's.cpu.registers[{r}]-={step}u;bank(&s);CHECK(write_value(&s,s.cpu.registers[{r}],{width},v));',f'nz(&s,v,{width*8});']
 elif kind=='rte':
  code=[privilege(),'CHECK(read_value(&s,s.cpu.registers[15],2,&v));CHECK(read_value(&s,s.cpu.registers[15]+2u,4,&u));s.cpu.ssp=s.cpu.registers[15]+6u;s.cpu.sr=(uint16_t)(v&0x271fu);s.cpu.registers[15]=(s.cpu.sr&0x2000u)?s.cpu.ssp:s.cpu.usp;s.cpu.pc=u;*state=s.cpu;return 11;'];terminal=True
 elif kind in ['eor','eori','ori']:
  assert parts[1]not in ['sr','ccr'];code=[load(parts[0]),load(parts[1],name='u'),'v=u'+('|'if kind=='ori'else'^')+'v;',store(parts[1]),f'nz(&s,v,{width*8});']
 elif kind=='subi':code=[load(parts[0]),load(parts[1],name='u'),f'v=alu(&s,u,v,{width*8},1,0);',store(parts[1])]
 elif kind in ['seq','scc','scs','shi']:
  assert width==1 and base.register(parts[0])is not None
  condition={'seq':'(s.cpu.sr&4u)!=0','scc':'(s.cpu.sr&1u)==0','scs':'(s.cpu.sr&1u)!=0','shi':'(s.cpu.sr&5u)==0'}[kind];code=[f'v=({condition})?255u:0u;',store(parts[0],1)]
 elif kind=='subx':
  assert width==4 and all(base.register(x)is not None and base.register(x)<8 for x in parts)
  a,b=map(base.register,parts);code=[f'{{uint32_t source=s.cpu.registers[{a}],destination=s.cpu.registers[{b}],extend=(s.cpu.sr>>4)&1u;uint32_t result=destination-source-extend;unsigned carry=(uint64_t)source+extend>destination;unsigned overflow=((destination^source)&(destination^result)&0x80000000u)!=0;unsigned zero=(s.cpu.sr&4u)&&result==0;s.cpu.registers[{b}]=result;s.cpu.sr=(uint16_t)((s.cpu.sr&0xffe0u)|(carry?0x11u:0u)|(overflow?2u:0u)|(result&0x80000000u?8u:0u)|(zero?4u:0u));}}']
 elif kind in ['rol','ror']:
  assert width==4 and base.register(parts[1])is not None
  r=base.register(parts[1]);left=kind=='rol';loop='carry=v>>31;v=(v<<1)|carry;'if left else'carry=v&1u;v=(v>>1)|(carry<<31);'
  code=[load(parts[0],4,'u'),f'{{unsigned count=u&63u,carry=0;v=s.cpu.registers[{r}];for(unsigned i=0;i<count;i++){{{loop}}}s.cpu.registers[{r}]=v;nz(&s,v,32);s.cpu.sr=(uint16_t)((s.cpu.sr&~3u)|carry);}}']
 elif kind=='bset':
  assert parts[0].startswith('#')
  r=base.register(parts[1]);actual_width=4 if r is not None else 1
  bit=base.number(parts[0])&(31 if r is not None else 7);code=[load(parts[1],actual_width),f's.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((v&{1<<bit}u)?0u:4u));v|={1<<bit}u;',store(parts[1],actual_width)]
 else:raise ValueError(('Additional native formatter instruction semantics required',hex(pc),asm))
 if not terminal:code.append(f's.cpu.pc={hex(nxt)}u;break;')
 return f'case {hex(pc)}u: /* {asm}; experimental fixed native-image C */\n'+'\n'.join(code)
