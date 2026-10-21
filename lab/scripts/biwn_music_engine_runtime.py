"""Live C-owned banked DSP engine through declared startup word/timer events."""
import ctypes as c,hashlib,struct
from check_biwn_music_DSP_engine import State,logical,dsp,media,Bus
class MusicEngineMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.music_engine_active=False;self.music_engine_calls=[];self.music_word_events=[];self.music_tick=0;self.engine_trace=[]
        self.engine_step=self.lib.biwn_dsp_music_engine_step;self.engine_step.argtypes=[c.POINTER(Bus),c.POINTER(State)];self.engine_step.restype=c.c_int
        self.engine_irq=self.lib.biwn_dsp_music_engine_assert_interrupt;self.engine_irq.argtypes=[c.POINTER(State),c.c_uint32];self.engine_irq.restype=c.c_int
        self.core.DSPGetReg.argtypes=[c.c_int];self.core.DSPGetReg.restype=c.c_uint32;self.core.DSPGetFlags.restype=c.c_uint32
        media_run=self.dsp_run;media_irq=self.dsp_irq
        self.dsp_run=lambda bus,state,budget:media_run(bus,c.cast(state,c.POINTER(dsp.State)),budget)
        self.dsp_irq=lambda state:media_irq(c.cast(state,c.POINTER(dsp.State)))
        self.engine_callbacks=[dsp.R8(lambda _,a,v:(v.__setitem__(0,self.core.JaguarReadByte(a,2)),0)[1]),dsp.R32(lambda _,a,v:(v.__setitem__(0,self.core.DSPReadLong(a,2)),0)[1]),dsp.W32(lambda _,a,v:(self.core.DSPWriteLong(a,v,2),0)[1]),Bus._fields_[3][1](lambda _,a,v:(self.core.DSPWriteWord(a,v,2),0)[1]),dsp.OBS(lambda _,pc:self.engine_trace.append(pc))];self.engine_bus=Bus(*self.engine_callbacks,None)
    def logical_DSP(self):
        if self.mode=='C'and isinstance(self.C_DSP,State):return logical(self.C_DSP)
        return super().logical_DSP()
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode!='C'or not isinstance(self.C_DSP,State)or w!=4:return
        if a==0xf1a100:self.C_DSP.bank=0 if self.C_DSP.flags&8 else (self.C_DSP.flags>>14)&1;self.C_DSP.prestore_bank=self.C_DSP.bank;self.C_DSP.flags_delay=0
        if a==0xf1a110 and v!=0xf1b126:self.music_engine_active=False
    def engine_wait(self):
        if self.mode=='native':return self.core.DSPGetPC()==0xf1b212 and self.raw_DSP()[8495]==1 and not self.core.DSPGetFlags()&8 and self.core.DSPGetReg(2)==self.core.DSPGetReg(28)and struct.unpack_from('=I',self.raw_DSP(),8239+21*4)[0]==self.core.DSPGetReg(28)
        s=self.C_DSP;return s.pc==0xf1b212 and s.bank==1 and not s.flags&8 and s.registers[1][2]==s.registers[1][28]and s.registers[0][21]==s.registers[1][28]
    def engine_pump(self,label):
        trace=[];count=0;before=self.counter.value;begin=self.C_DSP.instructions if self.mode=='C'else 0
        for _ in range(100000):
            if self.engine_wait():break
            if self.mode=='native':pc=self.core.DSPGetPC();trace.append(pc);n=self.counter.value;self.core.DSPExec(1);count+=(self.counter.value-n)&0xffffffff
            else:
                self.engine_trace.clear();assert self.engine_step(c.byref(self.engine_bus),c.byref(self.C_DSP))==0,(label,hex(self.C_DSP.pc));trace.extend(self.engine_trace)
        else:raise AssertionError(('Engine wait budget',label))
        if self.mode=='C':count=self.C_DSP.instructions-begin;assert self.counter.value==before;c.memmove(self.core.DSPGetRAM(),bytes(self.C_DSP.local_RAM),8192)
        self.music_engine_calls.append(dict(label=label,blocks=len(trace),instructions=count,PC_sha256=hashlib.sha256(b''.join(struct.pack('>I',p)for p in trace)).hexdigest(),DSP_sha256=hashlib.sha256(self.logical_DSP()).hexdigest()))
    def source_entry(self,*args,**kwargs):
        self.music_engine_active=False;result,checks=super().source_entry(*args,**kwargs);self.music_engine_calls=[];self.music_word_events=[];self.music_tick=0
        if self.mode=='C':
            s=State()
            for name,_ in dsp.State._fields_:
                if name=='registers':
                    for k in range(2):s.registers[k][:]=self.C_DSP.registers[k]
                elif name=='local_RAM':s.local_RAM[:]=self.C_DSP.local_RAM
                else:setattr(s,name,getattr(self.C_DSP,name))
            self.C_DSP=s
        self.music_engine_active=True;self.engine_pump('live_bank1_mixer_init');result['music_engine_init']=list(self.music_engine_calls);result['after_music_engine_hardware']=self.hardware();return result,checks
    def clock_tick(self):
        self.source_system_clock_tick()
        if not self.music_engine_active:return
        events=[2,1]if self.music_tick%4==0 else [1]
        for irq in events:
            if self.mode=='native':self.core.DSPSetIRQLine(irq,1)
            else:assert self.engine_irq(c.byref(self.C_DSP),irq)==0
            self.engine_pump(f'startup_word{self.music_tick}_IRQ{irq}')
        self.core.DACWordStrobe();pair=dsp.strobed_pair(self.dac());self.music_word_events.append(dict(word=self.music_tick,IRQs=events,PCM=pair,DSP_sha256=hashlib.sha256(self.logical_DSP()).hexdigest(),DAC_sha256=hashlib.sha256(self.dac()).hexdigest()));self.music_tick+=1
