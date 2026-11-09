"""Verify packed script producers and the actual ordinary CLevel weather owner."""
import argparse
import json
import math
from fractions import Fraction as Q
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,require,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario
from probe_client455_sky_fade import bits,number,ops,single
from probe_client455_sky_lighting import sampler,pack


def verify(run,native):
    rows=[json.loads(x) for x in (run/'weather-owner.jsonl').read_text().splitlines()]
    packed=[x for x in rows if x['kind']=='packed']
    require(len(packed)==90 and {x['tag'] for x in packed}=={0,1,2}
            and {(x['cw']>>8)&3 for x in packed}=={0,2,3},'Three packed producers in three x87 precisions')
    for row in packed:
        value=Q(0) if row['value']=='not_a_number' else Q(float(row['value']))
        converted=int(ops(row['cw'])(value*255))&0xffffffff
        shift=row['tag']*8
        expected=((row['seed']&~(255<<shift))|(converted<<shift))&0xffffffff
        require(row['packed']==expected,'Unclamped double conversion and overlapping DWORD bits '+str(row))
    case=next(x for x in rows if x['kind']=='casefold')
    require(case['flags']==7 and case['environment']=='MiXeD.r3e'
            and case['day_fog']==[bits(900),bits(10000),0xff010203]
            and case['far']==bits(10000),'Uppercase FOG/ENV followed by lowercase weather/scene flags')
    first=next(x for x in rows if x['kind']=='map_owner')
    require(first['packed']==first['owned']==0x00bf3f7f,'Actual map loader consumes persistent material DWORD')
    other=next(x for x in rows if x['kind']=='other_owner')
    require(other['calls']==1 and other['owned']==0x123456c0 and other['first']==first['owned'],
            'Virtual dispatch and per-level weather storage')
    for row in [first,other]:
        require(row['exposure']==bits(single(ops(row['cw'])(Q(row['owned']&255,255)))), 'Only low byte affects global fog exposure')
    frames=[x for x in rows if x['kind']=='frame']
    require(len(frames)==5 and native['native']['frames']==5,'Five actual ordinary world/sky frames')
    for row,color in zip(frames,[0x01020300,0xaabbcc40,0x11223380,0x556677c0,0x8899aaff]):
        rnd=ops(row['cw']);exposure=single(rnd(Q(color&255,255)))
        require(row['owned']==color and row['exposure']==bits(exposure) and row['draws']>0,'Actual level owner feeds ordinary frame and BSP')
        scale=Q(.89999997615814208984375);divisor=int(rnd(Q(289)*single(rnd(rnd(exposure*scale)+scale))))
        require(row['sample_count']==289 and row['divisor']==divisor,'Weather changes actual software-fog exposure divisor')
        sums=[0,0,0]
        for i in range(-8,9):
            for j in range(-8,9):
                radius=single(Q(math.sqrt(i*i+j*j)));height=single(rnd(4-min(radius,Q(4))))
                xyz=[bits(i*1290),bits(single(rnd(rnd(height*5160)*Q(.25)))),bits(-float(j)*1290)]
                color=sampler(xyz,row['params'],row['sun_color'],row['intensity'],rnd)
                for k,shift in enumerate([16,8,0]):sums[k]+=(color>>shift)&255
        require(row['fog']==pack(*[min(255,x//divisor) for x in sums]),'Actual fog aggregate from independent selected arithmetic')
    return dict(packed_cases=90,precision_bits=[24,53,64],case_folded_FOG_ENV_weather=True,
                virtual_owner=True,ordinary_map_load=True,ordinary_frames=5,oracle_grid_samples=1445,
                software_aggregate_cases=5,individual_sample_outputs_compared=False,
                software_precision_bits=sorted({{0:24,2:53,3:64}[(x['cw']>>8)&3] for x in frames}),
                GPU_frames=5,full_lighting=False,all_CRT_FP_inputs=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args()
    file=WS/'inventory/client455-weather-owner-native.json'
    native=json.loads(file.read_text()) if args.verify_existing else scenario('client455_weather_owner_probe.cpp','weather-owner','client455-weather-owner-native','client455-sky-lighting-inputs')
    require(not native['natural_exit'] and native['native']['status']=='PASS','Completed weather owner run')
    require(native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current normal client libraries')
    for key in ['source','exe','map','console','output']:check(native[key])
    run=(WS/native['exe']['file']).parent
    native.update(status='PASS_SELECTED',scope='Actual ordinary CLevel weather owner and script producers;INS/Planet/material consumers and full lighting remain open',
                  driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),
                  world_source=record(WS/'scripts/native/client455_world_probe.cpp'),trace=record(run/'weather-owner.jsonl'),verdict=verify(run,native))
    file.write_text(json.dumps(native,indent=2)+'\n');print(json.dumps(native['verdict']))


if __name__=='__main__':main()
