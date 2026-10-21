"""Frame acquisition with actual original/production C resource loader bodies.

CD seek/start/stop/yield/copy remain explicit target-CPU fixtures. Four lanes
isolate caller and loader, without claiming real CD or interrupt integration.
"""
import argparse,copy,json,os,random,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_native_frame_acquire as g
import check_biwn_native_resource_load as loader
from check_biwn_native_resource_release import REGS
ROOT=g.ROOT;sha=g.sha;save=g.save
PROVIDER=0x14c000

def cases():
    _,source,_=g.vectors();rng=random.Random(0x1ac681b044);rows=[]
    for mode in [1,2,3]:
        for count in [1,2]:
            for pattern in [1,2]:
                for supervisor in [0,0x2000]:
                    for flags in [0,16,31]:
                        c=copy.deepcopy(next(c for c in source if c['mode_word']==mode and c['count_word']==count and c['pattern']==pattern and c['reserved_word']==0 and c['adjusted_word']<32768))
                        # Stable bounded payload sizes; division remainder/nonzero
                        # quotient both exercised, resource ID follows new bias.
                        adjusted=3;c.update(adjusted_word=adjusted,id_word=mode*100+adjusted,sr=supervisor|flags,initial=[x for x in c['initial'] if x[0] not in [0x15b530,0x15b532]],incoming=[rng.getrandbits(32) for _ in range(15)])
                        tag=0x53524300+len(rows);q=adjusted//count;base_tag=tag-q;marker=0x1c0000;size=count*8192;destination=0x120000
                        c['initial'] += [[0x15b530,2,mode],[0x15b532,2,0],[0x464c8+mode*2,2,mode*100],[0x464b8+mode*4,4,base_tag],[0x4674c,4,destination],[0x47b80,2,0],[0x47b82,2,0],[0x134004,2,2],[0x134006,2,0],[0x134020,2,1],[0x13403c,2,flags]]
                        c['initial'] += [[0x134040+4*i,4,rng.getrandbits(32)] for i in range(4)]
                        c['initial'] += [[marker+4*i,4,tag] for i in range(16)]
                        c['payload']=bytes((i*7+len(rows))%256 for i in range(size)).hex();c['size']=size;c['tag']=tag
                        rows.append(c)
    return rows

def seed(image,case):
    b=bytearray(g.seed(image,case));b[0x134000:0x134100]=bytes(256);b[0x1c0000:0x1c8400]=bytes(0x8400)
    b[0x120000:0x124000]=b'\xa9'*0x4000
    for a,w,v in case['initial']:b[a:a+w]=v.to_bytes(w,'big')
    b[0x1c0040:0x1c0040+case['size']]=bytes.fromhex(case['payload'])
    return bytes(b)

def allowed(pc,frame_length,provider_length,parent,compiled,with_native_loader):
    if pc in loader.HELPERS or PROVIDER<=pc<PROVIDER+provider_length:return True
    if g.ENTRY<=pc<g.END and (not compiled or pc==g.ENTRY):return True
    if compiled and g.BASE<=pc<g.BASE+frame_length:return True
    if g.LOADER<=pc<0x1b154 and (not with_native_loader or pc==g.LOADER):return True
    return with_native_loader and parent['resident_address']<=pc<parent['resident_address']+parent['linked_component_bytes']

def run(n,image,case,frame_length,plen,parent,compiled,with_native_loader,ordered=False):
    image=seed(image,case);calls=[];minimum=g.SP;coverage=set();current=g.ENTRY
    def readcall(pc,registers,read,with_sr=None):
        name,argc=('frame_loader',5) if pc==g.LOADER else loader.HELPERS[pc]
        sp=registers[15];item=dict(helper=name,args=[int.from_bytes(read(sp+4+4*i,4),'big') for i in range(argc)],registers=registers)
        if with_sr is not None:item['SR']=with_sr
        calls.append(item)
    if ordered:
        u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,image);u.reg_write(UC_M68K_REG_SR,case['sr'])
        for r,v in zip(REGS,case['incoming']+[g.SP]):u.reg_write(r,v)
        events=[]
        def code(e,pc,w,_):
            nonlocal current,minimum
            assert allowed(pc,frame_length,plen,parent,compiled,with_native_loader),hex(pc);current=pc;minimum=min(minimum,e.reg_read(UC_M68K_REG_A7))
            if pc==g.LOADER or pc in loader.HELPERS:
                readcall(pc,[e.reg_read(r) for r in REGS],e.mem_read);events.append(['call',calls[-1]])
        def ignored(a,w):return g.private(a,w) or g.BASE<=a and a+w<=g.BASE+frame_length
        def rd(e,t,a,w,v,_):
            if not ignored(a,w):events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
        def wr(e,t,a,w,v,_):
            if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
        u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(g.ENTRY,g.STOP,count=1000000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==g.STOP
        return dict(ram=bytes(u.mem_read(0,0x200000)),events=events,calls=calls,minimum=minimum)
    n.device.seed(image,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,g.SSP);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1ec000);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[g.SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,g.ENTRY)
    for steps in range(1000000):
        pc=l.m68k_get_reg(None,16)
        if pc==g.STOP:break
        assert allowed(pc,frame_length,plen,parent,compiled,with_native_loader),hex(pc);coverage.add(pc);minimum=min(minimum,l.m68k_get_reg(None,15))
        if pc==g.LOADER or pc in loader.HELPERS:
            readcall(pc,[l.m68k_get_reg(None,i) for i in range(16)],lambda a,w:n.device.read(a,w).to_bytes(w,'big'),l.m68k_get_reg(None,17))
        l.m68k_execute(1)
    else:raise AssertionError('Nested loader instruction limit')
    result=g.cpu(n);assert result[15]==g.SP+4
    return dict(cpu=result,ram=n.device.ram(),calls=calls,minimum=minimum,coverage=coverage,steps=steps)

def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);a=p.parse_args();out=ROOT/'verification/native-frame-acquire-nested'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),native_cases=0,ordered_cases=0,source_accepted=False,game_frames=0,default_promoted=False,new_training=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-frame-acquire-nested-active.json',state)
    mark();n=None
    try:
        proofpath=ROOT/'verification/native-frame-acquire-current.json';proof=json.loads(proofpath.read_text());assert proof['source_accepted']
        for path,h in proof['dependencies_sha256'].items():assert sha(path)==h
        payload=Path(proof['binary']).read_bytes();assert sha(proof['binary'])==proof['binary_sha256']
        parentpath=ROOT/'verification/native-fast-core-wait-format-disc-build-current.json';parent=json.loads(parentpath.read_text());resident=Path(parent['linked_component']).read_bytes();assert len(resident)==parent['linked_component_bytes']
        assert sha(parent['derived_stage'])==parent['derived_stage_sha256']
        offset=parent['staging_address']-0x4000+40;assert Path(parent['derived_stage']).read_bytes()[offset:offset+len(resident)]==resident
        sources=[Path(__file__),Path(g.__file__),Path(loader.__file__),g.ND/'resource-load-providers.S'];snap=out/'source-snapshot';snap.mkdir()
        for path in sources:shutil.copy2(path,snap/path.name)
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');commands=[[prefix+'as','-m68000','-o',str(out/'providers.o'),str(g.ND/'resource-load-providers.S')],[prefix+'ld','-Ttext='+hex(PROVIDER),'-e','load_provider_yield','-o',str(out/'providers.elf'),str(out/'providers.o')],[prefix+'objcopy','-O','binary',str(out/'providers.elf'),str(out/'providers.bin')]]
        with (out/'build.log').open('w') as log:
            for command in commands:assert subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode==0
        helpers=(out/'providers.bin').read_bytes();symbols={}
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(out/'providers.elf')],text=True).splitlines():
            q=line.split()
            if len(q)==3:symbols[q[2]]=int(q[0],16)
        image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());image[PROVIDER:PROVIDER+len(helpers)]=helpers;image[parent['resident_address']:parent['resident_address']+len(resident)]=resident
        for addr,(name,_) in loader.HELPERS.items():image[addr:addr+6]=b'\x4e\xf9'+symbols['load_provider_'+name].to_bytes(4,'big')
        rows=cases()
        if a.limit:rows=rows[:a.limit]
        save(out/'fixtures.json',rows);state.update(status='running_four_native_lanes',planned_fixtures=len(rows),component_proof=str(proofpath),component_proof_sha256=sha(proofpath),parent_build=str(parentpath),parent_sha256=sha(parentpath));mark();n=g.Native();results=[];minimum=g.SP
        for i,case in enumerate(rows):
            row=dict(case=i,mode=case['mode_word'],count=case['count_word'],pattern=case['pattern'],SR=case['sr'],lanes=[])
            for native_loader in [False,True]:
                common=bytearray(image)
                if native_loader:common[g.LOADER:g.LOADER+6]=b'\x4e\xf9'+parent['symbols']['biwn_native_resource_load'].to_bytes(4,'big')
                candidate=bytearray(common);candidate[g.BASE:g.BASE+len(payload)]=payload;candidate[g.ENTRY:g.ENTRY+8]=b'\x4e\xf9'+g.BASE.to_bytes(4,'big')+b'\x4e\x71'
                left=run(n,common,case,len(payload),len(helpers),parent,False,native_loader);right=run(n,candidate,case,len(payload),len(helpers),parent,True,native_loader)
                normalized=g.normalize(right['ram'],left['ram'],len(payload))
                if left['cpu']!=right['cpu'] or left['calls']!=right['calls'] or normalized!=left['ram']:
                    save(out/'mismatch.json',dict(case=i,native_loader=native_loader,original_CPU=left['cpu'],candidate_CPU=right['cpu'],original_calls=left['calls'],candidate_calls=right['calls'],RAM_differences=[dict(address=hex(j),original=x,candidate=y) for j,(x,y) in enumerate(zip(left['ram'],normalized)) if x!=y][:64]));raise AssertionError('Nested full CPU/RAM/helper mismatch')
                assert right['ram'][0x120000:0x120000+case['size']]==bytes.fromhex(case['payload']),'Actual loader copy payload mismatch'
                assert int.from_bytes(right['ram'][0x13402c:0x134030],'big')==1 and int.from_bytes(right['ram'][0x47b80:0x47b82],'big')==0
                traced=False
                if i%6==0:
                    x=run(n,common,case,len(payload),len(helpers),parent,False,native_loader,True);y=run(n,candidate,case,len(payload),len(helpers),parent,True,native_loader,True)
                    if x['events']!=y['events'] or g.normalize(y['ram'],x['ram'],len(payload))!=x['ram']:
                        save(out/'ordered-mismatch.json',dict(case=i,native_loader=native_loader,original=x['events'],candidate=y['events']));raise AssertionError('Nested ordered mismatch')
                    traced=True;state['ordered_cases']+=1
                minimum=min(minimum,right['minimum']);state['native_cases']+=1;row['lanes'].append(dict(native_loader=native_loader,CPU=right['cpu'],helper_calls=right['calls'],original_steps=left['steps'],native_steps=right['steps'],minimum_SP=hex(right['minimum']),ordered=traced))
            results.append(row)
            if i%6==0:state['completed_fixtures']=len(results);mark();print('Nested frame/loader',len(results),'/',len(rows),flush=True)
        save(out/'results.json',results);state.update(status='terminal_native_frame_acquire_nested_preflight_pass' if a.limit else 'terminal_native_frame_acquire_original_and_production_loader_pass',completed_fixtures=len(results),source_accepted=not a.limit,maximum_stack_bytes=g.SP-minimum,minimum_stack_address=hex(minimum),dependencies_sha256={str(path):sha(path) for path in sources},scope='Four CPU lanes: original vs compiled complete 1AC68 with each of original 1B044 and production native C loader at its resident address. Cache empty/eviction, modes1-3, group1/2, two stack modes/three CCR profiles; exact actual 8KB/16KB marker payload copies, caller CPU/public44-byte frame/2MB RAM/helper entry registers+SR+args and selected ordered bus. Lower CD/yield/copy are declared guest CPU providers; no live CD/IRQ/gameplay/physical proof. Private8KB below public frame and candidate code excluded. Loader args/CPU separately compared. No source/default/preview changes.');mark()
        if not a.limit:save(ROOT/'verification/native-frame-acquire-nested-current.json',state)
        print(state['status'],state['native_cases'],state['ordered_cases'],state['maximum_stack_bytes'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if n:n.close()

if __name__=='__main__':main()
