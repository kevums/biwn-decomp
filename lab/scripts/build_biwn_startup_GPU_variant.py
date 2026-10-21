"""Compile captured cold main initializer instructions and branch delays."""
import hashlib
import argparse
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
import generate_biwn_game_firstboot_GPU as generator

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import binary_tools


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--capture',type=Path)
    parser.add_argument('--base-candidate',type=Path)
    parser.add_argument('--candidate-output',type=Path)
    parser.add_argument('--stem',default='biwn_gpu_cold_main_init')
    args=parser.parse_args()
    assert not args.capture or (args.base_candidate and args.candidate_output)
    assert re.fullmatch(r'biwn_gpu_[a-z0-9_]+',args.stem)
    capture=args.capture or ROOT/'runs/zero-warm-startup-CPU-GPU-discovery/regular-GPU-bundles/unknown-instructions.bin'
    data=capture.read_bytes()
    assert len(data)%4422==0
    rows={}
    for offset in range(0,len(data),4422):
        pc,opcode=struct.unpack('>IH',data[offset:offset+6])
        raw=data[offset+6:offset+4422]
        assert raw[4395]==0
        targets=[pc]+([pc+2]if opcode>>10 in [52,53]else[])
        for address in targets:
            slot=address-0xf03000
            word=int.from_bytes(raw[slot:slot+2],'big')
            size=6 if word>>10==38 else 2
            decoded,_=binary_tools.jaguar_instructions(raw[slot:slot+size],address,'gpu')
            row=decoded[0]
            if address in rows:assert rows[address]['bytes']==row['bytes']
            rows[address]=row
    out=ROOT/'verification/startup-GPU-variant-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    stem=args.stem
    rename=lambda text:text.replace('biwn_game_firstboot_GPU',stem).replace('BIWN_GAME_FIRSTBOOT_GPU',stem.upper())
    original=ROOT/'projects/black-ice-white-noise/restoration/biwn_game_firstboot_GPU.c'
    prefix=rename(original.read_text().split('#define CHECK',1)[0])
    helpers=re.findall(r'^static\s+(?:[A-Za-z_]\w*\s+)+([A-Za-z_]\w*)\s*\(',prefix,re.M)
    header=ROOT/'projects/black-ice-white-noise/restoration/biwn_game_firstboot_GPU.h'
    (out/(stem+'.h')).write_text(rename(header.read_text()))
    body=prefix+'\n#define CHECK(e) do{int status=(e);if(status)return(enum BIWN_UNUSED_STATUS)status;}while(0)\n'
    body=body.replace('enum BIWN_UNUSED_STATUS','enum '+stem+'_status')
    body+='enum '+stem+'_status '+stem+'_bundle_run(struct '+stem+'_bus*bus,struct '+stem+'_state*state,uint32_t budget){struct '+stem+'_state s;uint32_t v=0,target=0;unsigned pending=0;'
    body+='(void)v;'+' '.join('(void)'+helper+';'for helper in helpers)
    body+='if(!bus||!state||budget!=1||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank)return 1;s=*state;do{unsigned delayed=pending;uint32_t resume=target;pending=0;s.instructions++;switch(s.pc){\n'
    for row in sorted(rows.values(),key=lambda row:row['address']):
        word=int(row['bytes'][:4],16)
        if word>>10==37:
            source_register=(word>>5)&31;destination_register=word&31
            code='case '+hex(row['address'])+'u: /* source MOVEFA, bank0 active; flags unchanged */ s.registers[0]['+str(destination_register)+']=s.registers[1]['+str(source_register)+'];s.pc='+hex(row['address']+row['size'])+'u;break;'
        elif word>>10==29:
            count=(word>>5)&31
            register=word&31
            operand='s.registers[0]['+str(register)+']'
            code='case '+hex(row['address'])+'u: /* source RORQ */ v='+operand+';s.c=v>>31;'+operand+'=(v>>'+str(count)+')|(v<<'+str((-count)&31)+');zn(&s,'+operand+');s.pc='+hex(row['address']+row['size'])+'u;break;'
        else:code=rename(generator.emit(row))
        body+=code+'\n'
    body+='default:return '+stem.upper()+'_BAD_PC;}if(delayed){if(pending)return '+stem.upper()+'_BAD_DELAY;s.pc=resume;}if(!pending){*state=s;return 0;}}while(1);}\n'
    if 'sx16(' in body and 'static uint32_t sx16(' not in body:
        body=body.replace('#define CHECK','static uint32_t sx16(uint32_t value){value&=0xffffu;return(value^0x8000u)-0x8000u;}\n#define CHECK',1)
    source=out/(stem+'.c')
    source.write_text(body)
    library=out/'libcold-main-init.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    prior=json.loads((args.base_candidate or ROOT/'verification/startup-GPU-bundles-experimental-candidate.json').read_text())
    row=dict(name=stem.removeprefix('biwn_gpu_'),stem=stem,function=stem+'_bundle_run',kind='firstboot',
             library=str(library),instructions_decoded=sorted(rows.values(),key=lambda row:row['address']),
             witness_source=str(capture),witness_sha256=hashlib.sha256(data).hexdigest(),
             source_sha256=hashlib.sha256(body.encode()).hexdigest())
    report=dict(status='compiled_pending_live_comparison',directory=str(out),programs=prior['programs']+[row],
                additional_source_instructions=len(rows),whole_game_complete=False,new_training=False)
    (args.candidate_output or ROOT/'verification/startup-variant-GPU-bundles-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,'cases',len(rows),flush=True)


if __name__=='__main__':
    main()
