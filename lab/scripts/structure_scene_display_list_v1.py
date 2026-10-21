"""Restructure the checked 185B2 static semantics into three passes and the actual table switch.
No binary decoding or PC dispatch occurs in the produced C. Instruction operation
semantics are inherited from the checked translation; control structure is coordinator-authored.
"""
import re
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
SRC=ROOT/'projects/black-ice-white-noise/restoration'
OUT=SRC/'experimental/scene-display-list-structured-v1'

def main():
    OUT.mkdir(parents=True,exist_ok=True);source=SRC/'biwn_display_list_cpu.c';text=source.read_text()
    matches=list(re.finditer(r'  case (0x[0-9a-f]+)u: /\* (.*?) \*/\n([\s\S]*?)(?=  case |  default:)',text))
    blocks={int(m[1],16):(m[2],m[3])for m in matches};assert len(blocks)==254
    names=['sx16','sx8','bank','pop','put','nz','alu','shift','read_value','write_value','push']
    def convert(s):
        s=s.replace('struct dispatch','struct biwn_deck_context').replace('s.cpu','s->cpu').replace('&s','s').replace('s->write8','s->write8')
        for name in sorted(names,key=len,reverse=True):s=re.sub(r'\b'+name+r'\b','dl_'+name,s)
        return s
    # Reuse exact ALU/word/register effects; memory is delegated to the existing bus.
    helpers=text[text.index('static uint32_t sx16'):text.index('static int read_value')]
    helpers=helpers.replace('struct dispatch','struct biwn_deck_context');
    for name in sorted(names,key=len,reverse=True):helpers=re.sub(r'\b'+name+r'\b','dl_'+name,helpers)
    helpers+='''static int dl_read_value(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t *v){*v=deck_read(s,a,w);return s->error;}
static int dl_write_value(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){deck_write(s,a,w,v);return s->error;}
static int dl_push(struct biwn_deck_context *s,uint32_t v,unsigned w){s->cpu.registers[15]-=w;deck_bank(s);deck_write(s,s->cpu.registers[15],w,v);return s->error;}
#ifndef SCENE_DISPLAY_BEGIN
#define SCENE_DISPLAY_BEGIN(s) ((void)(s))
#define SCENE_DISPLAY_END(s) ((void)(s))
#endif
#define DL_CHECK(e) do{int dl_status=(e);if(dl_status){s->error=dl_status;return;}}while(0)
#ifdef SCENE_DISPLAY_NATIVE_DIRECT
#define DL_WORK() ((void)0)
#else
#define DL_WORK() do{if(!s->budget){s->error=4;return;}s->budget--;}while(0)
#endif
'''
    (OUT/'primitives.inc').write_text('/* Inherited checked CPU operation primitives; coordinator bus/work wrapper. */\n'+helpers)
    used=[];lines=['/* Structured three-pass185B2..18852 from checked static instruction semantics.',' * Original guest LINK/MOVEM/private table and source jump-table reads retained.',' * Normal completed calls only. Host work limits are not target deadlines.',' * This is restructuring of an already recovered routine, not new original source. */','static void scene_display_list_body(struct biwn_deck_context *s){',' uint32_t v,u,jump;',' if(s->error)return;',' SCENE_DISPLAY_BEGIN(s);',' DL_WORK();']
    def add(s):lines.extend(s.splitlines())
    def seq(lo,hi,indent=' '):
        for pc,(asm,body)in blocks.items():
            if not lo<=pc<=hi:continue
            assert not re.match(r'b(?:ra|eq|ne|hi|ge|cs)\.|jmp|rts',asm),asm
            body=re.sub(r'   s\.cpu\.pc=.*?;break;\n?','',body)
            assert 's.cpu.pc'not in body,(hex(pc),body)
            body=convert(body.replace('CHECK(','DL_CHECK('));add(indent+'/* '+hex(pc)+' '+asm+' */')
            add('\n'.join(indent+x.strip()for x in body.splitlines()if x.strip()));used.append(pc)
    seq(0x185b2,0x185c6)
    add(' /* Pass1: count records, including the terminating type4. */\n while(!(s->cpu.sr&4u)){\n  DL_WORK();');seq(0x185cc,0x185d2,'  ');add(' }')
    seq(0x185d8,0x185e8);add(' if(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u){');seq(0x185ec,0x185ec,'  ');add(' }');seq(0x185f2,0x185fa)
    add(' /* Pass2: build the original dynamically sized guest-stack link table. */\n do{\n  DL_WORK();');seq(0x185fc,0x185fe,'  ')
    add('  if(s->cpu.sr&4u){');seq(0x1861a,0x18622,'   ')
    add('  }else if(s->cpu.sr&1u){');seq(0x1860e,0x18616,'   ')
    add('  }else{');seq(0x18606,0x18606,'   ');add('   if(s->cpu.sr&4u){');seq(0x18626,0x18626,'    ');add('   }');seq(0x18628,0x18628,'   ');add('  }')
    seq(0x1862a,0x18632,'  ');add(' }while(s->cpu.sr&4u);');seq(0x18636,0x1863e)
    add(' if(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u){');seq(0x18642,0x18642,'  ');add(' }');seq(0x18648,0x1866a)
    add(' /* Pass3: reread records and pack phrases. The switch follows the actual source table. */\n do{\n  DL_WORK();');seq(0x1866e,0x18676,'  ')
    add('  if((s->cpu.sr&5u)!=0){');seq(0x1867e,0x18688,'   ');add('   jump=0x18690u+dl_sx16((uint16_t)s->cpu.registers[0]);\n   switch(jump){\n   case 0x1869a: /* ordinary bitmap */');seq(0x1869a,0x1869a,'    ')
    add('    goto bitmap;\n   case 0x1869e: /* scaled bitmap */');seq(0x1869e,0x1869e,'    ');add('   bitmap:\n    /* Phrase-alignment padding, including original register effects. */');seq(0x186c4,0x186c6,'    ')
    add('    while(!(s->cpu.sr&4u)){\n     DL_WORK();');seq(0x186a2,0x186c2,'     ');seq(0x186c4,0x186c6,'     ');add('    }')
    seq(0x186ca,0x186ca,'    ');add('    if(!(s->cpu.sr&4u)){');seq(0x186ce,0x186d6,'     ');add('    }')
    seq(0x186da,0x18784,'    ');add('    if(s->cpu.sr&4u){');seq(0x1878c,0x187a4,'     ');seq(0x187bc,0x187c0,'     ');add('    }\n    break;\n   case 0x187a8: /* type2 GPU object */');seq(0x187a8,0x187ba,'    ');seq(0x187bc,0x187c0,'    ')
    add('    break;\n   case 0x187c4: /* type3 branch; original packing cursor does not advance */');seq(0x187c4,0x18808,'    ')
    add('    break;\n   case 0x1880c: /* type4 stop */');seq(0x1880c,0x18826,'    ')
    add('    break;\n   default:s->error=7;return;\n   }\n  }');seq(0x18828,0x18844,'  ')
    add(' }while(s->cpu.sr&4u);\n /* Restore original callee saves and LINK frame, leaving outer RTS to the caller. */');seq(0x1884a,0x18850)
    add(' s->cpu.pc=0x18852u;\n SCENE_DISPLAY_END(s);\n}\n#undef DL_CHECK\n#undef DL_WORK')
    (OUT/'coordinator-reference.inc').write_text('\n'.join(lines)+'\n')
    wrapper=(SRC/'experimental/scene-clear-structured-v1/host-wrapper.c').read_text().replace('biwn_scene_draw_cpu.h','biwn_display_list_cpu.h').replace('#include "coordinator-reference.inc"','#include "primitives.inc"\n#include "coordinator-reference.inc"').replace('scene_clear_body','scene_display_list_body').replace('0xe03a','0x185b2').replace('biwn_scene_clear_body','biwn_display_list_cpu_body').replace('biwn_scene_clear_call','biwn_display_list_cpu_call').replace('||stop)return 1;','||(stop!=0&&stop!=1))return 1;')
    wrapper=wrapper.replace('biwn_scene_display_list_body','biwn_display_list_cpu_body')
    # Exact public return types match the existing header enum.
    wrapper=wrapper.replace('int biwn_display_list_cpu_body','enum biwn_display_list_cpu_status biwn_display_list_cpu_body').replace('int biwn_display_list_cpu_call','enum biwn_display_list_cpu_status biwn_display_list_cpu_call')
    (OUT/'host-wrapper.c').write_text(wrapper)
    required={pc for pc,(asm,_)in blocks.items()if not re.match(r'b(?:ra|eq|ne|hi|ge|cs)\.|jmp|rts',asm)}
    assert set(used)==required,(required-set(used),set(used)-required)
    save(OUT/'lineage.json',dict(status='structured_control_produced_not_yet_executed',source_static=str(source),source_static_sha256=sha(source),generator=str(Path(__file__)),generator_sha256=sha(__file__),original_instruction_blocks=254,original_operation_blocks=len(required),preserved_operation_locations=sorted(required),runtime_instruction_decode=False,PC_dispatch_loop=False,actual_source_jump_table_switch=True,new_unique_original_functions=0,new_training=False))
    print('Produced',OUT,len(required),'original operation sites',flush=True)
if __name__=='__main__':main()
