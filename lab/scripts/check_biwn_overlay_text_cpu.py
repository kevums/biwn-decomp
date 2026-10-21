"""FullCPU overlay/text/multiply with real pinned blitter and full formatter."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_formatter_cpu as base
import check_biwn_overlay as overlay
ROOT=base.ROOT;CPU=base.CPU;SP=base.SP;STOP=base.STOP;save=base.save;read=base.read
TEXT_ENTRIES={0x181f8,0x14776,0x147a6,0x149ae,0xe540};ALL_ENTRIES=TEXT_ENTRIES|base.ENTRIES
base.ENTRIES=ALL_ENTRIES;base.queue.ENTRIES=ALL_ENTRIES
base.RETURNS|={0x18552,0x147a4,0x149ac,0x14ca8,0xe586}
FONT=0x60000;STRING=0x160000;TARGET=0xb29d0
pack=base.pack
class Runtime(base.Runtime):
    def __init__(self,library,rows):
        super().__init__(library,rows);self.format_body=self.fn;self.format_call=self.call
        self.text_body=self.lib.biwn_overlay_text_cpu_body;self.text_call=self.lib.biwn_overlay_text_cpu_call
        for f in [self.text_body,self.text_call]:f.argtypes=self.format_body.argtypes;f.restype=c.c_int
        def select(state,full):
            pc=c.cast(state,c.POINTER(CPU)).contents.pc if state is not None else 0
            return(self.text_call if full else self.text_body)if pc in TEXT_ENTRIES or pc==0 else(self.format_call if full else self.format_body)
        self.fn=lambda bus,state,*args:select(state,False)(bus,state,*args)
        self.call=lambda bus,state,*args:select(state,True)(bus,state,*args)
def cases(snapshot):
    rng=random.Random(0x181f8642);rows=[]
    def add(entry,args=b'',initial=(),kind='text'):
        i=len(rows);sup=i%2;rows.append(dict(id=i,entry=entry,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if sup else 0)|((i%8)<<8)|rng.randrange(32),usp=0x170000 if sup else SP,ssp=SP if sup else 0x1d0000,body=i%3==1,render=False,outer_RTS={0x181f8:0x18552,0x14776:0x147a4,0x147a6:0x149ac,0x149ae:0x14ca8,0xe540:0xe586}[entry],read_queues=[],argument_hex=args.hex(),initial=[[a,bytes(v).hex()]for a,v in initial],kind=kind))
    def text(entry,typ,width=9,flags=0x3420,font=FONT,string=b' ABZ~\xff\0',mode=1):
        initial=[(STRING,string)]
        if font==FONT:
            memory=bytearray(16384);memory[:8]=bytes([typ,96,width,11,32,127])+pack(0x5400,2)
            if typ==2:
                table=8+96*11*2
                for j in range(256):memory[table+j]=[0,1,7,8,9,16,17,24,31,32,33,255][j%12]
            initial.append((FONT,memory))
        args=pack(22,2)+pack(2,2)+pack(STRING,4)+pack(TARGET,4)+pack(flags,4)+pack(font,4)+pack(3,2)+pack(mode,2)
        add(entry,args,initial,kind='captured_font'if font!=FONT else'controlled_valid_font')
    # Representative cases first, including both signed-multiply branches.
    add(0x14776,pack(0x8000,4)+pack(0xffff,2)+pack(7,2),kind='alignment')
    add(0xe540,pack(0x80000000,4)+pack(0xffffffff,4),kind='multiply')
    for t in [1,2,3]:text(0x149ae,t)
    text(0x147a6,3)
    for i,old in enumerate(overlay.cases()[:128]):
        initial=[]
        for a,w,v in old['initial']:
            if a in [0x44518,0x49d6a]:v=8+v%180
            if a in [0x4451a,0x49d68]:v=16+v%260
            initial.append((a,pack(v,w)))
        add(0x181f8,initial=initial,kind='overlay_valid_marker_coordinates')
    for pos in [0,1,7,8,0x7fff,0x8000,0xffff]:
        for width in [0,1,8,255,0x7fff,0x8000,0xffff]:
            for mask in [0,1,3,7,15,0x8000,0xffff]:add(0x14776,pack(pos,4)+pack(width,2)+pack(mask,2),kind='alignment')
    for i in range(1024):
        a=[0,1,0x7fffffff,0x80000000,0xffffffff][i%5]if i<25 else rng.getrandbits(32);b=[0,1,0x7fffffff,0x80000000,0xffffffff][i//5%5]if i<25 else rng.getrandbits(32)
        add(0xe540,pack(a,4)+pack(b,4),kind='multiply')
    for typ in [0,1,2,3,4,255]:
        for width in [1,7,8,9,16,17,24,25,32,33,255]:
            for flags in range(0,64,8):text(0x149ae,typ,width,0x3400|flags,mode=(len(rows)%3))
    for flags in range(0,64,8):text(0x147a6,3,33,0x3400|flags)
    for font in [0x4c3e0,0x4cca0]:
        for string in [b'\0',b'$200\0',b'$-2147483648\0',b'My First\0',b'A'*64+b'\0']:
            for flags in [0x3420,0x3428,0x3430,0x3438]:text(0x149ae,snapshot[font],flags=flags,font=font,string=string)
    return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'overlay-text-fullCPU-generation.json');fmt=read(session/'formatter-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=ROOT/'verification/biwn-overlay-text-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'liboverlay-text-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_overlay_text_cpu.c'),str(source/'biwn_formatter_cpu.c'),'-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    runtime=Runtime(library,mapping['instructions_decoded']+fmt['instructions_decoded']);vectors=cases(snapshot)[:opt.limit or None];rows=[];coverage=set()
    try:
        for case in vectors:
            save(out/'status.json',dict(status='running',case=case['id']));ram=base.fixture(snapshot,case);left,expected,native=runtime.native(ram,case,coverage);observed,observer,independent=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case,budget=1000000)
            if rebuilt['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or independent['trace']!=rebuilt['trace']or native['calls']!=rebuilt['calls']:
                save(out/'mismatch.json',dict(case=case,CPU_native=base.queue.cd.scheduler.cpu_dict(expected),CPU_Unicorn=base.queue.cd.scheduler.cpu_dict(observer),CPU_C=base.queue.cd.scheduler.cpu_dict(actual),native=native,Unicorn=independent,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:40],Unicorn_RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(observed,right))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
            rows.append(dict(case=case,CPU=base.queue.cd.scheduler.cpu_dict(actual),original=native,rebuilt=rebuilt,fullCPU_RAM_private_global_scratch_bus_helpers_and_pinned_blitter_match=True))
        save(out/'fixtures.json',rows);addresses={r['address']for r in mapping['instructions_decoded']};missing=sorted(addresses-coverage);save(out/'coverage.json',dict(covered=list(map(hex,sorted(addresses&coverage))),uncovered=list(map(hex,missing))))
        if opt.limit:save(out/'status.json',dict(status='terminal_preflight',cases=len(rows)));print(json.dumps(dict(directory=str(out),cases=len(rows),coverage=[642-len(missing),642],uncovered=list(map(hex,missing)))));return
        assert missing==[0x14ac6],list(map(hex,missing));guards=[];case=vectors[2];ram=base.fixture(snapshot,case)
        for options in [{'missing':i}for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2)]:
            _,_,r=runtime.translated(ram,case,**options);assert r['status']==1 and r['CPU_unchanged']and not r['trace'];guards.append(options)
        for options,statuses in [(dict(bad_pc=True),[7]),(dict(budget=1),[4]),(dict(fail=('read',4)),[2,3]),(dict(fail=('write',4)),[2])]:
            _,_,r=runtime.translated(ram,case,**options);assert r['status']in statuses and r['CPU_unchanged'];guards.append(options)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='overlay_text_multiply_native_Unicorn_C_fullCPU_RAM_private_global_scratch_real_blitter_match',directory=str(out),CPU_cases=len(rows),source_instruction_coverage=[641,642],reachable_instruction_coverage=[641,641],unreachable_instructions=['0x14ac6'],unreachable_basis='D0 is masked with38hex, giving only multiples of8. CMP8/BEQ and BLT handle8 and greater; remainingD0=0 is taken byTST/BEQ. The subsequentBRA14AC6 has no entry-path input.',host_guards=len(guards),source_sha256=mapping['source_sha256'],formatter_source_sha256=fmt['source_sha256'],generator_sha256=mapping['generator_sha256'],compiler=command,source_function_entries=mapping['source_function_entries'],new_components=0,already_counted_logical_components=True,live_scene_report=str(ROOT/'verification/biwn-disc-world-overlay-text-checks.json'),
            matched=['Native CPU and independent Unicorn compare full D/A,SR,USP/SSP,whole2MBRAM/private frames/global scratch,ordered CPUbus and nested fullCPU helpers including real fullformatter. Pinned blitter executes submitted commands on allpaths; resultingRAM compares, no private/pixel exclusions.',
                     'All641reachable of642sourceinstructions across overlay181F8,alignment14776,font3 147A6,text149AE and signedmultiplyE540; controlled valid font buffers,actual two capturedfonts,allfont3jump classes,sourcejump-table reads and signedmultiply edge/random cases. Cside executes no originalCPU/GPUinstructions.'],
            limits=['Bounded supplied RAM/fonts/coordinates/strings and synchronous pinned emulator blitter, not timing/physicalhardware/scanout. Original blitter remains a shared dependency. Stable fontmemory; older logicalproof separately checks changingreads/device mutations.',
                    'Overlay coordinate/extreme fields use valid marker positions for device rasterization; arbitrary DMA aliases/self-modifying code and impossible font/drawing fields are outside this set. General formatter/unsignedmath has its separate3038case proof; no zero-divisor exception equivalence.',
                    'Standalone source functions plus separately reported live16case scene; assistedstartup/GPUresetfixture/blockedtasks/othermodes/audio/boot/fullplayablegame remain incomplete.'])
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-overlay-text-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',case=case.get('id'),error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()
