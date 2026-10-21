"""Classify live free returns and OP writeback progress; preserve failed full replay."""
from pathlib import Path
from datetime import datetime,timezone
import json,struct,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 rp=ROOT/'verification/native-free-live-returns-current.json';live=json.loads(rp.read_text());assert live['status']=='terminal_live_free_entries_returns_captured_pending_analysis';directory=Path(live['directory']);control=json.loads(Path(live['control_proof']).read_text());assert sha(live['control_proof'])==live['control_proof_sha256'];cd=Path(control['directory']);fp=ROOT/'verification/native-free-fixed-route-current.json';fixed=json.loads(fp.read_text());fd=Path(fixed['directory'])
 reference_rows={'original_free':json.loads((cd/'initializer_only/report.json').read_text())['frames'],'source_free':json.loads((fd/'native25_fixed/report.json').read_text())['frames'][:6400]}
 for lane in live['lanes']:
  rows=json.loads((directory/lane/'report.json').read_text())['frames'];assert rows==reference_rows[lane],('Observer changed frame rows',lane)
  assert all(not x[k]for x in live['results'][lane]['cases']for k in ['outside_steps','high_sr_steps','task_change_steps','overlapping_entries'])
 mask=0xfffff80000ffc000;phrases=[0x776f0,0x77710,0x77720];cases=[];scratch=[];artifacts=[]
 for i in range(2):
  metadata={lane:live['results'][lane]['cases'][i]for lane in live['lanes']};s=metadata['source_free'];scratch.append((s['min_sp'],s['entry_sp']-8));u=lambda b,a:int.from_bytes(b[a:a+4],'big');images={};cpus={}
  for phase in ['entry','return']:
   images[phase]={};cpus[phase]={}
   for lane in live['lanes']:
    prefix=directory/lane/f'gameplay-events.bin.live-{i}-{phase}';ram=Path(str(prefix)+'-RAM.bin');cpu=Path(str(prefix)+'-CPU.bin');artifacts += [ram,cpu];images[phase][lane]=ram.read_bytes();cpus[phase][lane]=struct.unpack('<19IH2x',cpu.read_bytes())
   assert cpus[phase]['original_free']==cpus[phase]['source_free'],(i,phase,'CPU')
  a=images['return']['original_free'];b=images['return']['source_free'];SP=s['entry_sp'];assert a[SP-8:SP]==b[SP-8:SP]
  excluded=lambda address:0x1545c<=address<0x15464 or any(lo<=address<hi for lo,hi in scratch)
  differences=[address for address,(x,y)in enumerate(zip(a,b))if x!=y and not excluded(address)]
  assert differences and all(any(base<=address<base+8 for base in phrases)for address in differences),(i,differences[:32])
  if i==0:
   left=images['entry']['original_free'];right=images['entry']['source_free'];assert all(x==y or 0x1545c<=j<0x15464 for j,(x,y)in enumerate(zip(left,right)))
  decoded=[]
  for base in phrases:
   old=int.from_bytes(a[base:base+8],'big');new=int.from_bytes(b[base:base+8],'big');p1=int.from_bytes(a[base+8:base+16],'big');assert a[base+8:base+16]==b[base+8:base+16]
   height=lambda x:(x&0xffc000)>>14;data=lambda x:(x&0xfffff80000000000)>>40;stride=(p1&0xffc0000)>>15;delta=height(old)-height(new)
   assert old&7==new&7==0 and ((old^new)&~mask)==0 and delta>0 and data(new)-data(old)==delta*stride
   decoded.append(dict(address=hex(base),object_type=0,previous_height=height(old),new_height=height(new),extra_writeback_lines=delta,previous_data=data(old),new_data=data(new),data_stride=stride,only_object_processor_writeback_bits_changed=True,advance_equals_lines_times_stride=True))
  assert s['task']+38<=s['min_sp']<=SP<=s['task']+1024
  cases.append(dict(case=i,frame=s['frame'],returned_CPU_equal=True,original_public8save_bytes_equal=True,initial_CPU_equal=True,public_RAM_return_different_bytes=len(differences),public_RAM_return_difference_addresses=[hex(x)for x in differences],OP_writeback_decode=decoded,no_observed_CPU_interrupt_or_task_switch=True,original_live_metadata=metadata['original_free'],source_live_metadata=s))
 source=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/src/tom/op.c';display=ROOT/'projects/black-ice-white-noise/restoration/biwn_display_list.c';cpu_source=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/src/m68000/m68kinterface.c'
 report=dict(status='terminal_live_free_CPU_returns_match_OP_progress_differs',recorded_at=datetime.now(timezone.utc).isoformat(),cases=cases,read_only_observer_repeats_both6400frame_profiles_exactly=True,first_entry_CPU_RAM_equal_except_redirect=True,interpretation='No observed CPU interrupt, task switch, outside-function instruction or nested free across these first two live calls. Actual returned full CPU and original8save bytes match, but sharedRAM does not: after excluding cumulative private scratch, only three bitmap-object first phrases differ. Their fields match ObjectProcessorheight decrements/data-stride advancement by two then three extra scanlines under the longer compiled C routine. This supports a scheduling/device-progress timing mechanism in the retained emulator, rather than an observed caller-register error or task-stack overflow on these two inputs. Writer identity is inferred from exact OP writeback bit/stride semantics and source; no bus-writer watch was installed. Later calls, general IRQ/device concurrency and physical hardware are unproven. Equal29783frame fixed-input equivalence remains rejected.',fixed_input_equivalence=False,physical_console_verified=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),source,display,cpu_source]})
 out=ROOT/'verification/native-free-live-return-analysis'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'analysis.json',report);deps={};snapshots={}
 def pin(p,snapshot=False):
  p=Path(p).resolve();assert p.is_relative_to(ROOT);rel=str(p.relative_to(ROOT));digest=sha(p)
  if snapshot:
   dest=out/(hashlib.sha256(rel.encode()).hexdigest()[:12]+'-'+p.name)
   if not dest.exists():shutil.copy2(p,dest)
   assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;snapshots[rel]=str(dest.relative_to(ROOT))
  else:deps[rel]=digest
 for p in [rp,fp,*[Path(p)for p in report['source_sha256']]]:pin(p,True)
 for p,d in live['source_sha256'].items():assert sha(p)==d;pin(p,True)
 for lane in live['lanes']:
  for p in (directory/lane).glob('*'):
   if p.is_file()and(p.suffix in ['.bin','.json','.s16le']):pin(p)
 for p in artifacts:pin(p)
 pin(out/'analysis.json');parent=ROOT/'verification/native-free-prefix-isolation-current.json';manifest=dict(status='published_live_free_return_OP_timing_observation',recorded_at=report['recorded_at'],directory=str(out),analysis=report,parent_prefix_isolation_sha256=sha(parent),dependencies_sha256=deps,source_snapshots=snapshots,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-free-live-return-analysis-current.json',manifest);print(json.dumps({'status':report['status'],'directory':str(out),'case0_extra_lines':2,'case1_extra_lines':3,'dependencies':len(deps)}),flush=True)
if __name__=='__main__':main()
