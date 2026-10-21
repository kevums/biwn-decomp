"""Cost-only model from pinned UAE compatible handlers; no CPU execution.

Matches emulator base instruction timing, not Jaguar bus contention or physical
clock accuracy. Unsupported operands/exception paths fail rather than guess.
"""
import ctypes as c
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def divs_cycles(dividend,divisor):
    dividend=signed(dividend,32);divisor=signed(divisor,16)
    if not divisor:return -4
    assert dividend!=-0x80000000,'Pinned C abs(INT_MIN) is not defined'
    mcycles=6+(dividend<0)
    if abs(dividend)>>16>=abs(divisor):return (mcycles+2)*2-4
    quotient=abs(dividend)//abs(divisor);mcycles+=55
    if divisor>=0:mcycles+=-1 if dividend>=0 else 1
    for _ in range(15):
        mcycles+=not bool(quotient&0x8000);quotient=(quotient<<1)&0xffffffff
    return mcycles*2-4


def condition(cc,sr):
    z,n,v,carry=bool(sr&4),bool(sr&8),bool(sr&2),bool(sr&1)
    return [True,False,not carry and not z,carry or z,not carry,carry,not z,z,
            not v,v,not n,n,n==v,n!=v,not z and n==v,z or n!=v][cc]

def signed(value,bits):
    value&=(1<<bits)-1
    return value-(1<<bits) if value&(1<<(bits-1)) else value

class Cost:
    def __init__(self,read):
        pointer=json.loads((ROOT/'verification/CPU-cycle-metadata-current.json').read_text())
        self.data=json.loads(Path(pointer['metadata']).read_text());self.read=read
        self.models=[]
        for info in self.data['opcodes']:
            h=self.data['handlers'].get(str(info['handler']))
            self.models.append((info,h))
    def operand(self,info,s,width=2):
        mode,reg=info['smode'],info['sreg'];pc=s.pc;r=s.registers
        if mode==0:return r[reg]&((1<<(width*8))-1)
        if mode==1:return r[8+reg]&((1<<(width*8))-1)
        ext=pc+2
        if mode in [2,3]:a=r[8+reg]
        elif mode==4:a=r[8+reg]-(2 if width==1 and reg==7 else width)
        elif mode==5:a=r[8+reg]+signed(self.read(ext,2),16)
        elif mode==6:
            x=self.read(ext,2);index=r[(x>>12)&15];index=index if x&0x800 else signed(index,16)
            a=r[8+reg]+signed(x&255,8)+index
        elif mode==7:a=signed(self.read(ext,2),16)
        elif mode==8:a=self.read(ext,4)
        elif mode==9:a=ext+signed(self.read(ext,2),16)
        elif mode==10:
            x=self.read(ext,2);index=r[(x>>12)&15];index=index if x&0x800 else signed(index,16)
            a=ext+signed(x&255,8)+index
        elif mode==11:return self.read(ext,width)
        elif mode in [12,13,14,15]:return reg
        else:raise ValueError(('cycle operand mode',mode))
        a&=0xffffff
        assert a<0x200000,('cost-only operand would read device',hex(a))
        return self.read(a,width)
    def predict(self,opcode,s):
        info,h=self.models[opcode]
        if not h:raise ValueError(('unsupported opcode',hex(opcode)))
        if h['constant_cycles'] is not None:return h['constant_cycles'],h['name']
        name=h['name'];base=re.search(r'\(\s*(\d+)\+retcycles',h['returns'][-1])
        if name=='Bcc':return (10 if condition(info['condition'],s.sr)else(12 if opcode&255 in [0,255]else 8)),name
        if name=='DBcc':return (12 if condition(info['condition'],s.sr)else(14 if s.registers[opcode&7]&65535==0 else 10)),name
        if name=='Scc':return (6 if condition(info['condition'],s.sr)else 4),name
        if name=='BCLR':return (min(int(v)for v in h['returns'])if (self.operand(info,s,4)&31)<16 else max(int(v)for v in h['returns'])),name
        if name in ['MVMLE','MVMEL']:
            mask=self.read(s.pc+2,2);return int(base.group(1))+mask.bit_count()*(8 if info['size']==2 else 4),name
        if name in ['ASR','ASL','LSR','LSL','ROR','ROL','ROXR','ROXL']:
            count=(s.registers[(opcode>>9)&7]&63)if opcode&32 else(((opcode>>9)&7)or 8)
            return int(base.group(1))+2*count,name
        if name=='MULU':return int(base.group(1))+2*self.operand(info,s).bit_count(),name
        if name=='MULS':
            source=(signed(self.operand(info,s),16)<<1)&0xffffffff;transitions=0
            while source:
                transitions+=source&3 in [1,2];source>>=1
            return int(base.group(1))+2*transitions,name
        if name in ['DIVU','DIVS']:
            divisor=self.operand(info,s)
            assert divisor,'Divide-by-zero exception needs separate cost accounting'
            dividend=s.registers[info['dreg']]
            if name=='DIVU':
                from biwn_divu_cycle_cost_local import divu_cycles
                extra=divu_cycles(dividend,divisor)
            else:extra=divs_cycles(dividend,divisor)
            return int(base.group(1))+extra,name
        raise ValueError(('variable cost not yet modeled',name,h['returns']))
