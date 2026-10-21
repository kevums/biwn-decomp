"""Instrument an isolated instruction-timed bridge for live attack-call evidence.

Captures are observations, never a replacement CPU provider or default change.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

CAPTURE=r'''
static unsigned cap_id,cap_active;
static uint32_t cap_sp,cap_supervisor;
static FILE *cap_trace;
static const char *cap_directory=CAPTURE_DIRECTORY;
static void cap_u32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static FILE *cap_file(const char *suffix){char path[4096];snprintf(path,sizeof(path),"%s/%03u-%s",cap_directory,cap_id,suffix);return fopen(path,"wb");}
static void cap_snapshot(const struct biwn_task_cpu *s,const char *cpu_name,const char *ram_name){
 uint8_t b[78];unsigned r;FILE *f;
 for(r=0;r<16;r++)cap_u32(b+r*4,s->registers[r]);
 cap_u32(b+64,s->pc);cap_u32(b+68,s->usp);cap_u32(b+72,s->ssp);b[76]=(uint8_t)(s->sr>>8);b[77]=(uint8_t)s->sr;
 f=cap_file(cpu_name);if(f){fwrite(b,1,78,f);fclose(f);}
 f=cap_file(ram_name);if(f){fwrite(H.RAM,1,0x200000,f);fclose(f);}
}
static void cap_finish(const struct biwn_task_cpu *s,int complete){
 FILE *f;if(complete)cap_snapshot(s,"after-CPU.bin","after-RAM.bin");
 if(cap_trace)fclose(cap_trace);cap_trace=NULL;
 f=cap_file("result.json");if(f){fprintf(f,"{\"complete\":%s,\"stop_PC\":%u,\"entry_SP\":%u}\n",complete?"true":"false",s->pc,cap_sp);fclose(f);}cap_active=0;
}
static void cap_before(const struct biwn_task_cpu *s){
 uint16_t state;
 if(cap_active){
  if((s->sr&0x2000u)!=cap_supervisor){cap_finish(s,0);return;}
  if(s->pc==0x19f2a&&s->registers[15]==cap_sp){cap_finish(s,1);return;}
  /* Abort at an external helper/context switch, never invent its effects. */
  switch(s->pc){case 0x190bc:case 0xe4c0:case 0x1a0f8:case 0xdf60:case 0x1aade:case 0xdf22:case 0x11e6c:case 0x18160:case 0x1aa40:case 0x1ab2a:case 0xdf3e:case 0x18e92:case 0x1b044:case 0xdf8c:case 0xdf9c:cap_finish(s,0);return;default:break;}
 }
 if(!cap_active&&cap_id<32&&s->pc==0x191f4){
  state=((uint16_t)H.RAM[0x49cb8]<<8)|H.RAM[0x49cb9];if(state!=2)return;
  cap_id++;cap_sp=s->registers[15];cap_supervisor=s->sr&0x2000u;cap_active=1;
  cap_snapshot(s,"before-CPU.bin","before-RAM.bin");cap_trace=cap_file("bus.bin");
 }
}
static void cap_bus(unsigned op,uint32_t address,unsigned width,uint32_t value){
 uint8_t b[10];if(!cap_active||!cap_trace)return;
 if(address>=cap_sp-0x1000u&&address<cap_sp+8u)return;
 b[0]=(uint8_t)op;cap_u32(b+1,address);b[5]=(uint8_t)width;cap_u32(b+6,value);fwrite(b,1,10,cap_trace);
}
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--routine',choices=['controls','scene_cleanup','scene_setup'],default='controls')
    parser.add_argument('--capture-limit',type=int,default=32)
    args=parser.parse_args()
    assert 1<=args.capture_limit<=128
    base=json.loads(args.base.read_text())
    source_path=Path(base['directory'])/'fast_CPU_bridge.c'
    source=source_path.read_text()
    out=ROOT/'verification/controls-live-capture-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);captures=out/'captures';captures.mkdir()
    if base.get('private_CPU_state'):
        shutil.copytree(source_path.parent/'pinned-CPU-headers',out/'pinned-CPU-headers')
    marker='static struct host H;static struct stats S;static int mode;static FILE*state_file,*cost_file;'
    assert source.count(marker)==1
    code=CAPTURE.replace('CAPTURE_DIRECTORY',json.dumps(str(captures))).replace('cap_id<32','cap_id<'+str(args.capture_limit))
    entry,exit,state_filter='0x191f4','0x19f2a',2
    if args.routine in['scene_cleanup','scene_setup']:
        entry,exit,state_filter=('0x20f0c','0x20f76',None)if args.routine=='scene_cleanup'else('0x20f78','0x21240',None)
        code=code.replace('0x191f4',entry).replace('0x19f2a',exit)
        code=code.replace(' uint16_t state;\n','').replace('state=((uint16_t)H.RAM[0x49cb8]<<8)|H.RAM[0x49cb9];if(state!=2)return;','')
    source=source.replace(marker,marker+'\n'+code)
    before='H.read_cpu(&s);if(s.pc!=PC)return fail(PC,91);'
    assert source.count(before)==1
    source=source.replace(before,'H.read_cpu(&s);if(s.pc!=PC)return fail(PC,91);if(mode==2)cap_before(&s);')
    for width in [8,16,32]:
        old=f'*p=(uint{width}_t)H.read{width}(a);return 0;' if width!=32 else '*p=H.read32(a);return 0;'
        assert source.count(old)==1,old
        source=source.replace(old,old.replace('return 0;',f'cap_bus(0,a,{width//8},*p);return 0;'))
        old=f'H.write{width}(a,v);return 0;'
        assert source.count(old)==1
        source=source.replace(old,old.replace('return 0;',f'cap_bus(1,a,{width//8},v);return 0;'))
    source=source.replace('if(state_file)fclose(state_file);','if(cap_active){struct biwn_task_cpu unfinished;H.read_cpu(&unfinished);cap_finish(&unfinished,0);}if(state_file)fclose(state_file);')
    path=out/'fast_CPU_bridge.c';path.write_text(source)
    library=out/'libcapture-CPU-bridge.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(path),base['CPU_library'],base['cost_library'],'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    receipt={**base,'status':'compiled_unverified_live_capture_instrumentation','directory':str(out),'library':str(library),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'base_manifest':str(args.base.resolve()),'base_source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'captures':str(captures),'capture_limit':args.capture_limit,'routine':args.routine,'capture_entry':entry,'entry_state_filter':state_filter,'exit_before_RTS':exit,'instruction_timing_unchanged_intended':True,'default_promoted':False,'scope':'Temporary bus/state observer in instruction-level CPU provider; actual run comparison still required. No high-level function substitution.'}
    args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'report.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'receipt':str(args.receipt),'captures':str(captures)}),flush=True)


if __name__=='__main__':main()
