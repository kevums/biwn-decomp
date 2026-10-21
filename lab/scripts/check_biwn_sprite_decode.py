"""Original GPU4B00overlay in pinned emulator versus high-level C decoder."""
import argparse,ctypes as c,csv,hashlib,json,os,random,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import extract_biwn_stage as stage
ROOT=stage.ROOT;sys.path.insert(0,str(ROOT));import binary_tools
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8));R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16);W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32)
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write16',W16),('write32',W32),('context',c.c_void_p),('read_budget',c.c_uint32)]
class Result(c.Structure):_fields_=[('width',c.c_uint32),('height',c.c_uint32),('declared_pixels',c.c_uint32),('emitted_pixels',c.c_uint32),('origin_x',c.c_int16),('origin_y',c.c_int16),('source_next',c.c_uint32),('destination_next',c.c_uint32),('palette',c.c_uint32),('remaining_counter',c.c_uint32),('reservoir',c.c_uint32),('bits_left',c.c_uint32)]
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

class Memory:
    def __init__(self,ram):self.ram=bytearray(ram);self.trace=[];self.division=0xa5a50001;self.fail_read=None;self.fail_write=None;self.errors=[]
    def read(self,address,width):
        if self.fail_read==(address,width):raise RuntimeError('injectedreadfailure')
        assert 0<=address and address+width<=len(self.ram),hex(address)
        value=int.from_bytes(self.ram[address:address+width],'big');self.trace.append(('r',address,width,value));return value
    def write(self,address,width,value):
        if self.fail_write==(address,width):raise RuntimeError('injectedwritefailure')
        if address==0xf0211c:assert width==4;self.division=value
        else:assert 0<=address and address+width<=len(self.ram);self.ram[address:address+width]=value.to_bytes(width,'big')
        self.trace.append(('w',address,width,value))

def translated(fn,memory,args,budget=1000000,missing=None):
    def reader(width):
        def callback(_,address,value):
            try:value[0]=memory.read(address,width);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return callback
    def writer(width):
        def callback(_,address,value):
            try:memory.write(address,width,value);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return callback
    types=[R8,R16,R32,W16,W32];callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4))]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=Bus(*callbacks,None,budget);result=Result();c.memset(c.byref(result),0xa5,c.sizeof(result));before=bytes(result);status=fn(c.byref(bus),*args,c.byref(result))
    return status,{name:getattr(result,name)for name,_ in result._fields_},bus.read_budget,bytes(result)==before

class Encoder:
    def __init__(self):self.data=bytearray();self.left=0;self.index=0
    def bits(self,value,width):
        for shift in range(width-1,-1,-1):
            if not self.left:self.index=len(self.data);self.data.append(0);self.left=8
            self.left-=1;self.data[self.index]|=((value>>shift)&1)<<self.left
    def zero(self,n):self.bits(1,1);self.bits(n-2,4)
    def repeat(self,n,index):self.bits(0,1);self.bits(1,1);self.bits(n-2,3);self.data.append(index)
    def literal(self,indices):self.bits(0,1);self.bits(0,1);self.bits(len(indices)-1,4);self.data.extend(indices)

def synthetic(initial,runs,dimensions,origin):
    ram=bytearray(initial);base=0x100000;frame=base+0x100;palette=base+0x2000;dest=0x180000
    def put(a,w,v):ram[a:a+w]=v.to_bytes(w,'big')
    put(base,4,1);put(base+4,4,0x2000);put(base+12,4,0x100)
    for i in range(256):put(palette+i*2,2,((i*0x1235)^0xa57f)&0xffff)
    encoder=Encoder();count=0
    for kind,values in runs:
        if kind=='zero':encoder.zero(values);count+=values
        elif kind=='repeat':n,index=values;encoder.repeat(n,index);count+=n
        else:encoder.literal(values);count+=len(values)
    payload=bytes(dimensions)+bytes(origin)+encoder.data+b'\0\0'
    ram[frame:frame+len(payload)]=payload
    return ram,[base,0,dest],{'dimensions':dimensions,'origins':origin,'expected_emitted_pixels':count,'runs':runs,'encoded_hex':payload.hex()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage.digest(image)==stage.STAGE_SHA
    initial=bytearray(0x200000);initial[0x4000:0x4000+len(image)]=image
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib';assert binary_tools.sha(core)=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    out=ROOT/'verification/biwn-sprite-decode'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbiwn_sprite_decode.dylib'
    compiler=['clang','-dynamiclib','-std=c11','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_sprite_decode.c'),'-o',str(library)];subprocess.run(compiler,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));fn=lib.biwn_sprite_decode;fn.argtypes=[c.POINTER(Bus),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(Result)];fn.restype=c.c_int
    overlay=image[0x4b08-0x4000:0x4d68-0x4000];decoded,decoder=binary_tools.jaguar_instructions(overlay,0xf03240,'gpu');opcodes={row['address']:int(row['bytes'][:4],16)>>10 for row in decoded}
    cases=[];rng=random.Random(0x4b00);asset_count=int.from_bytes(initial[0x6e6a0:0x6e6a4],'big');assert asset_count==61
    for i in range(asset_count):cases.append(('asset',initial,[0x6e6a0,i,0x10a688],{'asset_index':i}))
    def add(runs,dimensions=None,origin=None):
        count=sum(v if k=='zero'else v[0]if k=='repeat'else len(v)for k,v in runs);dimensions=dimensions or [count,1];origin=origin or [rng.randrange(256),rng.randrange(256)]
        ram,args,details=synthetic(initial,runs,dimensions,origin);cases.append(('synthetic',ram,args,details))
    for n in range(2,18):add([('zero',n)])
    for n in range(2,10):
        for index in [0,255]:add([('repeat',[n,index])])
    for n in range(1,17):add([('literal',[rng.randrange(256)for _ in range(n)])])
    for _ in range(128):
        runs=[]
        for _ in range(rng.randrange(5,13)):
            kind=rng.choice(['zero','repeat','literal']);n=rng.randrange(2,18)if kind=='zero'else rng.randrange(2,10)if kind=='repeat'else rng.randrange(1,17)
            runs.append((kind,n if kind=='zero'else[n,rng.randrange(256)]if kind=='repeat'else[rng.randrange(256)for _ in range(n)]))
        add(runs)
    for runs,dimensions in [([('zero',17)],[1,1]),([('literal',[255])],[0,0]),([('repeat',[9,0])],[0,255]),([('zero',2)],[255,0])]:add(runs,dimensions)
    for kind in ['zero','repeat','literal']:
        runs=[];remaining=255*255
        while remaining:
            if kind=='zero'and remaining>=2:n=min(17,remaining);runs.append(('zero',n))
            elif kind=='repeat'and remaining>=2:n=min(9,remaining);runs.append(('repeat',[n,255]))
            else:n=min(16,remaining);runs.append(('literal',[rng.randrange(256)for _ in range(n)]))
            remaining-=n
        add(runs,[255,255],[128,255])
    if options.limit:cases=cases[:options.limit]
    rows=[];env=os.environ.copy();env.update(VJ_TRACE_RING='4194304',VJ_EXPECT_BUILD='unknown')
    for n,(kind,ram,args,details)in enumerate(cases):
        folder=out/f'case-{n:04d}';folder.mkdir();(folder/'input-ram.bin').write_bytes(ram);save(out/'status.json',{'status':'running','case':n,'kind':kind,'args':args})
        cmd=[str(ROOT/'tools/biwn-gpu-sprite-oracle'),str(core),str(folder/'input-ram.bin'),str(folder/'output-ram.bin'),str(folder/'watch.csv'),*[str(a)for a in args],str(rng.getrandbits(32)),str(session/'emulator-runtime/inventory-draw-20261013T045440.167975Z/inputs')]
        process=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=20);(folder/'stdout.txt').write_text(process.stdout);(folder/'stderr.txt').write_text(process.stderr);save(folder/'protocol.json',{'command':cmd,'exit_code':process.returncode,'details':details})
        assert process.returncode==0,(folder,process.returncode);GPU=json.loads(next(line for line in process.stdout.splitlines()if line.startswith('{')))
        assert GPU['returned_to_dispatcher']and not GPU['unreadable']and not GPU['CPU_frames_executed']and GPU['division_control']==0
        memory=Memory(ram);status,result,budget,_=translated(fn,memory,args)
        with (folder/'watch.csv').open()as stream:events=list(csv.DictReader(stream))
        shape=[];writes=[]
        for event in events:
            assert event['who']=='3';address=int(event['addr'],16);pc=int(event['pc'],16)-2;opcode=opcodes[pc]
            if event['type']=='11':assert event['value']=='00000000';width={39:1,40:2,41:4}[opcode];shape.append(('r',address,width))
            else:assert event['type']=='12';width={46:2,47:4}[opcode];shape.append(('w',address,width));writes.append(('w',address,width,int(event['value'],16)))
        predicted=[t for t in memory.trace if t[1]!=0xf0211c];predicted_shape=[t[:3]for t in predicted];predicted_writes=[t for t in predicted if t[0]=='w']
        expected_regs={'source_next':1,'remaining_counter':2,'destination_next':3,'palette':4,'bits_left':6,'reservoir':7}
        good_regs=all(result[name]==GPU['bank0'][index]for name,index in expected_regs.items())
        if status!=0 or bytes(memory.ram)!=(folder/'output-ram.bin').read_bytes()or shape!=predicted_shape or writes!=predicted_writes or not good_regs or memory.division!=0:
            save(folder/'mismatch.json',{'GPU':GPU,'C_status':status,'C_result':result,'C_errors':memory.errors,'original_shape':shape,'C_trace':memory.trace,'original_writes':writes});raise AssertionError(str(folder/'mismatch.json'))
        if kind=='synthetic':assert result['emitted_pixels']==details['expected_emitted_pixels']
        (folder/'decoded-pixels.bin').write_bytes(memory.ram[args[2]:result['destination_next']]);save(folder/'C-result.json',result)
        rows.append({'kind':kind,'directory':str(folder),'args':args,'details':details,'GPU':GPU,'C_result':result,'external_bus_shape_and_write_values_match':True,'whole_RAM_match':True,'C_remaining_read_budget':budget,'pixel_words_sha256':binary_tools.sha(folder/'decoded-pixels.bin')})
    save(out/'fixtures.json',rows)
    if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}),flush=True);return
    guards=[];base_args=cases[0][2]
    assert fn(None,*base_args,c.byref(Result()))==1 and fn(c.byref(Bus()),*base_args,None)==1;guards.extend([{'case':'null_bus','status':1},{'case':'null_output','status':1}])
    for missing in range(5):
        memory=Memory(initial);status,_,_,unchanged=translated(fn,memory,base_args,missing=missing);assert status==1 and unchanged and not memory.trace;guards.append({'case':'missing_callback','index':missing,'status':status})
    for name,budget,r,w in [('zero_budget',0,None,None),('mid_stream_budget',12,None,None),('palette_offset_failure',100000,(0x6e6a4,4),None),('frame_header_failure',100000,(0x6e7a0,1),None),('metadata_write_failure',100000,None,(0x10a67c,2)),('pixel_write_failure',100000,None,(0x10a688,2)),('completion_write_failure',100000,None,(0xf0211c,4))]:
        memory=Memory(initial);memory.fail_read=r;memory.fail_write=w;status,_,remaining,unchanged=translated(fn,memory,base_args,budget);expected=2 if 'budget'in name else 3;assert status==expected and unchanged,(name,status);guards.append({'case':name,'status':status,'remaining_read_budget':remaining,'trace':memory.trace,'errors':memory.errors})
    save(out/'guards.json',guards)
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'original_GPU_sprite_overlay_and_C_decoder_match','directory':str(out),'stage_sha256':stage.STAGE_SHA,'processor':'GPU','portable_components':1,'GPU_cases':len(rows),'actual_asset_cases':asset_count,'synthetic_cases':len(rows)-asset_count,'host_guard_cases':len(guards),'core_sha256':binary_tools.sha(core),'oracle_binary_sha256':binary_tools.sha(ROOT/'tools/biwn-gpu-sprite-oracle'),'overlay_source_interval':'[0x4b08,0x4d68)','overlay_GPU_interval':'[0xf03240,0xf034a0)','overlay_bytes':608,'overlay_sha256':hashlib.sha256(overlay).hexdigest(),
        'matched':['All2MBmainRAM after originalGPUoverlay vsC, including signed origin metadata and16bitpixel words.','Every externalRAM read address/width/order and write address/width/value/order; discarded literal trailing prefetch preserved.','Finalsource/destination/palette/counter/reservoir/bitsleft match originalGPUregisters; division-control sentinel cleared.','All61actual frames plus exhaustive tokenlengths, mixed interleavedcontrol/data, signed origins,zero dimensions,runovershoot and255x255stress images.'],
        'excluded':['Readvalues in originalwatch are placeholders, not observed data. Read widths inferred from exact decodedopcode at recordedGPU_PCminus2.','Isolated pinned softwareemulator, not hardware/device timing. No CPU/DSP/frame execution or complete-game rebuild.','Originaldispatcher loading is modeled by copying preservedheader-selected608bytes. GPUregister/CCRABI, interrupts and arbitraryoverlap/busmapping schedules not reconstructed.','Raw16bitwords only; video color interpretation, text rasterization, blitter/objectprocessor and final inventoryframe unfinished.','Hostreadlimits/callbackerrors have no originalcounterpart; partialeffects retained.'] ,
        'compiler':compiler,'source_sha256':{n:binary_tools.sha(source/n)for n in ['biwn_sprite_decode.c','biwn_sprite_decode.h']}}
    examples={}
    for label,kind,target in [('zero_run_max','zero',17),('repeat_run_max','repeat',9),('literal_run_max','literal',16)]:
        for i,row in enumerate(rows):
            runs=row['details'].get('runs',[])
            if len(runs)!=1 or runs[0][0]!=kind:continue
            length=runs[0][1] if kind=='zero' else runs[0][1][0] if kind=='repeat' else len(runs[0][1])
            if length==target:
                assert row['GPU']['bank0'][3]-row['args'][2]==length*2
                examples[label]={'length':length,'original_GPU_destination_advance_bytes':length*2,'original_GPU_returned':True,'source_fixture':str(out/'fixtures.json'),'row_index':i};break
    assert len(examples)==3
    report['checked_examples']=examples;report['token_lengths']={'zero':[2,17],'repeat':[2,9],'literal':[1,16]}
    report['actual_frames_emitted_exact_declared_size']=all(z['C_result']['declared_pixels']==z['C_result']['emitted_pixels']for z in rows[:61])
    save(out/'report.json',report);save(ROOT/'verification/biwn-sprite-decode-checks.json',report);save(out/'status.json',{'status':'terminal','exit_code':0});print(json.dumps(report),flush=True)

if __name__=='__main__':main()
