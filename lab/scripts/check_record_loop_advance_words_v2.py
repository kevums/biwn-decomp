"""Exhaust low D3 words in actual68000 code against independent flag arithmetic."""
import ctypes as c,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
import check_biwn_scheduler as scheduler

def main():
    out=V/'record-loop-advance-all-words-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    header=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-update-v2/deck-coordinate-contract.h'
    helper=ROOT/'projects/black-ice-white-noise/restoration/experimental/coordinator-record-loop-advance-v1/model-native-advance.inc'
    source=out/'probe.c';source.write_text('#include <stddef.h>\n#include "'+str(header)+'"\n#include "'+str(helper)+'"\n'+r'''
struct result{uint32_t d3;uint16_t sr,take;};
static __attribute__((noinline))int probe(struct biwn_deck_context*s){return gr_next_native(s);}
void run(void){
 struct biwn_deck_context*s=(void*)0x170000u;volatile uint8_t*bytes=(void*)s;
 volatile struct result*out=(void*)0x80000u;volatile uint32_t*bad=(void*)0x110000u;*bad=0;
 unsigned d3off=offsetof(struct biwn_deck_context,cpu.registers[3]),sroff=offsetof(struct biwn_deck_context,cpu.sr);
 for(uint32_t i=0;i<65536u;i++){
  for(unsigned k=0;k<128;k++)bytes[k]=0xa5u;
  s->cpu.registers[3]=((i^0xa5a5u)<<16)|i;
  s->cpu.sr=(uint16_t)((((i<<5)^0xa700u)&0xffe0u)|(i&31u));
  int taken=probe(s);out[i].d3=s->cpu.registers[3];out[i].sr=s->cpu.sr;out[i].take=(uint16_t)taken;
  for(unsigned k=0;k<128;k++)if(!(d3off<=k&&k<d3off+4u)&&!(sroff<=k&&k<sroff+2u)&&bytes[k]!=0xa5u)(*bad)++;
 }
}
''')
    prefix=ROOT/'tools/m68k-elf/bin/m68k-elf-';elf=out/'probe.elf';binary=out/'probe.bin'
    command=[str(prefix)+'gcc','-m68000','-msoft-float','-Os','-std=c11','-ffreestanding','-fno-builtin','-fno-ipa-cp','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x180000,-e,run',str(source),'-o',str(elf)]
    q=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    subprocess.run([str(prefix)+'objcopy','-O','binary',str(elf),str(binary)],check=True)
    nm=subprocess.check_output([str(prefix)+'nm','-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm)
    entry=next(int(x.split()[0],16)for x in nm.splitlines()if x.split()[-1]=='run')
    memory=bytearray(0x200000);payload=binary.read_bytes();memory[0x180000:0x180000+len(payload)]=payload;memory[0x1ffe00:0x1ffe02]=bytes.fromhex('60fe');memory[0x1ff000:0x1ff004]=(0x1ffe00).to_bytes(4,'big')
    native=scheduler.Native();core=native.lib;state=dict(status='running_all_word_native_probe',directory=str(out),pid=os.getpid(),completed_banks=0,new_predictions=0,new_training=False);pointer=V/'record-loop-advance-all-words-v2-current.json'
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();rows=[]
    try:
        # Disable host bus journaling for this isolated pure-RAM batch; results,
        # canaries and whole-table hashes are checked after native execution.
        native.device.lib.lab_device_observe.argtypes=[c.c_void_p];native.device.lib.lab_device_observe(None)
        for bank in [0,0x2000]:
            native.device.seed(bytes(memory),0);core.m68k_pulse_reset();core.m68k_set_irq(0)
            core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(17,0);core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(17,bank|31);core.m68k_set_reg(16,entry)
            for chunks in range(50000):
                core.m68k_execute(100000)
                if chunks%2000==0:
                    state.update(raw_PC=core.m68k_get_reg(None,16),raw_output_pointer=core.m68k_get_reg(None,10),execution_chunks=chunks+1);mark();print('Native batch',hex(bank),'chunks',chunks+1,'output pointer',hex(state['raw_output_pointer']),flush=True)
                if core.m68k_get_reg(None,16)==0x1ffe00:break
            else:
                state.update(boundary_CPU_registers=[core.m68k_get_reg(None,i)for i in range(18)]);mark();(out/'RAM-at-execution-bound.bin').write_bytes(native.device.ram());raise AssertionError('All-word native driver did not return at five-billion-cycle bound')
            raw=native.device.ram();assert int.from_bytes(raw[0x110000:0x110004],'big')==0,'Helper changed unrelated context/canary bytes'
            table=raw[0x80000:0x100000];tablep=out/('bank-'+hex(bank)+'-outputs.bin');tablep.write_bytes(table)
            for i in range(65536):
                value=(i+1)&65535;difference=(value-39)&65535
                negative=bool(difference&0x8000);overflow=bool((value^39)&(value^difference)&0x8000)
                flags=(16 if i==65535 else 0)|(8 if negative else 0)|(4 if difference==0 else 0)|(2 if overflow else 0)|(1 if value<39 else 0)
                expected_d3=((i^0xa5a5)<<16)|value;expected_sr=(((i<<5)^0xa700)&0xffe0)|flags;expected_take=int(difference==0 or negative!=overflow)
                at=i*8;actual=(int.from_bytes(table[at:at+4],'big'),int.from_bytes(table[at+4:at+6],'big'),int.from_bytes(table[at+6:at+8],'big'))
                assert actual==(expected_d3,expected_sr,expected_take),(hex(i),actual,(expected_d3,expected_sr,expected_take))
            rows.append(dict(physical_stack_bank=bank,logical_low_D3_cases=65536,logical_upper_SR_values=2048,logical_initial_CCR_values=32,context_canary_errors=0,table_sha256=sha(tablep),execution_chunks=chunks+1))
            state['completed_banks']=len(rows);mark();print('All-word native bank',hex(bank),'65536 pass',flush=True)
        state.update(status='terminal_131072_native_loop_tail_cases_match_independent_flags_and_context_canaries',cases=rows,total_cases=131072,source_sha256={str(p):sha(p)for p in [Path(__file__),header,helper,source,elf,binary,out/'compiler.log',out/'symbols.txt',*out.glob('*outputs.bin')]},scope='Pure helper contract,all65536lowD3words with varied upperD3/all2048logicalupperSR/all32logicalCCR patterns,both physical stack banks. Independent Python arithmetic computes ADDX and CMPNZVC/BLE. Whole128bytecontext canaries permit only logicalD3/SRchanges. Initial logicalSR/upperD3 patterns are correlated,not a full Cartesian product. This is not disc integration,arbitraryIRQ,timing or whole-game fidelity.');mark()
    except BaseException as error:state.update(status='terminal_all_word_native_probe_failed',error=repr(error));mark();raise
    finally:native.close()

if __name__=='__main__':main()
