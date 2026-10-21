"""Reuse finite observer proofs only after exact rendered-monitor identity."""
from datetime import datetime,timezone
from pathlib import Path
import shared_deck_input_arena_image_full_observer_v2 as old
import shared_deck_frame_phased_image_full_observer_v3 as new
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    old_path=V/'native-input-arena-disc-build-v1-current.json';new_path=V/'frame-acquire-phased-disc-build-v1-current.json'
    old_build,new_build=read(old_path),read(new_path)
    previous,current=old.resource_monitor(old_build),new.resource_monitor(new_build)
    assert previous==current,'Resource/input observer bindings changed; prior finite results cannot be transferred'
    out=V/'frame-phased-resource-observer-identity-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    monitor=out/'identical-resource-input-monitor.c';monitor.write_text(current);names=[]
    for name in ['resource-input-arena-observer-qualified-v1','resource-input-observer-owner-order-v1','resource-input-observer-actual-wait-CPU-v1','resource-input-observer-actual-input-CPU-v1']:
        path=V/(name+'-current.json');prior=read(path)
        assert prior['status'].startswith('terminal_')and'failed'not in prior['status']
        for p,h in prior['source_sha256'].items():assert sha(p)==h,p
        receipt=dict(prior,status='terminal_identical_resource_input_monitor_reuses_prior_finite_qualification',directory=str(out),previous_terminal_status=prior['status'],previous_proof=str(path),new_v40_execution=False,qualification_reused_only_for_identical_monitor=True,source_sha256={**prior['source_sha256'],**{str(p):sha(p)for p in [Path(__file__),old_path,new_path,path,Path(old.__file__),Path(new.__file__),monitor]}})
        target=V/('frame-phased-image-'+name+'-current.json');save(out/(name+'.json'),receipt);save(target,receipt);names.append(str(target))
    save(out/'review.json',dict(status='terminal_resource_input_observer_body_and_bindings_identical_v39_v40',proofs=names,new_execution=False,new_predictions=0,new_training=False))
    print('Bound four unchanged finite observer proofs; no new CPU/game execution.',flush=True)


if __name__=='__main__':main()
