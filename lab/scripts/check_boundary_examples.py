"""Freeze original CPU boundary examples for exact local-model contracts."""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_boundary_handlers as boundary
ROOT=boundary.ROOT

def main():
 report=json.loads((ROOT/'verification/biwn-boundary-handlers-checks.json').read_text());lib=c.CDLL(str(Path(report['directory'])/'libboundary-handlers.dylib'));one=lib.biwn_boundary_type1;one.argtypes=[c.POINTER(boundary.world.Bus),c.c_uint16,c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];one.restype=c.c_int;two=lib.biwn_boundary_type2;two.argtypes=[c.POINTER(boundary.world.Bus),c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];two.restype=c.c_int;functions={0x19f2c:one,0x19fda:two};snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 rows=[]
 for edge,old,delta,returned,effects in [(0x2345,10,5,0,[]),(0xffff,10,5,0x12340000,[[0x102c4,0x49c8c,2,100]])]:
  incoming=[0]*len(boundary.REGS);incoming[0]=0xabcd1234;case={'entry':0x19f2c,'params':[edge,0,delta],'incoming':incoming,'initial':[[0x49c8c,2,old]],'default_helper_return':returned,'helper_effects':effects};a=boundary.Script(snapshot,case);b=boundary.Script(snapshot,case);d0,_=boundary.original(a,case,set());status,actual=boundary.translated(functions,b,case);assert status==0 and actual==d0 and a.trace==b.trace and a.memory==b.memory
  rows.append({'edge':hex(edge),'full_D0':d0,'full_D0_hex':hex(d0),'neighbor_word':int.from_bytes(a.memory[0x49c8c:0x49c8e],'big'),'trace':a.trace,'original_CPU_and_C_match':True})
 assert rows[0]['full_D0']==0xabcd0000 and rows[1]['neighbor_word']==95 and rows[1]['full_D0']==0x12340000
 fixtures=json.loads((Path(report['directory'])/'fixtures.json').read_text());negative=next(x for x in fixtures if x['parameters']['kind']=='matching_negative_flags');cross=next(x for x in fixtures if x['parameters']['kind']=='cross64k' and any(v==[0x81016,2,0]for v in x['parameters']['initial']))
 assert any(t[0]=='call'and t[1]==0x10652 for t in negative['trace']);assert cross['full_D0']==0x90000
 output={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'four_original_CPU_boundary_contract_examples_verified','new_type1_examples':rows,'matching_negative_flags_calls_target_helper':True,'negative_flag_source_fixture':{'directory':report['directory'],'case':negative['case']},'cross64k_scan_return_D0':cross['full_D0'],'cross64k_scan_return_D0_hex':hex(cross['full_D0']),'cross64k_source_fixture':{'directory':report['directory'],'case':cross['case']},'scope':'Two fresh original-vs-C type1cases and two already checked original-vs-C type2fixtures. Full D0 differs from caller-used lowword.'}
 (ROOT/'verification/boundary-checked-examples.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'unsupported_return':hex(rows[0]['full_D0']),'modified_neighbor_after_undo':95,'cross64k_return':'0x90000','matching_negative_flags_calls_helper':True}))
if __name__=='__main__':main()
