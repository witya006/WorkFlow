"""Compare the live NeutralB frames before and after staging the selected sky."""
import json
from pathlib import Path

from PIL import Image

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASELINE = WS / 'artifacts/client455-progress/before182'
SKY_DIR = 'map/neutralb/sky2'
SKY_INPUTS = {f'{SKY_DIR}/neutralbsky2.{suffix}' for suffix in ('r3e', 'r3m', 'r3t')}
BACKGROUND = (32, 90, 460, 190)


def read_json(file):
    return json.loads(file.read_text())


def relative_inputs(report):
    run = Path(report['staged_executable']).parent
    result = {}
    for row in report['inputs']:
        name = Path(row['file']).relative_to(run).as_posix().lower()
        # The Windows WaveList.spt appears with two spellings in the manifest.
        existing = result.setdefault(name, row)
        require(existing['sha256'] == row['sha256'], 'Conflicting staged input: ' + name)
    return result


def background_pixels(frame):
    check(frame)
    with Image.open(WS / frame['file']) as image:
        require(image.size == (640, 500), 'Comparable world frame dimensions')
        pixels = list(image.convert('RGB').crop(BACKGROUND).get_flattened_data())
    return dict(black=pixels.count((0, 0, 0)), distinct_rgb=len(set(pixels)), total=len(pixels))


def main():
    baseline_path = BASELINE / 'inventory/client455-world-observation-checkpoint.json'
    before = read_json(baseline_path)
    after = read('world-observation-checkpoint')
    require(before['normal_executable'] == after['normal_executable']
            and before['normal_link_sha256'] == after['normal_link_sha256']
            and after['normal_link_sha256'] == sha(path('normal-link')), 'A/B must use the identical own PE')
    old_report_path = BASELINE / before['source_report']['file']
    require(sha(old_report_path) == before['source_report']['sha256'], 'Pinned baseline report changed')
    check(after['source_report'])
    old_report, new_report = read_json(old_report_path), read_json(WS / after['source_report']['file'])
    for report in (old_report, new_report):
        require(sha(WS / report['staged_executable']) == after['normal_executable']['sha256'],
                'Actual staged PE differs')
    old_inputs, new_inputs = relative_inputs(old_report), relative_inputs(new_report)
    require(set(new_inputs) - set(old_inputs) == SKY_INPUTS and
            all(new_inputs.get(name, {}).get('sha256') == row['sha256'] for name, row in old_inputs.items()),
            'A/B inputs differ by more than the three stock sky files')
    for name in SKY_INPUTS:
        check(new_inputs[name])
    require(len(before['samples']) == len(after['samples']) == 3, 'Comparable passive observations')
    for a, b in zip(before['samples'], after['samples']):
        require(all(a[key] == b[key] for key in a if key != 'elapsed_ms'), 'Camera/avatar state differs')
    comparisons = []
    for a, b in zip(before['frames'], after['frames']):
        require(a['sample_index'] == b['sample_index'], 'Mismatched capture samples')
        dark, textured = background_pixels(a), background_pixels(b)
        require(dark['black'] == dark['total'] and textured['black'] == 0 and textured['distinct_rgb'] > 100,
                'Expected black background to become textured terrain')
        comparisons.append(dict(sample=a['sample_index'], before_frame=a, after_frame=b,
                                before_region=dark, after_region=textured))
    require(len(comparisons) == 2, 'Expected early and settled comparisons')
    fresh = dict(after['fresh_evidence'], **{'world-observation-checkpoint': record(path('world-observation-checkpoint'))})
    save('neutralb-sky-checkpoint', dict(
        status='PASS_LIVE_TERRAIN_VISIBLE_WITH_PINNED_SKY_ASSETS',
        normal_executable=after['normal_executable'], normal_link_sha256=after['normal_link_sha256'],
        script=record(Path(__file__)), fresh_evidence=fresh, baseline=record(baseline_path),
        baseline_report=record(old_report_path), common_inputs=len(old_inputs),
        sky_assets=[new_inputs[name] for name in sorted(SKY_INPUTS)],
        region_xyxy=BACKGROUND, comparisons=comparisons, matched_camera_samples=3,
        sky_pixels_visible_at_sampled_pitch=False, movement_verified=False,
        renderer_changed=False, server_modified=False, M6='OPEN', M9='OPEN'))
    print(f'PASS: {len(old_inputs)} common inputs, {len(SKY_INPUTS)} added sky assets, two terrain comparisons')


if __name__ == '__main__':
    main()
