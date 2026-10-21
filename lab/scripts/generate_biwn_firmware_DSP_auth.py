"""Fixed observed firmware DSP check, including source-decrypted code.

Compiled plaintext blocks are guarded against the live instruction bytes;
the C path must produce those bytes through the original arithmetic before
executing them. Nothing copies the decrypted code into C state from a host.
"""
import hashlib,json
from pathlib import Path
import generate_biwn_dsp_media_audio as audio
ROOT=audio.ROOT
rename=lambda s:s.replace('biwn_dsp_media_audio','biwn_firmware_DSP_auth').replace('BIWN_DSP_MEDIA_AUDIO','BIWN_FIRMWARE_DSP_AUTH').replace('generate_biwn_dsp_media_audio.py','generate_biwn_firmware_DSP_auth.py')

def emit(row):
    word=int(row['bytes'][:4],16);op,m,n=word>>10,(word>>5)&31,word&31;pc=row['address'];nxt=pc+row['size'];M=f's.registers[0][{m}]';N=f's.registers[0][{n}]';line=None
    if op==1:line=f'{{uint64_t t=(uint64_t){N}+{M}+s.c;{N}=(uint32_t)t;s.c=(uint32_t)(t>>32)&1u;zn(&s,{N});}}'
    elif op==5:line=f'{{uint64_t t=(uint64_t){N}+(uint32_t)(~{M})+(s.c^1u);{N}=(uint32_t)t;s.c=((uint32_t)(t>>32)&1u)^1u;zn(&s,{N});}}'
    elif op==7:line=f'{N}-={m or 32}u;'
    elif op==12:line=f'{N}=~{N};zn(&s,{N});'
    elif op==23:line=f'if({M}&0x80000000u){{s.c={N}>>31;{N}=(int32_t){M}<=-32?0u:{N}<<(0u-{M});}}else{{s.c={N}&1u;{N}={M}>=32?0u:{N}>>{M};}}zn(&s,{N});'
    elif op in [28,29]:line=f's.c={N}>>31;{N}=rot({N},'+(f'{M}'if op==28 else str(m or 32)+'u')+f');zn(&s,{N});'
    elif op==37:line=f'{N}=s.registers[1][{m}];'
    elif op in [58,59]:line=f'CHECK(rd32(bus,&s,s.registers[0][{14 if op==58 else 15}]+{M},&v));{N}=v;'
    elif op in [60,61]:line=f'CHECK(wr32(bus,&s,s.registers[0][{14 if op==60 else 15}]+{M},{N}));'
    if line is None:body=rename(audio.emit(row))
    else:body=f'case {hex(pc)}u: /* {row["assembly"]} */ {line}s.pc={hex(nxt)}u;break;'
    # Guard all bytes, including MOVEI's immediate. This verifies generated
    # source code has appeared in local RAM before its compiled block runs.
    raw=bytes.fromhex(row['bytes']);guard='||'.join(f's.local_RAM[{pc-0xf1b000+i}]!={v}u'for i,v in enumerate(raw))
    return body.replace('*/','*/ if('+guard+')return BIWN_FIRMWARE_DSP_AUTH_CHANGED_CODE;',1)

def main():
    observation=json.loads((ROOT/'verification/firmware-DSP-auth-native-discovery.json').read_text());probe=observation['first_DSP_observation']
    assert probe['execution_quantum']==1 and probe['stop_reason']=='source_DSP_GO_cleared'
    assert observation['emulator_BIOS_boot_stub_injection_and_GPU_magic_stomp_disabled']
    rows=probe['visited_instructions'];assert len(rows)==462
    prefix=rename(audio.PREFIX)
    prefix=prefix.replace('static void zn(', 'static uint32_t sar(uint32_t v,unsigned n){return n>=32u?((v&0x80000000u)?0xffffffffu:0u):((v>>n)|((v&0x80000000u)&&n?(0xffffffffu<<(32u-n)):0u));}\nstatic uint32_t rot(uint32_t v,unsigned n){n&=31u;return n?((v>>n)|(v<<(32u-n))):v;}\nstatic void zn(')
    prefix=prefix.replace('if(!delayed&&bus->observe_PC)','if(bus->observe_PC)')
    suffix=rename(audio.SUFFIX);suffix=suffix[:suffix.index('enum biwn_firmware_DSP_auth_status biwn_firmware_DSP_auth_run')]
    suffix+='''enum biwn_firmware_DSP_auth_status biwn_firmware_DSP_auth_run(struct biwn_firmware_DSP_auth_bus *bus,struct biwn_firmware_DSP_auth_state *state,uint32_t budget){struct biwn_firmware_DSP_auth_state s;int status;if(!bus||!valid(state)||!budget||!bus->read8||!bus->read32||!bus->write32)return 1;s=*state;while(budget--){if(!(s.control&1u)){*state=s;return 0;}status=biwn_firmware_DSP_auth_step(bus,&s);if(status)return(enum biwn_firmware_DSP_auth_status)status;}*state=s;return(s.control&1u)?4:0;}
'''
    header=rename(audio.HEADER).replace('BIWN_FIRMWARE_DSP_AUTH_STOPPED=6','BIWN_FIRMWARE_DSP_AUTH_STOPPED=6,BIWN_FIRMWARE_DSP_AUTH_CHANGED_CODE=7')
    a=header.index('/* Fixed');b=header.index('enum biwn_firmware_DSP_auth_status biwn_firmware_DSP_auth_step',a)
    header=header[:a]+'''/* Fixed observed source firmware DSP path: initial ROM-derived code
 * F1B2EC..F1B662 and code produced by its own arithmetic atF1B6AC..F1B7B4.
 * Each instruction checks live source bytes, including MOVEI immediates.
 * C must compute/decrypt/erase local data itself; no decrypted payload copy.
 * Bank0, pinned retail userROM and observed input path only. No runtime
 * decoder, emulator execution, magic-value injection, IRQs or clocks.
 * run retains state on a quantum budget return4; returns0 when sourceGO
 * clears. Error retains earlier external writes, not intermediate local
 * state. Other keys/ROMs/failure branches, firmware CPU/GPU boot/disc
 * loading/global schedule and full game remain separate. */
'''+header[b:]
    header=header[:header.index('enum biwn_firmware_DSP_auth_status biwn_firmware_DSP_auth_ssi_interrupt')]+'#endif\n'
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_firmware_DSP_auth.c','biwn_firmware_DSP_auth.h']
    (src/names[0]).write_text(prefix+'\n'.join(emit(row)for row in rows)+'\n'+suffix);(src/names[1]).write_text(header)
    record=dict(status='generated_unverified',instructions=len(rows),instructions_decoded=rows,source_BIOS_sha256=observation['source_BIOS_sha256'],source_observation=observation['directory'],original_program_instructions=probe['instructions'],initial_fixture_DSP_sha256=probe['initial_logical_DSP_sha256'],decrypted_instruction_interval=['0xf1b6ac','0xf1b7b4'],live_code_byte_guards=True,decrypted_code_host_copy=False,implementation_authorship='coordinator',source_sha256={n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_emitter_sha256=hashlib.sha256(Path(audio.__file__).read_bytes()).hexdigest(),whole_game_complete=False,full_firmware_boot_verified=False)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    (session/'firmware-DSP-auth-generation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items()if k!='instructions_decoded'}))

if __name__=='__main__':main()
