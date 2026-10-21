"""Typed lowering with per-bit CCR liveness; v2 remains unchanged.

Only semantic-frame flag computations are elided. Every original data access,
register assignment and control-flow edge retains its v2 lowering. IRQ/fault
visibility and aliases into the compiler's private semantic frame are outside
the existing helper contract and require separate verification.
"""
FLAG_BITS={'X':16,'N':8,'Z':4,'V':2,'C':1}
SUPPORTED={'move','movea','moveq','lea','clr','tst','cmpa','addq','subq','bra','bgt','ble','beq','bne','rts'}


def liveness(packet,exit_flags=31):
    if exit_flags&~31:raise ValueError('Unknown exit CCR bits')
    rows=packet['instructions'];by_pc={r['pc']:r for r in rows}
    if len(by_pc)!=len(rows)or packet['start']not in by_pc:raise ValueError('Invalid instruction PCs')
    uses={};defs={};successors={}
    for row in rows:
        pc=row['pc'];op=row['op']
        if op not in SUPPORTED:raise ValueError('Unsupported CCR lowering operation: '+op)
        mode=row['ccr']['mode']
        defs[pc]=0 if mode=='unchanged'else 31 if row['ccr']['X']=='from_carry'else 15
        uses[pc]=exit_flags if op=='rts'else 14 if op in ['bgt','ble']else 4 if op in ['beq','bne']else 0
        edges=[]if op=='rts'else [row['target']]if op=='bra'else [row['target'],pc+row['size']]if op in ['bgt','ble','beq','bne']else [pc+row['size']]
        if edges!=row['successors']or any(target not in by_pc for target in edges):raise ValueError('Invalid/unsupported CFG edge')
        successors[pc]=edges
    incoming={pc:0 for pc in by_pc};outgoing=dict(incoming);iterations=0
    while True:
        changed=False;iterations+=1
        for row in reversed(rows):
            pc=row['pc'];out=0
            for target in successors[pc]:out|=incoming[target]
            live=uses[pc]|(out&~defs[pc])
            if outgoing[pc]!=out or incoming[pc]!=live:changed=True;outgoing[pc]=out;incoming[pc]=live
        if not changed:break
    return dict(exit_flags=exit_flags,iterations=iterations,flag_bits=FLAG_BITS,
        rows=[dict(pc=r['pc'],assembly=r['assembly'],successors=successors[r['pc']],
                   defines=defs[r['pc']],uses=uses[r['pc']],live_in=incoming[r['pc']],
                   live_out=outgoing[r['pc']],computed_flags=outgoing[r['pc']]&defs[r['pc']])for r in rows],
        scope='Backward least fixed point over declared CFG, independently per CCR bit. Full XNZVC required at original return by default. Memory accesses and semantic data-register writes are never removed by this pass.')


HELPERS='''
static inline void lf_logic(uint32_t *r,uint32_t value,unsigned bits,uint32_t live){
 uint32_t mask=bits==32?0xffffffffu:((1u<<bits)-1u),flags;
 value&=mask;flags=(value==0u?4u:0u)|((value&(1u<<(bits-1u)))?8u:0u);
 r[16]=(r[16]&~live)|(flags&live);
}
static inline uint16_t lf_add16(uint32_t *r,uint16_t a,uint16_t b,uint32_t live){
 uint32_t sum=(uint32_t)a+b;uint16_t value=(uint16_t)sum;
 uint32_t flags=(sum>65535u?17u:0u)|((~(a^b)&(a^value)&0x8000u)?2u:0u)|
  (value==0u?4u:0u)|((value&0x8000u)?8u:0u);
 r[16]=(r[16]&~live)|(flags&live);return value;
}
static inline uint16_t lf_sub16(uint32_t *r,uint16_t a,uint16_t b,uint32_t live){
 uint16_t value=(uint16_t)((uint32_t)a-b);
 uint32_t flags=(a<b?17u:0u)|(((a^b)&(a^value)&0x8000u)?2u:0u)|
  (value==0u?4u:0u)|((value&0x8000u)?8u:0u);
 r[16]=(r[16]&~live)|(flags&live);return value;
}
static inline void lf_cmp32(uint32_t *r,uint32_t a,uint32_t b,uint32_t live){
 uint32_t value=a-b,flags=(a<b?1u:0u)|(((a^b)&(a^value)&0x80000000u)?2u:0u)|
  (value==0u?4u:0u)|((value&0x80000000u)?8u:0u);
 r[16]=(r[16]&~live)|(flags&live);
}
'''


def lower(packet,function='biwn_native_format_string_body',abi_header='format-string-native.h',exit_flags=31):
    analysis=liveness(packet,exit_flags);needed={row['pc']:row['computed_flags']for row in analysis['rows']}
    lines=[f'#include "{abi_header}"','#include "m68k-fact-helpers-v2.h"',
           '/* Deterministic typed-IR CCR-liveness lowering. Not model-authored. */',HELPERS,
           f'void {function}(uint32_t *r) {{',' uint32_t value,address;',f' goto L_{packet["start"]:x};']
    def address(o):
        if o['index']==15:
            offset=o['entry_SP_offset'];return f'r[15] {"+"if offset>=0 else"-"} {abs(offset)}u'
        offset=o['displacement'];return f'r[{o["index"]}] {"+"if offset>=0 else"-"} {abs(offset)}u'
    def pre(o,bits):
        if o.get('kind')=='memory'and o['index']!=15 and o['mode']=='predecrement':lines.append(f' r[{o["index"]}]-={bits//8}u;')
    def post(o,bits):
        if o.get('kind')=='memory'and o['index']!=15 and o['mode']=='postincrement':lines.append(f' r[{o["index"]}]+={bits//8}u;')
    def read(o,bits):
        pre(o,bits);mask=(1<<bits)-1
        if o['kind']in ['immediate','address']:expression=f'0x{o["value"]&mask:x}u'
        elif o['kind']=='register':
            if o['index']==15:raise ValueError('Direct A7 operand unsupported')
            expression=f'r[{o["index"]}] & 0x{mask:x}u'
        else:expression=f'PR{bits}({address(o)})'
        lines.append(' value='+expression+';');post(o,bits)
    def logic(bits,live):
        if live:lines.append(f' lf_logic(r,value,{bits},{live}u);')
    for row in packet['instructions']:
        pc=row['pc'];op=row['op'];bits=row['width_bits'];live=needed[pc]
        lines.append(f'L_{pc:x}: /* {row["assembly"]}; computed CCR mask {live} */')
        if op=='rts':lines.append(' return; /* The unchanged boundary performs original RTS. */');continue
        if op=='bra':lines.append(f' goto L_{row["target"]:x};');continue
        if op in ['bgt','ble','beq','bne']:
            condition=f'mf_{row["condition"]}(r)'if op in ['bgt','ble']else '(r[16]&4u)'if op=='beq'else '!(r[16]&4u)'
            lines.append(f' if({condition})goto L_{row["target"]:x};');lines.append(f' goto L_{pc+row["size"]:x};');continue
        if op in ['move','moveq','movea','lea']:
            read(row['src'],bits);dst=row['dst']
            if dst['kind']=='register':
                index=dst['index']
                if index==15:raise ValueError('Direct A7 writes unsupported')
                if op in ['movea','lea']:lines.append(f' r[{index}]='+(f'(uint32_t)(int32_t)(int16_t)value;'if bits==16 else'value;'))
                elif bits==32:lines.append(f' r[{index}]=value;');logic(bits,live)
                elif bits==16:lines.append(f' mf_word(r,{index},value);');logic(bits,live)
                else:lines.append(f' r[{index}]=(r[{index}]&0xffffff00u)|(value&255u);');logic(bits,live)
            else:
                pre(dst,bits);lines.append(' address='+address(dst)+';');lines.append(f' PW{bits}(address,value);');post(dst,bits);logic(bits,live)
        elif op=='clr':
            lines.append(' value=0u;');lines.append(f' mf_word(r,{row["dst"]["index"]},value);');logic(bits,live)
        elif op=='tst':read(row['src'],bits);logic(bits,live)
        elif op=='cmpa':
            read(row['src'],bits)
            if live:lines.append(f' lf_cmp32(r,r[{row["dst"]["index"]}],(uint32_t)(int32_t)(int16_t)value,{live}u);')
        elif op in ['addq','subq']:
            dst=row['dst'];operation='add'if op=='addq'else'sub';symbol='+'if op=='addq'else'-';immediate=row['src']['value']
            if dst['kind']=='register':
                if live:lines.append(f' value=lf_{operation}16(r,(uint16_t)r[{dst["index"]}],{immediate}u,{live}u);')
                else:lines.append(f' value=(uint16_t)((uint16_t)r[{dst["index"]}]{symbol}{immediate}u);')
                lines.append(f' mf_word(r,{dst["index"]},value);')
            else:
                if dst['mode']!='indirect':raise ValueError('Unsupported RMW addressing')
                read(dst,bits)
                if live:lines.append(f' value=lf_{operation}16(r,(uint16_t)value,{immediate}u,{live}u);')
                else:lines.append(f' value=(uint16_t)((uint16_t)value{symbol}{immediate}u);')
                lines.append(f' PW16({address(dst)},value);')
        else:raise ValueError('Unsupported lowering operation: '+op)
        lines.append(f' goto L_{pc+row["size"]:x};')
    lines.append('}');return '\n'.join(lines)+'\n'
