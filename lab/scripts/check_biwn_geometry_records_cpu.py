"""Rendering-record full CPU with actual copy and originalGPU/C matrix math."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess,types
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_cd_cpu as cd
import check_biwn_actor_lifecycle_runtime as lifecycle
ROOT=cd.ROOT;CPU=cd.CPU;SP=0x1ff000;STOP=0x1ffe00;save=cd.save
queue_path=ROOT/'scripts/check_biwn_render_queue_cpu.py';queue=types.ModuleType('geometry_record_queue_harness');queue.__file__=str(queue_path)
# Dense80-record inputs exceed the queue harness's10000-instruction ceiling.
# Raise only this private observer's instruction ceiling; accepted queue
# harness and source C stay unchanged. Final state must still reach RTS/STOP.
exec(compile(queue_path.read_text().replace('count=10000','count=100000'),str(queue_path),'exec'),queue.__dict__)
queue.ENTRIES={0xe3e0,0xe220,0xe098};queue.RETURNS={0xe4a8,0xe26a,0xe0a4};queue.SCRIPTS=set()
read=lambda p:json.loads(p.read_text())
class Runtime(queue.Runtime):
    def __init__(self,library,rows):
        self.native_oracle=cd.scheduler.Native();self.device=self.native_oracle.device;self.core=self.native_oracle.lib;self.prefix=self.native_oracle.prefix;self.lib=c.CDLL(str(library));self.rows={r['address']:r for r in rows}
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.geometry=self.lib.biwn_geometry_records_cpu_body;self.copy=self.lib.biwn_resource_cpu_body;self.call=self.lib.biwn_geometry_records_cpu_call
        for fn in [self.geometry,self.copy,self.call]:fn.argtypes=[c.POINTER(cd.world.Bus),c.POINTER(CPU),cd.dispatch.W8,cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
    def fn(self,bus,state,w8,service,context,budget,stop):
        pc=c.cast(state,c.POINTER(CPU)).contents.pc
        return (self.copy if 0xe3e0<=pc<0xe4aa else self.geometry)(bus,state,w8,service,context,budget,stop)
    def unicorn(self,ram,case,coverage):
        result=super().unicorn(ram,case,coverage)
        assert result[1].pc==(0x17324 if case['body']else STOP),'Independent CPU did not reach its declared endpoint'
        return result
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);lifecycle.seed_cpu(self,queue.make_cpu(case));steps=[];stack=[];pending=None
        for _ in range(100000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP or(case['body']and pc==0x17324):break
            assert pc in self.rows,hex(pc)
            if pending==pc:
                row={'target':pc,'actual_body':True,'incoming':cd.scheduler.cpu_dict(self.cpu())};self.calls.append(row);stack.append(row);pending=None
            if pc in queue.RETURNS and stack:stack.pop()['return']=cd.scheduler.cpu_dict(self.cpu())
            source=self.rows[pc]
            if source['assembly'].startswith('jsr '):
                target=int(source['assembly'].split('$')[1].split('.')[0],16);pending=target if target in queue.ENTRIES else None
            coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
            if self.core.GPUReadLong(0xf03204,0)==0x4320:self.device.write(0xf03204,0x4320)
        else:raise AssertionError('geometry record native CPU did not return')
        assert not stack
        return self.device.ram(),self.cpu(),{'steps':steps,'calls':self.calls,'device':self.stats()}

def cases():
    rng=random.Random(0x170a0152);result=[]
    for i in range(512):
        registers=[rng.getrandbits(32)for _ in range(15)]+[SP];sup=i%2
        result.append(dict(id=i,entry=0x170a0,registers=registers,SR=(0x2000 if sup else 0)|((i%8)<<8)|rng.randrange(32),usp=0x170000 if sup else SP,ssp=SP if sup else 0x1d0000,body=i%3==1,render=False,outer_RTS=0x17324,read_queues=[],seed=rng.getrandbits(32),mode=[0,1,2,3][i%4],initial_count=[0,1,7,40,0xffffffff,0x3fffffff,0x80000000,0x40000000][(i//4)%8],density=[0,1,2,3,40][(i//32)%5],region=[0,1,0x7fff,0x8000,0xffff][(i//8)%5]))
    return result

def fixture(snapshot,case):
    rng=random.Random(case['seed']);ram=bytearray(snapshot)
    def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
    def fill(a,n):ram[a:a+n]=rng.randbytes(n)
    fill(0x47b48,128*64+64);fill(0x49ccc,64)
    put(SP,4,STOP);put(0x49b88,4,case['initial_count']);put(0x49c60,2,case['mode'])
    region=case['region'];signed=region if region<0x8000 else region-0x10000
    put(0x49c1c,4,signed if case['id']%7 else region);put(0x49c52,2,rng.getrandbits(16));put(0x49c58,2,rng.getrandbits(16));put(0x49b8e,2,rng.getrandbits(16))
    put(0x49caa,4,0x110100);put(0x110100,4,0x180000)
    for j in range(12):put(0x437e0+j*2,2,0x4000 if j in [0,4,8]else 0)
    for typ in range(1,32):put(0x4208c+typ,1,(2 if (typ+case['id'])%2 else 0)|(case['id']&0xfc))
    for j in range(40):
        actor=0x49d6c+j*206;static=0x4bd9c+j*30;fill(actor,206);fill(static,30)
        active=j<case['density']or(case['density']in [2,3]and (j+case['id'])%5==0)
        put(actor,2,1 if active else 0);put(actor+42,2,region if j%3 else(region+1)&0xffff)
        put(actor+160,2,8 if (j+case['id'])%3 else 7)
        handle=0x110200+j*4;put(handle,4,0x180100+j*256);put(actor+94,4,handle if (j+case['id'])%4 else 0)
        put(static,2,1+(j%31)if active else 0);put(static+16,2,region if j%3 else(region+1)&0xffff)
        put(static+20,4,handle);put(static+24,4,0x180100+j*256)
    return bytes(ram)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opts=parser.parse_args()
    out=ROOT/'verification/biwn-geometry-records-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_geometry_records_cpu.c','biwn_resource_cpu.c'];library=out/'libgeometry-records-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'geometry-records-fullCPU-generation.json');resource=read(session/'resource-fullCPU-generation.json');copy_rows=[r for r in resource['instructions_decoded']if 0xe3e0<=r['address']<0xe4aa]
    runtime=Runtime(library,mapping['instructions_decoded']+copy_rows);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();rows=[];coverage=set()
    if opts.limit:vectors=[vectors[i]for i in [0,1,32,33,64,65,96,97,128,129,130,131,159,160,161,162,163,164,192,255,256,511][:opts.limit]]
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,original=runtime.native(ram,case,coverage);observed,observer,independent=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case,budget=100000)
            if rebuilt['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or independent['trace']!=rebuilt['trace']or original['calls']!=rebuilt['calls']:
                save(out/'mismatch.json',dict(case=case,CPU_original=cd.scheduler.cpu_dict(expected),CPU_Unicorn=cd.scheduler.cpu_dict(observer),CPU_C=cd.scheduler.cpu_dict(actual),RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:40],Unicorn_RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(observed,right))if a!=b][:40],original=original,Unicorn=independent,rebuilt=rebuilt));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']and not rebuilt['device']['device_error']
            rows.append(dict(case=case,CPU=cd.scheduler.cpu_dict(actual),final_record_count=int.from_bytes(right[0x49b88:0x49b8c],'big'),record_buffer_sha256=hashlib.sha256(right[0x47b48:0x49b88]).hexdigest(),original=original,rebuilt=rebuilt,full_CPU_RAM_privateframes_orderedbus_match=True))
        save(out/'fixtures.json',rows)
        covered=[r for r in mapping['instructions_decoded']if r['address']in coverage];missing=[r for r in mapping['instructions_decoded']if r['address']not in coverage]
        if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps(dict(directory=str(out),cases=len(rows),coverage=[len(covered),166],uncovered=[hex(r['address'])for r in missing])));return
        save(out/'coverage.json',dict(instructions=mapping['instructions_decoded'],uncovered=missing,actual_copy_instruction_addresses=sorted(coverage-set(r['address']for r in mapping['instructions_decoded']))));assert not missing,[hex(r['address'])for r in missing]
        guards=[];case=vectors[0];ram=fixture(snapshot,case)
        for kw in [{'missing':i}for i in range(6)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'budget':0},{'stop_flag':2}]:
            _,_,r=runtime.translated(ram,case,**kw);assert r['status']==1 and r['CPU_unchanged']and not r['trace'];guards.append(kw)
        for kw,status in [({'bad_pc':True},7),({'budget':1},4)]:
            _,_,r=runtime.translated(ram,case,**kw);assert r['status']==status and r['CPU_unchanged'];guards.append(kw)
        for failure in [('read',1),('read',2),('read',4),('write',2),('write',4)]:
            probe=next(r['case']for r in rows if any(t[0]==('r'if failure[0]=='read'else'w')and t[2]==failure[1]for t in r['rebuilt']['trace']));_,_,r=runtime.translated(fixture(snapshot,probe),probe,fail=failure);assert r['status']in [2,3]and r['CPU_unchanged'];guards.append({'failure':failure})
        _,_,r=runtime.translated(ram,case,fail=('helper',0xe3e0));assert r['status']==3 and r['CPU_unchanged'];guards.append({'helper_failure':0xe3e0})
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='geometry_record_builder_fullCPU_actual_copy_and_GPUmatrix_dual_CPU_match',directory=str(out),CPU_cases=len(rows),new_components=1,count_scope='170A0 is one new CPU entry; E220/E098 and E3E0copy already counted.',source_instruction_coverage=[166,166],geometry_builder_instructions=152,host_guards=len(guards),actual_copy_calls=sum(sum(c['target']==0xe3e0 for c in r['rebuilt']['calls'])for r in rows),actual_movement_matrix_submissions=sum(sum(c['target']==0xe220 for c in r['rebuilt']['calls'])for r in rows),scripted_helpers=[],source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},generator_sha256=mapping['generator_sha256'],stage_sha256=mapping['stage_sha256'],matched=['NativeCPU and independent Unicorn compare allregisters/PC/SR/USP/SSP,privateframes,complete2MBRAM,orderedCPUbus and actual nested helper CPU states. Both stack banks and body/call contracts.', 'Actual64byteCPUcopy and source E220/E098 nested submissions with originalGPU4320 versus reconstructedCmatrix.40actor/40static entries,region filter,modelhandle absence,active/type/flag selection,word/fullcount wrapping and descriptor writes.'],limits=['Standalone finite synthetic records/valid handles/buffers and pinned synchronous GPU. Source has no general count/capacity guards; arbitrary invalid memory is not supported. Shared pinned blitter is a device provider if copy reaches it.', 'Render record construction only, not GPU4D80geometry transform/full3Ddraw/viewport/scanout/audio/fullgame/physicaltiming. Live disc-scene integration still pending.'],compiler=command)
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-geometry-records-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
