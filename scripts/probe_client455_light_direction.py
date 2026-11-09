"""Verify actual indexed LitGrass submissions and their direction constants."""
import argparse,json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from compare_client_binaries import WS
from lit_transform455 import value,bits,direction
from probe_client455_lighting_consumers import verify as consumers
from probe_client455_nuclear_registry import main as scenario


def verify(run):
    rows=[json.loads(x) for x in (run/'light-direction.jsonl').read_text().splitlines()]
    require(len(rows)==72 and {((x['cw']>>8)&3,(x['cw']>>10)&3) for x in rows}=={(p,r) for p in [0,2,3] for r in range(4)},'72 actual draws in12 FP modes')
    for row in rows:
        expected=direction(list(map(value,row['world'])),list(map(value,row['input'])),row['cw'])
        require(row['output']==list(map(bits,expected)),'Actual shader19.xyz from independent rational oracle '+str((row['id'],row['cw'],row['output'],list(map(bits,expected)))))
        require(row['draws'] and row['shader_bytes']==300 and row['stride']==36,'Actual LitGrass submission')
    return dict(actual_LitGrass_submissions=72,world_transforms=6,FP_modes=12,shader19_xyz_bits_exact=True,full_CRT=False,full_gameplay=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args();file=WS/'inventory/client455-light-direction-native.json'
    r=load('client455-light-direction-native') if args.verify_existing else scenario('client455_light_direction_gpu_probe.cpp','light-direction','client455-light-direction-native','client455-sky-lighting-inputs',['System/Shader/grass1.vso','System/Shader/LitGrass1.vso'])
    require(not r['natural_exit'] and r['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current completed own client probe');run=(WS/r['exe']['file']).parent
    r.update(status='PASS_SELECTED',scope='Actual CEntity LitGrass inverse/transform/normalization and GPU direction constants in12FP modes;full CRT/gameplay open',
             driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_lighting_consumers_probe.cpp'),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),material_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),
             oracle=record(WS/'scripts/lit_transform455.py'),consumer_verifier=record(WS/'scripts/probe_client455_lighting_consumers.py'),trace=record(run/'light-direction.jsonl'),consumers_trace=record(run/'lighting-consumers.jsonl'),verdict=verify(run),consumer_verdict=consumers(run,r),
             captured_shaders=[record(run/f'draw-shader-{i}.bin') for i in [3,4]],vertices=record(run/'entity-vertices.bin'),resolved_input=record(run/'entity-resolved.r3e'),normal_diagnostic=record(run/'normal-diagnostic.jsonl'))
    file.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
