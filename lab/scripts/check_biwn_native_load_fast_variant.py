"""Exact loader variants versus original or explicitly word-repaired target code."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,json,subprocess,os,hashlib
import check_biwn_native_resource_load as base
from check_biwn_native_button_digit import ROOT,sha,save

FLAGS='-m68000 -msoft-float -std=c99 -Os -ffreestanding -ffunction-sections -fdata-sections -fno-common -fno-pie -fno-pic -fno-stack-protector'
def vectors(word):
 cases=base.vectors()
 if not word:return cases
 for source_kind,delta,description in [('copy_ready',2,'halfword_marker'),('copy_ready',-30,'halfword_at_start'),('null_handle',2,'halfword_null_handle'),('marker_end_boundary',-2,'halfword_end_boundary'),('partial_marker',2,'halfword_partial_marker')]:
  for original in base.vectors():
   if original['kind']!=source_kind:continue
   c=copy.deepcopy(original);c['scan_case']=description;c['initial']=[[a+delta if 0x1c0000<=a<0x1c8400 else a,w,v]for a,w,v in c['initial']];cases.append(c)
 return cases

def main():
 p=argparse.ArgumentParser();p.add_argument('--word-scan',action='store_true');p.add_argument('--optimization',choices=['O2','Os'],default='Os');p.add_argument('--limit',type=int);p.add_argument('--target-proof',type=Path);p.add_argument('--label');args=p.parse_args()
 label=args.label or('native-load-word-fast-os'if args.word_scan else'native-load-original-os')
 nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';source=nd/('resource-load-word-scan-fast.c'if args.word_scan else'resource-load-reference.c');out=ROOT/'verification'/label/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),word_scan=args.word_scan,optimization=args.optimization,limit=args.limit,controlled_component_pass=False,whole_game_complete=False,game_frames=0)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(label+'-active.json'),state)
 mark()
 try:
  build=out/'build';cmd=['make','-f','Makefile.resource-load','resource-load','BUILD='+str(build),'LOAD_SOURCE='+str(source)]
  if args.optimization=='Os':cmd+=['CFLAGS='+FLAGS]
  run=subprocess.run(cmd,cwd=nd,capture_output=True,text=True);(out/'make.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
  prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
  for stem in ['native-resource-load','load-providers']:
   for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
    t=line.split()
    if len(t)==3:symbols[t[2]]=int(t[0],16)
  binary=build/'native-resource-load.bin';payload=binary.read_bytes();target_paths=[]
  if args.target_proof:
   tp=args.target_proof.resolve();target=json.loads(tp.read_text());assert sha(target['binary'])==target['binary_sha256'];binary=Path(target['binary']);payload=binary.read_bytes();symbols.update(target['symbols']);base.BASE=target['resident_base'];target_paths=[tp];state.update(target_proof=str(tp),target_proof_sha256=sha(tp),payload_base=base.BASE)
  save(out/'symbols.json',symbols);providers=(build/'load-providers.bin').read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';image=bytearray(baseline.read_bytes());paths=[Path(__file__),Path(base.__file__),source,baseline,*target_paths,*[nd/n for n in ['resource-load-native.h','resource-load-shim.S','resource-load-providers.S','resource-load.ld','Makefile.resource-load','Makefile']]]
  if args.word_scan:
   rp=ROOT/'verification/native-word-scan-build-current.json';repair=json.loads(rp.read_text());rb=Path(repair['binary']);assert sha(rb)==repair['binary_sha256'];fragment=rb.read_bytes();assert len(fragment)==18 and fragment.hex()==repair['repaired_fragment'];image[0x1b0ee:0x1b100]=fragment;paths+=[rp,rb]
  patched_baseline=out/'reference-RAM.bin';patched_baseline.write_bytes(image);asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000','--start-address=0x1b044','--stop-address=0x1b154',str(patched_baseline)],text=True);(out/'reference-loader.asm').write_text(asm)
  image[base.PROVIDER:base.PROVIDER+len(providers)]=providers
  for addr,(name,_)in base.HELPERS.items():image[addr:addr+8]=b'\x4e\xf9'+symbols['load_provider_'+name].to_bytes(4,'big')+b'\x4e\x71'
  candidate=bytearray(image);candidate[base.BASE:base.BASE+len(payload)]=payload;candidate[base.ENTRY:base.ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_resource_load'].to_bytes(4,'big')+b'\x4e\x71'
  cases=vectors(args.word_scan)
  if args.limit:cases=[next(c for c in cases if c.get('scan_case',c['kind'])==kind)for kind in dict.fromkeys(c.get('scan_case',c['kind'])for c in cases)][:args.limit]
  save(out/'fixtures.json',cases);n=base.sched.Native();rows=[];coverage=set();traces=0
  try:
   for i,c in enumerate(cases):
    left=base.native(n,image,c,len(payload),len(providers),True);right=base.native(n,candidate,c,len(payload),len(providers),False);norm=base.normalize(right[0],left[0],len(payload))
    if left[1]!=right[1]or left[3]!=right[3]or norm!=left[0]:
     save(out/'mismatch.json',dict(case=i,parameters=c,original_CPU=left[1],compiled_CPU=right[1],original_calls=left[3],compiled_calls=right[3],RAM_differences=[dict(address=hex(j),original=x,compiled=y)for j,(x,y)in enumerate(zip(left[0],norm))if x!=y][:128]));raise AssertionError(str(out/'mismatch.json'))
    assert int.from_bytes(right[0][0x47b80:0x47b82],'big')==(1 if c['kind']=='null_handle'else 0)
    assert int.from_bytes(right[0][0x118004:0x118006],'big')==(0x1357 if c['kind']in ['null_handle','copy_no_ready']else 1)
    if c.get('scan_case'):assert int.from_bytes(right[0][0x13401c:0x134020],'big')==1,'Halfword marker should be found on first read'
    if c['trace']:
     a=base.trace(image,c,len(payload),len(providers),True);b=base.trace(candidate,c,len(payload),len(providers),False)
     if a[1:]!=b[1:]or base.normalize(b[0],a[0],len(payload))!=a[0]:save(out/'trace-mismatch.json',dict(case=i,original=a[1:],compiled=b[1:]));raise AssertionError(str(out/'trace-mismatch.json'))
     traces+=1
    coverage.update(left[2]);rows.append(dict(case=i,kind=c['kind'],scan_case=c.get('scan_case'),sr=c['sr'],CPU=right[1],helper_calls=right[3],minimum_compiled_SP=right[4],original_cycles=left[5],compiled_cycles=right[5],ordered_trace_checked=c['trace']))
    if i%64==0:state['completed']=len(rows);mark();print('Variant',len(rows),'/',len(cases),flush=True)
  finally:n.close()
  save(out/'results.json',rows);expected={int(line.split(':',1)[0].strip(),16)for line in asm.splitlines()if ':'in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()}
  if not args.limit:assert expected<=coverage,sorted(hex(x)for x in expected-coverage)
  state.update(status='terminal_loader_variant_preflight_pass'if args.limit else'terminal_loader_variant_full_CPU_RAM_helpers_ordered_access_pass',controlled_component_pass=not args.limit,native_cases=len(rows),trace_cases=traces,reference_instruction_coverage=[len(expected&coverage),len(expected)],binary_bytes=len(payload),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),symbols=symbols,payload_base=base.BASE,build_command=cmd,source_sha256={str(p):sha(p)for p in paths},scope='Exact compiled loader variant vs original or explicitly repaired reference. FullCPU/publicRAM/original24savebytes/helperentryD/A/SR/SP/args and selected orderedaccess checked. Original780matrix plus320halfword/partial/boundary cases when repaired. TestCPUproviders remain; no realCD/IRQ/game/physical proof.')
  mark();save(ROOT/'verification'/(label+'-current.json'),state);print(state['status'],len(rows),traces,len(payload),state['reference_instruction_coverage'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
