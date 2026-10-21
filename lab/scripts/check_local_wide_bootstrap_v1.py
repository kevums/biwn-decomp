"""Unedited local patch helper plus real68000 copy/clear/restore execution.

This is a startup component prototype with synthetic payloads, not a disc
build, module-arena relocation proof or a game-boot qualification.
"""
import ast
import os
from pathlib import Path
import random
import runpy
import struct
import subprocess
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from publish_geometry_records_progress_v1 import clone
from wide_bootstrap_support_v1 import plan_input_layout,stage_clear_lines,align

TEMPLATE=bytes.fromhex('46fc27002e7c0020000048e7fffe41fa001843f90015edc0303c000032d851c8fffc4ef90015edd4')
BASE=0x15edc0
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
      UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
      UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
      UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]


def main():
    author_path=V/'local-wide-bootstrap-author-v1-current.json';author=read(author_path)
    assert author['new_predictions']==1 and author['candidate_statement_edits']==0
    for path,digest in author['source_sha256'].items():assert sha(path)==digest,path
    candidate=Path(author['directory'])/'candidate.py'
    tree=ast.parse(candidate.read_text())
    assert len(tree.body)==1 and isinstance(tree.body[0],ast.FunctionDef)
    assert tree.body[0].name=='widen_biwn_loader'
    assert not any(isinstance(x,(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal))for x in ast.walk(tree))
    # The raw source has been inspected: one pure function with local bytearray
    # mutation, exact type checks and built-ins only; no I/O or top-level work.
    widen=runpy.run_path(str(candidate))['widen_biwn_loader']
    out=V/'local-wide-bootstrap-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'local-wide-bootstrap-reviewed-v1-current.json'
    state=dict(status='checking_unedited_wide_loader_host_contract',directory=str(out),pid=os.getpid(),
        host_valid_cases=0,host_invalid_cases=0,native_copy_cases=0,native_integrated_cases=0,
        native_negative_controls=0,new_predictions=0,optimizer_updates=0,new_disc_built=False)

    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();rng=random.Random(0x303c22d8);rows=[];commands=[]

    def expect_invalid(header,size):
        try:widen(header,size)
        except ValueError:state['host_invalid_cases']+=1
        else:raise AssertionError(('Invalid loader accepted',repr(header)[:100],repr(size)))

    def compile_finalizer(folder,address,staging,clear_bytes):
        folder.mkdir(parents=True,exist_ok=True)
        assembly=folder/'clear.S';link=folder/'clear.ld';elf=folder/'clear.elf';binary=folder/'clear.bin'
        assembly.write_text('\n'.join(['.text','.globl wide_startup_finalize','wide_startup_finalize:',
            *stage_clear_lines(staging,clear_bytes),'movem.l (%sp)+,%d0-%d7/%a0-%a6',
            'move.w #0x2700,%sr','jmp 0x400a'])+'\n')
        link.write_text('SECTIONS { . = '+hex(address)+'; .text : { *(.text*) } /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) } }\n')
        cross=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        for command in [[cross+'as','-m68000',str(assembly),'-o',str(folder/'clear.o')],
                        [cross+'ld','-T',str(link),str(folder/'clear.o'),'-o',str(elf)],
                        [cross+'objcopy','-O','binary',str(elf),str(binary)]]:
            commands.append(command);subprocess.run(command,check=True,capture_output=True)
        return binary.read_bytes(),assembly,link

    def execute(header,size,staging,last,integrated=False,old_wrapped=False):
        cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000)
        before=bytearray(b'\xa5'*0x200000);payload=bytearray(rng.randbytes(size));payload[-4:]=last.to_bytes(4,'big')
        clear_bytes=align(40+size,64);finalizer=None
        if integrated:
            address=BASE+size-32
            blob,_,_=compile_finalizer(out/f'integrated-{size}-{last:08x}',address,staging,clear_bytes)
            assert len(blob)<=32 and size>=64
            payload[20:26]=b'\x4e\xf9'+address.to_bytes(4,'big')
            payload[-32:-32+len(blob)]=blob
        before[staging:staging+40]=header
        before[staging+40:staging+40+size]=payload
        before[staging+40+size:staging+clear_bytes]=b'\x6c'*(clear_bytes-40-size)
        cpu.mem_write(0,bytes(before));initial=[rng.getrandbits(32)for _ in REGS]
        for reg,value in zip(REGS,initial):cpu.reg_write(reg,value)
        usp=0x1de000;cpu.reg_write(UC_M68K_REG_SR,0);cpu.reg_write(UC_M68K_REG_A7,usp)
        cpu.reg_write(UC_M68K_REG_SR,0x2000|(rng.randrange(8)<<8)|rng.randrange(32));cpu.reg_write(UC_M68K_REG_A7,0x1fc000)
        saved_sp=0x200000-60;writes=0
        def write(engine,access,a,w,value,user):
            nonlocal writes
            assert(BASE<=a and a+w<=BASE+size or saved_sp<=a and a+w<=0x200000
                or integrated and staging<=a and a+w<=staging+clear_bytes),(hex(a),w)
            writes+=1
        cpu.hook_add(UC_HOOK_MEM_WRITE,write)
        stop=0x400a if integrated else BASE+20
        cpu.emu_start(staging,stop,count=600000,timeout=10000000)
        assert cpu.reg_read(UC_M68K_REG_PC)==stop
        actual=bytes(cpu.mem_read(0,0x200000));expected=bytearray(before)
        copied=2*((int.from_bytes(header[26:28],'big')+1))if old_wrapped else size
        expected[BASE:BASE+copied]=payload[:copied]
        expected[saved_sp:0x200000]=struct.pack('>15I',*initial)
        if integrated:
            expected[staging:staging+clear_bytes]=bytes(clear_bytes)
            assert [cpu.reg_read(reg)for reg in REGS]==initial
            assert cpu.reg_read(UC_M68K_REG_A7)==0x200000 and cpu.reg_read(UC_M68K_REG_SR)==0x2700
        else:
            assert cpu.reg_read(UC_M68K_REG_A7)==saved_sp
            assert cpu.reg_read(UC_M68K_REG_A0)==staging+40+copied
            assert cpu.reg_read(UC_M68K_REG_A1)==BASE+copied
        assert actual==expected,'Complete RAM/canary/copy/clear mismatch'
        sr=cpu.reg_read(UC_M68K_REG_SR);cpu.reg_write(UC_M68K_REG_SR,sr&~0x2000)
        assert cpu.reg_read(UC_M68K_REG_A7)==usp
        return dict(bytes=size,copied=copied,staging=staging,clear_bytes=clear_bytes,
                    integrated=integrated,last_payload_long=last,write_events=writes,
                    complete_RAM_and_fences_equal=True,inactive_USP_unchanged=True)

    try:
        sizes=[4,8,64,1024,121536,121600,131068,131072,131076,132096,132160,148608,262140,262144]
        for count in range(65536):
            header=TEMPLATE[:26]+count.to_bytes(2,'big')+TEMPLATE[28:];size=sizes[count%len(sizes)]
            actual=widen(header,size)
            want=TEMPLATE[:26]+(size//4-1).to_bytes(2,'big')+b'\x22\xd8'+TEMPLATE[30:]
            assert type(actual)is bytes and actual==want and len(actual)==40
            state['host_valid_cases']+=1
        for offset in range(40):
            if offset in [26,27]:continue
            for value in range(256):
                if value==TEMPLATE[offset]:continue
                mutated=bytearray(TEMPLATE);mutated[offset]=value;expect_invalid(bytes(mutated),132160)
        class IntSubclass(int):pass
        class BytesSubclass(bytes):pass
        for header in [None,1,'x',bytearray(TEMPLATE),memoryview(TEMPLATE),BytesSubclass(TEMPLATE),b'',TEMPLATE[:-1],TEMPLATE+b'\0']:
            expect_invalid(header,132160)
        for size in [None,True,False,4.0,'4',IntSubclass(4),-4,0,1,2,3,5,6,262145,262148,1<<100]:
            expect_invalid(TEMPLATE,size)
        expect_invalid(widen(TEMPLATE,132160),132160)
        mark()
        plans={};original_session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
        original_stage=original_session/'nextstage-68000-candidate.bin';original=original_stage.read_bytes()
        deps=[author_path,candidate,Path(__file__),ROOT/'scripts/wide_bootstrap_support_v1.py',original_stage]
        for name in ['native-record-strides-disc-build-v1','native-record-loop-image-disc-build-v1']:
            path=V/(name+'-current.json');build=read(path);plan=plan_input_layout(build,10580)
            assert not any(original[plan['staging_address']-0x4000:0xfe200-0x4000])
            stage=Path(build['derived_stage']).read_bytes();offset=build['staging_address']-0x4000
            header=stage[offset:offset+40]
            assert widen(header,plan['copy_bytes'])==widen(TEMPLATE,plan['copy_bytes'])
            plans[name]=plan;deps.extend([path,Path(build['derived_stage'])])
        assert plans['native-record-strides-disc-build-v1']['copy_bytes']==132160
        assert plans['native-record-strides-disc-build-v1']['clear_bytes']==132224
        assert plans['native-record-strides-disc-build-v1']['initial_heap_bytes']==123520
        save(out/'planned-layouts.json',plans)
        state['status']='executing_real_68000_wide_copy_and_clear_prototypes';mark()
        for size in sizes:
            for last in [0,1,0x80000000,0xffffffff]:
                rows.append(execute(widen(TEMPLATE,size),size,0x80000,last));state['native_copy_cases']+=1
        for size in [64,1024,121536,121600,131072,131076,132096,132160,148608]:
            for last in [0,0x80000000]:
                staging=0xfe200-align(40+size,64)
                rows.append(execute(widen(TEMPLATE,size),size,staging,last,integrated=True));state['native_integrated_cases']+=1
        # A deliberately naive wrapped legacy counter is a negative control,
        # not an assertion that the current guarded builder emits a bad image.
        size=132160;bad=TEMPLATE[:26]+((size//2-1)&65535).to_bytes(2,'big')+TEMPLATE[28:]
        negative=execute(bad,size,0x80000,0xffffffff,old_wrapped=True)
        assert negative['copied']==1088 and negative['copied']!=size
        state['native_negative_controls']=1;save(out/'negative-control.json',negative)
        save(out/'native-cases.json',rows);save(out/'compiler-commands.json',commands)
        # One newly generated clear routine is rebuilt with the copied SDK.
        first=out/'integrated-132160-00000000';copydir=P/'workbench/builds/input-wide-bootstrap-clear-v1'/out.name;copydir.mkdir(parents=True)
        for name in ['clear.S','clear.ld']:clone(first/name,copydir/name)
        cross=P/'workbench/tools/m68k-elf/bin/m68k-elf-'
        assert Path(str(cross)+'as').resolve().is_relative_to(P)
        for command in [[str(cross)+'as','-m68000',str(copydir/'clear.S'),'-o',str(copydir/'clear.o')],
                        [str(cross)+'ld','-T',str(copydir/'clear.ld'),str(copydir/'clear.o'),'-o',str(copydir/'clear.elf')],
                        [str(cross)+'objcopy','-O','binary',str(copydir/'clear.elf'),str(copydir/'clear.bin')]]:
            subprocess.run(command,check=True,capture_output=True)
        assert (copydir/'clear.bin').read_bytes()==(first/'clear.bin').read_bytes()
        profile=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/input-wide-startup-prototype-v1';profile.mkdir()
        clone(candidate,profile/'widen_loader.py');clone(ROOT/'scripts/wide_bootstrap_support_v1.py',profile/'wide_bootstrap_support_v1.py')
        deps.extend([profile/'widen_loader.py',profile/'wide_bootstrap_support_v1.py'])
        deps.extend(path for path in out.rglob('*')if path.is_file()and path.name!='protocol.json')
        state.update(status='terminal_unedited_local_wide_copy_and_68000_clear_restore_pass_uninstalled',
            model_statement_edits=0,local_function_used_in_prototype=True,source_profile=str(profile),
            copied_clear_build_byte_identical=True,copied_clear_build=str(copydir),
            native_integrated_all_registers_SR_SSP_and_USP_preserved=True,
            full_RAM_copy_clear_and_canary_checks=True,negative_control_wrapped_copy_bytes=1088,
            plans=plans,copy_loop_capacity=262144,original_blank_staging_limit_still_required=True,
            whole_image_module_arena_heap_relocation_qualified=False,
            installed_builder_changed=False,source_sha256={str(path):sha(path)for path in deps},
            scope='PurePythonpatcheruneditedfromlocalCoder. Hostexact-template/count/typeguards;M68000syntheticpayloadcopyplusgeneratedlongclear/savedGPRrestoreto400A. EveryRAMbyte/canaryandstackbankchecked. Feasiblev34/v37layoutplansonly;module/arena/heaprelink,exactproviders/alias/IRQ/startup/freshimagequalificationnotdone. Existingbuildersstillusewordloops/guardsandarenotchanged.')
        mark();print(state['status'],state['host_valid_cases'],state['host_invalid_cases'],state['native_copy_cases'],state['native_integrated_cases'],flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',rows);state.update(status='terminal_wide_bootstrap_review_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
