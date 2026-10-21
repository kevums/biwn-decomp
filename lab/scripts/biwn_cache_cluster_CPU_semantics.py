"""Additional fixed-instruction C emission for the cache-cluster experiment.

Coordinator instruction semantics; not newly recovered game algorithms or
local-model output. Native CPU and cost comparisons are required separately.
"""
import re


def parts(row):
    op, _, operands = row['assembly'].partition(' ')
    return op, [s.strip() for s in operands.split(',')]


def handles(row):
    op, args = parts(row)
    return (op == 'move.w' and ('sr' in args or 'ccr' in args)
            or op == 'movem.l' and row['bytes'] in ['48d77fff', '4cd77fff', '4cd07fff']
            or op in ['scs.b', 'scc.b', 'shi.b', 'seq.b', 'subx.l', 'subi.l', 'ori.l']
            or row['bytes'] == '2528000c'
            or op == 'divs.w' and re.fullmatch(r'd[0-7]', args[0]))


def operand(text, var='v'):
    if text.startswith('#$'):
        return var+'='+hex(int(text[2:], 16))+'u;'
    if re.fullmatch(r'd[0-7]', text):
        return var+'=s.cpu.registers['+text[1]+'];'
    match = re.fullmatch(r'\$([0-9a-f]+)\(a([0-7])\)', text)
    assert match, text
    return 'CHECK(read_value(&s,s.cpu.registers['+str(8+int(match[2]))+']+'+hex(int(match[1], 16))+'u,2,&'+var+'));'


def emit(row):
    pc, nxt = row['address'], row['address']+row['size']
    op, args = parts(row)
    code = ''
    if op == 'move.w' and args[1] == 'sr':
        assert args[0].startswith('#$')
        code = ('if(!(s.cpu.sr&0x2000u)){v=s.cpu.sr;s.cpu.usp=s.cpu.registers[15];'
                's.cpu.sr|=0x2000u;s.cpu.registers[15]=s.cpu.ssp;'
                'CHECK(push(&s,s.cpu.pc,4));CHECK(push(&s,v,2));'
                'CHECK(read_value(&s,0x20u,4,&u));s.cpu.pc=u;*state=s.cpu;return 11;}'
                's.cpu.ssp=s.cpu.registers[15];s.cpu.sr='+hex(int(args[0][2:], 16)&0x271f)+'u;'
                'if(!(s.cpu.sr&0x2000u))s.cpu.registers[15]=s.cpu.usp;')
    elif op == 'move.w' and args[0] == 'sr':
        if args[1] == '-(a7)':
            code = 'v=s.cpu.sr;CHECK(push(&s,v,2));'
        else:
            match = re.fullmatch(r'\$([0-9a-f]+)\(a([0-7])\)', args[1])
            assert match
            code = 'CHECK(write_value(&s,s.cpu.registers['+str(8+int(match[2]))+']+'+hex(int(match[1],16))+'u,2,s.cpu.sr));'
    elif op == 'move.w' and args[1] == 'ccr':
        code = operand(args[0])+'s.cpu.sr=(uint16_t)((s.cpu.sr&0xffe0u)|(v&31u));'
    elif op == 'movem.l':
        if row['bytes'] == '48d77fff':
            code = 'u=s.cpu.registers[15];'+''.join('CHECK(write_value(&s,u+'+str(i*4)+'u,4,s.cpu.registers['+str(i)+']));' for i in range(15))
        else:
            base = 15 if row['bytes'] == '4cd77fff' else 8
            code = 'u=s.cpu.registers['+str(base)+'];'+''.join('CHECK(read_value(&s,u+'+str(i*4)+'u,4,&v));s.cpu.registers['+str(i)+']=v;' for i in range(15))
    elif op in ['scs.b', 'scc.b', 'shi.b', 'seq.b']:
        assert re.fullmatch(r'd[0-7]', args[0])
        condition = {'scs.b':'s.cpu.sr&1u', 'scc.b':'!(s.cpu.sr&1u)', 'shi.b':'!(s.cpu.sr&5u)', 'seq.b':'s.cpu.sr&4u'}[op]
        code = 'put(&s,'+args[0][1]+',1,('+condition+')?255u:0u);'
    elif op == 'subx.l':
        assert all(re.fullmatch(r'd[0-7]', arg) for arg in args)
        source, dest = int(args[0][1]), int(args[1][1])
        code = ('{uint32_t src=s.cpu.registers['+str(source)+'],dst=s.cpu.registers['+str(dest)+'],x=(s.cpu.sr>>4)&1u;'
                'uint32_t result=dst-src-x;unsigned carry=(uint64_t)src+x>(uint64_t)dst;'
                'unsigned overflow=((src^dst)&(result^dst)&0x80000000u)!=0;'
                'unsigned zero=(s.cpu.sr&4u)&&result==0;s.cpu.registers['+str(dest)+']=result;'
                's.cpu.sr=(uint16_t)((s.cpu.sr&0xffe0u)|(carry?17u:0u)|(result&0x80000000u?8u:0u)|(overflow?2u:0u)|(zero?4u:0u));}')
    elif op in ['subi.l', 'ori.l']:
        assert args[0].startswith('#$') and re.fullmatch(r'd[0-7]', args[1])
        reg, value = int(args[1][1]), int(args[0][2:], 16)
        if op == 'subi.l':
            code = 'v=alu(&s,s.cpu.registers['+str(reg)+'],'+hex(value)+'u,32,1,0);put(&s,'+str(reg)+',4,v);'
        else:
            code = 'v=s.cpu.registers['+str(reg)+']|'+hex(value)+'u;put(&s,'+str(reg)+',4,v);nz(&s,v,32);'
    elif row['bytes'] == '2528000c':
        code = 'CHECK(read_value(&s,s.cpu.registers[8]+12u,4,&v));s.cpu.registers[10]-=4u;CHECK(write_value(&s,s.cpu.registers[10],4,v));nz(&s,v,32);'
    elif op == 'divs.w':
        source, dest = int(args[0][1]), int(args[1][1])
        code = ('{int64_t dividend=(int32_t)s.cpu.registers['+str(dest)+'],divisor=(int16_t)s.cpu.registers['+str(source)+'];'
                'if(!divisor){v=s.cpu.sr&~2u;s.cpu.sr=(uint16_t)v;'
                'if(!(s.cpu.sr&0x2000u)){s.cpu.usp=s.cpu.registers[15];s.cpu.registers[15]=s.cpu.ssp;}'
                's.cpu.sr|=0x2000u;CHECK(push(&s,'+hex(nxt)+'u,4));CHECK(push(&s,v,2));'
                'CHECK(read_value(&s,20u,4,&u));s.cpu.pc=u;*state=s.cpu;return 11;}'
                'int64_t q=dividend/divisor,r=dividend%divisor;'
                'if(q< -32768||q>32767)s.cpu.sr=(uint16_t)((s.cpu.sr&~11u)|10u);'
                'else{s.cpu.registers['+str(dest)+']=((uint32_t)(uint16_t)r<<16)|(uint16_t)q;nz(&s,(uint16_t)q,16);}}')
    else:
        raise ValueError(row)
    return 'case '+hex(pc)+'u: /* '+row['assembly']+' */ '+code+'s.cpu.pc='+hex(nxt)+'u;break;'
