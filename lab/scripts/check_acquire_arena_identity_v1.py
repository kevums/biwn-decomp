"""Test acquire adapter slot identity/capture/restore, with a declared RTS body.

All101task slots and7invalid IDs exercise user/supervisor modes and flag
endpoints. This is adapter-only: the C body is an explicit no-effect provider,
not a resource, scheduler, IRQ, ownership-lifetime or game-image proof.
"""
import os
import random
import struct
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]


def main():
    proof_path=V/'acquire-arena-prototype-v1-current.json';proof=read(proof_path)
    for p,h in proof['source_sha256'].items():assert sha(p)==h,p
    bp=Path(proof['parent_build']);b=read(bp)
    out=V/'acquire-arena-identity-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'acquire-arena-identity-v1-current.json'
    state=dict(status='running_adapter_identity',pid=os.getpid(),directory=str(out),completed=0,new_predictions=0,optimizer_updates=0)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();rng=random.Random(0x19400a168);pool=0xc0928;body=b['symbols']['biwn_native_resource_acquire_body'];entry=proof['symbols']['biwn_acquire_arena_entry'];base=proof['existing_GPU_arena_base'];stop=0x3000
    snapshot=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    snapshot[b['resident_address']:b['heap_start']]=Path(proof['component']).read_bytes()
    payload=Path(proof['payload']).read_bytes();snapshot[entry:entry+len(payload)]=payload
    snapshot[body:body+2]=bytes.fromhex('4e75')
    slots=[pool+i*1024 for i in range(101)];invalid=[0,2,pool-1,pool-1024,pool+101*1024,pool+100*1024+2,0xffffffff]
    rows=[]
    try:
        for task in slots+invalid:
            slot=(task-pool)//1024 if task in slots else 101
            for mode in [0,0x2000]:
                for flags in [0,31]:
                    memory=bytearray(snapshot);memory[base:base+102*256]=bytes([0xa5])*(102*256)
                    memory[0xc0920:0xc0924]=task.to_bytes(4,'big');sp=task+900 if task in slots else 0x1d9000
                    memory[sp:sp+4]=stop.to_bytes(4,'big');incoming=[rng.getrandbits(32)for _ in REGS];sr=mode|0x700|flags
                    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(memory))
                    alternate=0x1ee000
                    cpu.reg_write(UC_M68K_REG_SR,sr^0x2000);cpu.reg_write(UC_M68K_REG_A7,alternate);cpu.reg_write(UC_M68K_REG_SR,sr);cpu.reg_write(UC_M68K_REG_A7,sp)
                    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
                    cpu.emu_start(entry,body,count=1000,timeout=1000000)
                    assert cpu.reg_read(UC_M68K_REG_PC)==body
                    ctx=base+slot*256+168
                    frame=bytes(cpu.mem_read(ctx,72))
                    assert frame[:60]==struct.pack('>15I',*incoming)
                    assert int.from_bytes(frame[60:64],'big')==sp and int.from_bytes(frame[64:68],'big')==sr
                    assert cpu.reg_read(UC_M68K_REG_A7)==ctx-8
                    assert int.from_bytes(cpu.mem_read(ctx-4,4),'big')==ctx
                    cpu.emu_start(body,stop,count=1000,timeout=1000000)
                    assert cpu.reg_read(UC_M68K_REG_PC)==stop
                    assert [cpu.reg_read(reg)for reg in REGS]==incoming
                    assert cpu.reg_read(UC_M68K_REG_A7)==sp+4 and cpu.reg_read(UC_M68K_REG_SR)==sr
                    cpu.reg_write(UC_M68K_REG_SR,sr^0x2000);assert cpu.reg_read(UC_M68K_REG_A7)==alternate
                    actual=bytearray(cpu.mem_read(0,0x200000))
                    public=struct.pack('>6I',*[incoming[i]for i in [2,3,4,5,10,11]])
                    expected_stack=struct.pack('>IIH',incoming[0],incoming[8],sr)+public
                    assert actual[sp-34:sp]==expected_stack
                    if task in slots:assert actual[task:task+64]==memory[task:task+64]
                    for index in range(102):
                        at=base+index*256
                        assert actual[at:at+16]==actual[at+240:at+256]==bytes([0xa5])*16
                    comparable=bytearray(actual);comparable[base+slot*256+16:base+slot*256+240]=memory[base+slot*256+16:base+slot*256+240];comparable[sp-34:sp]=memory[sp-34:sp]
                    assert comparable==memory
                    rows.append(dict(task=task,slot=slot,mode=mode,flags=flags,context=ctx,all_registers_SR_banks_and_outside_explicit_private_regions_match=True,guest_save_bytes_exact=True))
                    state['completed']=len(rows)
                    if len(rows)%32==0:mark()
        save(out/'cases.json',rows)
        # Independently validate the symbol-address identity claimed by v6.
        v6_path=V/'native-input-arena-admission-v6-current.json';v6=read(v6_path);nd=Path(v6['source_profile']);old=nd.parent/'input-dispatch-native-v5-rebased'
        import subprocess
        def symbols(path):
            text=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(path)],text=True)
            return {parts[2]:parts[0]for line in text.splitlines()if len(parts:=line.split())==3}
        assert symbols(old/'build-portable/native-input.elf')==symbols(nd/'build-portable/native-input.elf')
        paths=[Path(__file__),proof_path,bp,Path(proof['component']),Path(proof['payload']),ROOT/'render-assets/biwn-inventory-baseline.bin',out/'cases.json',v6_path,nd/'build-portable/native-input.elf',old/'build-portable/native-input.elf']
        state.update(status='terminal_acquire_adapter101task_slots7invalid_ids_capture_restore_fences_pass',completed=len(rows),valid_task_slots=101,invalid_ids=7,boot_fallback_slot=101,privilege_modes=2,incoming_flag_states=2,C_body_explicit_RTS_provider=True,v6_all_symbol_addresses_independently_verified=True,unrelated_arena_slots_unchanged=True,all102slot_guards_unchanged=True,new_RAM_reserved=0,arena_lifetime_aliases_qualified=False,real_scheduler_IRQ_qualified=False,new_disc_built=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__)
        mark();print(state['status'],len(rows),flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',rows);state.update(status='terminal_acquire_arena_identity_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
