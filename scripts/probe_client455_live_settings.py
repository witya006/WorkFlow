"""Exercise the real settings window after live entry; credentials stay on stdin."""
import json
import os
import sys
from pathlib import Path
from compare_client_binaries import WS
from client455_asset_staging import sha
import probe_client455_live_launcher


def main():
    previous = os.environ.get('RF455_OBSERVE_SETTINGS')
    os.environ['RF455_OBSERVE_SETTINGS'] = '1'
    try:
        sys.argv = ['probe_client455_live_launcher.py', '--authenticate', '--interactive',
                    '--own-login', '--select-character', '--world-map-index', '0',
                    '--observe-entry', '--nation', 'Russia', '--resolution', '1920x1080']
        probe_client455_live_launcher.main()
    finally:
        if previous is None:
            os.environ.pop('RF455_OBSERVE_SETTINGS', None)
        else:
            os.environ['RF455_OBSERVE_SETTINGS'] = previous
    live_path = WS / 'artifacts/client455-progress/client455-world-entry-live-russia-native.json'
    live = json.loads(live_path.read_text())
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    samples = [event['value'] for event in events if event.get('kind') == 'debug_string'
               and event.get('value', '').startswith('RF455 Protocol:settings-live:')]
    phases = [value.split(':')[2:] for value in samples]
    passed = (len(phases) == 6 and [p[0] for p in phases] == [str(i) for i in range(6)]
              and all(p[1] == '1' for p in phases))
    run = (WS / live['staged_executable']).parent
    names = ['settings-world-before.png', 'settings-world-menu.png',
             'settings-world-menu-applied.png', 'settings-world-enhanced.png',
             'settings-world-restored.png']
    def record(path):
        return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))
    frames = [record(run / name) for name in names if (run / name).is_file()]
    passed = passed and len(frames) == len(names)
    report = dict(status='PASS' if passed else 'FAIL',
                  scope='Live own-client graphics tab, apply and restore lighting/character visibility; '
                        'not exhaustive settings or visual parity acceptance',
                  executable=live['executable'], live_entry=record(live_path),
                  script=record(Path(__file__)),
                  observer=record(WS / 'scripts/native/client455_live_settings_observation.inc'),
                  phases=samples, frames=frames, resolution=[1920, 1080],
                  server_files_modified=False, credentials_persisted=False,
                  physical_mouse_keyboard_tested=False, M6='OPEN', M9='OPEN')
    destination = WS / 'inventory/client455-live-settings.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], phases=samples, frames=frames)))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
