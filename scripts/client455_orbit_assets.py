"""Stage immutable authored orbital textures into either owned runtime."""
import json
from pathlib import Path
from client455_asset_staging import stage_asset,sha

ROOT=Path(__file__).resolve().parents[1]

def stage_orbit_assets(runtime):
    runtime=Path(runtime).resolve()
    if not runtime.is_relative_to((ROOT/'work').resolve()):
        raise ValueError('Orbital assets require an owned runtime')
    manifest=json.loads((ROOT/'config/lobby-orbit-assets.json').read_text(encoding='utf-8-sig'))
    rows=[]
    for row in manifest['assets']:
        source=(ROOT/row['file']).resolve();target=(runtime/row['runtime']).resolve()
        if not source.is_relative_to((ROOT/'work/client-art/lobby-orbit').resolve()) or not target.is_relative_to(runtime):
            raise ValueError('Orbital texture path escapes its owned root')
        stage_asset(source,target,row['sha256'],owned_immutable=source)
        rows.append(dict(file=row['runtime'],sha256=sha(target),bytes=target.stat().st_size))
    return rows
