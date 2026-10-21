"""Separate fresh Deck experiment with two existing selector repairs declared."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parent=ROOT/'scripts/run_biwn_native_format_deck_pair.py';source=parent.read_text()
    text=source.replace('native-format-deck-pair','native-format-selector-deck-pair').replace('fresh_format_deck_pair','fresh_format_selector_deck_pair')
    marker="    source=ROOT/'scripts/native_gameplay_observer.c';"
    assert text.count(marker)==1
    addition='''    # Same declared selector repairs in both lanes; never patch guest RAM.
    recipe_path=ROOT/'verification/interactive-preview-recipe.json'
    recipe=json.loads(recipe_path.read_text());command=recipe['candidate']
    overlay_path=Path(command[command.index('--experimental-code-overlay')+1])
    overlay=json.loads(overlay_path.read_text());repairs=[row for row in overlay['patches']if int(row['address'],16)in [0x464a6,0x10ac2]]
    assert len(repairs)==2 and sum(len(bytes.fromhex(row['original']))for row in repairs)==38
    candidate_disc=out/'BIWN-23-format-selector-repaired-experimental.cdi'
    shutil.copyfile(build['derived_disc'],candidate_disc)
    repair_intervals=[]
    for row in repairs:
        old=bytes.fromhex(row['original']);new=bytes.fromhex(row['replacement']);assert len(old)==len(new)and len(old)%2==0
        at=offset+int(row['address'],16)-0x4000;repair_intervals.append((at,at+len(old)))
        for path in [candidate_disc,control]:
            with path.open('r+b')as stream:
                stream.seek(at);assert stream.read(len(old))==swap16(old)
                stream.seek(at);stream.write(swap16(new));stream.flush();os.fsync(stream.fileno())
    # Independently compare the entire patched candidate against its parent.
    repair_changed=0;position=0
    with Path(build['derived_disc']).open('rb')as a,candidate_disc.open('rb')as b:
        while True:
            left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
            if not left:break
            for i,(x,y)in enumerate(zip(left,right)):
                if x!=y:assert any(lo<=position+i<hi for lo,hi in repair_intervals);repair_changed+=1
            position+=len(left)
    # Control must still differ only in the two formatting redirects.
    pair_changed=0;position=0
    with candidate_disc.open('rb')as a,control.open('rb')as b:
        while True:
            left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
            if not left:break
            for i,(x,y)in enumerate(zip(left,right)):
                if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);pair_changed+=1
            position+=len(left)
    assert pair_changed==differences==12
    repair_proof=dict(status='separate_shared_selector_repair_discs_built',parent_disc=build['derived_disc'],parent_disc_sha256=sha(build['derived_disc']),
        candidate=str(candidate_disc),candidate_sha256=sha(candidate_disc),control=str(control),control_sha256=sha(control),
        parent_build_proof=str(bp),parent_build_proof_sha256=sha(bp),selector_repairs=repairs,
        declared_shared_repair_bytes=38,actual_candidate_changed_CDI_bytes=repair_changed,pair_changed_CDI_bytes=pair_changed,
        source_overlay=str(overlay_path),source_overlay_sha256=sha(overlay_path),host_guest_RAM_writes=0,
        default_promoted=False,whole_game_complete=False,
        scope='Two existing experimental selector/count repairs at464A6/10AC2 applied to both derived discs. Native compiled word-scan loader is inherited. Parent entry proof covers shared startup only; repaired gameplay requires this new run. Not untouched-original behavior.')
    save(out/'shared-selector-repair-build.json',repair_proof)
'''
    text=text.replace(marker,addition+marker)
    needle="for lane,disc in [('candidate',Path(build['derived_disc'])),('control',control)]:"
    assert text.count(needle)==1
    text=text.replace(needle,"for lane,disc in [('candidate',candidate_disc),('control',control)]:")
    needle="control_change_scope='Only two6byte formatting redirects restored; identical payload/heap/startup/other rebuilt helpers.',"
    assert text.count(needle)==1
    text=text.replace(needle,needle+"shared_selector_repairs=repair_proof,entry_proof_shared_startup_only=True,")
    needle="[Path(__file__),observer,source,library,probe,inputs,prefix,core]"
    assert text.count(needle)==1
    text=text.replace(needle,"[Path(__file__),observer,source,library,probe,inputs,prefix,core,recipe_path,overlay_path,out/'shared-selector-repair-build.json']")
    needle='2600fresh HLEboot frames per lane with same ordinary pad schedule.'
    assert text.count(needle)==1
    text=text.replace(needle,needle+' Both discs contain the same two declared38byte selector/count repairs; not untouched-original behavior.')
    path=ROOT/'scripts/run_biwn_native_format_selector_deck_pair.py';compile(text,str(path),'exec');path.write_text(text)
    out=ROOT/'verification/native-format-selector-deck-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/parent.name).write_bytes(parent.read_bytes());(out/path.name).write_bytes(path.read_bytes())
    proof=dict(status='separate_selector_repaired_fresh_Deck_pair_prepared',directory=str(out),parent=str(parent),parent_sha256=sha(parent),derived=str(path),derived_sha256=sha(path),
               transformations=['Separate outputs/status names','Build new candidate/control CDI copies with identical existing38byte selector repairs','Full-file raw CDI difference checks','Bind source overlay and repair build proof; parent entry proof is shared-startup only'],
               frame_or_observer_tests_removed=False,ordinary_pad_schedule_unchanged=True,guest_RAM_patch_added=False,new_training=False,whole_game_complete=False)
    (out/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n');(ROOT/'verification/native-format-selector-deck-preparation-current.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(path)
if __name__=='__main__':main()
