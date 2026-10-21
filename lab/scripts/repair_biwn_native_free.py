"""Bounded local code-only translation after medium reasoning budget exhausted."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys,os,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    failed=json.loads((ROOT/'verification/native-free-reasoning-budget-review.json').read_text());out=ROOT/'runs'/('local-native-free-guided-'+lab.stamp());out.mkdir();print(out,flush=True)
    header=(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/free-native.h').read_text()
    system='You are local guided C Author. Return one complete C99 file in one c code fence, include "free-native.h", implement only void biwn_native_free_body(uint32_t *r). No asm, libc, mutable globals, added guards or tests claims. Follow supplied complete algorithm literally, using goto labels if clearer. This is coordinator-guided translation, not autonomous decompilation.'
    user='Coordinator header:\n'+header+'''\nUse locals d0=r[0],d1=r[1],a0=r[8],a1=r[9],sp=r[15],sr=r[16],X=sr&16u; uint32_t block,handle,v,t,head.
Original public prologue: FW32(sp-4u,r[11]);FW32(sp-8u,r[10]);handle=FR32(sp+4u). If handle==0 go restore. Read FR32(handle);if zero go restore. block=FR32(handle)-8u (separate reread). d1=FR32(block);v=FR32(0x112d64u);FW32(0x112d64u,biwn_free_add(v,d1,&X)).
Read FR32(0x112d60u). If zero:FW32(0x112d60u,block);biwn_native_free_clear32(block+4u);biwn_native_free_clear32(block+8u);goto finish_handle.
Read head=FR32(0x112d60u) AGAIN. If block<head unsigned:
 a0=block+FR32(block) (address addition, no X change). Read head=FR32(0x112d60u) AGAIN.
 if a0==head:FW32(block+4u,FR32(a0+4u));d1=FR32(a0);v=FR32(block);FW32(block,biwn_free_add(v,d1,&X));read FR32(a0+4u);if nonzero {a0=FR32(a0+4u) AGAIN;FW32(a0+8u,block);}
 else:FW32(block+4u,FR32(0x112d60u));a0=FR32(0x112d60u) AGAIN;FW32(a0+8u,block).
 Then biwn_native_free_clear32(block+8u);FW32(0x112d60u,block);goto finish_handle.
If block>=head: a1=FR32(0x112d60u) AGAIN. Read FR32(a1+4u);if zero goto tail.
scan: read v=FR32(a1+4u). If block>=v unsigned goto advance.
 a0=block+FR32(block) (address addition, no X). Read v=FR32(a1+4u) AGAIN.
 if a0==v:
  t=FR32(a0+4u);FW32(block+4u,t);if t!=0 {a0=FR32(block+4u);FW32(a0+8u,block);}
  a0=FR32(a1+4u);d1=FR32(a0);v=FR32(block);FW32(block,biwn_free_add(v,d1,&X));
 else:FW32(block+4u,FR32(a1+4u));a0=FR32(a1+4u) AGAIN;FW32(a0+8u,block).
 FW32(block+8u,a1);d0=a1;v=FR32(a1);d0=biwn_free_add(d0,v,&X).
 If block==d0:
  d1=FR32(block);v=FR32(a1);FW32(a1,biwn_free_add(v,d1,&X));t=FR32(block+4u);FW32(a1+4u,t);if t!=0 {a0=FR32(block+4u) AGAIN;FW32(a0+8u,a1);}
 Else FW32(a1+4u,block).
 goto finish_handle.
advance: a1=FR32(a1+4u);read FR32(a1+4u);if nonzero goto scan. Otherwise fall through to tail.
tail: d0=a1;v=FR32(a1);d0=biwn_free_add(d0,v,&X).
 If block==d0:d1=FR32(block);v=FR32(a1);FW32(a1,biwn_free_add(v,d1,&X)).
 Else:FW32(a1+4u,block);biwn_native_free_clear32(block+4u);FW32(block+8u,a1).
finish_handle: biwn_native_free_clear32(handle).
restore: r[10]=FR32(sp-8u);r[11]=FR32(sp-4u);r[0]=d0;r[1]=d1;r[8]=a0;r[9]=a1;r[16]=(sr&0xffe0u)|X|4u;return.
No other frame cells change. Every FR32 occurrence above is a fresh volatile read in that exact relative order. Never replace a read used only as a nonzero test with a cached preceding value. Literal labels are legal C. No unreachable "cleanup" rewrites or automatic invariants may simplify these original flows. Calls to CLR helper have private hardware register clobbers, not changes to your semantic a0 variable.\n'''
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),previous_reasoning_budget_failure=failed,coordinator_supplied_complete_algorithm=True,reasoning='off',new_training=False,same_weights=True,independent_model_validation=False,native_Chat=False,source_accepted=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-free-guided-active.json',state)
    mark();(out/'prepared-author.json').write_text(json.dumps({'system':system,'user':user,'reasoning':'off','max_output_tokens':4200},indent=2));(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\n')
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game');lab.CONFIG['models']['game']['reasoning']='off';state['status']='guided_author_running';mark();a=lab.generate('game',system,user,4200)
        save(out/'response.json',a)
        with(out/'prompts-and-responses.txt').open('a')as f:f.write('RESPONSE\n'+a['text'])
        blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
        p=out/'free-native.c';p.write_text(blocks[0].strip()+'\n');state.update(status='terminal_guided_free_draft_pending_native_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,reported_seconds=a['seconds'],usage=a['usage'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-free-current.json',state);print(state['status'],a['seconds'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
