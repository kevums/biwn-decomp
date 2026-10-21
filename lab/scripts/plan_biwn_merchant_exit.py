"""Ask the local planner for waypoints grounded in an actual ground-floor room.

This is a guided source-data interpretation test, not an execution verdict.
The checkpoint comes from ordinary elevator inputs, with no scene RAM transplant.
"""
import argparse, fcntl, hashlib, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import lmstudio
import sdk_thinking_override_probe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repair-from', type=Path)
    args = parser.parse_args()
    sdk_thinking_override_probe.install()
    checkpoint = ROOT / 'runs/merchant-exit-discovery-20261017T083450.542060Z/reference'
    raw = (checkpoint / 'final-RAM.bin').read_bytes()
    get = lambda address, width=2: int.from_bytes(raw[address:address + width], 'big')
    assert [get(a) for a in [0x49c60, 0x49c62, 0x49c64]] == [2, 0, 312]
    room = get(0x49c78, 4)
    base = get(get(0x49c18, 4) + 8, 4)
    first = base + get(room + 22) * 6
    evidence = dict(checkpoint=str(checkpoint / 'report.json'), RAM_sha256=hashlib.sha256(raw).hexdigest(),
                    player=dict(X=get(0x49c50, 4), Z=get(0x49c56, 4)),
                    floor=get(0x49c62), scene=get(0x49c64),
                    bounds=dict(X_min=get(0x49c80, 4), X_max=get(0x49c7c, 4),
                                Z_min=get(0x49c88, 4), Z_max=get(0x49c84, 4)),
                    room_width=get(room + 6), room_height=get(room + 8),
                    door=dict(key=get(first), flags=hex(get(first + 2)), target=hex(get(first + 4))))
    system = ('You are the local Route Planner for a source-verified game restoration. '
              'Treat the supplied recovered records as evidence. Return JSON only. '
              'Do not claim execution or successful reachability. Do not invent game semantics.')
    prompt = ('Find an exit path from this actual ground-floor interior room. Evidence:\n' +
              json.dumps(evidence, indent=2) + '\nRecovered source boundary rule: the east X_max edge '
              'has key = room_height + room_width + floor((Z_max-playerZ)/64). '
              'This room has a single boundary record with the supplied key. Flags & 0x7000 are nonzero; '
              'target FFFF means outdoor exit if floor is zero. Other directions are not needed for this task. '
              'Choose the midpoint of the matching east-edge Z strip. First waypoint: room X center and '
              'that Z midpoint, staying inside the room. Second waypoint: X32 beyond the east boundary at '
              'the same Z. The controller only reads player state and chooses ordinary buttons; it cannot '
              'change positions or readiness. Return exactly {"waypoints":[{"X":integer,"Z":integer},'
              '{"X":integer,"Z":integer}],"position_tolerance":8,"opening_A_frames":0,"stop_scene_mode":1}.')
    repair = None
    if args.repair_from:
        previous = json.loads((args.repair_from / 'protocol.json').read_text())
        assert previous['status'] == 'terminal_planner_failed' and previous['evidence'] == evidence
        draft = (args.repair_from / 'raw-response.txt').read_text()
        feedback = ('The preceding draft used the upper Z edge of the strip, not its midpoint. '
                    'Solve 4 <= (42688-Z)/64 < 5, and choose the midpoint of the resulting 64-unit interval. '
                    'Keep the other requested fields. Return corrected JSON only.')
        prompt += '\nPrevious draft (quoted evidence):\n' + draft + '\nCoordinator feedback:\n' + feedback
        repair = dict(directory=str(args.repair_from.resolve()), feedback=feedback,
                      response_sha256=hashlib.sha256(draft.encode()).hexdigest())
    out = ROOT / 'runs' / ('local-merchant-exit-planner-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    print(out, flush=True)
    record = dict(status='pending', directory=str(out), role='local Route Planner', model='advertising-scholar',
                  evidence=evidence, system=system, prompt=prompt, new_training=False,
                  directed_repair=repair,
                  scope='Guided arithmetic from coordinator-recovered geometry and boundary semantics. No execution or autonomy claim.')
    transcript = out / 'prompts-and-responses.txt'
    transcript.write_text('SYSTEM\n' + system + '\nUSER\n' + prompt + '\n')
    (out / 'protocol.json').write_text(json.dumps(record, indent=2) + '\n')
    with (ROOT / 'runs/.inference.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'], text=True))
        assert len(models) == 1 and models[0]['identifier'] == 'advertising-scholar' and models[0]['status'] == 'idle'
        chat = lmstudio.Chat(system)
        chat.add_user_message(prompt)
        started = time.monotonic()
        response = lmstudio.llm('advertising-scholar').respond(chat, config={
            'temperature': 0.1, 'maxTokens': 400, 'raw': {'fields': [
                {'key': 'llm.prediction.reasoning.enableThinking', 'value': False},
                {'key': 'ext.virtualModel.customField.enableThinking', 'value': False},
                {'key': 'ext.virtualModel.customField.preserveThinking', 'value': False}]}})
        record['seconds'] = time.monotonic() - started
    answer = response.content
    (out / 'raw-response.txt').write_text(answer)
    with transcript.open('a') as stream:
        stream.write('\nASSISTANT\n' + answer + '\n')
    try:
        plan = json.loads(answer)
        assert plan == dict(waypoints=[dict(X=12864, Z=42400), dict(X=13024, Z=42400)],
                            position_tolerance=8, opening_A_frames=0, stop_scene_mode=1), plan
        record.update(status='source_grounded_waypoints_pass_execution_pending', plan=plan)
        (out / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    except Exception as error:
        record.update(status='terminal_planner_failed', error=repr(error))
        raise
    finally:
        (out / 'protocol.json').write_text(json.dumps(record, indent=2) + '\n')
        (ROOT / 'verification/local-merchant-exit-plan-current.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(status=record['status'], seconds=record['seconds'], plan=plan)), flush=True)


if __name__ == '__main__':
    main()
