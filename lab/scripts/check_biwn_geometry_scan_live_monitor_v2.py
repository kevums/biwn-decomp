"""Qualify the read-only scanner oracle against both native implementations."""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_geometry_scan as gate
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
class CPU(c.Structure):
    _fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
    bp=ROOT/'verification/native-geometry-scan-disc-build-current.json';build=json.loads(bp.read_text());assert build['status']=='terminal_native_geometry_scan_disc_built_entry_verified_pending_gameplay'
    out=ROOT/'verification/native-geometry-scan-monitor'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'scripts/native_geometry_scan_observer.inc.c';text=source.read_text()
    for key,value in {'__SCAN_START__':build['geometry_scan_start'],'__SCAN_END__':build['geometry_scan_end'],'__SCAN_ENTRY__':build['geometry_scan_entry'],'__SCAN_RETURN__':build['geometry_scan_return']}.items():text=text.replace(key,str(value)+'u')
    header='''#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char *ram;static uint32_t frame,errors;static void (*read_cpu)(struct cpu*);
static uint32_t rd16(uint32_t a){if(a>0x1ffffe){errors++;return 0;}return ((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){if(a==0xc0920u)return 0x1dfbfcu;if(a>0x1ffffc){errors++;return 0;}return (rd16(a)<<16)|rd16(a+2);}
static void emit(uint32_t pc){(void)pc;}
static void select_debug_cpu(FILE *file,const struct cpu *cpu){(void)cpu;fprintf(file,"{}");}
'''
    footer='''
void begin(const void *memory,void *reader){ram=memory;read_cpu=(void(*)(struct cpu*))reader;memset(scan_calls,0,sizeof(scan_calls));scan_slots=scan_pending=scan_debug_count=0;scan_entries=scan_returns=scan_errors=scan_stack_outside=0;errors=0;}
void step(uint32_t pc){watch_scan(pc);}
uint32_t check(void){return errors+(uint32_t)scan_errors+(uint32_t)scan_stack_outside+scan_pending+(scan_entries!=1)+(scan_returns!=1);}
void dump(const char *path){FILE *f=fopen(path,"w");fputs("{\\\"diagnostics\\\":true",f);scan_debug_dump(f);fputs("}",f);fclose(f);}
'''
    cpp=out/'monitor.c';cpp.write_text(header+text+footer);lib=out/'monitor.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    l=c.CDLL(str(lib));l.begin.argtypes=[c.c_void_p,c.c_void_p];l.step.argtypes=[c.c_uint32];l.check.restype=c.c_uint32;l.dump.argtypes=[c.c_char_p]
    current=CPU();callback=c.CFUNCTYPE(None,c.POINTER(CPU))(lambda target:c.memmove(target,c.byref(current),c.sizeof(current)))
    baseline=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    patched=bytearray(baseline);payload=Path(build['linked_component']).read_bytes();start=build['resident_address'];patched[start:start+len(payload)]=payload;patched[gate.ENTRY:gate.ENTRY+8]=b'\x4e\xf9'+build['geometry_scan_entry'].to_bytes(4,'big')+b'\x4e\x71'
    gate.BASE=build['geometry_scan_start'];length=build['geometry_scan_end']-gate.BASE;n=gate.Native();checks=[];cases=gate.vectors();state=dict(status='running_scanner_live_oracle_fixtures',pid=os.getpid(),directory=str(out),planned=len(cases)*2,completed=0,source_sha256={str(p):sha(p)for p in [source,Path(__file__),cpp,lib,bp]},new_training=False,default_promoted=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-geometry-scan-monitor-active.json',state)
    mark()
    try:
        for index,case in enumerate(cases):
            for original,image in [(True,baseline),(False,patched)]:
                seeded=gate.seed(image,case);memory=c.create_string_buffer(seeded);current.r[:]=case['incoming']+[gate.SP];current.pc=gate.ENTRY;current.sr=case['sr'];current.usp=0x1fe000 if case['sr']&0x2000 else gate.SP;current.ssp=gate.SP if case['sr']&0x2000 else 0x1ff000
                l.begin(memory,c.cast(callback,c.c_void_p));l.step(gate.ENTRY)
                ram,cpu,_,steps,cycles,minimum=gate.native(n,image,case,length,original)
                c.memmove(memory,ram,len(ram));current.r[:]=cpu[:16];current.r[15]=gate.SP;current.pc=0x1039a if original else build['geometry_scan_return'];current.sr=cpu[17];current.usp=cpu[18]-(4 if not case['sr']&0x2000 else 0);current.ssp=cpu[19]-(4 if case['sr']&0x2000 else 0)
                l.step(current.pc);error=l.check()
                if error:l.dump(str(out/'failure.json').encode());save(out/'failure-case.json',dict(index=index,original=original,case=case,errors=error));raise AssertionError(f'oracle mismatch {index} original={original} errors={error}')
                checks.append(dict(index=index,original=original,steps=steps,cycles=cycles,private_depth=gate.SP-minimum));state['completed']+=1
            if index%128==0:mark()
        save(out/'results.json',checks);state.update(status='terminal_scanner_live_oracle_stable_fixtures_pass',original_cases=len(cases),compiled_cases=len(cases),scope='Read-only entry/return oracle qualified against original and final-address compiled native execution for all1377stable component fixtures including32768entry miss, flags/tags and both stack modes. The harness supplies a synthetic current-task lookup independently of the record table, which deliberately overlaps C0920 in maximum-count fixtures. This fixture adapts post-RTS states to pre-RTS at publicSP; no live gameplay, changing-read prediction, per-instruction stack observation or physical hardware claim.');mark();save(ROOT/'verification/native-geometry-scan-monitor-current.json',state);print(json.dumps({k:state[k]for k in ['status','original_cases','compiled_cases']}),flush=True)
    except BaseException as error:state.update(status='terminal_scanner_live_oracle_failed',error=repr(error));mark();raise
    finally:n.close()
if __name__=='__main__':main()
