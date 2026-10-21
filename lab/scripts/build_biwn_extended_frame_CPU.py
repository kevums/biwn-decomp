"""Add source-reached CPU cases in an isolated wrapper over accepted dispatcher."""
import hashlib,json,os,re,subprocess,capstone
from pathlib import Path
from datetime import datetime,timezone
import generate_biwn_atomic_startup_math as math
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=json.loads((ROOT/'verification/controller-direction-library-current.json').read_text());run=Path(json.loads((ROOT/'verification/native-GPU-1200-run-current.json').read_text())['directory']);reference=json.loads((run/'reference/report.json').read_text());ram=(run/'reference/warm-RAM.bin').read_bytes();selected=dict(prior['selected_case_sources']);new=sorted({int(x,16)for x in reference['PC_counts']}-set(map(lambda x:int(x,16),selected))-{0x303c,0x3042,0x304e,0x4088})
    decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    out=ROOT/'verification/extended-frame-CPU-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[];unsupported=[]
    for pc in new:
        instruction=next(decoder.disasm(ram[pc:pc+24],pc,count=1));row=math.base.binary_tools.m68k_instructions(ram[pc:pc+instruction.size],pc)[0][0];assert row['classification']=='decoded_instruction'
        try:
            if row['assembly']=='trap #$2':
                assert pc==0xdf7a
                code=('case 0xdf7au: /* source TRAP2, exception-entry boundary only */\n'
                      'v=s.cpu.sr;if(!(v&0x2000u)){s.cpu.usp=s.cpu.registers[15];s.cpu.registers[15]=s.cpu.ssp;}'
                      's.cpu.sr=(uint16_t)((v&0x7fffu)|0x2000u);CHECK(push(&s,0xdf7cu,4));CHECK(push(&s,v,2));'
                      's.cpu.ssp=s.cpu.registers[15];'
                      'CHECK(read_value(&s,0x88u,4,&v));if(v!=0xdeb6u)return 7;s.cpu.pc=v;break;')
            else:code=math.emit(row)
        except Exception as e:unsupported.append(dict(row=row,error=repr(e)));continue
        code=re.sub(r'CHECK\(invoke\(&s,[^;]+?\)\);','',code)
        if 's.service('in code or 'invoke('in code:unsupported.append(dict(row=row,error='unstripped service'));continue
        rows.append(dict(row=row,code=code))
    (out/'unsupported.json').write_text(json.dumps(unsupported,indent=2)+'\n');print('new cases',len(new),'generated',len(rows),'unsupported',len(unsupported),flush=True)
    if unsupported:raise SystemExit('Source generator needs additional semantics; no candidate published. '+str(out))
    source_dir=Path(prior['directory'])/'source';template=(source_dir/'biwn_world_missing_single_step.c').read_text();prefix=template[:template.index('#define CHECK')];functions=re.findall(r'^static\s+(?:[A-Za-z_]\w*\s+)+([A-Za-z_]\w*)\s*\(',prefix,re.M)
    body=prefix+'\n#define CHECK(e) do{int status=(e);if(status)return status;}while(0)\nextern int biwn_source_CPU_step(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);\nint biwn_extended_CPU_step(struct biwn_world_bus*bus,struct biwn_task_cpu*state,biwn_input_write8 write8,biwn_world_cpu_service service,void*context){struct dispatch s;uint32_t v=0,u=0;int full_call=1,stop_on_yield=0;(void)full_call;(void)stop_on_yield;(void)v;(void)u;'+' '.join('(void)'+f+';'for f in functions)+'s.bus=bus;s.cpu=*state;s.write8=write8;s.service=service;s.context=context;switch(s.cpu.pc){\n'
    for x in rows:body+=x['code']+'\n';selected[hex(x['row']['address'])]='biwn_extended_frame_CPU.c'
    body+='default:return biwn_source_CPU_step(bus,state,write8,service,context);}\n*state=s.cpu;return 0;}\n'
    source=out/'biwn_extended_frame_CPU.c';source.write_text(body);library=out/'libextended-frame-CPU.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source_dir),'-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(source),prior['library'],'-o',str(library)];p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    report=dict(status='compiled_unverified',directory=str(out),library=str(library),function='biwn_extended_CPU_step',base_library=prior['library'],selected_case_sources=selected,new_cases=[x['row']for x in rows],warm_RAM_source=str(run/'reference/warm-RAM.bin'),source_sha256=hashlib.sha256(body.encode()).hexdigest(),new_training=False,coordinator_authored=True,whole_game_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/extended-frame-CPU-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
