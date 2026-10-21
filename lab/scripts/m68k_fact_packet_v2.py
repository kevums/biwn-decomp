"""Explicit 68000 subset: typed operands, CFG, stack bias and executable facts.

This is an analysis/interpreter tool, not generated C or a complete decompiler.
Unsupported instructions/addressing modes and ambiguous stack joins fail closed.
"""
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import binary_tools
MANUAL='https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf'
MASK32=0xffffffff
def reg(name):return int(name[1:])+(8 if name[0]=='a'else 0)
def number(value):
 sign=-1 if value.startswith('-')else 1;value=value.lstrip('-')
 assert value.startswith('$'),value
 return sign*int(value[1:],16)
def operand(text):
 if re.fullmatch('[da][0-7]',text):return dict(kind='register',name=text,index=reg(text))
 if text.startswith('#'):return dict(kind='immediate',value=number(text[1:]))
 match=re.fullmatch(r'-\((a[0-7])\)',text)
 if match:return dict(kind='memory',base=match[1],index=reg(match[1]),mode='predecrement',displacement=0)
 match=re.fullmatch(r'\((a[0-7])\)(\+)?',text)
 if match:return dict(kind='memory',base=match[1],index=reg(match[1]),mode='postincrement'if match[2]else'indirect',displacement=0)
 match=re.fullmatch(r'\$([0-9a-f]+)\((a[0-7])\)',text)
 if match:
  displacement=int(match[1],16);assert displacement<=65535
  if displacement>=32768:displacement-=65536
  return dict(kind='memory',base=match[2],index=reg(match[2]),mode='displacement',displacement=displacement)
 raise ValueError('Unsupported operand: '+text)
def packet(image,start,stop):
 rows,decoder=binary_tools.m68k_instructions(image[start:stop],start);facts=[]
 allowed={'move.b','move.w','move.l','movea.l','movea.w','moveq','tst.w','tst.b','clr.w','addq.w','subq.w','bgt.b','ble.b','bra.b','beq.b','bne.b','cmpa.w','lea.l','rts'}
 for row in rows:
  mnemonic,_,args=row['assembly'].partition(' ')
  if mnemonic not in allowed:raise ValueError('Unsupported instruction: '+row['assembly'])
  op=mnemonic.split('.')[0];width=32 if op in ['moveq','rts']else {'b':8,'w':16,'l':32}[mnemonic.rsplit('.',1)[-1]]
  fact=dict(pc=row['address'],size=row['size'],bytes=row['bytes'],assembly=row['assembly'],op=op,width_bits=width,successors=[])
  if op in ['bgt','ble','bra','beq','bne']:
   target=number(args);fact.update(condition={'bgt':'gt','ble':'le','bra':'always','beq':'eq','bne':'ne'}[op],target=target,ccr=dict(mode='unchanged'))
   fact['successors']=[target]+([]if op=='bra'else[row['address']+row['size']])
  elif op=='rts':fact.update(ccr=dict(mode='unchanged'),src=dict(kind='memory',base='a7',index=15,mode='postincrement',displacement=0))
  else:
   parts=args.split(', ')
   if op in ['tst','clr']:
    assert len(parts)==1;fact['src'if op=='tst'else'dst']=operand(parts[0])
   else:
    assert len(parts)==2
    if op=='lea':
     assert re.fullmatch(r'\$[0-9a-f]+\.l',parts[0]),'Only absolute-long LEA is supported'
     fact['src']=dict(kind='address',value=number(parts[0][:-2]))
    else:fact['src']=operand(parts[0])
    fact['dst']=operand(parts[1])
   if op=='moveq':fact['src']['value']=int.from_bytes(bytes.fromhex(row['bytes'])[-1:],'big',signed=True)
   if op in ['addq','subq']:
    assert fact['src']['kind']=='immediate'and 1<=fact['src']['value']<=8
    assert ((fact['dst']['kind']=='register'and fact['dst']['name'].startswith('d'))or
            (fact['dst']['kind']=='memory'and fact['dst']['mode']=='indirect')),'RMW supports indirect memory only'
   if op=='clr':assert fact['dst']['kind']=='register','Memory CLR not supported in this subset'
   if op in ['movea','lea','cmpa']:assert fact['dst']['kind']=='register'and fact['dst']['name'].startswith('a')
   if op=='move':assert fact['dst'].get('name','d').startswith('d'),'Use explicit MOVEA'
   if 'dst'in fact and fact['dst']['kind']=='register':
    fact['dst']['write_mask']=MASK32 if op in ['movea','moveq','lea']else(1<<width)-1
    fact['dst']['source_rule']='signed_extend_16_to_32'if op=='movea'and width==16 else'signed_extend_8_to_32'if op=='moveq'else'width_mask'
   fact['ccr']=dict(mode='unchanged')if op in ['movea','lea']else dict(mode='add'if op=='addq'else'sub'if op in ['subq','cmpa']else'logic',X='from_carry'if op in ['addq','subq']else'preserve')
   if op=='cmpa':
    fact['ccr']['effective_width_bits']=32
    fact['dst'].pop('write_mask',None);fact['dst'].pop('source_rule',None)
   fact['successors']=[row['address']+row['size']]
  facts.append(fact)
 by_pc={f['pc']:f for f in facts};biases={start:0};pending=[start]
 while pending:
  pc=pending.pop();f=by_pc[pc];bias=biases[pc];f['entry_SP_delta_before']=bias
  for which in ['src','dst']:
   o=f.get(which,{})
   if o.get('kind')!='memory' or o['base']!='a7':continue
   stride=2 if f['width_bits']==8 else f['width_bits']//8
   if o['mode']=='predecrement':bias-=stride
   o['entry_SP_offset']=bias+o['displacement']
   if o['mode']=='postincrement':bias+=stride
  f['entry_SP_delta_after']=bias
  for successor in f['successors']:
   if successor not in by_pc:raise ValueError('External/misaligned CFG edge: '+hex(successor))
   if successor in biases:
    if biases[successor]!=bias:raise ValueError('Ambiguous SP at CFG join '+hex(successor))
   else:biases[successor]=bias;pending.append(successor)
 if len(biases)!=len(facts):raise ValueError('Unreachable instructions require explicit separate analysis')
 return dict(status='static_facts_pending_CPU_validation',start=start,stop=stop,range_sha256=hashlib.sha256(image[start:stop]).hexdigest(),decoder=decoder,instructions=facts,
  contract='Original A7 is a virtual stack pointer. In the coordinator C ABI r[15] remains ORIGINAL entrySP; use the derived entry_SP_offset for each original stack access. D0-D7/A0-A6 map to r0..14. Word writes to data registers preserve upper16bits. Static facts are not CPU proof until validation succeeds.',
  CCR_rules=dict(logic='N=result sign at operand width;Z=zero;V=C=0;X preserved',add='width-wrapped addition;C/X carry;V signed overflow;N/Z result',sub='width-wrapped subtraction;C/X borrow;V signed overflow;N/Z result',unchanged='all CCR bits preserved',gt='Z==0 and N==V',le='Z==1 or N!=V'),
  reference=dict(url=MANUAL,sections=['1.7.1','2.2','3.3.2/Table3-19','MOVE4-116','MOVEA4-119','MOVEQ4-134','SUBQ4-181','TST4-192']),
  scope='Explicit instruction/addressing subset only. Per-instruction ISA effects plus CFG-derived original SP offsets; no whole-C target or high-level game algorithm supplied. Generalization,IRQ,faults and cycle behavior are unverified.')

def execute(facts,initial_ram,incoming,sr,entry_sp,changing_reads=None):
 """Interpret the emitted facts, exposing exact data-memory events for validation."""
 ram=bytearray(initial_ram);registers=list(incoming)+[entry_sp];pc=facts['start'];by_pc={r['pc']:r for r in facts['instructions']};events=[];steps=0;coverage=set();queues=copy.deepcopy(changing_reads or {})
 def access(o,width,write=None):
  mask=(1<<width)-1
  if o['kind']in ['immediate','address']:assert write is None;return o['value']&mask
  if o['kind']=='register':
   index=o['index']
   if write is None:return registers[index]&mask
   value=write&mask
   if o.get('source_rule')=='signed_extend_16_to_32':value=(value-(65536 if value&32768 else 0))&MASK32
   write_mask=o['write_mask'];registers[index]=((registers[index]&~write_mask)|(value&write_mask))&MASK32;return
  index=o['index'];stride=2 if index==15 and width==8 else width//8
  if o['mode']=='predecrement':registers[index]=(registers[index]-stride)&MASK32
  address=(registers[index]+o['displacement'])&MASK32
  if index==15:assert address==(entry_sp+o['entry_SP_offset'])&MASK32,'Static SP-offset fact disagrees with virtual original A7'
  size=width//8;assert 0<=address and address+size<=len(ram),'Out-of-range target RAM access'
  if write is None:
   queue=queues.get((address,size))
   if queue:ram[address:address+size]=queue.pop(0).to_bytes(size,'big')
   result=int.from_bytes(ram[address:address+size],'big');events.append(['r',address,size,result])
  else:
   result=write&mask;ram[address:address+size]=result.to_bytes(size,'big');events.append(['w',address,size,result])
  if o['mode']=='postincrement':registers[index]=(registers[index]+stride)&MASK32
  return result
 def flags(f,value,a=0,b=0):
  nonlocal sr
  rule=f['ccr'];mode=rule['mode']
  if mode=='unchanged':return
  bits=rule.get('effective_width_bits',f['width_bits']);mask=(1<<bits)-1;sign=1<<(bits-1);value&=mask;n=8 if value&sign else 0;z=4 if value==0 else 0;v=c=0
  if mode=='add':c=int(a+b>mask);v=2 if (~(a^b)&(a^value)&sign)else 0
  elif mode=='sub':c=int(a<b);v=2 if ((a^b)&(a^value)&sign)else 0
  else:assert mode=='logic'
  x=sr&16 if rule['X']=='preserve'else 16*c if rule['X']=='from_carry'else 0
  sr=(sr&~31)|x|n|z|v|c
 while pc in by_pc:
  steps+=1;assert steps<=1000000,'Fact execution did not return';f=by_pc[pc];coverage.add(pc);op=f['op'];width=f['width_bits'];mask=(1<<width)-1;next_pc=pc+f['size']
  assert registers[15]==(entry_sp+f['entry_SP_delta_before'])&MASK32,'CFG stack-bias mismatch'
  if op in ['move','movea','moveq','lea']:
   value=access(f['src'],width);access(f['dst'],width,value);flags(f,value)
  elif op=='clr':access(f['dst'],width,0);flags(f,0)
  elif op=='tst':flags(f,access(f['src'],width))
  elif op=='cmpa':
   b=access(f['src'],width);b=(b-(65536 if b&32768 else 0))&MASK32
   a=registers[f['dst']['index']];flags(f,(a-b)&MASK32,a,b)
  elif op in ['addq','subq']:
   a=access(f['dst'],width);b=access(f['src'],width);value=(a+b if op=='addq'else a-b)&mask;access(f['dst'],width,value);flags(f,value,a,b)
  elif op in ['bgt','ble','bra','beq','bne']:
   n=bool(sr&8);v=bool(sr&2);z=bool(sr&4)
   condition=dict(always=True,gt=not z and n==v,le=z or n!=v,ne=not z,eq=z)[f['condition']]
   if condition:next_pc=f['target']
  elif op=='rts':next_pc=access(f['src'],32)
  else:raise ValueError(op)
  assert registers[15]==(entry_sp+f['entry_SP_delta_after'])&MASK32
  pc=next_pc
 return dict(registers=registers,pc=pc,sr=sr,RAM=bytes(ram),events=events,steps=steps,coverage=coverage)
def main():
 p=argparse.ArgumentParser();p.add_argument('--start',type=lambda x:int(x,0),default=0x1b1a8);p.add_argument('--stop',type=lambda x:int(x,0),default=0x1b200);a=p.parse_args()
 image_path=ROOT/'render-assets/biwn-inventory-baseline.bin';image=image_path.read_bytes();assert binary_tools.sha(image_path)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
 result=packet(image,a.start,a.stop);out=ROOT/'verification/m68k-fact-packets'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);path=out/'packet.json';path.write_text(json.dumps(result,indent=2)+'\n')
 pointer=dict(status=result['status'],packet=str(path),packet_sha256=binary_tools.sha(path),instructions=len(result['instructions']),range=[a.start,a.stop],builder=str(Path(__file__)),builder_sha256=binary_tools.sha(Path(__file__)))
 (ROOT/'verification/m68k-string-fact-packet-current.json').write_text(json.dumps(pointer,indent=2)+'\n');print(json.dumps(pointer),flush=True)
if __name__=='__main__':main()
