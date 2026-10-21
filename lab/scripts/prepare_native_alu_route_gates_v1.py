"""Create isolated ALU-image versions of existing qualified checks;retain every assertion."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'scripts'
REPLACE={
 'check_native_deck_retained_faces_v1':'check_native_deck_retained_alu_v1',
 'native-Deck-faces-disc-build-v1':'native-Deck-alu-disc-build-v1',
 'native-Deck-faces-final-geometry-v1':'native-Deck-alu-final-geometry-v1',
 'native-Deck-faces-final-v1':'native-Deck-alu-final-v1',
 'native-deck-retained-faces-final-v1':'native-deck-retained-alu-final-v1',
 'shared-Deck-fallback-faces-final-v1':'shared-Deck-fallback-alu-final-v1',
 'native-Deck-outer-fallback-faces-final-v1':'native-Deck-outer-fallback-alu-final-v1',
 'native-Deck-outer-waits-faces-final-v1':'native-Deck-outer-waits-alu-final-v1',
 'native-Deck-outer-faces-final-v1':'native-Deck-outer-alu-final-v1',
 'native-deck-alias-nesting-faces-final-v1':'native-deck-alias-nesting-alu-final-v1',
 'native-faces-geometry-alias-v1':'native-alu-geometry-alias-v1',
 'native-Deck-outer-connected-faces-v1':'native-Deck-outer-connected-alu-v1',
 'outer-faces-observer-qualified-v1':'outer-alu-observer-qualified-v1',
 'outer-faces-observer-qualification-v1':'outer-alu-observer-qualification-v1',
 'faces-observer-qualified-v1':'alu-observer-qualified-v1',
 'faces-observer-qualification-v1':'alu-observer-qualification-v1',
 'shared-Deck-region-check-faces-v1':'shared-Deck-region-check-alu-v1',
 'native-Deck-faces-startup-heap-v1':'native-Deck-alu-startup-heap-v1',
 'native-Deck-faces-capacity-v1':'native-Deck-alu-capacity-v1',
 'native-Deck-faces-geometry-route-v1':'native-Deck-alu-geometry-route-v1',
 'native-Deck-faces-geometry-v1':'native-Deck-alu-geometry-v1',
 'native-Deck-faces-gameplay-review-v1':'native-Deck-alu-gameplay-review-v1',
 'native-Deck-faces-gameplay-reviewed-v1':'native-Deck-alu-gameplay-reviewed-v1',
}
FILES=[
 ('check_native_faces_geometry_alias_v1.py','check_native_alu_geometry_alias_v1.py'),
 ('check_native_deck_alias_nesting_faces_final_v1.py','check_native_deck_alias_nesting_alu_final_v1.py'),
 ('check_native_deck_outer_connected_faces_v1.py','check_native_deck_outer_connected_alu_v1.py'),
 ('qualify_faces_observer_v1.py','qualify_alu_observer_v1.py'),
 ('qualify_outer_faces_observer_v1.py','qualify_outer_alu_observer_v1.py'),
 ('check_shared_deck_observer_regions_faces_v1.py','check_shared_deck_observer_regions_alu_v1.py'),
 ('run_native_deck_faces_geometry_route_v1.py','run_native_deck_alu_geometry_route_v1.py'),
 ('review_native_deck_faces_geometry_v1.py','review_native_deck_alu_geometry_v1.py')]
def main():
 for old,new in FILES:
  p=S/new;assert not p.exists();text=(S/old).read_text()
  for a,b in REPLACE.items():text=text.replace(a,b)
  p.write_text(text);print(new)
if __name__=='__main__':main()
