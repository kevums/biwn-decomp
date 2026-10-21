"""Qualify the additive read-only trace and bind unchanged acceptance monitors."""
import ctypes as c,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import shared_deck_faces_handoff_observer_v1 as composed
import shared_deck_faces_observer_v1 as prior
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';build=read(v/'native-Deck-faces-disc-build-v1-current.json');parent=read(v/'native-Deck-coordinate-disc-build-current.json')
    text,old=composed.observer_source(build,parent);baseline,_=prior.observer_source(build,parent)
    positive=read(v/'faces-observer-qualified-v1-current.json');assert sha(positive['observer'])==__import__('hashlib').sha256(baseline.encode()).hexdigest()
    for lo,hi in [('static unsigned g5_gpu_pending[101]','static const uint32_t o6_inner_returns'),('/* O6_WATCHER_BEGIN:','/* O6_WATCHER_END */'),('static unsigned native_deck_regions(','static uint8_t deck_used')]:
        assert text[text.index(lo):text.index(hi,text.index(lo))]==baseline[baseline.index(lo):baseline.index(hi,baseline.index(lo))]
    out=v/'faces-handoff-observer-qualification-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=out/'observer.c';source.write_text(text);library=out/'observer.dylib'
    direction=old.with_name('direction-shadow-model.c');p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),str(direction),'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    extra=text[text.index('/* Read-only diagnostic: keypad'):]
    stub='''#include <stdint.h>
#include <stdio.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static uint32_t frame;static uint8_t memory[0x200000];
static uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)memory[a]<<8)|memory[a+1];}
static void read_cpu(struct cpu *s){s->r[0]=0x12340000u;s->r[1]=16u;}
static void handoff_retained_set_frame(uint32_t v){frame=v;}
static int32_t handoff_retained_observe(uint32_t pc){(void)pc;return 77;}
uint8_t *fixture_memory(void){return memory;}
'''
    fixture=out/'fixture.c';fixture.write_text(stub+extra);libpath=out/'fixture.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(fixture),'-o',str(libpath)],capture_output=True,text=True);assert p.returncode==0,p.stderr
    lib=c.CDLL(str(libpath));lib.fixture_memory.restype=c.POINTER(c.c_uint8);memory=(c.c_uint8*0x200000).from_address(c.addressof(lib.fixture_memory().contents));lib.handoff_dump.argtypes=[c.c_char_p];lib.observe.argtypes=[c.c_uint32];lib.set_frame.argtypes=[c.c_uint32]
    def put(a,n,value):memory[a:a+n]=value.to_bytes(n,'big')
    put(0xc0920,4,0xc0928);put(0x49bac,4,16);put(0x49ba4,4,16);put(0x49d54,2,9);put(0x49d56,2,9);put(0x403d6,2,2);put(0x49c60,2,1);put(0x778cc,4,123)
    before=bytes(memory);lib.set_frame(23999);assert lib.observe(0x1b718)==77;lib.handoff_dump(str(out/'before-window.json').encode());assert not read(out/'before-window.json')['events']
    lib.set_frame(24000);assert lib.observe(0x1b718)==77;lib.handoff_dump(str(out/'legal.json').encode());data=read(out/'legal.json');assert data['overflow']==0 and len(data['events'])==2
    assert data['events'][1]['held']==16 and data['events'][1]['inventory_selected']==9 and data['events'][1]['D0']==0x12340000 and data['events'][1]['D1']==16
    for _ in range(8192):assert lib.observe(0x1b718)==77
    lib.handoff_dump(str(out/'overflow.json').encode());assert read(out/'overflow.json')['overflow']>0
    assert before==bytes(memory),'Trace mutated guest memory'
    paths=[Path(__file__),Path(composed.__file__),Path(prior.__file__),Path(composed.__file__).with_name('faces_handoff_trace_v1.inc.c'),source,library,fixture,libpath,out/'before-window.json',out/'legal.json',out/'overflow.json',v/'faces-observer-qualified-v1-current.json',v/'outer-faces-observer-qualified-v1-current.json',v/'shared-Deck-region-check-faces-v1-current.json']
    state=dict(status='terminal_readonly_handoff_trace_and_unchanged_monitors_qualified',directory=str(out),observer=str(source),observer_sha256=sha(source),base_monitors_byte_identical=True,read_only_fixture=True,original_acceptance_fault_controls=[50,18,88],source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Trace fixture validates frame guard,register/RAM capture,pass-through return,overflow recording and no guest-memory writes. Actual same-image nonintrusion remains required in the diagnostic route.')
    save(out/'review.json',state);save(v/'faces-handoff-observer-qualified-v1-current.json',state);print(out,state['status'],flush=True)
if __name__=='__main__':main()
