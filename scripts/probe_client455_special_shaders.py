"""Compile the four actual shader sources through the ordinary device owner."""
import argparse,json,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from probe_client455_nuclear_registry import main as scenario
from prepare_client455_special_shaders import parse_init


def verify(run,r):
    native=r['native'];require(native['actual_programs']==4 and native['restore_cycles']==3 and native['retained_COM_checks']==3 and native['overlap_objects']==2 and native['overlap_parameter_bytes']==196 and native['published_count_remains_zero'],'Actual device owner/registry/binary object semantics')
    require(native['handles_before']==native['handles_after'] and native['warnings']==0,'Real file handles balanced/no shader warnings')
    rows=[json.loads(x) for x in (run/'special-shaders.jsonl').read_text().splitlines()];require(len(rows)==4,'Actual four GPU bytecode/reflection records')
    require([x['name'] for x in rows]==['vFraction.sho','vPlazma.sho','pFraction.sho','pPlazma.sho'],'Actual binary list names')
    for i,row in enumerate(rows):
        code=(run/f'program-{i}.bin').read_bytes();require(len(code)==row['bytes'] and struct.unpack_from('<I',code)[0]==row['version']==(0xfffe0200 if i<2 else 0xffff0200),'Real CreateVertex/PixelShader bytecode2.0')
    original=parse_init((run/'System/shader/init.r3o').read_bytes());require(original==load('client455-special-shaders-inputs')['init'],'Pinned staged shader list restored after fixture')
    fixture=parse_init((run/'fixture.r3o').read_bytes());require(len(fixture['objects'])==2 and fixture['objects'][0]['parameters']==[bytes(range(196)).hex()],'Independent serialized fixture interpretation')
    require(all(row['constants'] for row in rows),'Actual constant table reflection')
    return dict(programs=4,shader_model='2.0',ordinary_restore_cycles=3,actual_invalidation_and_final_teardown=True,bytecode_stable=True,retained_COM_lifetime=True,overlap_objects=2,parameter_bytes=196,published_count_remains_zero=True,handles_balanced=True,full_special_draw=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args();r=load('client455-special-shaders-native') if args.verify_existing else scenario('client455_special_shaders_probe.cpp','special-shaders','client455-special-shaders-native',expected_frames=0)
    require(not r['natural_exit'] and r['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current ordinary engine owner run');run=(WS/r['exe']['file']).parent
    r.update(status='PASS_SELECTED',scope='Actual binary special shader registry through ordinary device restore/invalidate;material draw/Init.r3s fallback remain open',driver_script=record(Path(__file__)),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),trace=record(run/'special-shaders.jsonl'),outputs=[record(run/f'program-{i}.bin') for i in range(4)]+[record(run/'fixture.r3o')],verdict=verify(run,r))
    (WS/'inventory/client455-special-shaders-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
