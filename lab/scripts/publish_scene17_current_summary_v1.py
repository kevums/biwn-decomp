"""Correct stale top-level status prose while retaining immutable prior evidence."""
from datetime import datetime, timezone
from pathlib import Path
import shutil, sys
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
sys.path.insert(0, str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    packet = load(ROOT)
    s = packet['native_scene_draw_progress']
    assert s['fresh_scene_native_returns'] == 6473 and s['fresh_differing_video_frames'] == 7374
    wp = V/'native-Deck-current-status-v1-current.json'
    wrapper = read(wp)
    out = V/'scene17-current-summary-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    save(out/'previous-wrapper.json', wrapper)
    packet['installed_preview_report'] = packet.get('installed_preview_report', packet['report'])
    packet['report'] = s['report']
    summary = ('The v24 experimental native scene completes 24,978 fresh frames versus 24,962 in its original-scene control. '
               'All 6,473 native scene calls and 38,424 helper calls return with clear monitors. '
               'Final video and selected game fields agree, but 7,374 paired video frames and 323 held-input samples differ. '
               'An identical-input 1,000-frame prefix still has 194 video differences versus 189 for v23. '
               'Direct polling alone has not established fidelity or a whole-game speedup. '
               'The installed checkpoint preview is unchanged; full readable-source rebuilding and physical-console validation remain incomplete. '
               'No new local predictions, training updates or trained weights were adopted in this continuation.')
    for key in ['checked_current_summary', 'checked_answer', 'current_verified_route_summary']:
        packet[key] = summary
    packet['milestone'] = 'Partial native scene reconstruction; fresh route completes, fidelity remains open'
    save(out/'current-status-packet.json', packet)
    shutil.copy2(__file__, out/'publisher-source.py')
    context = ROOT/'native_deck_source_context_v13.py'
    shutil.copy2(context, out/context.name)
    deps = {str(p):sha(p) for p in out.iterdir() if p.is_file()}
    pub = V/'scene17-current-summary-v1-current.json'
    atomic(pub, dict(status='terminal_current_summary_matches_v24_evidence', directory=str(out), dependencies_sha256=deps))
    wrapper.update(packet=str(out/'current-status-packet.json'), dependencies_sha256={**wrapper['dependencies_sha256'], **deps, str(pub):sha(pub)})
    atomic(wp, wrapper)
    for source in [*out.iterdir(), pub, wp, context]:
        if not source.is_file():
            continue
        dest = P/'workbench'/source.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    print('Current headline and detailed v24 facts agree; copied package updated.', flush=True)


if __name__ == '__main__':
    main()
