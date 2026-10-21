"""Separate read-only watcher cohort for384-byte persistent outer contexts."""
from pathlib import Path
import ast
S=Path(__file__).resolve().parent

def main():
    templates=['deeper_geometry_observer_v2.inc.c','plane_geometry_observer_v3.inc.c','faces_geometry_observer_v1.inc.c','debug_geometry_observer_v1.inc.c']
    for name in templates:
        p=S/('outer_compact_'+name);assert not p.exists()
        p.write_text((S/name).read_text().replace('G4_OUTER_ARENA+slot*576u','G4_OUTER_ARENA+slot*384u'))
    names=[p.name for p in S.glob('shared_deck_scene17_gpu_family_*_observer_v1.py')]
    names += ['qualify_scene17_gpu_family_'+k+'_observer_v1.py'for k in ['geometry','outer','shared','reset','commit','clear_commit']]
    names += ['check_shared_deck_observer_regions_scene17_gpu_family_v1.py','check_scene17_gpu_family_shared_observer_actual_CPU_v1.py','check_scene17_gpu_family_geometry_observer_actual_cpu_v1.py']
    for name in names:
        text=(S/name).read_text().replace('scene17_gpu_family','outer_compact').replace('scene17-gpu-family','outer-compact')
        for template in templates:text=text.replace("'"+template+"'","'outer_compact_"+template+"'")
        if 'outer_observer' in name or name in ['qualify_scene17_gpu_family_geometry_observer_v1.py','check_shared_deck_observer_regions_scene17_gpu_family_v1.py']:
            text=text.replace('576','384').replace('560','368')
        if name=='shared_deck_scene17_gpu_family_outer_observer_v1.py':
            old='csp<base+144u||csp+60u>base+368u||cp<base+144u||cp+78u>base+368u'
            assert text.count(old)==1
            text=text.replace(old,'csp<base+144u||csp+60u>base+368u||cp!=f+4u')
        if name=='qualify_scene17_gpu_family_outer_observer_v1.py':
            text=text.replace("base+(100 if name=='bad_CPU_pointer'else 300)","base+(100 if name=='bad_CPU_pointer'else 20)")
            text=text.replace('put(base+300+64,','put(base+20+64,').replace('put(base+450,1)','put(base+300,1)')
            text=text.replace('two_legal_eighteen_fault_controls','two_legal_eighteen_fault_controls')
        if name=='check_shared_deck_observer_regions_scene17_gpu_family_v1.py':
            text=text.replace('for offset in [16,144,204,559]','for offset in [16,144,204,367]')
        ast.parse(text);p=S/name.replace('scene17_gpu_family','outer_compact');assert not p.exists();p.write_text(text)

if __name__=='__main__':main()
