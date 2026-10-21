"""Linked readable input/attack/RNG/math versus original instructions.

Other dispatcher helper routines remain identical explicit fixture services.
"""
import ctypes as c
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import struct
import zlib
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_input_dispatch as dispatch
import check_biwn_attack_effect as attack
import check_biwn_media_setup_cpu as media

ROOT=dispatch.ROOT
world=dispatch.world
SP,STOP=dispatch.SP,dispatch.STOP
DISPLAY_SCRATCH=SP-46
POLL_SELECTS=[0x810e,0x810d,0x810b,0x8107]
POLL_READ_PCS={0xe4d4,0xe4e8,0xe4fc,0xe512}
POLL_SELECT_PCS=dict(zip([0xe4cc,0xe4e0,0xe4f4,0xe50a],POLL_SELECTS))
SOURCE={0x18df2:0x18e92,0x1a77c:0x1a7f4,0xe540:0xe61c,0xeac4:0xec04,
        0x15200:0x1557a,0xe3e0:0xe4aa,0x1af04:0x1b044,0x1a0f8:0x1a188,0x190bc:0x191f4,
        0x1b160:0x1b478,0xe61c:0xe68c,0x12620:0x12896,0x14776:0x14caa,0xe4c0:0xe53c,
        0x20f0c:0x20f78,0x20e40:0x20e8c,0x1ae56:0x1ae88}
RESOURCE_SERVICES={0x1b044:[4]*5,0xdf8c:[4],0xdf9c:[4]}
SCENE_SERVICES={0x20f78:[2]}
DISPLAY_SERVICES={}
EXTRA_SERVICES={**RESOURCE_SERVICES,**SCENE_SERVICES,**DISPLAY_SERVICES}
FALLBACK=[a for a in dispatch.HELPERS if a not in[0x18df2,0xe588,0xeb04,0x152a2,0x1545c,0x1af04,0x1b002,0x1a0f8,0x190bc,0xe4c0]]+list(EXTRA_SERVICES)
WIDTHS={**dispatch.WIDTHS,**EXTRA_SERVICES}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')


def controller_mapping():
    proof=json.loads((ROOT/'verification/biwn-input-poll-checks.json').read_text())
    path=Path(proof['directory'])/'fixtures.json';rows=json.loads(path.read_text());mapping={}
    # Encode fixtures from previously observed original-CPU single-bit results,
    # independently of the C decoder under test.
    for row in rows:
        p=row['parameters'];held=row['held']
        if p.get('kind')=='single_raw_bit'and p['previous']==0 and held:
            assert held&(held-1)==0 and held not in mapping
            mapping[held]=(p['row'],p['bit'])
    assert len(mapping)==24 and sum(mapping)==0x33ff33ff
    return mapping,path


CONTROLLER_MAPPING,CONTROLLER_MAPPING_PATH=controller_mapping()


def raw_rows(held):
    assert held&~0x33ff33ff==0,hex(held)
    rows=[0xffffffff]*4
    for bit,(row,raw_bit)in CONTROLLER_MAPPING.items():
        if held&bit:rows[row]&=~(1<<raw_bit)
    return rows


def diagnostic_png(core,raw,path,palette_source=None):
    """Render numeric framebuffer data with the pinned core's CRY16 table."""
    # This core hides its lookup-table symbol. Reproduce TOMFillLookupTables
    # from its pinned source, using only the three literal numeric tables.
    tom=Path(palette_source)if palette_source else Path(core._name).parent/'src/tom/tom.c';source=tom.read_text();tables=[]
    for name in ['redcv','greencv','bluecv']:
        match=re.search(r'uint8_t\s+'+name+r'\[16\]\[16\]\s*=\s*\{(.*?)\};',source,re.S);assert match,name
        body=re.sub(r'/\*.*?\*/|//[^\n]*','',match[1],flags=re.S)
        values=[int(x,0)for x in re.findall(r'0[xX][0-9a-fA-F]+|\b\d+\b',body)]
        assert len(values)==256 and all(0<=v<=255 for v in values);tables.append(values)
    palette=[]
    for value in range(65536):
        index=((value>>12)&15)*16+((value>>8)&15);intensity=value&255
        red,green,blue=[table[index]*intensity>>8 for table in tables];palette.append((red<<16)|(green<<8)|blue)
    lines=[]
    for y in range(50,111):
        row=bytearray()
        for x in range(55,205):
            value=int.from_bytes(raw[(y*224+x)*2:(y*224+x)*2+2],'big');rgb=palette[value]
            row.extend(bytes([(rgb>>16)&255,(rgb>>8)&255,rgb&255])*4)
        lines.extend([b'\0'+row]*4)
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',600,244,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(lines)))+chunk(b'IEND',b''))
    save(path.with_suffix('.json'),dict(pixel_encoding='CRY16 diagnostic',palette_source=str(tom),palette_source_sha256=sha(tom.read_bytes()),source_framebuffer=[224,240],crop=[55,50,150,61],nearest_neighbor_scale=4,physical_scanout_verified=False))


class Script(dispatch.Script):
    def __init__(self,snapshot,case):self.MMIO={};self.poll_reads=0;self.poll_selects=0;super().__init__(snapshot,case)
    def put(self,a,w,v):
        if a>=0x200000:
            assert 0xf02000<=a<0xf03000 or a==0xf14000;self.MMIO[(a,w)]=v;self.changed.append((a,w,v));return
        return super().put(a,w,v)
    def read(self,a,w):
        if self.fail_read==(a,w):raise RuntimeError('injected read error')
        if a==0xf14000:
            assert w==4
            index=self.poll_reads//4;row=self.poll_reads%4
            if 'raw_poll_rows'in self.case:values=self.case['raw_poll_rows'];value=values[min(index,len(values)-1)][row]
            else:
                values=self.case.get('poll_values',[0x10000000]);value=raw_rows(values[min(index,len(values)-1)])[row]
            self.poll_reads+=1;self.trace.append(['r',a,w,value]);return value
        if a>=0x200000:
            assert 0xf02000<=a<0xf03000;value=self.MMIO.get((a,w),0);self.trace.append(['r',a,w,value]);return value
        if SP-0x1000<=a<SP+8:return int.from_bytes(self.memory[a:a+w],'big')
        return super().read(a,w)
    def write(self,a,w,v):
        if self.fail_write==(a,w):raise RuntimeError('injected write error')
        if a==0xf14000:
            assert w==2 and v==POLL_SELECTS[self.poll_selects%4];self.poll_selects+=1
        if SP-0x1000<=a<SP+8:self.put(a,w,v);return
        return super().write(a,w,v)
    def call(self,address,args):
        if address not in EXTRA_SERVICES:return super().call(address,args)
        if self.fail_call==address:raise RuntimeError('injected resource dependency error')
        self.trace.append(['call',address,args]);n=self.calls.get(address,0);self.calls[address]=n+1
        if address==0x1b044:
            # Explicit loader fixture; neither disc I/O nor scheduler is recovered
            # by this check. Allocation, cache state and handles are real C/CPU.
            _,_,handle,_,completion=args
            pointer=int.from_bytes(self.memory[handle:handle+4],'big')
            self.put(pointer+8,4,0x80)
            if completion:self.put(completion,2,1)
            if self.case.get('resource_shared_during_load'):self.put(completion-2,2,2)
        elif address==0xdf8c and n+1>=self.case.get('resource_ready_after',2):
            self.put(0x15b53c,2,1)
        for target,a,w,v in self.case.get('helper_effects',[]):
            if target==address:self.put(a,w,v)
        return self.case['default_helper_return']


def original(script,case,coverage,entries):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_map(0xf14000,0x1000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    for address in FALLBACK:cpu.mem_write(address,b'\x4e\x75')
    steps=[]
    def code(e,address,width,_):
        if address in FALLBACK:
            stack=e.reg_read(UC_M68K_REG_A7);values=[];offset=4
            for size in WIDTHS.get(address,[]):
                values.append(int.from_bytes(e.mem_read(stack+offset,size),'big'));offset+=size
            script.changed=[];value=script.call(address,values)
            for a,size,v in script.changed:e.mem_write(a,v.to_bytes(size,'big'))
            e.reg_write(UC_M68K_REG_D0,value);return
        assert 0x191f4<=address<0x19f2c or any(a<=address<b for a,b in SOURCE.items()),hex(address)
        if address in SOURCE or address in[0x18df2,0x1a77c,0xe540,0xe588,0xe60a,0xeb04,0xeac4,0x152a2,0x1545c,0x15200,0xe3e0,0xe3ee,0x1af04,0x1b002,0x1af04,0x1a0f8,0x190bc,0x1b45a,0x1b29c,0x1b212,0xe61c,0xe67c,0x12620,0x149ae,0x147a6,0x14776,0xe4c0,0x20f0c,0x20e40,0x1ae56]:entries[address]=entries.get(address,0)+1
        coverage.add(address);steps.append(address)
    def read(e,access,address,width,value,_):
        if SP-0x1000<=address<SP+8:return
        if hasattr(script,'observe_read'):script.observe_read(e.reg_read(UC_M68K_REG_PC),address,width)
        e.mem_write(address,script.read(address,width).to_bytes(width,'big'))
    def write(e,access,address,width,value,_):
        if SP-0x1000<=address<SP+8:return
        script.write(address,width,value&((1<<(width*8))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x191f4,STOP,count=30000,timeout=2000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for index,reg in enumerate(world.REGS):
        if index not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][index]
    memory=bytearray(cpu.mem_read(0,0x200000))
    for address in FALLBACK:memory[address:address+2]=script.memory[address:address+2]
    assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+8:]==script.memory[SP+8:]
    return cpu.reg_read(UC_M68K_REG_D0),len(steps)


def cases(snapshot):
    rows=dispatch.cases(snapshot)
    for row in rows:
        row['helper_effects']=[effect for effect in row.get('helper_effects',[])if effect[0]in FALLBACK]
    seed=next(row for row in rows if row['state']==2 and not row.get('read_queues'))
    for attack_case in attack.fixtures():
        if not attack_case['linked_rng']and attack_case['kind']!='threshold_boundary':continue
        row=json.loads(json.dumps(seed));row['kind']='linked_attack_'+attack_case['kind'];row['incoming']=attack_case['incoming']
        row['initial']+=attack_case['initial']+[[0x49cb8,2,2],[0x49c4e,2,0],[0x90002,1,2],[0x4c24c,4,0]]
        row['initial'] += [[0x462e8,4,44488],[0x462ec,4,3399]]
        if not attack_case['linked_rng']:row['initial'].append([0x113082+400,4,1])
        rows.append(row)
    # The older isolated-dispatch fixtures supplied arbitrary animation helper
    # returns/flag writes. Linked animation requires actual finite records and
    # a progressing external clock. This coupling fixture uses actor0/slot0,
    # real immutable sequence tables, a valid current two-record sequence,
    # and delta1. Raw weapon slots are retained; the earlier raw actor-index
    # and clock proof remains separate.
    for row in rows:
        row['initial'] += [[0x49c4c,2,0],[0x49d16,2,1],
                           [0x49cae,2,1],[0x49d18,2,0],[0x4c24c,4,1],
                           [0x90000,1,0],[0x90001,1,127],[0x90003,1,1],
                           [0x90004,1,1],[0x90005,1,127],[0x90006,1,1],[0x90007,1,0],
                           [0x112940,2,0]]
        # A coherent free block and owned old animation buffer replace the
        # earlier allocator's arbitrary return pointer. No heap outcome is
        # supplied: original instructions and recovered C perform the free,
        # insertion/coalescing, allocation, split and handle registration.
        row['initial'] += [[0x112d60,4,0x180000],[0x112d64,4,0x40000],
                           [0x180000,4,0x40000],[0x180004,4,0],[0x180008,4,0],
                           [0x93ff8,4,0x200],[0x93ffc,4,0x93000]]
        row['initial'] += [[0x112960+i*4,4,0]for i in range(256)]
        row['initial'] += [[0x410b2,4,0xb1002],[0x410b6,4,0xb1007],[0x410ba,4,0xb1010],[0xbd830,4,0x100000]]
        row['initial'] += [[0x410f6+i*2,2,v]for i,v in enumerate([55,50,150,61,4])]+[[0x41100,4,0xb1000]]
        label_records=b'\x05\x05  \0\x1e\x05      \0\x3c\x05    \0\0'
        row['initial'] += [[0xb1000+i,1,v]for i,v in enumerate(label_records)]
        # Coherent resident region and inactive actor resources. Dedicated
        # transition cases below populate texture groups and allocated handles.
        row['initial'] += [[0x49c18,4,0xa8000],[0xa8002,2,0],[0xa8008,4,0xb2000],
                           [0xa800c,2,0],[0xb2000,2,0]]
        row['initial'] += [[0x4bd9c+i*30,2,0]for i in range(40)]
        row['initial'] += [[0x4bdb0+i*30,4,0]for i in range(40)]
        for i in range(36):row['initial'] += [[0x15b4a0+i*4,2,0x200+i],[0x15b4a2+i*4,2,2]]
        # Five resident actor0 equipment resources with real reference counts.
        # Their coherent data/heap state is supplied, not a get/release result.
        for i in range(50):
            row['initial'] += [[0x15b534+i*12,2,0xffff],[0x15b53a+i*12,2,0],[0x15b53c+i*12,2,0]]
        for i in range(5):
            handle=0x91000+i*4;data=0xa0000+i*0x1000;entry=0x15b534+i*12
            row['initial'] += [[entry,2,i],[entry+2,4,handle],[entry+6,2,2],[entry+8,2,1],
                               [handle,4,data],[data+8,4,0x80],[data-8,4,0x200],[data-4,4,handle],
                               [0x464d0+i*12,4,0x123456],[0x464d4+i*12,4,0x4d455350],[0x464d8+i*12,4,0x200]]
        row['helper_effects']=[effect for effect in row.get('helper_effects',[])if effect[0]in FALLBACK]
    heap_seed=next(row for row in rows if row['kind']=='equipment_slot'and next(v for a,w,v in reversed(row['initial'])if a==0x49d5a)==1)
    shapes={
        'empty':[[0x112d60,4,0],[0x112d64,4,0]],
        'merge_previous':[[0x112d60,4,0x93ef8],[0x112d64,4,0x100],[0x93ef8,4,0x100],[0x93efc,4,0],[0x93f00,4,0]],
        'merge_next':[[0x112d60,4,0x941f8],[0x112d64,4,0x400],[0x941f8,4,0x400],[0x941fc,4,0],[0x94200,4,0]],
        'merge_both':[[0x112d60,4,0x93ef8],[0x112d64,4,0x500],[0x93ef8,4,0x100],[0x93efc,4,0x941f8],[0x93f00,4,0],[0x941f8,4,0x400],[0x941fc,4,0],[0x94200,4,0x93ef8]],
        'insert_middle':[[0x112d60,4,0x88000],[0x112d64,4,0x200],[0x88000,4,0x100],[0x88004,4,0x98000],[0x88008,4,0],[0x98000,4,0x100],[0x98004,4,0],[0x98008,4,0x88000]],
        'append_tail':[[0x112d60,4,0x88000],[0x112d64,4,0x100],[0x88000,4,0x100],[0x88004,4,0],[0x88008,4,0]],
    }
    for name,initial in shapes.items():
        row=json.loads(json.dumps(heap_seed));row['kind']='heap_'+name;row['initial']+=initial;rows.append(row)
    for name,initial,extra in [
        ('resource_evict',[[0x15b546,2,1]],{}),
        ('resource_cache_miss',[[0x15b53a,2,0]],{}),
        ('resource_pending',[[0x15b53c,2,0]],{'resource_ready_after':2}),
        ('resource_load_shared',[[0x15b53a,2,0]],{'resource_shared_during_load':True}),
    ]:
        row=json.loads(json.dumps(heap_seed));row['kind']=name;row['initial']+=initial;row.update(extra);rows.append(row)
    elevator_seed=next(row for row in rows if row['kind']=='idle_poll_wait')
    for name,held,permissions in [('up',0x00100000,0x8000),('down',0x00200000,0x4000),('up_priority',0x00300000,0xc000),('up_blocked',0x00100000,0),('down_blocked',0x00200000,0)]:
        row=json.loads(json.dumps(elevator_seed));row['kind']='elevator_'+name
        row['initial'] += [[0x46250,2,0],[0x49c18,4,0xa8000],[0xa800c,2,permissions],[0x49c62,2,0x7fff],[0x49c64,2,0xffff]]
        row['poll_values']=[held,0x10000000]
        row['helper_effects'] += [[0x20f78,0xa8020,4,0x12345678]]
        rows.append(row)
    for floor in[0,0x7fff,0x8000,0xffff]:
        row=json.loads(json.dumps(elevator_seed));row['kind']='display_floor_'+hex(floor)
        row['initial'] += [[0x46250,2,0],[0x49c18,4,0xa8000],[0xa800c,2,0xc000],[0x49c62,2,floor]]
        row['poll_values']=[0x10000000];rows.append(row)
    for raw_row in range(4):
        for bit in range(32):
            row=json.loads(json.dumps(elevator_seed));row['kind']='poll_raw_'+str(raw_row)+'_'+str(bit)
            row['initial'] += [[0x46250,2,0],[0x49c18,4,0xa8000],[0xa800c,2,0xc000]]
            values=[0xffffffff]*4;values[raw_row]^=1<<bit
            row['raw_poll_rows']=[values,raw_rows(0x10000000)];rows.append(row)
    scene_seed=next(row for row in rows if row['kind']=='elevator_up')
    for name,groups,actors in [('empty',0,[]),('textures',2,[]),('null_handle',0,[(0,0,0)]),('empty_handle',0,[(0,0x97000,0)]),('free_one',1,[(0,0x97000,0x160008)]),('free_two',2,[(0,0x97000,0x160008),(39,0x97004,0x160108)])]:
        row=json.loads(json.dumps(scene_seed));row['kind']='scene_cleanup_'+name
        row['initial'] += [[0xb2000,2,groups],[0xb2002,2,0x200],[0xb2004,2,0x206]]
        for i in range(12):row['initial'].append([0x15b4a2+i*4,2,[0,1,2,0x7fff,0x8000,0xffff][i%6]])
        for slot,handle,data in actors:
            row['initial'] += [[0x4bd9c+slot*30,2,0xffff],[0x4bdb0+slot*30,4,handle]]
            if handle:row['initial'].append([handle,4,data])
            if data:row['initial'] += [[data-8,4,0x100],[data-4,4,handle]]
        rows.append(row)
    return rows


def native_check(runtime,fn,snapshot,case,expected_d0,expected_memory,evidence_dir):
    script=Script(snapshot,case);memory=bytearray(script.memory)
    for address in FALLBACK:memory[address:address+2]=b'\x4e\x75'
    memory[SP:SP+4]=STOP.to_bytes(4,'big')
    cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP
    cpu.pc=0x191f4;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP
    runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0;fallback_count=0
    while runtime.cpu().pc!=STOP and steps<30000:
        cpu=runtime.cpu();address=cpu.pc
        if hasattr(script,'before_native_instruction'):script.before_native_instruction(runtime,address)
        if address in FALLBACK:
            values=[];offset=4;stack=cpu.registers[15]
            for width in WIDTHS.get(address,[]):
                values.append(getattr(runtime.core,'m68k_read_memory_'+str(width*8))(stack+offset));offset+=width
            # Real CPU writes create handles/cache entries after initial seeding.
            # Backend fixtures must inspect that live RAM, as Unicorn's hooked
            # writes already do, rather than dereference stale initial pointers.
            if address in EXTRA_SERVICES:script.memory[:]=runtime.device.ram()
            script.changed=[];value=script.call(address,values)
            for a,width,v in script.changed:runtime.device.direct(a,width,v)
            runtime.core.m68k_set_reg(0,value);fallback_count+=1
        if address in POLL_SELECT_PCS:script.write(0xf14000,2,POLL_SELECT_PCS[address])
        runtime.core.m68k_execute(1);steps+=1
        if address in POLL_READ_PCS:
            # Native fixture supplies opaque device read values at the four
            # MOVE.L boundaries. It supplies no held/edge result or helper D0.
            value=script.read(0xf14000,4);state=runtime.cpu()
            runtime.core.m68k_set_reg(0,value)
            runtime.core.m68k_set_reg(17,(state.sr&0xfff0)|(4 if not value else 0)|(8 if value&0x80000000 else 0))
    actual=runtime.cpu();memory=bytearray(runtime.device.ram())
    for address in FALLBACK:memory[address:address+2]=expected_memory[address:address+2]
    assert actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==expected_d0
    # Drive the same real blitter from C instead of comparing hardware writes
    # to the separate command-only (no-device-effects) fixture RAM.
    translated_script=Script(snapshot,case);initial=bytearray(translated_script.memory)
    for address in FALLBACK:initial[address:address+2]=b'\x4e\x75'
    initial[SP:SP+4]=STOP.to_bytes(4,'big');runtime.device.seed(bytes(initial),0)
    errors=[];commands=[]
    def reader(width):
        def cb(_,a,v):
            try:
                if hasattr(translated_script,'read_native'):v[0]=translated_script.read_native(runtime,a,width)
                else:v[0]=translated_script.read(a,width)if a==0xf14000 else getattr(runtime.core,'m68k_read_memory_'+str(width*8))(a)
                return 0
            except Exception as error:errors.append(str(error));return 1
        return cb
    def writer(width):
        def cb(_,a,v):
            try:
                if a==0xf14000:translated_script.write(a,width,v)
                getattr(runtime.core,'m68k_write_memory_'+str(width*8))(a,v)
                if a==0xf02238:commands.append(v)
                return 0
            except Exception as error:errors.append(str(error));return 1
        return cb
    def callback(_,a,args,n,result):
        try:
            translated_script.memory[:]=runtime.device.ram();translated_script.changed=[]
            result[0]=translated_script.call(a,list(args[:n]))
            for address,width,value in translated_script.changed:runtime.device.direct(address,width,value)
            return 0
        except Exception as error:errors.append(str(error));return 1
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(callback),dispatch.W8(writer(1))]
    bus=world.Bus(*callbacks[:6],None,0);output=c.c_uint32(0xa5a55a5a)
    status=fn(c.byref(bus),callbacks[6],1024,case['incoming'][0],c.byref(output))
    computed=bytearray(runtime.device.ram())
    for address in FALLBACK:computed[address:address+2]=expected_memory[address:address+2]
    mismatches=[a for a,(left,right)in enumerate(zip(memory,computed))if left!=right and not SP-0x1000<=a<SP+8]
    assert status==0 and not errors and output.value==expected_d0 and not mismatches and translated_script.trace==script.trace,dict(kind=case['kind'],status=status,errors=errors,expected=expected_d0,actual=output.value,raw_IO_and_helper_trace_match=translated_script.trace==script.trace,differences=[dict(address=hex(a),original=memory[a],C=computed[a])for a in mismatches[:30]])
    frame=slice(0x100000,0x100000+224*240*2)
    rendered=None
    if commands:
        stem='native-'+case['kind'];(evidence_dir/(stem+'-original-framebuffer.bin')).write_bytes(memory[frame]);(evidence_dir/(stem+'-C-framebuffer.bin')).write_bytes(computed[frame])
        rendered=evidence_dir/(stem+'-CRY16.png');diagnostic_png(runtime.core,computed[frame],rendered)
    return dict(kind=case['kind'],state=case['state'],D0=expected_d0,instructions=steps,remaining_fixture_helper_calls=fallback_count,actual_blitter_commands=len(commands),raw_controller_rows=translated_script.poll_reads,raw_native_read_results_injected=bool(script.poll_reads),raw_IO_and_external_helper_trace_match=True,held_or_edge_results_supplied=False,framebuffer_changed_bytes=sum(a!=b for a,b in zip(initial[frame],computed[frame])),framebuffer_sha256=sha(computed[frame]),native_original_vs_C_device_bus_RAM_match=True,diagnostic_image=str(rendered)if rendered else None,image_scope='CRY16 palette rendering,150x61panel crop from224x240fixture framebuffer,4xnearest-neighbor. Not full video scanout or natural game screenshot.'if rendered else None)


def animation_guards(fn,snapshot,vectors):
    guards=[]
    output=c.c_uint32(0xa5a55a5a)
    assert fn(None,dispatch.W8(lambda *args:0),1024,0,c.byref(output))==1 and output.value==0xa5a55a5a
    dummy=world.Bus();assert fn(c.byref(dummy),dispatch.W8(lambda *args:0),1024,0,None)==1
    guards += [dict(null_bus=True,status=1),dict(null_output=True,status=1)]
    for case in vectors:
        if not case['kind'].startswith('equipment_'):continue
        baseline=Script(snapshot,case);seen={};original(baseline,case,set(),seen)
        if seen.get(0xeb04):break
    else:raise AssertionError('No linked equipment-animation case')
    script=Script(snapshot,case);script.fail_read=(0x49cb4,4)
    status,value=dispatch.translated(fn,script,case,budget=1024)
    assert status==3 and value==0xa5a55a5a and any(event[0]=='w'for event in script.trace)
    index=next(i for i,event in enumerate(baseline.trace)if event[:3]==['r',0x49cb4,4])
    assert script.trace==baseline.trace[:index]
    guards.append(dict(nested_animation_bus_error=True,status=3,prior_effects_retained=True,output_untouched=True))
    pending=next(event[3]for event in baseline.trace if event[:3]==['w',0x49cb4,4])
    infinite=json.loads(json.dumps(case));infinite['initial'] += [[pending+i,1,0]for i in range(4)]
    script=Script(snapshot,infinite);status,value=dispatch.translated(fn,script,infinite,budget=1024)
    assert status==3 and value==0xa5a55a5a and len(script.trace)>1024
    guards.append(dict(nonprogressing_animation_sequence=True,per_update_work_limit=1024,status=3,output_untouched=True,
                       original_completion_claimed=False,scope='Added host limit; original infinite sequence is not assigned a completed result.'))
    return guards


def heap_guards(fn,snapshot,vectors):
    case=next(row for row in vectors if row['kind']=='heap_empty')
    baseline=Script(snapshot,case);original(baseline,case,set(),{})
    guards=[]
    for address in[0x112d60,0x112d5c]:
        script=Script(snapshot,case);script.fail_read=(address,4)
        status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,event in enumerate(baseline.trace)if event[:3]==['r',address,4])
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_heap_read_failure=hex(address),status=3,prior_effects_retained=True,output_untouched=True))
    cycle=json.loads(json.dumps(case));cycle['initial'] += [[0x112d60,4,0x88000],[0x88000,4,0x100],[0x88004,4,0x88000],[0x88008,4,0x88000]]
    script=Script(snapshot,cycle);status,value=dispatch.translated(fn,script,cycle,budget=1024)
    assert status==3 and value==0xa5a55a5a and len(script.trace)>1024
    guards.append(dict(cyclic_free_list=True,per_call_work_limit=1024,status=3,prior_effects_retained=True,original_completion_claimed=False))
    return guards


def resource_guards(fn,snapshot,vectors):
    guards=[]
    for kind,target in [('resource_cache_miss',0x1b044),('resource_pending',0xdf8c),('resource_load_shared',0xdf9c)]:
        case=next(row for row in vectors if row['kind']==kind)
        baseline=Script(snapshot,case);original(baseline,case,set(),{})
        script=Script(snapshot,case);script.fail_call=target
        status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,event in enumerate(baseline.trace)if event[:2]==['call',target])
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_resource_dependency_failure=hex(target),status=3,prior_effects_retained=True,output_untouched=True))
    case=next(row for row in vectors if row['kind']=='resource_cache_miss')
    baseline=Script(snapshot,case);original(baseline,case,set(),{})
    for field,event in [('fail_read',['r',0x464d0,4]),('fail_write',['w',0x15b53a,2])]:
        script=Script(snapshot,case);setattr(script,field,tuple(event[1:]))
        status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,row in enumerate(baseline.trace)if row[:3]==event)
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_resource_bus_failure=event,status=3,prior_effects_retained=True,output_untouched=True))
    case=json.loads(json.dumps(next(row for row in vectors if row['kind']=='resource_pending')))
    case['resource_ready_after']=2000;script=Script(snapshot,case)
    status,value=dispatch.translated(fn,script,case,budget=1024)
    assert status==3 and value==0xa5a55a5a and len(script.trace)>1024
    guards.append(dict(resource_wait_budget=1024,status=3,output_untouched=True,original_completion_claimed=False))
    return guards


def elevator_guards(fn,snapshot,vectors):
    case=next(row for row in vectors if row['kind']=='elevator_up');baseline=Script(snapshot,case);original(baseline,case,set(),{})
    guards=[]
    for field,event in [('fail_read',['r',0xa8008,4]),('fail_call',['call',0x20f78]),('fail_read',['r',0xa800c,2])]:
        script=Script(snapshot,case);setattr(script,field,event[1]if field=='fail_call'else tuple(event[1:]))
        status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event)
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_elevator_failure=event,status=3,prior_effects_retained=True,output_untouched=True))
    return guards


def display_guards(fn,snapshot,vectors):
    case=next(row for row in vectors if row['kind']=='display_floor_0x8000');baseline=Script(snapshot,case);original(baseline,case,set(),{})
    guards=[]
    for field,event in [('fail_read',['r',0x190b8,1]),('fail_write',['w',0xf02238,4]),('fail_write',['w',0xb1010,1]),('fail_read',['r',0x4c3e0,1])]:
        script=Script(snapshot,case);setattr(script,field,event[1]if field=='fail_call'else tuple(event[1:]))
        status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event)
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_display_failure=event,status=3,prior_effects_retained=True,output_untouched=True))
    return guards


def polling_guards(fn,snapshot,vectors):
    case=next(row for row in vectors if row['kind']=='display_floor_0x0');baseline=Script(snapshot,case);original(baseline,case,set(),{})
    guards=[]
    for field,event in [('fail_read',['r',0xf14000,4]),('fail_write',['w',0xf14000,2]),('fail_write',['w',0x49bac,4])]:
        script=Script(snapshot,case);setattr(script,field,tuple(event[1:]));status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event)
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_controller_poll_failure=event,status=3,prior_effects_retained=True,output_untouched=True))
    case=json.loads(json.dumps(case));case['raw_poll_rows']=[[0xffffffff]*4];script=Script(snapshot,case)
    status,value=dispatch.translated(fn,script,case,budget=8)
    assert status==4 and value==0xa5a55a5a and script.poll_reads>4
    guards.append(dict(controller_never_becomes_nonzero=True,dispatcher_work_budget=8,status=4,original_completion_claimed=False))
    return guards


def cleanup_guards(fn,snapshot,vectors):
    case=next(row for row in vectors if row['kind']=='scene_cleanup_free_two');baseline=Script(snapshot,case);original(baseline,case,set(),{})
    guards=[]
    for field,event in [('fail_read',['r',0x15b4a0,2]),('fail_write',['w',0x15b4a6,2]),('fail_read',['r',0x97000,4]),('fail_write',['w',0x97000,4]),('fail_write',['w',0x4bd9c,2])]:
        script=Script(snapshot,case);setattr(script,field,tuple(event[1:]));status,value=dispatch.translated(fn,script,case,budget=1024)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event)
        assert status==3 and value==0xa5a55a5a and script.trace==baseline.trace[:index]
        guards.append(dict(nested_cleanup_failure=event,status=3,prior_effects_retained=True,output_untouched=True))
    case=json.loads(json.dumps(case));case['initial'].append([0xb2000,2,0x7fff]);script=Script(snapshot,case)
    status,value=dispatch.translated(fn,script,case,budget=1024)
    assert status==3 and value==0xa5a55a5a and len(script.trace)>20000
    guards.append(dict(scene_cleanup_shared_work_limit=20000,status=3,output_untouched=True,original_completion_claimed=False))
    return guards


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opts=parser.parse_args()
    out=ROOT/'verification/game-controls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    names=['biwn_game_controls.c','biwn_input_dispatch.c','biwn_attack_effect.c','biwn_rng.c','biwn_signed_division.c','biwn_camera.c','biwn_animation.c','biwn_memory.c','biwn_transition_cleanup.c','biwn_resources.c','biwn_elevator_input.c','biwn_elevator_display.c','biwn_elevator_formatter.c','biwn_formatter_cpu.c','biwn_panel_refresh.c','biwn_text.c','biwn_input_poll.c']
    command=['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror']+[str(restore/name)for name in names]+['-o',str(out/'libcontrols.dylib')]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    lib=c.CDLL(str(out/'libcontrols.dylib'));raw_fn=lib.biwn_game_controls_with_scratch
    raw_fn.argtypes=[c.POINTER(world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];raw_fn.restype=c.c_int
    def fn(bus,write8,budget,incoming,result):return raw_fn(bus,write8,DISPLAY_SCRATCH,budget,incoming,result)
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();vectors=cases(snapshot)
    if opts.limit:vectors=vectors[:opts.limit]+[row for row in vectors if row['kind'].startswith(('resource_','elevator_','display_','poll_raw_','scene_cleanup_'))]
    coverage=set();entries={};results=[];native_vectors=[]
    seen_states=set();seen_heap_cases=set()
    for index,case in enumerate(vectors):
        left=Script(snapshot,case);right=Script(snapshot,case)
        try:
            case_entries={};expected,steps=original(left,case,coverage,case_entries)
            for address,count in case_entries.items():entries[address]=entries.get(address,0)+count
            status,actual=dispatch.translated(fn,right,case,budget=1024)
            assert not status and not right.errors and actual==expected and left.trace==right.trace
            assert left.memory[:SP-0x1000]==right.memory[:SP-0x1000]and left.memory[SP+8:]==right.memory[SP+8:]and left.MMIO==right.MMIO
        except Exception:
            save(out/'mismatch.json',dict(case=index,parameters=case,status=locals().get('status'),expected=locals().get('expected'),actual=locals().get('actual'),errors=right.errors,original_trace=left.trace,C_trace=right.trace));raise
        observation={}
        if case['kind'].startswith('scene_cleanup_'):
            read=lambda address,width:int.from_bytes(right.memory[address:address+width],'big')
            head=read(0x112d60,4)
            observation=dict(texture_refs=[read(0x15b4a2+i*4,2)for i in range(12)],actor_resource_flags=[read(0x4bd9c+i*30,2)for i in[0,39]],handles=[read(a,4)for a in[0x97000,0x97004]],free_head=hex(head),free_head_size=read(head,4)if head else None,total_free=read(0x112d64,4))
        results.append(dict(case=index,kind=case['kind'],D0=actual,instructions=steps,source_entry_counts={hex(a):n for a,n in case_entries.items()},trace_sha256=sha(json.dumps(left.trace).encode()),RAM_sha256=sha(left.memory),cleanup_observation=observation))
        heap_tag=(case['kind'],next((v for a,w,v in reversed(case['initial'])if a==0x49d5a),None))
        heap_case=bool(case_entries.get(0x152a2)or case_entries.get(0x1545c))and heap_tag not in seen_heap_cases and len(seen_heap_cases)<24
        native_poll=case['kind'].startswith('poll_raw_')and int(case['kind'].rsplit('_',1)[1])in[0,2,24]
        if not case.get('read_queues')and(case['state']not in seen_states or case['kind'].startswith(('linked_attack_','resource_','elevator_','display_','scene_cleanup_'))or heap_case or native_poll):
            native_vectors.append((case,actual,bytes(right.memory)));seen_states.add(case['state'])
            if heap_case:seen_heap_cases.add(heap_tag)
    decoded=[]
    for start,end in[(0x191f4,0x192a2),(0x192bc,0x19f2c),(0x18df2,0x18e92),(0x1a0f8,0x1a188),(0x190bc,0x191f4),(0xe4c0,0xe53c)]:
        part,_=world.select.binary_tools.m68k_instructions(snapshot[start:end],start);decoded+=part
    if opts.limit:
        save(out/'preflight.json',dict(status='terminal_preflight_pass',cases=len(results),entries={hex(a):n for a,n in entries.items()}));print('Preflight passed',len(results),flush=True);return
    missing=[row for row in decoded if row['address']not in coverage]
    assert not missing,[hex(row['address'])for row in missing]
    guards=[]
    for missing_callback in range(7):
        script=Script(snapshot,vectors[0]);status,value=dispatch.translated(fn,script,vectors[0],missing=missing_callback)
        assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(dict(missing_callback=missing_callback,status=status))
    script=Script(snapshot,vectors[0]);status,value=dispatch.translated(fn,script,vectors[0],budget=0)
    assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(dict(zero_budget=True,status=status))
    guards+=animation_guards(fn,snapshot,vectors)
    guards+=heap_guards(fn,snapshot,vectors)
    guards+=resource_guards(fn,snapshot,vectors)
    guards+=elevator_guards(fn,snapshot,vectors)
    guards+=display_guards(fn,snapshot,vectors)
    guards+=polling_guards(fn,snapshot,vectors)
    guards+=cleanup_guards(fn,snapshot,vectors)
    script=Script(snapshot,vectors[0])
    def missing_scratch(bus,write8,budget,incoming,result):return raw_fn(bus,write8,0,budget,incoming,result)
    status,value=dispatch.translated(missing_scratch,script,vectors[0],budget=1024)
    assert status==1 and value==0xa5a55a5a and not script.trace
    guards.append(dict(missing_display_scratch=True,status=1,output_untouched=True))
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    oracle=media.scheduler.Native(diagnostic_core=core);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    for width in[8,16,32]:
        reader=getattr(runtime.core,'m68k_read_memory_'+str(width));reader.argtypes=[c.c_uint32];reader.restype=c.c_uint32
        writer=getattr(runtime.core,'m68k_write_memory_'+str(width));writer.argtypes=[c.c_uint32,c.c_uint32];writer.restype=None
    try:native=[native_check(runtime,fn,snapshot,*vector,evidence_dir=out)for vector in native_vectors]
    finally:oracle.close()
    save(out/'fixtures.json',vectors);save(out/'results.json',results);save(out/'native.json',native);save(out/'guards.json',guards)
    report=dict(status='linked_input_poll_attack_animation_elevator_panel_text_formatter_scene_cleanup_resources_heap_RNG_math_original_and_native_match',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),cases=len(vectors),instruction_address_coverage=[len(decoded),len(decoded)],original_source_entries={hex(a):n for a,n in entries.items()},native_cases=len(native),guards=len(guards),remaining_scripted_helper_targets=[hex(a)for a in FALLBACK],remaining_scripted_helper_count=len(FALLBACK),compiler=command,source_sha256={name:sha((restore/name).read_bytes())for name in names+['biwn_game_controls.h','biwn_attack_effect.h','biwn_input_dispatch.h','biwn_animation.h','biwn_memory.h','biwn_transition_cleanup.h','biwn_resources.h','biwn_elevator_input.h','biwn_elevator_display.h','biwn_elevator_formatter.h','biwn_formatter_cpu.h','biwn_panel_refresh.h','biwn_text.h','biwn_input_poll.h']},core=str(core),core_sha256=sha(core.read_bytes()),authorship='Coordinator bus-routing glue; earlier input/RNG/math/animation/resource reconstruction; coordinator elevator body after rejected local draft and coordinator elevator display/panel/formatter ABI adapter with static source formatter and prior readable text; local attack body with disclosed coordinator repairs.',high_level_component_natural_gameplay_damage_verified=False,default_runtime_promoted=False,new_training=False,scope='Readable input191F4 -> rawcontroller pollE4C0 and attack18DF2 -> indexed RNG1A77C and real C division/remainder/multiply, real animation advanceEB04/enqueueEAC4 and elevator input1A0F8/display190BC, resource get1AF04/release1B002 with allocator152A2/free1545C and real scene cleanup20F0C/region20E40/texture release1AE56, ordered external bus effects/fullD0/2MBRAM. All13states,40attack locations,34elevator input and68display locations;990address coverage refers to dispatcher+attack+elevator input/display+poll, not all animation/math/formatter addresses. Coupling fixtures use actor0,delta1,finite current frame records and parentwaitbudget1024; rawweapon slots retained. Heap fixtures use coherent initial free blocks/handles; real original/C free, coalescing, allocation, splitting and handle registration determine results. Earlier rawactor/clock proof is separate. Nine other dispatcher targets, three resource backend services (loader1B044,waitDF8C,signalDF9C), one scene setup service (20F78) remain controlled fixture bodies on both sides; native checks retain those explicit effects. Five resident resource records/data and coherent heap headers are supplied. Resource reference counts, cache scans, eviction/free, allocation and handle registration are computed; loader completion/data and scheduler readiness/signaling are supplied. Compaction/copy are linked but not reached in this equipment integration proof; their existing standalone proofs remain separate. Display uses caller-mapped16byte private scratch and source C formatter1B45A/1B29C/1B212 with unsigned quotient/remainder. Formatter text/count/public scratch effects are computed, with no supplied text or hostprintf; panel12620 and text149AE execute source C. A separate native lane drives the actual pinned blitter from both original CPU and C and compares public RAM/framebuffer; command-only fixtures do not assign device effects. Glyph rasterization is included for the supplied coherent panel/text/font/framebuffer cases; natural gameplay, whole scanout and physical timing remain excluded. Older API without scratch leaves190BC external. Animation queue consumption/rendering is outside this component. Rawcontroller values are supplied at four orderedMMIOreads; held/edgeglobals are computed and poll preservesD0. Native fixture injects rawMOVE.L read results with flags, not final input globals. Scene cleanup computes region texture reference decrements,40actor flags/resource clears and actual frees/coalescing from supplied coherent scene/heap records; new scene setup remains external. Private stack/CCR/caller-saved registers, physical controller/timing and natural gameplay excluded.')
    report.update(
        remaining_dispatcher_helper_count=9,
        raw_controller_reads_supplied=True,
        controller_held_and_edge_results_supplied=False,
        original_controller_D0_preserved=True,
        raw_controller_cases=sum(row['kind'].startswith('poll_raw_')for row in vectors),
        native_controller_poll_cases=sum(bool(row['raw_controller_rows'])for row in native),
        native_raw_controller_read_fixture='Inject device read results at original MOVE.L E4D4/E4E8/E4FC/E512, including MOVE NZVC; selector instructions execute original writes. No held/edge/global or helper-return injection.',
        controller_mapping_original_fixture=str(CONTROLLER_MAPPING_PATH),
        controller_mapping_original_fixture_sha256=sha(CONTROLLER_MAPPING_PATH.read_bytes()),
        physical_controller_verified=False,
        remaining_display_backend_services=[hex(a)for a in DISPLAY_SERVICES],
        panel_and_text_results_supplied=False,
        native_actual_blitter_cases=sum(bool(row['actual_blitter_commands'])for row in native),
        native_actual_blitter_commands=sum(row['actual_blitter_commands']for row in native),
        native_blitter_framebuffer_matches_original=True,
        native_blitter_diagnostic_images=[row['diagnostic_image']for row in native if row['diagnostic_image']],
        supplied_panel_fixture='record4 at55,50,150,61,border4; three linked label text records; original4C3E0font; framebuffer100000',
        verified_API='biwn_game_controls_with_scratch',
        legacy_API_elevator_display_external=True,
        private_display_buffer=hex(DISPLAY_SCRATCH),
        elevator_formatted_text_supplied=False,
        formatter_implementation='Static source-specific C instruction blocks, not hostprintf or original CPU execution',
        formatter_private_register_seeds_supplied=True,
        formatter_public_scratch_effects_computed=True,
        formatter_remaining_host_execution=False,
        remaining_scene_backend_services=[hex(a)for a in SCENE_SERVICES],
        scene_cleanup_results_supplied=False,
        scene_setup_results_supplied=True,
        scene_cleanup_initial_region_texture_actor_heap_state_supplied=True,
        scene_cleanup_cases=[row['kind']for row in vectors if row['kind'].startswith('scene_cleanup_')],
        scene_cleanup_shared_budget=20000,
        elevator_cases=[row['kind']for row in vectors if row['kind'].startswith('elevator_')],
        remaining_resource_backend_services=[hex(a)for a in RESOURCE_SERVICES],
        resource_initial_cache_and_data_supplied=True,
        resource_get_release_results_supplied=False,
        resource_loader_and_scheduler_effects_supplied=True,
        resource_lifecycle_cases=[row['kind']for row in vectors if row['kind'].startswith('resource_')],
        heap_initial_state_supplied=True,allocator_free_results_supplied=False,
        linked_but_unreached_entries=[hex(a)for a in [0x15200,0xe3e0,0xe3ee]if not entries.get(a)],
        coalescing_cases=['empty','merge_previous','merge_next','merge_both','insert_middle','append_tail'],
        instruction_coverage_scope='990 dispatcher/attack/elevator-input/display/poll instruction addresses only; panel/text/formatter address coverage excluded; formatter/animation/math entry counts show execution, not complete address coverage.',
        separate_instruction_level_gameplay_damage_verified=True,
        separate_gameplay_damage_proof=str(ROOT/'verification/ordinary-gameplay-damage-current.json'),
        prior_heap_component=str(ROOT/'verification/status-archive/controls-before-resource-link/proof.json'),
        prior_resource_component=str(ROOT/'verification/status-archive/controls-before-elevator-link/proof.json'),
        prior_elevator_component=str(ROOT/'verification/status-archive/controls-before-elevator-display-link/proof.json'),
        prior_formatter_fixture_component=str(ROOT/'verification/status-archive/controls-before-source-formatter-link/proof.json'),
        prior_panel_fixture_component=str(ROOT/'verification/status-archive/controls-before-panel-text-link/proof.json'),
        prior_input_poll_component=str(ROOT/'verification/status-archive/controls-before-input-poll-link/proof.json'),
        prior_scene_cleanup_component=str(ROOT/'verification/status-archive/controls-before-scene-cleanup-link/proof.json'),
        verifier=str(Path(__file__).resolve()),verifier_sha256=sha(Path(__file__).read_bytes()))
    save(out/'report.json',report);save(ROOT/'verification/game-controls-current.json',report)
    print(json.dumps({key:report[key]for key in ['status','cases','native_cases','guards','original_source_entries','remaining_dispatcher_helper_count','remaining_resource_backend_services']}),flush=True)


if __name__=='__main__':main()
