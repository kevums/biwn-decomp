"""Native controller: retained-core full ABI plus arbitrary-row ordered bus trace.

Native CPU cases use the emulator's real joystick matrix on both ports.
Separate Unicorn cases supply raw rows and check access width/value/order;
Unicorn is not the full-SR oracle. No physical keyboard/controller claims.
"""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_scheduler import Native
import check_biwn_input_poll as fixtures
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x15edc0;ENTRY=BASE;SP=0x1e0000;STOP=0x1f0000
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]

def seeded(image,previous):
    ram=bytearray(image);ram[0x49ba4:0x49ba8]=previous.to_bytes(4,'big');ram[0x49bac:0x49bb0]=bytes.fromhex('a55aa55a');ram[SP:SP+4]=STOP.to_bytes(4,'big');return ram

def cpu_run(n,image,case,length,reference):
    ram=seeded(image,case['previous']);n.device.seed(bytes(ram),0);l=n.lib;l.JoystickReset()
    if hasattr(l,'JoystickSetTeamTap'):
        l.JoystickSetTeamTap(0,0);l.JoystickSetTeamTap(1,0)
    for port in [0,1]:
        buttons=(c.c_uint8*84).in_dll(l,'joypad'+str(port)+'Buttons');buttons[:]=bytes(84)
        for i in range(21):buttons[i]=int(bool(case['pad'+str(port)]&(1<<i)))
    l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if case['sr']&0x2000 else 0x1ff000)
    l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if case['sr']&0x2000 else SP);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['regs']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,0xe4c0 if reference else ENTRY);cycles=0;pcs=[]
    for _ in range(10000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert (0xe4c0<=pc<0xe53c)if reference else(BASE<=pc<BASE+length),hex(pc)
        pcs.append(pc);cycles+=l.m68k_execute(1)
    else:raise AssertionError('No controller return')
    cpu=dict(regs=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17))
    cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['regs'][15];cpu['ssp']=cpu['regs'][15]if cpu['SR']&0x2000 else n.prefix[17]
    assert cpu['regs']==case['regs']+[SP+4]
    return cpu,n.device.ram(),cycles,pcs

def trace_run(image,case,length,reference):
    memory=seeded(image,case['previous']);script=fixtures.Script(memory,case);script.memory[SP:SP+4]=STOP.to_bytes(4,'big')
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_map(0xf14000,0x1000);u.mem_write(0,bytes(script.memory))
    for reg,v in zip(REGS,case['regs']):u.reg_write(reg,v)
    u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,SP)
    steps=[]
    def ignored(a,w):return SP-0x1000<=a and a+w<=SP+4
    def code(emu,a,w,_):
        assert (0xe4c0<=a<0xe53c)if reference else(BASE<=a<BASE+length),hex(a)
        steps.append(a)
    def read(emu,access,a,w,v,_):
        if ignored(a,w):return
        emu.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(emu,access,a,w,v,_):
        if ignored(a,w):return
        script.write(a,w,v&((1<<(w*8))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0xe4c0 if reference else ENTRY,STOP,count=10000,timeout=1000000)
    assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4
    assert [u.reg_read(reg)for reg in REGS]==case['regs']
    return script.trace,bytes(u.mem_read(0,0x200000)),steps

def normalize(ram,reference,length):
    data=bytearray(ram);data[BASE:BASE+length]=reference[BASE:BASE+length];data[SP-0x1000:SP]=reference[SP-0x1000:SP];return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    global ENTRY
    proof=ROOT/'verification/local-native-controller-cleanup-current.json';author=json.loads(proof.read_text());candidate=Path(author['candidate']);assert sha(candidate)==author['candidate_sha256']
    out=ROOT/'verification/native-load-bundle-controller'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),limit=args.limit,author_proof=str(proof),author_proof_sha256=sha(proof),candidate=str(candidate),candidate_sha256=sha(candidate),source_accepted=False,whole_game_complete=False,physical_controller=False,game_frames=0)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-load-bundle-controller-active.json',state)
    mark()
    try:
        native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'build';command=['make','-f','Makefile.load-bundle','load-bundle','BUILD='+str(build),'CONTROLLER_SOURCE='+str(candidate)]
        compiled=subprocess.run(command,cwd=native,capture_output=True,text=True);(out/'make.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
        binary=build/'native-load-bundle.bin';payload=binary.read_bytes();original=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();new=bytearray(original);new[BASE:BASE+len(payload)]=payload
        assert sha(binary)=='418ae7d7f9c3a72da6231e694caaf1936ed55c85db3a1ba8e8420d07bb7aee85', "Wrong relocated bundle bytes"
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');ENTRY=int(next(line.split()[0]for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/'native-load-bundle.elf')],text=True).splitlines()if line.split()[-1]=='biwn_native_controller_poll'),16);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/'native-load-bundle.elf')],text=True))
        import binary_tools
        row=next(line.split()for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'native-load-bundle.elf')],text=True).splitlines()if line.split()[-1]=='biwn_native_controller_poll_body')
        lo=int(row[0],16)-BASE;size=int(row[1],16);assert size>0
        instructions,_=binary_tools.m68k_instructions(payload[lo:lo+size],BASE+lo)
        allowed={'move.l','move.w','movea.l','moveq','ror.l','rol.l','ori.l','or.l','and.l','not.l','rts'}
        assert all(row['classification']=='decoded_instruction'and row['assembly'].split()[0]in allowed for row in instructions)
        assert instructions[-1]['assembly']=='rts'
        save(out/'X-neutral-body-instructions.json',instructions);state['X_neutral_body_instructions']=len(instructions);state['X_neutral_instruction_whitelist']=sorted(allowed)
        rng=random.Random(0xe4c013);vectors=[]
        pads=[(0,0),(0x1fffff,0),(0,0x1fffff),(0x1fffff,0x1fffff)]+[(1<<bit,0)for bit in range(21)]+[(0,1<<bit)for bit in range(21)]
        for a,b in pads:vectors.append(dict(pad0=a,pad1=b,previous=rng.getrandbits(32),sr=0x2000,regs=[rng.getrandbits(32)for _ in range(15)]))
        while len(vectors)<1024:vectors.append(dict(pad0=rng.getrandbits(21),pad1=rng.getrandbits(21),previous=rng.getrandbits(32),sr=0x2000,regs=[rng.getrandbits(32)for _ in range(15)]))
        for mode in [0,0x2000,0x2700]:
            for ccr in range(32):
                for mask in [0,0x1fffff]:vectors.append(dict(pad0=mask,pad1=mask,previous=0 if not mask else 0xffffffff,sr=mode|ccr,regs=[rng.getrandbits(32)for _ in range(15)]))
        if args.limit:vectors=vectors[:args.limit]
        save(out/'native-fixtures.json',vectors);n=Native();rows=[];coverage=set();state['status']='native_full_CPU_Ram_joystick_matrix';mark()
        try:
            for i,case in enumerate(vectors):
                a,old_ram,old_cycles,pcs=cpu_run(n,original,case,len(payload),True);b,new_ram,cycles,newpcs=cpu_run(n,new,case,len(payload),False)
                assert a==b,(i,a,b)
                assert normalize(new_ram,old_ram,len(payload))==old_ram,('RAM',i)
                assert new_ram[BASE:BASE+len(payload)]==payload
                coverage.update(pcs);rows.append(dict(case=i,CPU=a,held=int.from_bytes(new_ram[0x49ba4:0x49ba8],'big'),edge=int.from_bytes(new_ram[0x49bac:0x49bb0],'big'),original_cycles=old_cycles,compiled_cycles=cycles,full_CPU_and_nonprivate_RAM_match=True))
                if i%128==0:state['completed_native']=len(rows);mark();print('Native',len(rows),'/',len(vectors),flush=True)
        finally:n.close()
        save(out/'native-results.json',rows)
        state['status']='ordered_arbitrary_raw_MMIO_rows';mark();trace_rows=[];trace_cases=fixtures.cases()
        if args.limit:trace_cases=trace_cases[:args.limit]
        for i,case in enumerate(trace_cases):
            case={**case,'sr':0x2000|(i%32),'regs':[rng.getrandbits(32)for _ in range(15)]}
            a,old_ram,_=trace_run(original,case,len(payload),True);b,new_ram,_=trace_run(new,case,len(payload),False)
            assert a==b and normalize(new_ram,old_ram,len(payload))==old_ram,('trace',i,a,b)
            assert new_ram[BASE:BASE+len(payload)]==payload
            trace_rows.append(dict(case=i,parameters=case,ordered_trace=a,full_registers_and_external_RAM_match=True))
            if i%128==0:state['completed_trace']=len(trace_rows);mark();print('Trace',len(trace_rows),'/',len(trace_cases),flush=True)
        save(out/'trace-results.json',trace_rows)
        if not args.limit:
            decoded,_=fixtures.world.select.binary_tools.m68k_instructions(original[0xe4c0:0xe53c],0xe4c0);assert {x['address']for x in decoded}<=coverage
        source_paths=[Path(__file__),ROOT/'scripts/check_biwn_input_poll.py',candidate,*[native/name for name in ['controller-native.c','controller-lean-shim.S','controller-bundle.ld','Makefile.controller-lean-bundle','Makefile.fast-rng','rng-native.c','rng-native.h','rng-shims.S','rng-fast-math.S','runtime-original.S','runtime-original.ld','fast-rng.ld','startup-finalize.S','button-digit-movable-shim.S','Makefile','Makefile.movable','Makefile.math','Makefile.bundle','Makefile.optimized','Makefile.native']]]
        state.update(status='terminal_native_controller_preflight_pass'if args.limit else'terminal_native_controller_CPU_RAM_and_ordered_MMIO_pass',native_cases=len(rows),trace_cases=len(trace_rows),original_instruction_locations=len(coverage),source_accepted=False,controller_entry=ENTRY,compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),compiled_ELF=str(build/'native-load-bundle.elf'),source_sha256={str(p):sha(p)for p in source_paths},execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},scope='Full16register/PC/SR/USP/SSP/nativeRAM compares under actual emulated two-port joystick matrix, no game frame/IRQ/deviceclock. Separate1024raw-row ordered width/value/read/write cases use Unicorn; its SR is not the flags oracle. Private scratch stack and new code bytes excluded from RAM identity; code immutability checked. No physicalpad, keyboard, bus-error or full-game proof.')
        mark();save(ROOT/'verification/native-load-bundle-controller-current.json',state);print(state['status'],len(rows),len(trace_rows),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
