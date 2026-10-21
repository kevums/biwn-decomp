"""Compare source TOC command with independently expressed MD5 compression.

The source processes16blocks of big-endian longwords without MD5 padding.
This is not the standard byte-oriented, padded MD5 API.
"""
import hashlib,json,math,struct
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
S=[7,12,17,22]*4+[5,9,14,20]*4+[4,11,16,23]*4+[6,10,15,21]*4
K=[int(abs(math.sin(i+1))*2**32)&0xffffffff for i in range(64)]

def compress(data):
    assert len(data)%64==0
    state=[0x67452301,0xefcdab89,0x98badcfe,0x10325476]
    checkpoints=[]
    for off in range(0,len(data),64):
        words=struct.unpack('>16I',data[off:off+64]);a,b,c,d=state
        for i in range(64):
            if i<16:f=(b&c)|((~b)&d);g=i
            elif i<32:f=(d&b)|((~d)&c);g=(5*i+1)%16
            elif i<48:f=b^c^d;g=(3*i+5)%16
            else:f=c^(b|(~d));g=(7*i)%16
            x=(a+f+K[i]+words[g])&0xffffffff
            rotated=((x<<S[i])|(x>>(32-S[i])))&0xffffffff
            a,d,c,b=d,c,b,(b+rotated)&0xffffffff
        state=[(u+v)&0xffffffff for u,v in zip(state,[a,b,c,d])]
        checkpoints.append(struct.pack('>4I',*state).hex())
    return struct.pack('>4I',*state),checkpoints

def main():
    source=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T083153.831713Z/fourth-DSP-command/DSP-after-CPU.bin';data=source.read_bytes();toc=data[0x800:0xc00]
    result,blocks=compress(toc);expected=bytes.fromhex('1f15655720541c9daf7557e7905ad21b')
    out=ROOT/'verification/BIWN-TOC-compression'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    r=dict(status='matched'if result==expected else'mismatch',directory=str(out),algorithm_reference='https://www.rfc-editor.org/rfc/rfc1321.html',scope='Independent Python expression of64-round compression; source uses big-endian words and no padding. Not full standardMD5 and not a hardware/global boot proof.',bytes=1024,blocks=16,computed=result.hex(),source_native=expected.hex(),block_checkpoints=blocks,standard_padded_MD5=hashlib.md5(toc).hexdigest(),whole_boot=False)
    (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');(ROOT/'verification/BIWN-TOC-compression-current.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r),flush=True)

if __name__=='__main__':main()
