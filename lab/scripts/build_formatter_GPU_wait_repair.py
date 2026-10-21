"""Experimental source behavior repair: wait for command acceptance and completion.

Appends one assembled routine within existing resident padding; all existing
14664 resident bytes, heap reservation and startup layout stay byte-identical.
"""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def check_wait(code,address):
    import ctypes as c
    from check_biwn_scheduler import Native
    plans=[[(0xffffffff,0)],[(0x6720,0),(0x6720,0),(0xffffffff,0xffffffff),(0xffffffff,0)],[(0x6720,0xffffffff),(0xffffffff,0xffffffff),(0xffffffff,0)],[(0xffffffff,0xffffffff),(0xffffffff,0)]]
    n=Native();lib=n.lib;lib.GPUGetRAM.restype=c.c_void_p
    rows=[];sp=0x1d0000;stop=0x190000
    def execute(body,plan,mode,flags,limit=1000):
        image=bytearray(0x200000);image[address:address+len(body)]=body;image[sp:sp+4]=stop.to_bytes(4,'big')
        n.device.seed(bytes(image),0);lib.m68k_pulse_reset();lib.m68k_set_irq(0);lib.m68k_set_reg(17,mode|flags)
        values=[(0x98765432+i*0x01020304)&0xffffffff for i in range(15)]+[sp]
        for i,v in enumerate(values):lib.m68k_set_reg(i,v)
        lib.m68k_set_reg(16,address);polls=[];gpu=lib.GPUGetRAM()
        for step in range(limit):
            pc=lib.m68k_get_reg(None,16)
            if pc==stop:break
            assert address<=pc<address+len(body),hex(pc)
            if pc==address:
                command,busy=plan[min(len(polls),len(plan)-1)];data=busy.to_bytes(4,'big')+command.to_bytes(4,'big');c.memmove(gpu+0x200,data,8);polls.append([command,busy])
            assert lib.m68k_execute(1)>0
        return dict(registers=[lib.m68k_get_reg(None,i)for i in range(16)],PC=lib.m68k_get_reg(None,16),SR=lib.m68k_get_reg(None,17)),polls,values
    try:
        for mode in [0,0x2000]:
          for flags in range(32):
           for plan in plans:
            result,polls,values=execute(code,plan,mode,flags)
            assert result['PC']==stop and len(polls)==len(plan)
            assert result['registers']==values[:15]+[sp+4]
            assert result['SR']==(mode|(flags&0x10)|4),result
            rows.append(dict(mode=mode,CCR=flags,polls=polls,all16registers_PC_SR_pass=True))
        symptom=[]
        for name,body in [('original',bytes.fromhex('0cb90000000000f0320066f44e75')),('repaired',code)]:
            result,polls,values=execute(body,[(0x6720,0)],0x2000,0)
            symptom.append(dict(lane=name,returned=result['PC']==stop))
        assert symptom==[dict(lane='original',returned=True),dict(lane='repaired',returned=False)]
        return rows,symptom
    finally:n.close()

def main():
    pp=ROOT/'verification/native-fast-core-format-disc-build-current.json';parent=json.loads(pp.read_text());bp=ROOT/'verification/native-fast-core-format-bundle-current.json';bundle=json.loads(bp.read_text());assert sha(parent['derived_disc'])==parent['derived_disc_sha256'];assert sha(bundle['binary'])==bundle['binary_sha256']
    out=ROOT/'builds/BIWN-native-fast-core-wait-format'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    payload=Path(bundle['binary']).read_bytes();address=parent['resident_address']+len(payload);asm=out/'gpu-wait-repair.S'
    asm.write_text('''.text
.globl biwn_GPU_wait_complete
biwn_GPU_wait_complete:
1: cmpi.l #-1,0xf03204
bne.s 1b
cmpi.l #0,0xf03200
bne.s 1b
rts
''');linker=out/'wait.ld';linker.write_text('SECTIONS { . = '+hex(address)+'; .text : { *(.text*) } /DISCARD/ : { *(.comment) *(.note*) } }\n')
    prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
    for command in [[prefix+'as','-m68000','-o',str(out/'wait.o'),str(asm)],[prefix+'ld','-T',str(linker),'-o',str(out/'wait.elf'),str(out/'wait.o')],[prefix+'objcopy','-O','binary',str(out/'wait.elf'),str(out/'wait.bin')]]:subprocess.run(command,check=True,capture_output=True,text=True)
    code=(out/'wait.bin').read_bytes();(out/'wait-disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(out/'wait.elf')],text=True));rows,symptom=check_wait(code,address);save(out/'wait-contract-cases.json',dict(cases=rows,pending_command_regression=symptom,scope='256 scripted mailbox plans across allCCR/modes; nativeCPU fixture uses mapped GPU RAM and explicit external transitions. No arbitrary IRQ or physical timing proof.'))
    linked=out/'resident-linked.bin';linked.write_bytes(payload+code);assert len(payload)+len(code)<=parent['component_bytes']
    padded=out/'resident-padded.bin';padded.write_bytes(payload+code+bytes(parent['component_bytes']-len(payload)-len(code)));assert padded.read_bytes()[:len(payload)]==payload
    stage=bytearray(Path(parent['derived_stage']).read_bytes());original_stage=bytes(stage);patches=[]
    def patch(at,before,after,reason):
        offset=at-0x4000;assert bytes(stage[offset:offset+len(before)])==before and len(before)==len(after);stage[offset:offset+len(before)]=after;patches.append(dict(address=hex(at),original=before.hex(),replacement=after.hex(),reason=reason))
    payload_at=parent['staging_address']+40+len(payload)
    patch(payload_at,bytes(len(code)),code,'Appended completion wait within existing resident padding; startup unchanged.')
    old=bytes(stage[0xe098-0x4000:0xe098-0x4000+6]);assert old==bytes.fromhex('0cb900000000')
    patch(0xe098,old,b'\x4e\xf9'+address.to_bytes(4,'big'),'Experimental source behavior repair: pending command must be accepted before busy0 permits return.')
    stagefile=out/'mainstage-wait-repaired.bin';stagefile.write_bytes(stage)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset']
    from extract_biwn_stage import swap16
    disc=out/'BIWN-23-native-fast-core-wait-experimental.cdi';shutil.copyfile(parent['derived_disc'],disc)
    with disc.open('r+b')as stream:
        for row in patches:
            at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['original']);after=bytes.fromhex(row['replacement']);stream.seek(at);assert stream.read(len(before))==swap16(before);stream.seek(at);stream.write(swap16(after))
        stream.flush();os.fsync(stream.fileno())
    intervals=[(offset+int(row['address'],16)-0x4000,offset+int(row['address'],16)-0x4000+len(bytes.fromhex(row['original'])))for row in patches];position=0;changes=0
    with Path(parent['derived_disc']).open('rb')as left,disc.open('rb')as right:
        while True:
            a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
            if not a:break
            for i,(x,y)in enumerate(zip(a,b)):
                if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changes+=1
            position+=len(a)
    assert sha(parent['derived_disc'])==parent['derived_disc_sha256']
    manifest=out/'stage-patches.json';prior=json.loads(Path(parent['patch_manifest']).read_text());all_patches=prior['patches']+patches;save(manifest,dict(patches=all_patches,delta_patches=patches,parent=str(pp),parent_sha256=sha(pp)))
    state={**parent,'directory':str(out),'derived_disc':str(disc),'derived_disc_sha256':sha(disc),'derived_stage':str(stagefile),'derived_stage_sha256':sha(stagefile),'component':str(padded),'linked_component':str(linked),'linked_component_bytes':linked.stat().st_size,'patch_manifest':str(manifest),'patch_manifest_sha256':sha(manifest),'symbols':dict(parent['symbols'],biwn_GPU_wait_complete=address),'source_sha256':{str(p):sha(p)for p in [Path(__file__),pp,bp,Path(parent['patch_manifest']),asm,linker,linked,padded,stagefile,manifest,out/'wait-contract-cases.json',out/'wait.bin']},'parent_build':str(pp),'parent_build_sha256':sha(pp),'parent_resident_prefix_byte_identical':True,'appended_wait_bytes':len(code),'new_mailbox_cases':len(rows),'pending_command_regression':symptom,'delta_CDI_changed_bytes':changes,'experimental_behavior_change':True,'full_linked_component_gates_revalidated':False,'game_frames':0,'default_promoted':False,'scope':'Experimental GPU completion wait change atE098; all14664existing residentbytes unchanged,new assembled routine in previouspadding. Existing16384reservation/heap162DC0 andstartup/staging retained.256scriptedCCR/mode cases and pending-command negativefixture; fresh entry and gameplay still required. No source equivalence for the intentionally repaired earlyreturn,hardware/fullgame claim,defaultpromotion or training.'}
    save(out/'build.json',state);save(ROOT/'verification/native-fast-core-wait-format-disc-build-current.json',state)
    entrysource=ROOT/'scripts/check_biwn_native_fast_core_format_disc_entry.py';entrytarget=ROOT/'scripts/check_biwn_native_fast_core_wait_format_disc_entry.py';entrytext=entrysource.read_text().replace('native-fast-core-format','native-fast-core-wait-format');compile(entrytext,str(entrytarget),'exec');entrytarget.write_text(entrytext)
    pairsource=ROOT/'scripts/run_biwn_native_fast_core_entry_deck_pair.py';pairtarget=ROOT/'scripts/run_biwn_native_fast_core_wait_entry_deck_pair.py';pairtext=pairsource.read_text().replace('native-fast-core-format','native-fast-core-wait-format').replace('native-fast-core-entry-selector','native-fast-core-wait-entry-selector');marker="left,right=reports['candidate']['frames'],reports['control']['frames'];assert len(left)==len(right)==state['frames']";assert pairtext.count(marker)==1
    pairtext=pairtext.replace(marker,marker+"\n    assert not any(int(row['CPU'],16)&1 for lane in reports.values()for row in lane['frames']), 'OddCPU PC: failed lane is not a pair pass'")
    compile(pairtext,str(pairtarget),'exec');pairtarget.write_text(pairtext)
    save(out/'generated-drivers.json',dict(source_sha256={str(p):sha(p)for p in [entrysource,entrytarget,pairsource,pairtarget]},exact_parent_resident_prefix=True))
    print(json.dumps(dict(status=state['status'],bytes=linked.stat().st_size,appended=len(code),cases=len(rows),CDI_changed=changes)),flush=True)

if __name__=='__main__':main()
