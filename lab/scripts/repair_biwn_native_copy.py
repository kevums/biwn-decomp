"""One guided local rewrite after failed original-CPU preflight."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys,os,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    previous=json.loads((ROOT/'verification/local-native-copy-current.json').read_text());out=ROOT/'runs'/('local-native-copy-repair-'+lab.stamp());out.mkdir();print(out,flush=True)
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    system='You are local Repair Author. Return exactly one complete C99 file in one c code fence, including "copy-native.h" and only void biwn_native_copy_body(uint32_t *r). No asm, libc, mutable globals, new guards or test claims. Follow the coordinator algorithm below literally. This is a guided rewrite, not autonomous discovery.'
    user='Updated coordinator header:\n'+(native/'copy-native.h').read_text()+'''\nThe failed draft swapped the register mapping, ignored CCR, repeated leading writes/saves, inverted the command choice and used a wrong count flag. Discard its code. The same-weight review was wrong. Implement this complete algorithm using plain uint32_t source,destination,count variables, NOT invented register mappings.
sp=r[15];sr=r[16]. Read arg0=CR32(sp+4),then arg1=CR32(sp+8),then count=CR32(sp+12). If r[17]==0:source=arg0,destination=arg1. Otherwise source=arg1,destination=arg0. result=r[0] (incoming D0).
If count==0: write r[1]=0, r[8]=destination,r[9]=source,r[16]=(sr&0xffe0u)|(sr&16u)|4u; return without changing r[0] or r[2..4]. No copy/MMIO/stack saves.
Else if ((count-128u)&0x80000000u)!=0: do {byte=CR8(source);source+=1u;CW8(destination,byte);destination+=1u;count-=1u;}while(count!=0). After loop write r[1]=0,r[8]=destination,r[9]=source,r[16]=(sr&0xffe0u)|4u; return, leaving r[0]/r[2..4] unchanged.
Otherwise large path: CW32(0xf02204u,0x4020u);CW32(0xf02228u,0x4020u);CW32(sp-4u,r[2]);CW32(sp-8u,r[3]);CW32(sp-12u,r[4]); do these ONCE, outside loop.
Loop:
 part=count. If (((part-65536u)&0x80000000u)==0),part=65536u. count-=part.
 signed-half=(part>>1)|(part&0x80000000u). CW32(0xf0223cu,signed-half|0x10000u). The literal is0x10000, NOT0x80000000.
 aligned=destination&0xfffffff8u;destination_offset=(destination-aligned)>>1;destination+=part;CW32(0xf02200u,aligned);CW32(0xf0220cu,destination_offset).
 aligned=source&0xfffffff8u;source_byte_offset=source-aligned;lastX=source_byte_offset&1u;source_offset=source_byte_offset>>1;source+=part;CW32(0xf02224u,aligned);CW32(0xf02230u,source_offset).
 result=source_offset>destination_offset?0x01800005u:0x01800001u;CW32(0xf02238u,result).
 Repeat while count!=0. Never add software payload copying, polling or arbitrary guards. All arithmetic unsigned32 wrap. Do not replace subtraction-N checks with signed comparisons or high-bit-only tests.
After loop: saved4=CR32(sp-12u);saved3=CR32(sp-8u);saved2=CR32(sp-4u), exact read order. r[4]=saved4;r[3]=saved3;r[2]=saved2.
r[0]=result;r[1]=0;r[8]=destination;r[9]=source;r[16]=(sr&0xffe0u)|(lastX?16u:0u)|(saved2==0?4u:0u)|(saved2&0x80000000u?8u:0u). Preserve all remaining cells including r[15]/r[17].
Do not emit original stack-pop increments: sp is the original entry SP and never changes in this C body. The wrapper handles its private frame and final RTS. Use one function; no comments claiming tests.\n'''
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),previous=previous,coordinator_supplied_full_algorithm=True,source_accepted=False,new_training=False,native_Chat=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-copy-repair-active.json',state)
    mark()
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game');state['status']='local_repair_running';mark()
            a=lab.generate('game',system,user,2700);save(out/'response.json',a);(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\nRESPONSE\n'+a['text'])
        blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
        p=out/'copy-native.c';p.write_text(blocks[0].strip()+'\n')
        state.update(status='terminal_guided_native_copy_rewrite_pending_CPU_device_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,seconds=a['seconds'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-copy-current.json',state);print(state['status'],a['seconds'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
