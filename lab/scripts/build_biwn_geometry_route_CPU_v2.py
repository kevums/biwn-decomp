"""Compile source-reached cases from a frozen original-route trace prefix.

The accepted dispatcher remains the fallback. No accepted pointer is changed.
Generated cases are experimental until original/C state and cost comparisons.
"""
import argparse, hashlib, json, os, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
import capstone
import numpy as np
import generate_biwn_atomic_startup_math as math
import biwn_geometry_CPU_semantics_v2 as cache_semantics

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output-manifest', type=Path, required=True)
    parser.add_argument('--base-candidate', type=Path)
    parser.add_argument('--static-listing',type=Path,help='Explicit static instruction listing instead of a runtime address trace; never implies execution coverage')
    parser.add_argument('--instruction-RAM',type=Path,
                        help='Explicit static code atlas for staged startup images; compilation metadata only, never injected into execution')
    parser.add_argument('--function', default='biwn_route_CPU_step')
    parser.add_argument('--replace-source-range',nargs=2,type=lambda value:int(value,0),action='append',default=[],
                        help='Explicit experimental code interval [start,stop); regenerate observed instructions instead of falling back to old bodies')
    parser.add_argument('--exclude-static-range',nargs=2,type=lambda value:int(value,0),action='append',default=[],help='Original listing intervals replaced by an explicit experimental program variant')
    parser.add_argument('--movie-privileged-events', action='store_true',
                        help='Isolated STOP/privilege event tokens; requires matching private-state native bridge')
    args = parser.parse_args()
    args.reference=args.reference.resolve()
    prior = json.loads((args.base_candidate or ROOT/'verification/extended-frame-CPU-candidate.json').read_text())
    if not args.base_candidate:
        accepted = json.loads((ROOT/'verification/extended-frame-CPU-accepted.json').read_text())
        assert prior['library'] == accepted['library']
    assert re.fullmatch(r'biwn_[A-Za-z0-9_]+', args.function)
    assert args.function != prior['function'], 'Wrapper and fallback symbols must differ'
    listing_rows=None
    if args.static_listing:
        listing=json.loads(args.static_listing.read_text())
        listing_rows={int(row['address'],16):row for row in listing['instructions']}
        assert len(listing_rows)==len(listing['instructions'])
        assert all(0<=start<stop for start,stop in args.exclude_static_range)
        pcs=sorted(pc for pc in listing_rows if not any(start<=pc<stop for start,stop in args.exclude_static_range));count=0
    else:
        raw = args.reference/'CPU-before-instructions.bin'
        # The writer may be live. Freeze a complete, already-written prefix;
        # future bytes do not alter this candidate's observed-address inventory.
        count = raw.stat().st_size//78
        assert count > 0
        dtype = np.dtype({'names':['PC'], 'formats':['>u4'], 'offsets':[64], 'itemsize':78})
        # Scan bounded windows so long reference traces do not keep tens of GB
        # mapped while the daily local model is loaded.
        observed = set()
        window = 1_000_000
        for first in range(0, count, window):
            records = np.memmap(raw, dtype=dtype, mode='r', offset=first*78,
                                shape=(min(window, count-first),))
            observed.update(map(int, np.unique(records['PC'])))
            del records
        pcs = sorted(observed)
    ram_path = args.reference/'warm-RAM.bin'
    warm_ram = ram_path.read_bytes()
    code_path=args.instruction_RAM.resolve()if args.instruction_RAM else ram_path
    ram = code_path.read_bytes()
    selected = dict(prior['selected_case_sources'])
    for start,stop in args.replace_source_range:
        assert 0<=start<stop<=len(ram)
        selected={pc:source for pc,source in selected.items()if not start<=int(pc,16)<stop}
    new = sorted(set(pcs)-set(int(x,16) for x in selected)-{0x303c,0x3042,0x304e,0x4088})
    out = ROOT/'verification/route-CPU-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    rows, unsupported = [], []
    for pc in new:
        try:
            assert 0 <= pc < len(ram)-24, ('PC outside captured RAM',hex(pc))
            instruction = next(decoder.disasm(ram[pc:pc+24], pc, count=1))
            if listing_rows is not None:
                listed=listing_rows[pc];assert instruction.size==listed['size']
                assert ram[pc:pc+instruction.size].hex()==listed['bytes'].lower(), 'Listing bytes differ from the pinned atlas'
            row = math.base.binary_tools.m68k_instructions(ram[pc:pc+instruction.size],pc)[0][0]
            assert row['classification'] == 'decoded_instruction'
            if cache_semantics.handles(row):
                code=cache_semantics.emit(row)
            elif row['bytes']=='4e71' and row['assembly']=='nop':
                code='case '+hex(pc)+'u: /* source NOP; CCR unchanged */ s.cpu.pc='+hex(pc+2)+'u;break;'
            elif args.movie_privileged_events and (row['bytes']=='4afc'or(len(row['bytes'])==4 and 0x4e40<=int(row['bytes'],16)<=0x4e4f)):
                # M68000 short exception frame. TRAP saves PC+2; ILLEGAL
                # saves the instruction PC. Token11 requests host prefetch
                # invalidation, as in the existing source privilege path.
                vector=4 if row['bytes']=='4afc'else 32+(int(row['bytes'],16)&15)
                saved_pc=pc if vector==4 else pc+2
                code=('case '+hex(pc)+'u: /* source '+('ILLEGAL'if vector==4 else'TRAP #'+str(vector-32))+' */ '
                      'v=s.cpu.sr;if(!(s.cpu.sr&0x2000u)){s.cpu.usp=s.cpu.registers[15];s.cpu.registers[15]=s.cpu.ssp;}'
                      's.cpu.sr|=0x2000u;CHECK(push(&s,'+hex(saved_pc)+'u,4));CHECK(push(&s,v,2));'
                      's.cpu.ssp=s.cpu.registers[15];CHECK(read_value(&s,'+hex(vector*4)+'u,4,&u));'
                      's.cpu.pc=u;*state=s.cpu;return 11;')
            elif pc==0x102bc and row['bytes']=='5cc0':
                code='case 0x102bcu: /* SGE.B D0; flags unchanged */ v=(((s.cpu.sr>>3)^(s.cpu.sr>>1))&1u)?0u:255u;put(&s,0,1,v);s.cpu.pc=0x102beu;break;'
            elif pc in [0x13420,0x1785e] and row['bytes'] in ['0000eb04','0001660c']:
                register=0 if pc==0x13420 else 1
                immediate=int(row['bytes'][-2:],16)
                code=('case '+hex(pc)+'u: /* ORI.B: high extension byte is ignored */ v=(s.cpu.registers['+str(register)+']|'+hex(immediate)+'u)&255u;put(&s,'+str(register)+',1,v);nz(&s,v,8);s.cpu.pc='+hex(pc+4)+'u;break;')
            elif pc in [0x14976,0x1bd60] and row['bytes'] in ['008009800609','0a8000020000']:
                operator='|'if pc==0x14976 else'^'
                immediate=int(row['bytes'][4:],16)
                code=('case '+hex(pc)+'u: /* source immediate long logic */ v=s.cpu.registers[0]'+operator+hex(immediate)+'u;put(&s,0,4,v);nz(&s,v,32);s.cpu.pc='+hex(pc+6)+'u;break;')
            elif pc==0x1479e and row['bytes']=='08c00010':
                code='case 0x1479eu: /* BSET #16,D0 is a register-long operation */ s.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((s.cpu.registers[0]&0x10000u)?0u:4u));s.cpu.registers[0]|=0x10000u;s.cpu.pc=0x147a2u;break;'
            elif pc==0x1bcf4 and row['bytes']=='e208':
                code='case 0x1bcf4u: /* LSR.B #1,D0 */ u=s.cpu.registers[0]&1u;v=(s.cpu.registers[0]&255u)>>1;put(&s,0,1,v);nz(&s,v,8);s.cpu.sr=(uint16_t)((s.cpu.sr&~0x11u)|(u?0x11u:0u));s.cpu.pc=0x1bcf6u;break;'
            elif pc==0x15cba and row['bytes']=='008000030000':
                code='case 0x15cbau: /* source ORI.L #$30000,D0 */ v=s.cpu.registers[0]|0x30000u;put(&s,0,4,v);nz(&s,v,32);s.cpu.pc=0x15cc0u;break;'
            elif pc==0x15d54 and row['bytes']=='08c30010':
                code='case 0x15d54u: /* source BSET #16,D3: register long, flags except Z preserved */ s.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((s.cpu.registers[3]&0x10000u)?0u:4u));s.cpu.registers[3]|=0x10000u;s.cpu.pc=0x15d58u;break;'
            elif pc==0x1622e and row['bytes']=='b344':
                code='case 0x1622eu: /* source EOR.W D1,D4 */ v=(s.cpu.registers[1]^s.cpu.registers[4])&0xffffu;put(&s,4,2,v);nz(&s,v,16);s.cpu.pc=0x16230u;break;'
            elif pc==0x165fc and row['bytes']=='4222':
                code='case 0x165fcu: /* source CLR.B -(A2), read-modify-write */ s.cpu.registers[10]-=1u;CHECK(read_value(&s,s.cpu.registers[10],1,&v));CHECK(write_value(&s,s.cpu.registers[10],1,0));nz(&s,0,8);s.cpu.pc=0x165feu;break;'
            elif args.movie_privileged_events and pc in [0xddfe,0x22a0e] and row['bytes']=='4e722000':
                code=('case '+hex(pc)+'u: /* source STOP #$2000 */ '
                    'if(s.cpu.sr&0x2000u){s.cpu.ssp=s.cpu.registers[15];s.cpu.sr=0x2000u;'
                    's.cpu.pc+=4u;*state=s.cpu;return 10;}'
                    'v=s.cpu.sr;s.cpu.usp=s.cpu.registers[15];s.cpu.sr|=0x2000u;s.cpu.registers[15]=s.cpu.ssp;'
                    'CHECK(push(&s,s.cpu.pc,4));CHECK(push(&s,v,2));'
                    's.cpu.ssp=s.cpu.registers[15];'
                    'CHECK(read_value(&s,0x20u,4,&v));if(v!=0xddfeu)return 7;'
                    's.cpu.pc=v;*state=s.cpu;return 11;')
            elif args.movie_privileged_events and pc==0xde06 and row['bytes']=='4e73':
                code=('case 0xde06u: /* source RTE */ if(!(s.cpu.sr&0x2000u))return 9;'
                    'CHECK(read_value(&s,s.cpu.registers[15],2,&v));'
                    'CHECK(read_value(&s,s.cpu.registers[15]+2u,4,&u));'
                    's.cpu.ssp=s.cpu.registers[15]+6u;s.cpu.sr=(uint16_t)v;'
                    's.cpu.registers[15]=(s.cpu.sr&0x2000u)?s.cpu.ssp:s.cpu.usp;'
                    's.cpu.pc=u;break;')
            elif pc==0xe806 and row['bytes']=='00400200':
                code='case 0xe806u: /* ori.w #$200,d0 */ v=(s.cpu.registers[0]|0x200u)&0xffffu;put(&s,0,2,v);nz(&s,v,16);s.cpu.pc=0xe80au;break;'
            elif pc==0xe7ca and row['bytes']=='40c0':
                code='case 0xe7cau: /* source MOVE SR,D0; flags unchanged */ put(&s,0,2,s.cpu.sr);s.cpu.pc=0xe7ccu;break;'
            elif args.movie_privileged_events and ((pc==0x4000 and row['bytes']=='46fc2700')or(pc==0xe7d0 and row['bytes']=='46c0')):
                # Pinned UAE MakeSR exposes S, interrupt mask and CCR only.
                # Preserve inactive stack bank and reject via the source
                # privilege vector when a privileged write occurs in user mode.
                operand='0x2700u'if pc==0x4000 else's.cpu.registers[0]'
                code=('case '+hex(pc)+'u: /* source MOVE to SR */ '
                    'if(!(s.cpu.sr&0x2000u)){v=s.cpu.sr;s.cpu.usp=s.cpu.registers[15];'
                    's.cpu.sr|=0x2000u;s.cpu.registers[15]=s.cpu.ssp;'
                    'CHECK(push(&s,s.cpu.pc,4));CHECK(push(&s,v,2));'
                    's.cpu.ssp=s.cpu.registers[15];CHECK(read_value(&s,0x20u,4,&v));'
                    'if(v!=0xddfeu)return 7;s.cpu.pc=v;*state=s.cpu;return 11;}'
                    's.cpu.ssp=s.cpu.registers[15];s.cpu.sr=(uint16_t)('+operand+'&0x271fu);'
                    'if(!(s.cpu.sr&0x2000u))s.cpu.registers[15]=s.cpu.usp;'
                    's.cpu.pc='+hex(pc+row['size'])+'u;break;')
            elif pc==0x1558a and row['bytes']=='04800015edc0':
                code='case 0x1558au: /* source SUBI.L */ v=alu(&s,s.cpu.registers[0],0x15edc0u,32,1,0);put(&s,0,4,v);s.cpu.pc=0x15590u;break;'
            elif pc in [0x22854,0x22982] and row['bytes'] in ['04000020','04000030']:
                immediate=int(row['bytes'][-2:],16)
                code=('case '+hex(pc)+'u: /* source SUBI.B */ v=alu(&s,s.cpu.registers[0],'+str(immediate)+'u,8,1,0);put(&s,0,1,v);s.cpu.pc='+hex(pc+4)+'u;break;')
            elif pc==0xea78 and row['assembly']=='bset.b #$7, $8(a2)':
                assert row['bytes']=='08ea00070008'
                # Source-specific byte BSET. Pinned UAE op_8e8_4 reads
                # the old bit into Z, preserves all other SR bits, then
                # writes the set byte and advances the six-byte opcode.
                code=('case 0xea78u: /* bset.b #$7,$8(a2) */ '
                    'CHECK(read_value(&s,s.cpu.registers[10]+8u,1,&v));'
                    's.cpu.sr=(uint16_t)((s.cpu.sr&~4u)|((v&0x80u)?0u:4u));'
                    'CHECK(write_value(&s,s.cpu.registers[10]+8u,1,v|0x80u));'
                    's.cpu.pc=0xea7eu;break;')
            elif int(row['bytes'][:4],16)&0xf1f8==0x81c0:
                # Pinned UAE op_81c0_4: X preserved; overflow leaves D0
                # unchanged with N/V set, C clear and Z preserved. Use int64_t to
                # avoid host overflow for INT32_MIN/-1. Zero rejects.
                word=int(row['bytes'][:4],16);destination=(word>>9)&7;operand=word&7
                assert row['size']==2 and row['assembly']==f'divs.w d{operand}, d{destination}'
                target=f's.cpu.registers[{destination}]'
                code=('case '+hex(pc)+'u: /* source register DIVS.W; pinned overflow flags */ '
                    '{int64_t a=(int32_t)'+target+',b=(int16_t)s.cpu.registers['+str(operand)+'],q,r;'
                    'if(!b)return 9;q=a/b;if(q< -32768||q>32767)'
                    's.cpu.sr=(uint16_t)((s.cpu.sr&~11u)|10u);'
                    'else{r=a%b;'+target+'=((uint32_t)(uint16_t)r<<16)|(uint16_t)q;'
                    'nz(&s,(uint16_t)q,16);}}s.cpu.pc='+hex(pc+2)+'u;break;')
            else:
                code = math.emit(row)
            code = re.sub(r'CHECK\(invoke\(&s,[^;]+?\)\);','',code)
            assert 'invoke(' not in code and 's.service(' not in code
            rows.append(dict(row=row,code=code))
        except Exception as error:
            unsupported.append(dict(PC=hex(pc),error=repr(error)))
    provenance = dict(reference=str(args.reference), inventory_kind='static_listing'if listing_rows is not None else'runtime_trace',
        static_listing=str(args.static_listing.resolve())if args.static_listing else None,
        static_listing_sha256=hashlib.sha256(args.static_listing.read_bytes()).hexdigest()if args.static_listing else None,
        addresses_are_execution_evidence=listing_rows is None,frozen_prefix_records=count,
        replaced_source_ranges=args.replace_source_range,excluded_static_ranges=args.exclude_static_range,
        frozen_prefix_bytes=count*78, inventoried_PC=pcs, new_PC=list(map(hex,new)),
        warm_RAM_sha256=hashlib.sha256(warm_ram).hexdigest(),
        instruction_RAM_source=str(code_path),instruction_RAM_sha256=hashlib.sha256(ram).hexdigest())
    provenance['observed_PC'if listing_rows is None else'listed_PC']=pcs
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    (out/'unsupported.json').write_text(json.dumps(unsupported,indent=2)+'\n')
    print('new',len(new),'generated',len(rows),'unsupported',len(unsupported),str(out),flush=True)
    if unsupported:
        raise SystemExit('Additional source semantics required; candidate not published')
    base = json.loads((ROOT/'verification/controller-direction-library-current.json').read_text())
    source_dir = Path(base['directory'])/'source'
    template = (source_dir/'biwn_world_missing_single_step.c').read_text()
    prefix = template[:template.index('#define CHECK')]
    functions = re.findall(r'^static\s+(?:[A-Za-z_]\w*\s+)+([A-Za-z_]\w*)\s*\(',prefix,re.M)
    old_fn = prior['function']
    body = prefix+'\n#define CHECK(e) do{int status=(e);if(status)return status;}while(0)\n'
    body += 'extern int '+old_fn+'(struct biwn_world_bus*,struct biwn_task_cpu*,biwn_input_write8,biwn_world_cpu_service,void*);\n'
    body += 'int '+args.function+'(struct biwn_world_bus*bus,struct biwn_task_cpu*state,biwn_input_write8 write8,biwn_world_cpu_service service,void*context){struct dispatch s;uint32_t v=0,u=0;int full_call=1,stop_on_yield=0;(void)full_call;(void)stop_on_yield;(void)v;(void)u;'
    body += ' '.join('(void)'+f+';'for f in functions)
    body += 's.bus=bus;s.cpu=*state;s.write8=write8;s.service=service;s.context=context;switch(s.cpu.pc){\n'
    for item in rows:
        body += item['code']+'\n'
        selected[hex(item['row']['address'])]='biwn_route_CPU.c'
    body += 'default:return '+old_fn+'(bus,state,write8,service,context);}\n*state=s.cpu;return 0;}\n'
    source = out/'biwn_route_CPU.c'
    source.write_text(body)
    library = out/'libroute-CPU.dylib'
    command = ['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',
        '-I',str(source_dir),'-I',str(ROOT/'projects/black-ice-white-noise/restoration'),
        str(source),prior['library'],'-o',str(library)]
    result = subprocess.run(command,capture_output=True,text=True,
        env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stderr
    report = dict(status='compiled_unverified',directory=str(out),library=str(library),
        function=args.function,base_library=prior['library'],inventory_kind=provenance['inventory_kind'],runtime_verified=False,
        selected_case_sources=selected,new_cases=[x['row']for x in rows],
        warm_RAM_source=str(ram_path),provenance=str(out/'provenance.json'),
        instruction_RAM_source=str(code_path),
        movie_privileged_event_tokens=args.movie_privileged_events,
        source_sha256=hashlib.sha256(body.encode()).hexdigest(),new_training=False,
        coordinator_authored=True,whole_game_complete=False)
    text=json.dumps(report,indent=2)+'\n'
    (out/'report.json').write_text(text)
    args.output_manifest.write_text(text)


if __name__ == '__main__':
    main()
