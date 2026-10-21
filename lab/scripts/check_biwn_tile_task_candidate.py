"""Compile exact local draft and compare guarded paths against originalM68000."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
parser=argparse.ArgumentParser();parser.add_argument('--candidate',type=Path);parser.add_argument('--author',type=Path);parser.add_argument('--report-pointer',type=Path,default=ROOT/'verification/tile-task-candidate-current.json');options=parser.parse_args();author=json.loads((options.author or ROOT/'verification/tile-task-local-author-current.json').read_text());candidate=options.candidate or Path(author['directory'])/'candidate.c';source=json.loads((ROOT/'verification/natural-world-entry-current.json').read_text())['captured'];RAM=(Path(source['directory'])/'RAM.bin').read_bytes();out=ROOT/'verification/BIWN-tile-task-candidate-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);lib=out/'libtile-task.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(candidate),'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);protocol=dict(candidate=str(candidate),candidate_sha256=sha(candidate.read_bytes()),author_protocol=str(Path(author['directory'])/'protocol.json'),compiler=cmd,model_fragment_edited_by_coordinator=False,coordinator_scaffolding_declared=bool(author.get('coordinator_prefix')),model_targeted_edits_declared=author.get('model_edits',[]),new_training=author.get('new_training',False),evaluation_phase=author.get('phase'),evaluation_case=author.get('case'))
if build.returncode:
 report=dict(status='candidate_compile_failed',directory=str(out),protocol=protocol,compiler_error=build.stderr,accepted=False);save(out/'report.json',report);save(options.report_pointer,report);print(report['status']);raise SystemExit(1)
helper=c.CDLL(str(lib));fn=helper.biwn_tile_task_cpu_run;fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];fn.restype=c.c_int
# Existing initialization-only library is not the candidate; CPU bus/oracle shared.
proof=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libentry-helpers.dylib',[]);rng=random.Random(0x21d1a);results=[];errors=[]
try:
 for entry in [0x21d1a,0x21d30]:
  for supervisor in [False,True]:
   for mode in [0,1,2,0x7fff,0x8000,0xffff]:
    for ccr in [0,1,2,4,8,16,23,31]:
     for mask in [0,0x700]:
      cpu=media.CPU();cpu.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];cpu.pc=entry;cpu.sr=(0x2000 if supervisor else 0)|mask|ccr;cpu.usp=0x1fe000 if supervisor else 0x1ff000;cpu.ssp=0x1ff000 if supervisor else 0x200000;ram=bytearray(RAM);ram[0x49c60:0x49c62]=mode.to_bytes(2,'big');ram[0x49c8c:0x49c8e]=(12).to_bytes(2,'big')
      runtime.reset(bytes(ram),0);runtime.seed_cpu(cpu);steps=0
      for _ in range(100):
       if runtime.cpu().pc==0xdf60:break
       runtime.core.m68k_execute(1);steps+=1
      else:raise AssertionError('native bound')
      expected=runtime.cpu();expected_RAM=runtime.device.ram();expected_hw=runtime.snapshot()['hardware'];runtime.reset(bytes(ram),0)
      def read(width):
       def cb(_,a,v):
        if not 0<=a<=0x200000-width:errors.append(('read_address',hex(a)));return 1
        v[0]=runtime.read(a,width);return 0
       return cb
      def write(width):
       def cb(_,a,v):
        if not 0<=a<=0x200000-width:errors.append(('write_address',hex(a)));return 1
        runtime.write(a,width,v);return 0
       return cb
      w=media.scheduler.cleanup.world;callbacks=[w.R8(read(1)),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4))];bus=media.Bus(*callbacks,w.CALL(),None,0);actual=media.CPU.from_buffer_copy(bytes(cpu));status=fn(c.byref(bus),c.byref(actual),100)
      if status!=6 or bytes(expected)!=bytes(actual)or expected_RAM!=runtime.device.ram()or expected_hw!=runtime.snapshot()['hardware']:
       mismatch=dict(case=len(results),entry=hex(entry),supervisor=supervisor,mode=mode,ccr=ccr,mask=mask,C_status=status,native_CPU=media.scheduler.cpu_dict(expected),C_CPU=media.scheduler.cpu_dict(actual),RAM_equal=expected_RAM==runtime.device.ram(),hardware_equal=expected_hw==runtime.snapshot()['hardware'],bus_errors=errors);save(out/'mismatch.json',mismatch);raise AssertionError(str(out/'mismatch.json'))
      results.append(dict(entry=hex(entry),mode=mode,supervisor=supervisor,ccr=ccr,mask=mask,native_instructions=steps))
 for budget,entry,mode,tile,expected_status in [(0,0x21d1a,1,12,1),(1,0x21d1a,1,12,4),(5,0x21d1a,1,12,4),(100,0x21d1a,1,11,7),(100,0x212fe,1,12,7)]:
  ram=bytearray(RAM);ram[0x49c60:0x49c62]=mode.to_bytes(2,'big');ram[0x49c8c:0x49c8e]=tile.to_bytes(2,'big');runtime.reset(bytes(ram),0);s=media.CPU();s.registers[15]=s.usp=0x1ff000;s.ssp=0x200000;s.pc=entry;s.sr=0x10;before=bytes(s);status=fn(c.byref(bus),c.byref(s),budget);assert status==expected_status and bytes(s)==before,(budget,entry,tile,status,expected_status)
 report=dict(status='guarded_tile_task_candidate_native_CPU_RAM_hardware_match',directory=str(out),protocol=protocol,cases=len(results),declared_host_error_checks=5,error_CPU_state_unchanged=True,disabled_mode_and_tile12_only=True,unsupported_tiles_unverified=True,accepted_for_standalone_scope=True,accepted_for_live_scope=False,whole_game_complete=False);save(out/'cases.json',results);save(out/'report.json',report);save(options.report_pointer,report);print(report['status'],len(results),flush=True)
except BaseException as e:
 report=dict(status='candidate_native_check_failed',directory=str(out),protocol=protocol,cases_passed=len(results),error=repr(e),accepted=False);save(out/'report.json',report);save(options.report_pointer,report);raise
finally:runtime.oracle.close()
