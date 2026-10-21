"""Original CPU/C examples for full D0 and word-versus-long shift behavior."""
import ctypes as c,json,copy
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_geometry as g

def main():
 report=json.loads((g.ROOT/'verification/biwn-geometry-checks.json').read_text());functions=g.bind(c.CDLL(str(Path(report['directory'])/'libgeometry.dylib')))
 snapshot=(g.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();obj=0x80000;table=0x100000;container=0x82000;rows=[]
 def check(case,label,address=None,expected=None):
  a=g.boundary.Script(snapshot,case);b=g.boundary.Script(snapshot,case);original,_=g.original(a,case,set());status,translated=g.translated(functions,b,case)
  assert status==0 and original==translated and a.trace==b.trace and a.memory==b.memory
  value=int.from_bytes(a.memory[address:address+4],'big')if address is not None else original
  assert value==expected,(label,hex(value),hex(expected))
  rows.append({'label':label,'original_D0':original,'C_D0':translated,'checked_value':value,'expected':expected,'case':case,'original_trace':a.trace})
 cases=g.cases(snapshot)
 for x,z,label,expected in [(0,0,'inside_incoming_abcd1234',0xabcd0000),(0,100,'late_Z_upper_outside_incoming_abcd1234',0xabcd0001),(-101,0,'early_X_outside_incoming_abcd1234',1)]:
  case=next(q for q in cases if q['entry']==0x1028e and q['incoming'][0]==0xabcd1234 and q['initial'][0][2]==x and q['initial'][1][2]==z);check(case,label,expected=expected)
 for entry,offset,address,label in [(0x1039c,10,obj+0x4c,'tile_word0400_shift6'),(0x10652,2,obj+0x34,'region_word0400_shift6'),(0x10430,18,obj+0x1e,'portal_word0400_shift6')]:
  case={'entry':entry,'kind':'shift_width_example','params':[obj,0],'incoming':[0]*len(g.REGS),'initial':[[obj+0x40,2,0],[0x49bb4,4,container],[container,2,1],[container+2,2,1],[container+4,4,table],[container+8,4,table],[container+12,4,table],[0x49c18,4,container],[obj+4,4,0],[obj+10,4,0],[obj+0x1e,4,0],[obj+0x26,4,0],[obj+0x4c,4,0]],'default_helper_return':0}
  case['initial'] += [[table+i,2,0]for i in range(0,28,2)];case['initial'].append([table+offset,2,1024])
  if entry==0x10430:case['params'].append(0);case['initial'] += [[table+11,1,0],[table+26,2,1]]
  check(case,label,address,65536 if entry==0x10430 else 0)
 out={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'six_original_CPU_and_C_examples_passed','source_sha256':report['source_sha256'],'examples':rows,'scope':'Original CPU execution, no helper stubs; finite private-memory examples, not full game.'}
 (g.ROOT/'verification/geometry-checked-examples.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':len(rows)}))
if __name__=='__main__':main()
