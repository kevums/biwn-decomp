"""Lower supported typed facts to straight-line/label C; no runtime decoder."""
def lower(packet,function='biwn_native_format_pad_body'):
 rows=packet['instructions'];lines=['#include "format-pad-native.h"','#include "m68k-fact-helpers.h"','/* Deterministic typed-IR lowering. Not local-model-authored C. */',f'void {function}(uint32_t *r) {{',' uint32_t value,address;',f' goto L_{packet["start"]:x};']
 def address(o):
  if o['index']==15:
   offset=o['entry_SP_offset'];return f'r[15] {"+"if offset>=0 else"-"} {abs(offset)}u'
  displacement=o['displacement'];return f'r[{o["index"]}] {"+"if displacement>=0 else"-"} {abs(displacement)}u'
 def pre(o,bits):
  if o.get('kind')=='memory'and o['index']!=15 and o['mode']=='predecrement':lines.append(f' r[{o["index"]}]-={bits//8}u;')
 def post(o,bits):
  if o.get('kind')=='memory'and o['index']!=15 and o['mode']=='postincrement':lines.append(f' r[{o["index"]}]+={bits//8}u;')
 def read(o,bits):
  pre(o,bits);mask=(1<<bits)-1
  if o['kind']=='immediate':expression=f'0x{o["value"]&mask:x}u'
  elif o['kind']=='register':
   if o['index']==15:raise ValueError('Direct A7 operand needs explicit virtual-stack lowering')
   expression=f'r[{o["index"]}] & 0x{mask:x}u'
  else:expression=f'PR{bits}({address(o)})'
  lines.append(' value='+expression+';');post(o,bits)
 for row in rows:
  pc=row['pc'];op=row['op'];bits=row['width_bits'];lines.append(f'L_{pc:x}: /* {row["assembly"]} */')
  if op=='rts':lines.append(' return; /* The native boundary performs the original RTS. */');continue
  if op=='bra':lines.append(f' goto L_{row["target"]:x};');continue
  if op in ['bgt','ble']:
   lines.append(f' if(mf_{row["condition"]}(r))goto L_{row["target"]:x};');lines.append(f' goto L_{pc+row["size"]:x};');continue
  if op in ['move','moveq','movea']:
   read(row['src'],bits);dst=row['dst']
   if dst['kind']=='register':
    index=dst['index']
    if index==15:raise ValueError('Direct A7 writes are unsupported')
    if op=='movea':lines.append(f' r[{index}]='+(f'(uint32_t)(int32_t)(int16_t)value;'if bits==16 else'value;'))
    elif bits in [16,32]:lines.append(f' mf_move{bits}(r,{index},value);')
    else:lines.append(f' r[{index}]=(r[{index}]&0xffffff00u)|(value&255u);mf_logic(r,value,8);')
   else:
    pre(dst,bits);lines.append(' address='+address(dst)+';');lines.append(f' PW{bits}(address,value);');post(dst,bits);lines.append(f' mf_logic(r,value,{bits});')
  elif op=='clr':lines.append(f' mf_move16(r,{row["dst"]["index"]},0u);')
  elif op=='tst':read(row['src'],bits);lines.append(f' mf_logic(r,value,{bits});')
  elif op in ['addq','subq']:lines.append(f' mf_{"add"if op=="addq"else"sub"}_word(r,{row["dst"]["index"]},{row["src"]["value"]}u);')
  else:raise ValueError('Unsupported lowering operation:'+op)
  lines.append(f' goto L_{pc+row["size"]:x};')
 lines.append('}');return '\n'.join(lines)+'\n'
