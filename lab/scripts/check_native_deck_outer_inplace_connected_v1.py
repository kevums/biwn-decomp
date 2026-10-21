"""Outer task executing all five retained native callers in one CPU image.

All six original callers and six deeper original helper bodies execute.
Other remaining helpers and GPU submissions are fixtures; E540 executes.
These are seeded component states, not a fresh disc or scheduler trial.
"""
import argparse,json,os,struct,subprocess
from collections import deque
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_outer_inplace_v1 as outer
import check_native_deck_scene_reset_v1 as shared
import check_deck_geometry_helpers_v1 as deeper
import check_deck_geometry_faces_v1 as faces
import check_deck_debug_overlay_cpu_v1 as debug
import fixture_ram_delta_v1 as delta
ROOT=outer.ROOT;CPU=outer.CPU;save=outer.save;sha=outer.sha;cpu_dict=outer.cpu_dict
SHARED_CODE=0x190000
ROOTS={v[0]:name for name,v in shared.LAYOUT.items()}
RANGES={**deeper.RANGES,0x110d4:0x11384,0x1142e:0x11762,0x10734:0x10968}
FIXTURES=((outer.original.HELPERS-set(ROOTS))|shared.HELPERS['input']|shared.HELPERS['geometry']|{0xe26c,0x110d4,0x1b45a,0x149ae})-set(RANGES)
FIXTURES-= {0x1102a}
ENTRIES=FIXTURES|set(ROOTS)|set(RANGES)|{0xe540,0x1102a}


class Engine(outer.Engine):
    arguments=debug.Engine.arguments
    def fixture(self,memory,state,target,case,index):
        if target in debug.WIDTHS:debug.Engine.effect(self,state,target,case,index)
        elif target==0xe26c:
            if case['logical_return']==0x11684:faces.Engine.effect(self,memory,state,case,index)
            else:self.gpu_fixture(memory,state,case)
        elif target==0x110d4:deeper.Engine.service_effect(self,memory,state,case)
        elif target in shared.HELPERS['input']:shared.inputs.Engine.helper(self,memory,state,target,case,index)
        elif target in shared.HELPERS['geometry']:shared.scene.Engine.helper(self,memory,state,target,case,index)
        else:outer.original.Engine.helper(self,memory,state,target,case,index)

    def run(self,ram,initial,case,osym,ssym,opayload,spayload,native):
        memory=bytearray(ram);patches={a:6 if name!='geometry'else 8 for a,name in ROOTS.items()};patches[0x11e6c]=12
        if native:
            for a,name in ROOTS.items():memory[a:a+patches[a]]=b'\x4e\xf9'+ssym['biwn_v4_'+name].to_bytes(4,'big')+bytes.fromhex('4e71')*(patches[a]//2-3)
            memory[0x11e6c:0x11e78]=b'\x4e\xf9'+osym['biwn_outer_entry'].to_bytes(4,'big')+bytes.fromhex('4e71')*3
        state=CPU.from_buffer_copy(bytes(initial))
        if native and state.pc!=0x11e6c:state.pc=osym['biwn_outer_resume']
        self.native.device.seed(bytes(memory),0);self.set_cpu(state,True)
        task=int.from_bytes(ram[0xc0920:0xc0924],'big');slot=(task-outer.POOL)//1024;obase=outer.ARENA+slot*outer.STRIDE;dbase=outer.DECK+slot*1024
        counts={name:0 for name in shared.LAYOUT};returns=dict(counts);markers={hex(a):0 for a in RANGES};original_deeper_steps=0;input_reset_markers=0;active=[];protected=[];checks=0;entries=[];trace=deque(maxlen=20);low=560
        def normalize(raw,final=False):
            result=bytearray(raw)
            if native:
                result[outer.ARENA:outer.ARENA+outer.SLOTS*outer.STRIDE]=ram[outer.ARENA:outer.ARENA+outer.SLOTS*outer.STRIDE]
                result[outer.DECK:outer.DECK+outer.SLOTS*1024]=ram[outer.DECK:outer.DECK+outer.SLOTS*1024]
                for a,n in patches.items():result[a:a+n]=ram[a:a+n]
                frames=[(obase+16,osym['biwn_outer_helper_return'])]+[(dbase+layout[1],ssym['biwn_v4_'+name+'_helper_return'])for name,layout in shared.LAYOUT.items()]
                for frame,physical in frames:
                    if int.from_bytes(raw[frame+114:frame+118],'big'):
                        sp=int.from_bytes(raw[frame+106:frame+110],'big');logical=int.from_bytes(raw[frame+110:frame+114],'big')
                        if int.from_bytes(raw[sp:sp+4],'big')==physical:
                            assert not final,'Outstanding helper return'
                            result[sp:sp+4]=logical.to_bytes(4,'big')
            return result
        for step in range(2000000):
            state=self.cpu();pc=state.pc;sp=state.registers[15];trace.append([hex(pc),hex(sp)])
            if pc==outer.STOP:status=0;break
            if native and pc==osym['biwn_outer_iteration_boundary']:state.pc=0x11e86;status=6;break
            if not native and pc==0x11e86 and step:status=6;break
            if native:
                for name in counts:
                    if pc==ssym['biwn_v4_'+name]:
                        counts[name]+=1;raw=self.native.device.ram();parent=active[-1]if active else None
                        saved=None
                        if parent:
                            _,off,lo,hi=shared.LAYOUT[parent];saved=(raw[dbase+off:dbase+off+118],raw[dbase+lo:dbase+hi])
                        protected.append((name,bytes(raw[obase:obase+outer.STRIDE]),parent,saved));active.append(name)
                    if pc==ssym['biwn_v4_'+name+'_return']:
                        assert active.pop()==name;returns[name]+=1;which,frame,parent,saved=protected.pop();assert which==name
                        raw=self.native.device.ram();assert raw[obase:obase+outer.STRIDE]==frame,'Nested caller overwrote outer suspended state'
                        if parent:
                            _,off,lo,hi=shared.LAYOUT[parent];assert (raw[dbase+off:dbase+off+118],raw[dbase+lo:dbase+hi])==saved,'Nested caller overwrote parent'
                        checks+=1
                if (pc>=osym['biwn_outer_asm_end']and pc<outer.CODE+len(opayload)or osym['biwn_outer_capture_initialize']<=pc<osym['biwn_outer_helper_return'])and obase<=sp<obase+outer.STRIDE:
                    low=min(low,sp-obase);assert sp>=obase+144,'Outer C stack overflow'
            if native and pc in [ssym['biwn_v5_deeper_helper_marker'],ssym['service_geometry_original'],ssym['service_geometry_faces'],ssym['service_geometry_debug']]:
                raw=self.native.device.ram();frame=int.from_bytes(raw[sp+4:sp+8],'big');target=int.from_bytes(raw[sp+(8 if pc==ssym['biwn_v5_deeper_helper_marker']else 16):sp+(12 if pc==ssym['biwn_v5_deeper_helper_marker']else 20)],'big')
                assert frame==dbase+16 and target in RANGES
                values=struct.unpack('>19IH',raw[frame+4:frame+82]);virtual=CPU();virtual.registers[:]=values[:16];virtual.pc,virtual.usp,virtual.ssp,virtual.sr=values[16:]
                if virtual.sr&0x2000:assert state.usp==initial.usp;virtual.usp=state.usp
                else:assert state.ssp==initial.ssp;virtual.ssp=state.ssp
                assert virtual.pc==target;entries.append(self.entry(normalize(raw),virtual));markers[hex(target)]+=1
            if native and pc==ssym['biwn_v18_scene_reset_marker']:
                raw=self.native.device.ram();frame=int.from_bytes(raw[sp+4:sp+8],'big');assert frame==dbase+144
                values=struct.unpack('>19IH',raw[frame+4:frame+82]);virtual=CPU();virtual.registers[:]=values[:16];virtual.pc,virtual.usp,virtual.ssp,virtual.sr=values[16:]
                if virtual.sr&0x2000:virtual.usp=state.usp
                else:virtual.ssp=state.ssp
                assert virtual.pc==0x1102a;entries.append(self.entry(normalize(raw),virtual));input_reset_markers+=1
            if pc in ENTRIES:
                raw=bytearray(self.native.device.ram());entries.append(self.entry(normalize(raw),state))
                if pc in FIXTURES:
                    logical=int.from_bytes(normalize(raw)[sp:sp+4],'big')
                    before=self.native.device.ram();self.fixture(raw,state,pc,dict(case,logical_return=logical),len(entries)-1)
                    delta.apply(self.native.device,before,bytes(raw));state.pc=self.native.device.read(sp,4);state.registers[15]+=4
                    if state.sr&0x2000:state.ssp=state.registers[15]
                    else:state.usp=state.registers[15]
                    self.set_cpu(state);continue
            helper_pc=any(a<=pc<b for a,b in RANGES.items())
            if helper_pc:original_deeper_steps+=1
            original_pc=0x11828<=pc<0x11f6c or 0xe540<=pc<0xe588 or helper_pc or 0x1102a<=pc<0x110d4
            if native:assert pc in patches or outer.CODE<=pc<outer.CODE+len(opayload)or SHARED_CODE<=pc<SHARED_CODE+len(spayload)or 0xe540<=pc<0xe588 or 0x1102a<=pc<0x110d4,dict(pc=hex(pc),trace=list(trace))
            else:assert original_pc,dict(pc=hex(pc),trace=list(trace))
            self.core.m68k_execute(1)
        else:raise AssertionError(('Connected work bound',list(trace)))
        raw=self.native.device.ram()
        if native:
            assert not active and not protected and counts==returns
            assert raw[outer.CODE:outer.CODE+len(opayload)]==opayload and raw[SHARED_CODE:SHARED_CODE+len(spayload)]==spayload
            for i in range(outer.SLOTS):
                a=outer.ARENA+i*outer.STRIDE
                for lo,hi in outer.FENCES:assert raw[a+lo:a+hi]==ram[a+lo:a+hi],('outer fence',i,lo)
                a=outer.DECK+i*1024
                for lo,hi in shared.FENCES:assert raw[a+lo:a+hi]==ram[a+lo:a+hi],('Deck fence',i,lo)
                assert raw[a+392:a+396]==ram[a+392:a+396],'Outer pointer changed'
            assert raw[outer.ARENA:obase]==ram[outer.ARENA:obase]and raw[obase+outer.STRIDE:outer.ARENA+outer.SLOTS*outer.STRIDE]==ram[obase+outer.STRIDE:outer.ARENA+outer.SLOTS*outer.STRIDE]
            assert raw[outer.DECK:dbase]==ram[outer.DECK:dbase]and raw[dbase+1024:outer.DECK+outer.SLOTS*1024]==ram[dbase+1024:outer.DECK+outer.SLOTS*1024]
            for _,offset,_,_ in shared.LAYOUT.values():assert raw[dbase+offset+114:dbase+offset+118]==bytes(4)
        return status,bytes(normalize(raw,True)),state,entries,dict(instructions=step,native_entries=counts,native_returns=returns,suspended_frame_checks=checks,outer_C_stack_bytes=560-low,native_deeper_helper_markers=markers,native_input_reset_markers=input_reset_markers,original_deeper_helper_steps=original_deeper_steps,blitter_registers=self.native.device.registers())


def main():
    global SHARED_CODE
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=128);args=ap.parse_args();assert 1<=args.limit<=256
    out=ROOT/'verification/native-Deck-outer-inplace-connected-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',directory=str(out),pid=os.getpid(),native_disc_changed=False,new_training=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state)
    mark()
    try:
        bp=ROOT/'verification/native-scene17-gpu-family-disc-build-v1-current.json';b=json.loads(bp.read_text())
        op=ROOT/'verification/native-Deck-outer-inplace-v1-current.json';og=json.loads(op.read_text());sgp=ROOT/'verification/native-deck-retained-scene17-gpu-family-final-v1-current.json';sg=json.loads(sgp.read_text())
        assert og['completed']==1280 and sg['completed']==4992
        for gate in [og,sg]:
            for p,h in gate['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
        outer.CODE=b['outer_code_address'];outer.ARENA=b['outer_arena_address'];outer.DECK=b['deck_arena_address'];SHARED_CODE=b['shared_Deck_code_address']
        rebuilt=out/'outer-build';q=subprocess.run(['make','BUILD='+str(rebuilt),'ADDRESS='+hex(outer.CODE),'ARENA_ADDRESS='+hex(outer.ARENA),'DECK_ADDRESS='+hex(outer.DECK)],cwd=outer.SRC,capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
        opayload=(rebuilt/'native-outer.bin').read_bytes();osym=outer.symbols(rebuilt/'symbols.txt');spayload=Path(sg['payload']).read_bytes();ssym=sg['symbols']
        assert len(opayload)==og['code_bytes'] and sha(spayload)==sg['payload_sha256']
        resident=Path(b['component']).read_bytes()
        for address,payload in [(SHARED_CODE,spayload)]:assert payload==resident[address-b['resident_address']:address-b['resident_address']+len(payload)]
        save(out/'outer-build/native-outer.bin',out/'outer-build/symbols.txt',*outer.SRC.glob('*'),out/'outer-gate.json',og);save(out/'shared-gate.json',sg);save(out/'build-as-run.json',b)
        shared.configure('scan');scans=shared.fixtures('scan');inputs=shared.inputs.fixtures();coords=shared.coordinate.fixtures()
        source=list(x for x in outer.original.fixtures()if x[1].pc in [0x11e6c,0x11e86]);shared.scene.HELPERS=ENTRIES
        rows=[];e=Engine()
        try:
            for i in range(args.limit):
                scan_ram,_,scan_case=scans[i];input_ram,_,input_case=inputs[(i*37)%1792];coord_ram,_,coord_case=coords[(i*19)%len(coords)]
                task_ram,initial,task_case=source[i%64 if i%8==0 else 64+i]
                memory=bytearray(coord_ram)
                for lo,hi in [(0x80088,0x8008a),(0x90088,0x9008a),(0x49ba4,0x49bb0),(0x403cc,0x403ce),(0x403dc,0x4040e)]:memory[lo:hi]=input_ram[lo:hi]
                memory[0x80000:0x80002]=(coord_case['index']%16).to_bytes(2,'big');memory[0x90000:0x90002]=(coord_case['index']%16).to_bytes(2,'big')
                for slot in range(16):a=0x400ea+46*slot;memory[a:a+2]=scan_ram[a:a+2]
                memory[outer.SP-512:outer.SP+128]=task_ram[outer.SP-512:outer.SP+128]
                for a,w,value in [(0x403d6,2,[0,1,3,4][i%4]),(0x10a684,4,0),(0x49b88,4,i%3)]:memory[a:a+w]=value.to_bytes(w,'big')
                case={**coord_case,**input_case,**scan_case,**task_case};memory[0x403cc:0x403ce]=[0,1,0x8000,0xffff][(i//8)%4].to_bytes(2,'big');memory[0x403ca:0x403cc]=(i%4).to_bytes(2,'big')
                case['mutate_globals']=False;case['mode']=[0,1,3,4][i%4];case['mutate_counter']=i%2==0;case['flip_descriptor']=i%3==0
                ram,initial,case=outer.prepare((bytes(memory),initial,case),i,opayload);memory=bytearray(ram);memory[SHARED_CODE:SHARED_CODE+len(spayload)]=spayload
                memory[outer.DECK:outer.DECK+outer.SLOTS*1024]=bytes([0xa5])*(outer.SLOTS*1024)
                for slot in range(outer.SLOTS):
                    a=outer.DECK+slot*1024
                    for _,offset,_,_ in shared.LAYOUT.values():memory[a+offset+114:a+offset+118]=bytes(4)
                    memory[a+392:a+396]=(outer.ARENA+slot*outer.STRIDE+16).to_bytes(4,'big')
                ram=bytes(memory);expected,eram,ecpu,events,expected_details=e.run(ram,initial,case,osym,ssym,opayload,spayload,False)
                status,actual,cpu,observed,details=e.run(ram,initial,case,osym,ssym,opayload,spayload,True)
                if status!=expected or eram!=actual or cpu_dict(cpu)!=cpu_dict(ecpu)or events!=observed or expected_details['blitter_registers']!=details['blitter_registers']:
                    save(out/'counterexample.json',dict(case=i,status=status,original_status=expected,original_CPU=cpu_dict(ecpu),native_CPU=cpu_dict(cpu),original_events=events,native_events=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(eram,actual))if u!=v][:32],details=details));raise AssertionError(out/'counterexample.json')
                rows.append(dict(case=i,entry=hex(initial.pc),task_slot=i%outer.SLOTS,full_CPU_nonarena_RAM_ordered_helper_entries_match=True,**details))
                if i%8==0:state.update(status='checking',completed=i+1);mark();print('case',i+1,flush=True)
        finally:e.native.close()
        totals={k:sum(x['native_returns'][k]for x in rows)for k in ROOTS.values()}
        if args.limit>=128:assert all(x>0 for x in totals.values()),totals
        helper_totals={hex(a):sum(x['native_deeper_helper_markers'][hex(a)]for x in rows)for a in RANGES}
        if args.limit>=128:assert all(x>0 for x in helper_totals.values()),helper_totals
        save(out/'cases.json',rows)
        paths=[Path(__file__),Path(outer.__file__),Path(shared.__file__),Path(deeper.__file__),Path(faces.__file__),Path(debug.__file__),Path(delta.__file__),Path(shared.scene.__file__),Path(shared.inputs.__file__),Path(shared.faces.__file__),Path(shared.coordinate.__file__),out/'outer-build/native-outer.bin',out/'outer-build/symbols.txt',*outer.SRC.glob('*'),out/'outer-gate.json',out/'shared-gate.json',out/'build-as-run.json',Path(og['payload']),Path(sg['payload']),out/'cases.json']
        state.update(prototype_only=True,outer_disc_byte_identity=False,original_arenas_unchanged=True,status='terminal_six_native_callers_six_deeper_helpers_connected_match',completed=len(rows),task_slots=len(set(x['task_slot']for x in rows)),native_returns=totals,native_deeper_helper_markers=helper_totals,
                     protected_suspended_frame_checks=sum(x['suspended_frame_checks']for x in rows),maximum_outer_C_stack_bytes=max(x['outer_C_stack_bytes']for x in rows),
                     source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' FullCPU/nonarenaRAM/ordered helper entries compare with all six original bodies. Outstanding compiler return addresses and declared root redirects normalized only. Both native arenas/canaries and suspended parent frames checked. No CPU fixtures are used for the six caller or six recovered helper bodies. Native marker snapshots compare logical CPU context at compiled helper entry; inactive stack bank comes from independently checked physical CPU. E26C,formatter/text and remaining services are explicit fixtures.')
        mark()
        if args.limit>=128:save(ROOT/'verification/native-Deck-outer-inplace-connected-v1-current.json',state)
        print(state['status'],totals,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
