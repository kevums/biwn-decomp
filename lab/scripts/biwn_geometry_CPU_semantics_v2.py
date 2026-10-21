"""Boundary extension plus the compiler's signed-less-or-equal byte result."""
import re
import biwn_geometry_CPU_semantics as prior


def handles(row):
    return prior.handles(row) or prior.cache.parts(row)[0]=='sle.b'


def emit(row):
    op,args=prior.cache.parts(row)
    if op!='sle.b':
        return prior.emit(row)
    assert re.fullmatch(r'd[0-7]',args[0]) and row['size']==2
    return ('case '+hex(row['address'])+'u: /* signed SLE.B; CCR unchanged */ '
            'put(&s,'+args[0][1]+',1,((s.cpu.sr&4u)||(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u))?255u:0u);'
            's.cpu.pc='+hex(row['address']+2)+'u;break;')
