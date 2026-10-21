"""Preserve raw accepted local function;qualify its portable composition and bus order."""
import ctypes as c,hashlib,json,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compile_host(source,out,name):
 library=out/(name+'.dylib');p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(h.SRC),str(source),str(h.SRC/'helper-adapter.c'),'-o',str(library)],capture_output=True,text=True);(out/(name+'-compiler.log')).write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
 fn=c.CDLL(str(library)).biwn_geometry_helper_call;fn.argtypes=[c.POINTER(h.Bus),h.W8,c.POINTER(h.CPU),h.SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int;return fn,library
def main():
 run=read(V/'game-decomposed-clear-v3-current.json');assert run['new_predictions']==2 and run['rounds'][-1]['verified']and not run['default_promoted']
 for p,d in run['source_sha256'].items():assert sha(p)==d,p
 folder=Path(run['accepted_candidate']).parent;gate=read(folder/'checker-result.json');assert gate['completed']==772 and gate['counts']['0x10968']==260 and gate['guard_cases']==173
 for p,d in gate['source_sha256'].items():assert sha(p)==d,p
 out=V/'typed-local-clear-reviewed-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 target=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-clear-local-typed-v3';assert not target.exists();target.mkdir();raw=(folder/'response.txt').read_text();match=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',raw.strip());assert match;body=match.group(1);assert body.startswith('static void clear_records(')
 (target/'raw-response.txt').write_bytes((folder/'response.txt').read_bytes());(target/'clear-records.c').write_text(body+'\n');suffix=(h.SRC/'coordinator-reference.c').read_text();suffix=suffix[suffix.index('static void advance_texture'):];source=target/'composed-helpers.c';source.write_text('#include "../typed-deck-primitives-v1/typed-registers.h"\n'+body+'\n'+suffix)
 # The include location alone changes;confirm identical compiler input tokens.
 outputs=[]
 for name,path in [('as-run',Path(run['accepted_candidate'])),('portable',source)]:
  p=subprocess.run(['clang','-E','-P','-std=c99','-I',str(h.SRC),str(path)],capture_output=True,text=True);assert not p.returncode,p.stderr;output=out/(name+'.i');output.write_text(p.stdout);outputs.append(p.stdout)
 assert outputs[0]==outputs[1],'Portable include changed preprocessed C'
 candidate,candlib=compile_host(source,out,'local');reference,reflib=compile_host(h.SRC/'coordinator-reference.c',out,'reference');e=h.Engine();rows=[];budgets=[]
 try:
  for ram,initial,case in h.fixtures():
   if case['root']!=0x10968:continue
   a=e.translated(reference,ram,initial,case);b=e.translated(candidate,ram,initial,case)
   assert a[0]==b[0]and not a[-1]and not b[-1]and a[1]==b[1]and h.cpu_dict(a[2])==h.cpu_dict(b[2])and a[3]==b[3]and a[4]==b[4],case
   rows.append(dict(case=case['variant'],ordered_events=len(b[4]),ordered_trace_sha256=hashlib.sha256(json.dumps(b[4]).encode()).hexdigest(),CPU_RAM_order_match=True))
   if case['variant']in [1,2,3,256,257,258,259]:
    for budget in [0,1,63,64,65,127]:
     a=e.translated(reference,ram,initial,case,byte_budget=budget);b=e.translated(candidate,ram,initial,case,byte_budget=budget)
     assert a[0]==b[0]and not a[-1]and not b[-1]and a[1]==b[1]and h.cpu_dict(a[2])==h.cpu_dict(b[2])and a[4]==b[4],(case,budget)
     budgets.append(dict(case=case['variant'],budget=budget,status=b[0],CPU_RAM_order_match=True))
 finally:e.native.close()
 save(out/'ordered-cases.json',rows);save(out/'budget-cases.json',budgets)
 obj=out/'local-helpers-m68000.o';command=[str(ROOT/'tools/m68k-elf/bin/m68k-elf-gcc'),'-m68000','-msoft-float','-std=c99','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-I',str(h.SRC),'-c',str(source),'-o',str(obj)];p=subprocess.run(command,capture_output=True,text=True);(out/'target-compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 report=ROOT/'reports/Local Typed Register Author and Repair v3 Review.txt';report.write_text('LOCAL TYPED-REGISTER AUTHOR/REPAIR — SOURCE REVIEW\n\nDaily27B6bit model,reasoning off,1800output-token budget. Exact original10968disassembly and coordinator ABI/typed primitives supplied;target function body not supplied. Primitive layer passed8320individual original68000instruction comparisons before generation.\n\nAuthor44.29seconds:wrong service budget used in byte loop;originalCPU gate rejected. Repair45.85seconds:uses the supplied byte budget;unmodified function passes260complete10968cases. Composition with two retained coordinator functions passes772cases/80instruction locations/173error controls in total. Of the controls,131clear-function bus failures and one clear-byte-budget limit concern the new function. Other functions remain coordinator source.\n\nPortable relative-include composition has identical preprocessed C tokens to the as-run candidate. New260case ordered callback traces and42budget boundary comparisons match the retained contract. M68000object compiles but has not been executed or put in a disc. No weights or installed preview promoted. This is exposed development work on one complete helper,not an untouched holdout or general decompilation-quality score.\n\nExact prompts/rawresponses:'+run['directory']+'/prompts-and-responses.txt\nPortable accepted source:'+str(source)+'\n')
 paths=[Path(__file__),V/'game-decomposed-clear-v3-current.json',V/'typed-deck-primitives-v1-current.json',folder/'checker-result.json',source,target/'clear-records.c',target/'raw-response.txt',out/'as-run.i',out/'portable.i',out/'ordered-cases.json',out/'budget-cases.json',obj,candlib,reflib,report]
 state=dict(status='terminal_local_typed_repair_complete_helper_and_order_qualified_unpromoted',directory=run['directory'],review_directory=str(out),report=str(report),new_predictions=2,new_training=False,accepted_complete_function='0x10968',new_model_authored_functions=1,model='advertising-scholar',reasoning='off',output_budget=1800,author_seconds=44.29,repair_seconds=45.85,helper_cases=260,composition_cases=772,composition_error_cases=173,clear_bus_failure_cases=131,clear_budget_failure_cases=1,ordered_contract_cases=len(rows),extra_budget_order_cases=len(budgets),portable_source=str(source),raw_function=str(target/'clear-records.c'),raw_function_hand_edited=False,portable_preprocessed_tokens_identical=True,native_object_compiled=True,native_object_executed=False,native_disc_integrated=False,installed_preview_changed=False,model_weights_adopted=False,native_Chat_verified=False,compiler_command=command,scope='One complete local-authored helper with coordinator typed arithmetic/ABI and two retained helper bodies. Development task;original instruction/CPU/RAM/error and ordered callback contract gates preserved. No native execution,disc,fresh gameplay or broad generalization claim.',source_sha256={str(p):sha(p)for p in paths});save(out/'review.json',state);save(target/'provenance.json',state);save(V/'typed-local-clear-reviewed-v3-current.json',state);print(state['status'])
if __name__=='__main__':main()
