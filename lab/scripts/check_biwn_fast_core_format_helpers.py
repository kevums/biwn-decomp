"""Re-run complete original helper fixtures on the exact new linked bundle."""
import argparse,ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_native_format_pad as pad
import check_biwn_native_format_string as string
ROOT=pad.ROOT
def main():
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['pad','string']);args=parser.parse_args();gate=pad if args.kind=='pad'else string
    proof=Path('/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-fast-core-format-bundle-current.json');bundle=json.loads(proof.read_text());payload=Path(bundle['binary']).read_bytes();assert gate.sha(bundle['binary'])==bundle['binary_sha256'];gate.BASE=bundle['base']
    target=bundle['symbols']['biwn_native_format_'+args.kind];out=ROOT/'verification'/('native-fast-core-format-'+args.kind)/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    driver_source=string.DRIVER.replace('entry+88','entry+'+str(gate.END-gate.ENTRY));(out/'driver.c').write_text(driver_source)
    run=subprocess.run(['clang','-std=c99','-O2','-dynamiclib',str(out/'driver.c'),'-o',str(out/'driver.dylib')],capture_output=True,text=True);(out/'driver-build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    driver=c.CDLL(str(out/'driver.dylib'));driver.run.argtypes=[c.c_void_p,c.c_void_p,*([c.c_uint32]*6),c.c_uint64,c.POINTER(string.Stats)];driver.run.restype=c.c_int
    def execute(n,image,case,original):
        n.device.seed(gate.seed(image,case),0);lib=n.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0);supervisor=bool(case['sr']&0x2000)
        lib.m68k_set_reg(17,0x2000);lib.m68k_set_reg(15,gate.SP if supervisor else 0x1ff000);lib.m68k_set_reg(17,0);lib.m68k_set_reg(15,0x1fe000 if supervisor else gate.SP);lib.m68k_set_reg(17,case['sr'])
        for i,v in enumerate(case['incoming']+[gate.SP]):lib.m68k_set_reg(i,v)
        lib.m68k_set_reg(16,gate.ENTRY);stats=string.Stats();budget=min(50000000,50000+1024*(case['left']if case['left']<32768 else 0))
        status=driver.run(c.cast(lib.m68k_execute,c.c_void_p),c.cast(lib.m68k_get_reg,c.c_void_p),gate.STOP,gate.SP,gate.BASE,gate.BASE+len(payload),gate.ENTRY,int(original),budget,c.byref(stats));assert status==0,('linked native boundary/budget',status,hex(stats.pc))
        cpu=[lib.m68k_get_reg(None,i)for i in range(18)];cpu += [n.prefix[16]if supervisor else cpu[15],cpu[15]if supervisor else n.prefix[17]]
        return n.device.ram(),cpu,{gate.ENTRY+i for i,x in enumerate(stats.coverage)if x}
    image=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();candidate=bytearray(image);candidate[gate.BASE:gate.BASE+len(payload)]=payload;candidate[gate.ENTRY:gate.ENTRY+8]=b'\x4e\xf9'+target.to_bytes(4,'big')+b'\x4e\x71'
    state=dict(status='running_exact_linked_helper_gates',pid=os.getpid(),directory=str(out),kind=args.kind,bundle_proof=str(proof),bundle_proof_sha256=gate.sha(proof),binary_sha256=bundle['binary_sha256'],linked_entry=target,native_cases=0,ordered_cases=0,source_accepted=False,whole_game_complete=False)
    def save():gate.save(out/'protocol.json',state);gate.save(ROOT/'verification'/('native-fast-core-format-'+args.kind+'-active.json'),state)
    save();cases=gate.vectors();gate.save(out/'fixtures.json',cases);n=gate.Native();coverage=set();rows=[];changing=0
    try:
        for index,case in enumerate(cases):
            left,lc,pcs=execute(n,image,case,True);right,rc,_=execute(n,candidate,case,False)
            assert lc==rc and gate.normalize(right,left,len(payload))==left,('linked helper CPU/RAM mismatch',index)
            assert right[gate.BASE:gate.BASE+len(payload)]==payload
            a=gate.trace(image,case,len(payload),True);b=gate.trace(candidate,case,len(payload),False)
            assert a[1]==b[1]and gate.normalize(b[0],a[0],len(payload))==a[0],('linked ordered access mismatch',index)
            coverage.update(pcs);rows.append(dict(case=index,ordered_events=len(a[1])));state.update(native_cases=len(rows),ordered_cases=len(rows))
            if index%128==0:save();print(args.kind,len(rows),'/',len(cases),flush=True)
        if args.kind=='pad':
            selected=cases[:16]
            for case in selected:
                a=gate.trace(image,case,len(payload),True,True);b=gate.trace(candidate,case,len(payload),False,True);assert a[1]==b[1]and gate.normalize(b[0],a[0],len(payload))==a[0];changing+=1
        else:
            for case in [x for x in cases if x['left']in [2,7]and x['string']in ['one','seven','high_bytes']][:16]:
                queues={(string.COUNT,2):[2,4,2,1],(string.SOURCE,1):[ord('Q'),255]};a=gate.trace(image,case,len(payload),True,queues);b=gate.trace(candidate,case,len(payload),False,queues);assert a[1]==b[1]and gate.normalize(b[0],a[0],len(payload))==a[0];changing+=1
        expected=27 if args.kind=='pad'else 36;assert len(coverage)==expected;gate.save(out/'results.json',rows)
        state.update(status='terminal_exact_linked_format_helper_CPU_RAM_ordered_pass',changing_read_cases=changing,original_instruction_coverage=[len(coverage),expected],source_accepted=True,source_sha256={str(p):gate.sha(p)for p in [Path(__file__),Path(gate.__file__),Path(bundle['binary']),out/'driver.c',out/'driver.dylib']},scope='Full unchanged standalone fixture set re-executed on actual14664byte linked bundle at its actual symbol. Native fullCPU/2MBRAM and public stack, stable plus changing ordered accesses; same private-stack/code/entry exclusions as original helper gates. Other28bundle contracts/heap floor,IRQ/timing and physicalconsole remain separate checks.');save();gate.save(ROOT/'verification'/('native-fast-core-format-'+args.kind+'-current.json'),state);print(state['status'],len(rows),changing,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));save();raise
    finally:n.close()
if __name__=='__main__':main()
