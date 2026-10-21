"""Four original-facing native navigation roots; no prescribed helpers.

Valid stored jump-table targets only. Full returnedCPU/SR/banks/publicRAM and
ordered public data access are compared. Private frames/installation/returnPCs
are exclusions; changed code targets/faults/concurrency remain unproved.
"""
import argparse
import os
import subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_actor_navigation_engine_v2 as e
ROOT=e.ROOT;ND=e.ND


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=ND/'actor-navigation-reference-v2.c');args=ap.parse_args()
    out=ROOT/'verification/native-actor-navigation-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    run=subprocess.run(['make','-f',str(ND/'Makefile.actor-navigation'),'actor-navigation','BUILD='+str(out/'build'),'NAV_SOURCE='+str(args.source.resolve())],capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    binary=out/'build/actor-navigation.bin';elf=out/'build/actor-navigation.elf';payload=binary.read_bytes();nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert e.g.sha(ROOT/'render-assets/biwn-inventory-baseline.bin')=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    rows=e.vectors();rows=sum([[row for row in rows if row['entry']==entry][:args.limit]for entry in e.g.PATCH_WIDTHS],[])if args.limit else rows
    inputs=[Path(__file__),Path(e.__file__),Path(e.g.__file__),Path(e.g.navigation.__file__),args.source.resolve(),binary,elf,*[ND/name for name in['actor-navigation-native.h','actor-navigation-shim.S','actor-navigation.ld','Makefile.actor-navigation']],ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'scripts/check_biwn_scheduler.py'];hashes={str(p):e.g.sha(p)for p in inputs}
    state=dict(status='checking_native_original_ABI_navigation',directory=str(out),pid=os.getpid(),planned=len(rows),completed=0,binary=str(binary),ELF=str(elf),binary_bytes=len(payload),code_address=e.BASE,symbols=symbols,source_sha256=hashes,disc_integrated=False,new_predictions=0)
    def mark():e.g.save(out/'protocol.json',state);e.g.save(ROOT/'verification/native-actor-navigation-active.json',state)
    mark();e.g.save(out/'fixtures.json',rows);results=[];coverage=set();native=e.Native()
    try:
        for index,case in enumerate(rows):
            a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);diff=[key for key in['ram','registers','trace']if a[key]!=b[key]]
            if diff:e.g.save(out/'mismatch.json',dict(index=index,case=case,differences=diff,original_trace=a['trace'],candidate_trace=b['trace'],original_regs=a['registers'],candidate_regs=b['registers']));raise AssertionError('Native navigation ordered comparison failed')
            an=e.replay(native,snapshot,case,payload,symbols,False,a);bn=e.replay(native,snapshot,case,payload,symbols,True,b)
            ram=native.device.ram();context=e.SP-96-(8 if case['entry']==0xf368 else 0);shadow=[int.from_bytes(ram[context+4*i:context+4*i+4],'big')for i in range(18)];assert shadow[:15]==bn['registers'][:15]and shadow[15]==e.SP and(shadow[16]&0xffff)==bn['SR']and shadow[17]==case['entry'],'Returned logical C context differs from physical CPU'
            if an!=bn:e.g.save(out/'native-mismatch.json',dict(index=index,case=case,original=an,candidate=bn));raise AssertionError('Native navigation CPU/SR/banks mismatch')
            coverage.update(a['coverage']);results.append(dict(index=index,entry=case['entry'],original_steps=len(a['machine']),candidate_steps=len(b['machine']),original_depth=a['private_depth'],candidate_depth=b['private_depth']))
            if index%64==0:state['completed']=len(results);mark();print('Native navigation',index+1,'/',len(rows),flush=True)
        assert all(e.g.sha(p)==h for p,h in hashes.items());e.g.save(out/'results.json',results)
        state.update(status='terminal_native_navigation_preflight_pass'if args.limit else'terminal_native_navigation_prototype_pass',completed=len(results),cases=len(results),per_root_cases={hex(entry):sum(row['entry']==entry for row in rows)for entry in e.g.PATCH_WIDTHS},original_sites=sorted(coverage),max_private_depth=max(row['candidate_depth']for row in results),scope=__doc__);mark()
        if not args.limit:e.g.save(ROOT/'verification/native-actor-navigation-current.json',state)
        print(state['status'],len(rows),'bytes',len(payload),'depth',state['max_private_depth'])
    except BaseException as error:state.update(status='terminal_native_navigation_failed',error=repr(error),completed=len(results));mark();raise
    finally:native.close()


if __name__=='__main__':main()
