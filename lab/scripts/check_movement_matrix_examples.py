"""Small originalGPU examples make signed raw fractions explicit."""
import ctypes as c,json
from datetime import datetime,timezone
import check_biwn_movement_matrix as matrix
ROOT=matrix.ROOT

def main():
 device=matrix.frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-movement-device.dylib');lib=device.lib;assert lib.lab_movement_setup()==0
 lib.lab_movement_original.argtypes=[c.c_uint32]*6;lib.lab_movement_C.argtypes=[c.c_uint32]*5+[c.POINTER(matrix.Result),c.c_uint32]
 rows=[]
 try:
  for angle,speed in [(0,0xffff),(0,1),(64,1),(192,1)]:
   ram=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base=0x49ccc;ram[base:base+32]=b'\xa5'*32;ram[base+18:base+24]=b'\0'*6
   params=[base,0,angle,0,speed];device.seed(ram,0);assert lib.lab_movement_original(*params,17)==0;a=device.ram();device.seed(ram,1);result=matrix.Result();assert lib.lab_movement_C(*params,c.byref(result),12)==0;b=device.ram();assert a==b
   words=[int.from_bytes(b[base+i:base+i+2],'big')for i in [18,20,22,26,28,30]]
   rows.append({'angle2':angle,'speed_low16':speed,'integer_translation_words':words[:3],'raw_fraction_words':words[3:],'caller_low14_fractions':[x&0x3fff for x in words[3:]],'C_result':matrix.result_dict(result),'originalGPU_and_C_full_RAM_match':True})
 finally:device.close()
 assert rows[0]['integer_translation_words']==[0,0,65535]and rows[0]['raw_fraction_words']==[0,0,0xc000]
 assert rows[1]['integer_translation_words']==[0,0,1]and rows[1]['raw_fraction_words']==[0,0,0x4000]
 assert rows[2]['integer_translation_words']==[65535,0,0]and rows[3]['integer_translation_words']==[1,0,0]
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'four_originalGPU_signed_movement_examples_match_C','examples':rows,'scope':'Zero initial translation, fixed matrix and isolated pinned GPUoracle; not physical axis labels/gameplay.'}
 (ROOT/'verification/movement-matrix-checked-examples.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows))
if __name__=='__main__':main()
