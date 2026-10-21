"""Build an isolated music owner with both banks and retirement context.

Reuses the checked media bridge's serialization layout. Source music and
routine media candidates remain unchanged; live proof is still required.
"""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    owner = json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())
    media = json.loads((ROOT/'verification/DSP-media-owner-experimental-candidate.json').read_text())
    session = Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping = json.loads((session/'music-DSP-engine-generation.json').read_text())
    rows = list(mapping['instructions_decoded'])
    observed = json.loads((ROOT/'runs/music-DSP-live-startup-observed/DSP-observation.json').read_text())
    for pc, raw in [(0xf1b144, 'd7e0'), (0xf1b146, 'e400')]:
        assert hex(pc)+':'+hex(int(raw, 16)) in observed['PC_opcodes']
        assert all(row['address'] != pc for row in rows)
        rows.append(dict(address=pc, bytes=raw))
    out = ROOT/'verification/DSP-music-owner-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    original = ROOT/'projects/black-ice-white-noise/restoration'
    body = (original/'biwn_dsp_music_engine.c').read_text()
    body = replace_once(body, 'default:return BIWN_DSP_MUSIC_ENGINE_BAD_PC;',
                        'case 0xf1b144u: /* observed JR -1, always */ pending=1;target=0xf1b144u;s.pc=0xf1b146u;break;\n'
                        'case 0xf1b146u: /* observed delay NOP */ s.pc=0xf1b148u;break;\n'
                        'default:return BIWN_DSP_MUSIC_ENGINE_BAD_PC;')
    body = replace_once(body, 's->bank=(s->flags&8u)?0u:((s->flags>>14)&1u);return 0;',
                        's->bank=(s->flags&8u)?0u:((s->flags>>14)&1u);return b->write32(b->context,a,v)?2:0;')
    body = replace_once(body, 's->control=(s->control&mask)|(v&~mask);return 0;',
                        's->control=(s->control&mask)|(v&~mask);return b->write32(b->context,a,v)?2:0;')
    body = 'static unsigned biwn_DSP_last_operands[2];\n'+body
    for row in rows:
        word = int(row['bytes'][:4], 16)
        marker = 'case '+hex(row['address'])+'u:'
        body = replace_once(body, marker, marker+'biwn_DSP_last_operands[0]='+str((word>>5)&31)+'u;biwn_DSP_last_operands[1]='+str(word&31)+'u;')
    body += '\nvoid biwn_DSP_get_last_operands(unsigned*p){p[0]=biwn_DSP_last_operands[0];p[1]=biwn_DSP_last_operands[1];}\n'
    (out/'biwn_dsp_music_engine.c').write_text(body)
    (out/'biwn_dsp_music_engine.h').write_text((original/'biwn_dsp_music_engine.h').read_text())
    template_path = Path(media['directory'])/'DSP_media_bridge.c'
    bridge = template_path.read_text().replace('biwn_dsp_media_audio', 'biwn_dsp_music_engine')
    bridge = bridge.replace('biwn_DSP_media_', 'biwn_DSP_music_')
    identities = []
    for row in sorted(rows, key=lambda row: row['address']):
        data = bytes.fromhex(row['bytes'])
        identities.append('{'+str(row['address'])+','+str(len(data))+',{'+','.join(str(x) for x in data)+'}},')
    bridge, count = re.subn(r'(static const struct identity identities\[\]=\{).*?(\};\nextern)',
                            lambda match: match[1]+''.join(identities)+match[2], bridge, count=1, flags=re.S)
    assert count == 1
    bridge = replace_once(bridge, 'void(*operands)(uint32_t,uint32_t);};',
                          'void(*operands)(uint32_t,uint32_t);void(*write16)(uint32_t,uint16_t,uint32_t);void(*context)(uint32_t*,uint32_t*);};')
    bridge = replace_once(bridge, 's->instructions=0;}',
                          's->instructions=0;s->bank=raw[8495];H.context(&s->flags_delay,&s->prestore_bank);}')
    bridge = replace_once(bridge, 'raw[8495]=0;', 'raw[8495]=(uint8_t)s->bank;')
    bridge = replace_once(bridge, 'static struct biwn_dsp_music_engine_bus B={rd8,rd32,wr32,NULL,NULL};',
                          'static int wr16(void*x,uint32_t a,uint16_t v){(void)x;H.write16(a,v,2);return 0;}\n'
                          'static struct biwn_dsp_music_engine_bus B={rd8,rd32,wr32,wr16,NULL,NULL};')
    bridge = replace_once(bridge, 'if(unsupported)return fail(pc,100+unsupported);',
                          'if(unsupported&6u)return fail(pc,100+unsupported);')
    bridge = replace_once(bridge, '||raw[8495])', '||raw[8495]>1u)')
    bridge = replace_once(bridge, '||!h->operands)return 1;', '||!h->operands||!h->write16||!h->context)return 1;')
    (out/'DSP_music_bridge.c').write_text(bridge)
    library = out/'libDSP-music-owner.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
               str(out/'DSP_music_bridge.c'), str(out/'biwn_dsp_music_engine.c'), '-o', str(library)]
    result = subprocess.run(command, capture_output=True, text=True,
                            env={**os.environ, 'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stderr
    report = dict(status='compiled_pending_live_music_comparison', directory=str(out), library=str(library),
                  required_core_sha256=owner['core_sha256'], instructions=len(rows),
                  bridge_template_sha256=hashlib.sha256(template_path.read_bytes()).hexdigest(),
                  bridge_sha256=hashlib.sha256(bridge.encode()).hexdigest(),
                  source_sha256=hashlib.sha256(body.encode()).hexdigest(),
                  state_ABI='media logical state plus bank/prestore_bank/flags_delay',
                  Host_ABI='media host plus DSPWriteWord and BIWNDSPReadRetirementContext',
                  original_late_load_and_divide_hazards_rejected=True, music_ownership_verified=False,
                  whole_game_complete=False)
    text = json.dumps(report, indent=2)+'\n'
    (out/'report.json').write_text(text)
    (ROOT/'verification/DSP-music-owner-experimental-candidate.json').write_text(text)
    print(out, flush=True)


if __name__ == '__main__':
    main()
