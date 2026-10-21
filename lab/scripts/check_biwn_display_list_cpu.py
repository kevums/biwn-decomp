"""Display-list fullCPU/private link table: native + independent Unicorn + C."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_render_queue_cpu as queue
import check_biwn_display_list as logical
ROOT=queue.ROOT;CPU=queue.CPU;SP=queue.SP;STOP=queue.STOP;save=queue.save;read=queue.read
queue.ENTRIES=set();queue.RETURNS=set();queue.SCRIPTS=set()
class Runtime(queue.Runtime):
    def __init__(self,library,rows):
        self.native_oracle=queue.cd.scheduler.Native();self.device=self.native_oracle.device;self.core=self.native_oracle.lib;self.prefix=self.native_oracle.prefix;self.lib=c.CDLL(str(library));self.rows={r['address']:r for r in rows}
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.fn=self.lib.biwn_display_list_cpu_body;self.call=self.lib.biwn_display_list_cpu_call
        for fn in [self.fn,self.call]:fn.argtypes=[c.POINTER(queue.world.Bus),c.POINTER(CPU),queue.cd.dispatch.W8,queue.cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int

def cases(snapshot):
    rng=random.Random(0x185b2c);rows=[]
    for number,old in enumerate(logical.cases(snapshot)):
        supervisor=number%2
        case=dict(id=number,entry=0x185b2,registers=old['incoming']+[SP],SR=(0x2000 if supervisor else 0)|((number%8)<<8)|rng.randrange(32),usp=0x170000 if supervisor else SP,ssp=SP if supervisor else 0x1d0000,body=number%3==1,render=False,outer_RTS=0x18852,read_queues=[],params=[old['records'],old['output']],initial=old['initial'],real_captured_descriptors=old.get('real_captured_descriptors',False))
        rows.append(case)
    return rows

def fixture(snapshot,case):
    ram=bytearray(snapshot)
    for a,w,v in case['initial']:ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
    for i,v in enumerate([STOP]+case['params']):ram[SP+i*4:SP+i*4+4]=v.to_bytes(4,'big')
    return bytes(ram)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'display-list-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    out=ROOT/'verification/biwn-display-list-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libdisplay-list-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_display_list_cpu.c'),'-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    runtime=Runtime(library,mapping['instructions_decoded']);vectors=cases(snapshot)[:opt.limit or None];rows=[];coverage=set()
    try:
        for case in vectors:
            save(out/'status.json',dict(status='running',case=case['id']));ram=fixture(snapshot,case);left,expected,native=runtime.native(ram,case,coverage);observed,observer,independent=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case)
            if rebuilt['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or independent['trace']!=rebuilt['trace']:
                save(out/'mismatch.json',dict(case=case,CPU_native=queue.cd.scheduler.cpu_dict(expected),CPU_Unicorn=queue.cd.scheduler.cpu_dict(observer),CPU_C=queue.cd.scheduler.cpu_dict(actual),native=native,Unicorn=independent,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:40],Unicorn_RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(observed,right))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
            rows.append(dict(case=case,CPU=queue.cd.scheduler.cpu_dict(actual),original=native,rebuilt=rebuilt,fullCPU_RAM_privateframes_orderedbus_match=True))
        save(out/'fixtures.json',rows)
        missing=sorted({r['address']for r in mapping['instructions_decoded']}-coverage)
        if opt.limit:save(out/'status.json',dict(status='terminal_preflight',cases=len(rows)));print(json.dumps(dict(directory=str(out),cases=len(rows),coverage=[254-len(missing),254])));return
        assert missing==[0x185ec,0x18642],list(map(hex,missing));guards=[];case=vectors[0];ram=fixture(snapshot,case)
        for options in [{'missing':i}for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2)]:
            _,_,result=runtime.translated(ram,case,**options);assert result['status']==1 and result['CPU_unchanged']and not result['trace'];guards.append(options)
        for options,status in [(dict(bad_pc=True),7),(dict(budget=1),4),(dict(fail=('read',4)),2),(dict(fail=('write',4)),2)]:
            _,_,result=runtime.translated(ram,case,**options);assert result['status']==status and result['CPU_unchanged'];guards.append(options)
        for width in [2]:
            _,_,result=runtime.translated(ram,vectors[1],fail=('read',width));assert result['status']==2 and result['CPU_unchanged'];guards.append(dict(read_failure=width))
            _,_,result=runtime.translated(fixture(snapshot,vectors[1]),vectors[1],fail=('write',width));assert result['status']==2 and result['CPU_unchanged'];guards.append(dict(write_failure=width))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='display_list_native_Unicorn_C_fullCPU_private_linktable_RAM_bus_match',directory=str(out),CPU_cases=len(rows),source_instruction_coverage=[252,254],reachable_instruction_coverage=[252,252],unreachable_instructions=list(map(hex,missing)),unreachable_reason='Two negative-literal alternates follow fixed positive776F0 literal/BGE; no allowed descriptor input changes that literal.',host_guards=len(guards),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],compiler=command,new_components=0,already_counted_logical_component=True,live_renderer_linked=False,
            matched=['Native CPU plus independent Unicorn compare full D/A,SR,USP,SSP and whole2MBRAM including original LINK/MOVEM saves,16-byte local frame,dynamically sized private link table and original argument/return frames. All ordered CPU bus reads/writes match independent oracle; no private exclusions.',
                     '1024 mixed-type/alignment/link/field descriptor fixtures plus preserved real descriptor list; both stack banks/body/fullcall, source jump-table reads and fixed776F0origin independent of output argument. Reconstructed path executes no original CPU/GPU instructions.'],
            limits=['Finite valid descriptor lists/indices, fixed source jump-table bytes and sufficient supplied stack/RAM. No arbitrary invalid jump targets/private-stack aliases/concurrent mutation proof. Older logical checker separately tests declared descriptor rereads; this fullCPU set uses stable descriptor memory.',
                    'Descriptor packing only; objectprocessor/scanout/timing/whole viewport/game/audio/boot not proved. Host bus/budget failures retain priorRAM effects and leave inputCPU unchanged.'])
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-display-list-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()
