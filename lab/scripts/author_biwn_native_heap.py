"""Two guided local C Author passes and one compact same-weight review."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat,binary_tools
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('local-native-heap-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';header=(native/'heap-native.h').read_text();image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    def listing(lo,hi):
        ins,_=binary_tools.m68k_instructions(image[lo:hi],lo);return'\n'.join(f"{x['address']:06x} {x['assembly']}"for x in ins)
    system='You are local Author. Return exactly one complete freestanding C99 file in one c code fence, including "heap-native.h". No inline assembly, structs, callbacks, main, new guards/budgets or mutable globals. Use the coordinator frame, volatile HR/HW and flag/dependency helpers below. Do not claim tests. This is guided translation, not autonomous discovery.'
    common='Coordinator header (supplied, not your authorship):\n'+header+'\nC changes ONLY r[0],r[1],r[8],r[9],r[16]. Preserve other frame cells. Full uint32 arithmetic wraps. Signed comparisons use (int32_t) only for comparison, never signed addition/subtraction. HR/HW target widths/order matter. Private frame stores may be ordinary. Follow supplied algorithm exactly.\n'
    allocate=common+'''Implement void biwn_native_heap_allocate_body(uint32_t *r).
Read requested=HR(r[15]+4). Set sum=requested+15u, need=sum&0xfffffff8u, r[0]=sum; update only Xbit in r[16] to (sum<requested ?16:0). Keep incoming r[1]/r[8] until logic changes them. Read r[9]=HR(0x112D60). Let from_head=1, compacted=0.
check: read block size HR(r[9]); if signed need>size:
 if compacted: biwn_heap_zero_result(r);return.
 Otherwise set r[8]=r[9]; r[9]=HR(r[9]+4). While r[9]!=0(full32 pointer), read HR(r[9]) and if signed need<=it set from_head=0 and go fit. If too small, r[8]=r[9]; r[9]=HR(r[9]+4).
 If no next block: call biwn_native_heap_compact_capture(r) exactly once. This helper seeds/captures original caller-saved regs/CCR and calls15200, which is redirected to the newly compiled compactor in coupled tests. Then r[9]=HR(0x112D60);from_head=1;compacted=1;goto check. Need remains original aligned value; do not recompute from changed r[0].
fit: read HR(r[9]) AGAIN, compute left=value-need wrapping. If (int32_t)left>15: HW(r[9],left);r[9]+=left;HW(r[9],need). Else read next=HR(r[9]+4); if from_head HW(0x112D60,next), else HW(r[8]+4,next).
Search handles: index=255. Each iteration set r[1]=index*4u; r[8]=0x112960u+r[1]; read HR(r[8]). If zero, success. If occupied and index==0, set r[8]=0x11295Cu (original final SUBQ address), set Xbit16 in r[16], biwn_heap_zero_result(r);return. Else decrement index and repeat.
success: HW(0x112960u+r[1],r[9]+8u);r[0]=0x112960u+r[1];HW(r[9]+4,r[0]);allocated=HR(r[9]);before=HR(0x112D64);after=before-allocated;HW(0x112D64,after);r[16]=(r[16]&0xffe0u)|biwn_heap_sub_ccr(before,allocated,after);return. Do not reject wrapped sizes, skip original rereads, undo block writes on handle exhaustion or invent validation.
Original listing:\n'''+listing(0x152a2,0x1545c)
    compact=common+'''Implement void biwn_native_heap_compact_body(uint32_t *r).
Read destination=HR(0x112D60); source=destination+HR(destination); set r[0]=0x1BFFFF. Unsigned pointer comparisons throughout. If source>0x1BFFFF goto tail. Exact labels/flow below preserve rereads; use gotos if clearer. No uninitialized size use at tail.
move_block: size=HR(source); call biwn_native_heap_copy_capture(r,source,destination,size). This calls original E3E0 real blitter copy and captures D0/D1/A0/A1/CCR. Then r[8]=HR(destination+4);r[9]=destination+8;HW(r[8],r[9]);source+=HR(destination). If source>0x1BFFFF goto next_destination.
Read HR(source+4); if >=BIWN_HEAP_FLOOR goto skip_block. Read HR(source+4) AGAIN; if nonzero goto next_destination. source+=HR(source); if source>0x1BFFFF goto next_destination. Read HR(source+4);if >=BIWN_HEAP_FLOOR goto skip_block. Read HR(source+4) AGAIN;if nonzero goto next_destination.
skip_block: source+=HR(source);if source>0x1BFFFF goto next_destination. Read HR(source+4);if >=BIWN_HEAP_FLOOR goto skip_block. Read HR(source+4) AGAIN;if zero goto skip_block.
next_destination: destination+=size; if source<=0x1BFFFF goto move_block.
tail: r[9]=0x1C0000u-destination;HW(destination,r[9]);call biwn_native_heap_clear_tail(destination) for exact original CLR.L reads/writes at+4,+8;HW(0x112D60,destination). Final original CCR comes from MOVE.L destination to global: r[16]=(r[16]&0xfff0u)|(destination==0?4u:0u)|(destination&0x80000000u?8u:0u). This preserves the X returned by copy, or input X when no copy. D0/D1 remain copy-captured, or incoming D1/constant1BFFFF on no move. r[8] stays last handle read or incoming A0 when no move. Do not set it to a C pointer helper's clobbered hardware register. Do not cache target rereads or inline memcpy/blitter effects.
Original listing:\n'''+listing(0x15200,0x152a2)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),roles=[],coordinator_supplied_full_algorithms_frame_flags_and_native_dependencies=True,native_Chat=False,new_training=False,same_weights=True)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-heap-active.json',state)
    mark();transcript='';sources={}
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game')
            for name,request in [('allocate',allocate),('compact',compact)]:
                state['status']='author_'+name+'_running';mark();a=lab.generate('game',system,request,3300);save(out/(name+'-response.json'),a)
                blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
                p=out/('heap-'+name+'-native.c');p.write_text(blocks[0].strip()+'\n');sources[name]=dict(path=str(p),sha256=binary_tools.sha(p));state['roles'].append(dict(role='local Author '+name,seconds=a['seconds']));transcript+='AUTHOR '+name+' SYSTEM\n'+system+'\nUSER\n'+request+'\nRESPONSE\n'+a['text']+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
            rs='You are local Reviewer, same weights not independent verification. Return compact JSON with booleans allocator_signed_fit, allocator_X_and_exhaustion, compactor_unsigned_skip, target_rereads, explicit_native_copy_dependency, plus issues array(max3shortitems). No prose, code or test claims. Under120words.'
            ru=allocate+'\nALLOCATOR C\n'+Path(sources['allocate']['path']).read_text()+'\nCOMPACTOR PLAN\n'+compact+'\nCOMPACTOR C\n'+Path(sources['compact']['path']).read_text();state['status']='reviewer_running';mark();b=lab.generate('game',rs,ru,550);save(out/'reviewer-response.json',b);state['roles'].append(dict(role='local Reviewer',seconds=b['seconds']));transcript+='REVIEWER SYSTEM\n'+rs+'\nUSER\n'+ru+'\nRESPONSE\n'+b['text']+'\n';(out/'prompts-and-responses.txt').write_text(transcript)
        state.update(status='terminal_native_heap_drafts_pending_CPU_bus_gates',sources=sources,raw_model_C_unchanged=True,reviewer_response=b['text'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-heap-current.json',state);print(state['status'],state['roles'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
