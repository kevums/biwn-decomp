"""Full formatter, unsigned quotient/remainder and all source scratch effects."""
import argparse,ctypes as c,hashlib,itertools,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_render_queue_cpu as queue
ROOT=queue.ROOT;CPU=queue.CPU;SP=queue.SP;STOP=queue.STOP;save=queue.save;read=queue.read
ENTRIES={0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c}
RETURNS={0x1b19e,0x1b1fe,0x1b29a,0x1b458,0x1b476,0xe676,0xe68a}
queue.ENTRIES=ENTRIES;queue.RETURNS=RETURNS;queue.SCRIPTS=set()
DEST=0x190000;FMT=0x18f000;STRING=0x18f400;ARGS=0x18f800;REMAINING=0x18fc00
pack=lambda v,w:(v&((1<<(8*w))-1)).to_bytes(w,'big')
class Runtime(queue.Runtime):
    def __init__(self,library,rows):
        self.native_oracle=queue.cd.scheduler.Native();self.device=self.native_oracle.device;self.core=self.native_oracle.lib;self.prefix=self.native_oracle.prefix;self.lib=c.CDLL(str(library));self.rows={r['address']:r for r in rows}
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.fn=self.lib.biwn_formatter_cpu_body;self.call=self.lib.biwn_formatter_cpu_call
        for fn in [self.fn,self.call]:fn.argtypes=[c.POINTER(queue.world.Bus),c.POINTER(CPU),queue.cd.dispatch.W8,queue.cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);queue.lifecycle.seed_cpu(self,queue.make_cpu(case));steps=[];stack=[];pending=None
        for _ in range(1000000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP or(case['body']and pc==case['outer_RTS']):break
            assert pc in self.rows,hex(pc)
            if pending==pc:
                row=dict(target=pc,actual_body=True,incoming=queue.cd.scheduler.cpu_dict(self.cpu()));self.calls.append(row);stack.append(row);pending=None
            if pc in RETURNS and stack:stack.pop()['return']=queue.cd.scheduler.cpu_dict(self.cpu())
            asm=self.rows[pc]['assembly']
            if asm.startswith(('jsr ','bsr.')):pending=int(asm.split('$')[1].split('.')[0],16)
            coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
        else:raise AssertionError('native formatter did not stop')
        assert not stack
        return self.device.ram(),self.cpu(),dict(steps=steps,calls=self.calls,device=self.stats())
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);e=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);e.ctl_set_cpu_model(UC_CPU_M68K_M68000);e.mem_map(0,0x200000);e.mem_map(0xf02000,0x2000);e.mem_write(0,ram)
        for target in queue.SCRIPTS:e.mem_write(target,b'\x4e\x75')
        e.reg_write(UC_M68K_REG_SR,case['SR'])
        for r,v in zip(queue.cd.REGS,case['registers']):e.reg_write(r,v)
        def code(cpu,pc,w,_):
            if(case['render']and pc==0xdf60)or(case['body']and pc==case['outer_RTS']):cpu.emu_stop();return
            if pc in queue.SCRIPTS:
                s=queue.make_cpu(case);s.registers[:]=[cpu.reg_read(r)for r in queue.cd.REGS];s.pc=pc;self.scripted(s,pc)
                for r in [0,1,8,9]:cpu.reg_write(queue.cd.REGS[r],s.registers[r])
                cpu.reg_write(UC_M68K_REG_SR,s.sr)
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def reader(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def writer(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(8*w))-1))
        hook=e.hook_add(UC_HOOK_CODE,code);e.hook_add(UC_HOOK_MEM_READ,reader);e.hook_add(UC_HOOK_MEM_WRITE,writer);e.emu_start(case['entry'],STOP,count=1000000,timeout=30000000)
        s=queue.make_cpu(case);s.registers[:]=[e.reg_read(r)for r in queue.cd.REGS];s.pc=e.reg_read(UC_M68K_REG_PC)
        if case['SR']&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
        output=self.device.ram();trace=list(self.trace);e.hook_del(hook);e.mem_write(STOP,b'\x40\xc7');e.emu_start(STOP,STOP+2,count=1);s.sr=e.reg_read(UC_M68K_REG_D7)&65535
        return output,s,{'trace':trace,'device':self.stats()}

def cases():
    rng=random.Random(0x1b45ac);rows=[]
    def add(entry,args,initial=(),kind='formatter'):
        i=len(rows);sup=i%2
        rows.append(dict(id=i,entry=entry,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if sup else 0)|((i%8)<<8)|rng.randrange(32),usp=0x170000 if sup else SP,ssp=SP if sup else 0x1d0000,body=i%3==1,render=False,outer_RTS={0x1b160:0x1b19e,0x1b1a8:0x1b1fe,0x1b212:0x1b29a,0x1b29c:0x1b458,0x1b45a:0x1b476,0xe61c:0xe676,0xe67c:0xe68a}[entry],read_queues=[],argument_hex=args.hex(),initial=[[a,bytes(data).hex()]for a,data in initial],kind=kind))
    for fmt,words in itertools.product([0x181da,0x181e9],itertools.product([0,1,7,16,0x7fff,0x8000,0xffff,0xffa0],repeat=3)):
        add(0x1b45a,pack(DEST,4)+pack(fmt,4)+b''.join(pack(v,2)for v in words),kind='actual_overlay_format')
    formats=[]
    for spec in ['d','u','o','x']:
        for width in ['','0','1','03','12','0255']:
            for long in ['', 'l','L']:
                for value in [0,1,0x7fff,0x8000,0xffff,0x7fffffff,0x80000000,0xffffffff]:
                    formats.append(('%'+width+long+spec,pack(value,4 if long else 2)))
    for fmt in ['','hello world','%%','%5%','%','trailing%','%0','%l','%L','%q','%z','%D/%U/%X/%f','a'*300]:formats.append((fmt,b''))
    for fmt in ['%c','%0c','%8c','%0255c']:
        for char in [0,32,65,255,0xffff]:formats.append((fmt,pack(char,2)))
    for fmt in ['%s','%0s','%1s','%20s','%0255s']:
        for ptr,text in [(0,b'ignored'),(STRING,b''),(STRING,b'hello'),(STRING,b'A'*300)]:
            add(0x1b45a,pack(DEST,4)+pack(FMT,4)+pack(ptr,4),[(FMT,fmt.encode()+b'\0'),(STRING,text+b'\0')],kind='string_format')
    formats.append(('%d:%03d:%ld:%u:%o:%x:%s:%c:%%',pack(0xffff,2)+pack(7,2)+pack(0x80000000,4)+pack(0xffff,2)+pack(511,2)+pack(0xbeef,2)+pack(STRING,4)+pack(90,2)))
    for i,(fmt,args)in enumerate(formats):
        initial=[(FMT,fmt.encode()+b'\0'),(STRING,b'mixed\0')]
        if i%5==0:add(0x1b29c,pack(DEST,4)+pack(FMT,4)+pack(ARGS,4),initial+[(ARGS,args)],kind='format_core')
        else:add(0x1b45a,pack(DEST,4)+pack(FMT,4)+args,initial,kind='general_format')
    for entry in [0x1b160,0x1b1a8,0x1b212]:
        for remaining in [0,1,2,7,254,0x7fff,0x8000,0xffff]:
            for width in [0,1,2,20,0x8000,0xffff]:
                initial=[(REMAINING,pack(remaining,2)),(STRING,b'letters\0')]
                if entry==0x1b160:args=pack(DEST,4)+pack(65,2)+pack(REMAINING,4)+pack(width,2)
                elif entry==0x1b1a8:args=pack(DEST,4)+pack(0 if width%2 else STRING,4)+pack(REMAINING,4)+pack(width,2)
                else:args=pack(DEST,4)+pack([0,1,0x80000000,0xffffffff][width%4],4)+pack([8,10,16][width%3],2)+pack(REMAINING,4)+pack(width,2)+pack(48,2)
                # Direct helper width/remaining can request enormous padding;
                # cap positive widths to20 while still checking negativewords.
                add(entry,args,initial,kind='direct_helper')
    math=[]
    for numerator in [0,1,2,0xffff,0x10000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]:
        for divisor in [1,2,3,8,10,16,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0xffffffff]:math.append((numerator,divisor))
    math += [(rng.getrandbits(32),rng.getrandbits(32)or 1)for _ in range(512)]
    for entry in [0xe61c,0xe67c]:
        for num,den in math:add(entry,pack(num,4)+pack(den,4),kind='unsigned_arithmetic')
    return rows

def fixture(snapshot,case):
    ram=bytearray(snapshot);ram[DEST:DEST+512]=b'\xa5'*512
    for a,h in case['initial']:
        raw=bytes.fromhex(h);ram[a:a+len(raw)]=raw
    raw=pack(STOP,4)+bytes.fromhex(case['argument_hex']);ram[SP:SP+len(raw)]=raw;return bytes(ram)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'formatter-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=ROOT/'verification/biwn-formatter-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libformatter-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_formatter_cpu.c'),'-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    runtime=Runtime(library,mapping['instructions_decoded']);vectors=cases()[:opt.limit or None];rows=[];coverage=set()
    try:
        for case in vectors:
            save(out/'status.json',dict(status='running',case=case['id']));ram=fixture(snapshot,case);left,expected,native=runtime.native(ram,case,coverage);observed,observer,independent=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case,budget=1000000)
            if rebuilt['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or independent['trace']!=rebuilt['trace']or native['calls']!=rebuilt['calls']:
                save(out/'mismatch.json',dict(case=case,CPU_native=queue.cd.scheduler.cpu_dict(expected),CPU_Unicorn=queue.cd.scheduler.cpu_dict(observer),CPU_C=queue.cd.scheduler.cpu_dict(actual),native=native,Unicorn=independent,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:40],Unicorn_RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(observed,right))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
            rows.append(dict(case=case,CPU=queue.cd.scheduler.cpu_dict(actual),output_hex=right[DEST:DEST+512].hex(),global_scratch_hex=right[0x15b7a0:0x15b7c0].hex(),original=native,rebuilt=rebuilt,fullCPU_RAM_private_global_scratch_bus_helpers_match=True))
        save(out/'fixtures.json',rows);missing=sorted({r['address']for r in mapping['instructions_decoded']}-coverage);save(out/'coverage.json',dict(covered=list(map(hex,sorted(coverage))),uncovered=list(map(hex,missing))))
        if opt.limit:save(out/'status.json',dict(status='terminal_preflight',cases=len(rows)));print(json.dumps(dict(directory=str(out),cases=len(rows),coverage=[323-len(missing),323])));return
        assert missing==[0xe678,0xe67a],list(map(hex,missing));guards=[];case=vectors[0];ram=fixture(snapshot,case)
        for options in [{'missing':i}for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2)]:
            _,_,r=runtime.translated(ram,case,**options);assert r['status']==1 and r['CPU_unchanged']and not r['trace'];guards.append(options)
        for options,statuses in [(dict(bad_pc=True),[7]),(dict(budget=1),[4]),(dict(fail=('read',4)),[2,3]),(dict(fail=('write',4)),[2]),(dict(fail=('helper',0x1b29c)),[3])]:
            _,_,r=runtime.translated(ram,case,**options);assert r['status']in statuses and r['CPU_unchanged'];guards.append(options)
        zero=next(v for v in vectors if v['entry']==0xe61c);zero={**zero,'argument_hex':(pack(1,4)+pack(0,4)).hex()};_,_,r=runtime.translated(fixture(snapshot,zero),zero);assert r['status']==8 and r['CPU_unchanged'];guards.append(dict(zero_divisor_host_error=True))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='formatter_unsigned_math_native_Unicorn_C_fullCPU_allRAM_private_global_scratch_bus_match',directory=str(out),CPU_cases=len(rows),source_instruction_coverage=[321,323],normal_return_instruction_coverage=[321,321],excluded_zero_divisor_exception_path=list(map(hex,missing)),host_guards=len(guards),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],compiler=command,source_function_entries=mapping['source_function_entries'],live_overlay_linked=False,new_components_pending_review=7,
            matched=['Native CPU and independent Unicorn match every register/CCR/bothstackbanks,whole2MBRAM including source LINK/MOVEM/JSR/RTS/args/private locals and actual global digit scratch15B7A0, ordered bus and every nested helper incoming/return state; no excluded private/global bytes.',
                     'Original signedword overlay formats plus source d/u/o/x/c/s/percent, long/word args, zero/space padding,widths,unknown/trailing/empty formats,NULL/longstrings,remaining limits,and all source functions directly. Original source upperhex digits and254character cap, not hostprintf semantics.',
                     'Unsigned quotient/remainder fastDIVU and32stepADDX/subtract paths compare for declared nonzero inputs, including highbit/edge/randomcases. Cexecutes no originalCPU/GPUinstructions.'],
            limits=['Standalone suppliedRAM/finite formatter strings/valid argument pointers; arbitrary aliasing/concurrent mutation not proved. Header/literal data remain exact source bytes through callbacks. No overlay/text/blitter/scene linkage yet.',
                    'Original divisorzero CPUexception path E678/E67A is excluded; hoststatus8 preserves inputCPU. DIVUoverflow is explicit hoststatus9; no corresponding original exception/undefined flags claim. Hosterrors retain priorRAM stores.',
                    'This is source-specific static reconstruction, not original recovered source or a runtime CPUdecoder. Fullgame/viewport/scanout/audio/boot remain incomplete.'])
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-formatter-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',case=case.get('id'),error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()
