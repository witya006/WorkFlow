"""Verify actual ordinary lighting, real loaders and CPU sky/fog integration."""
import argparse
import json
import math
import struct
from fractions import Fraction as Q
from pathlib import Path

from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,check,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario
from probe_client455_sky_fade import bits, number, ops, single
from probe_client455_sky_material import night
from probe_client455_sky_atmosphere import sun

MASK = 0xffffffff


def pack(r, g, b):
    return (b | ((g | ((r | 0xffffff00) << 8)) << 8)) & MASK


def mie(day, rnd):
    value = Q(0)
    if Q(.7708333333333334) < day < Q(.7916666865348816):
        elapsed = single(rnd(day-Q(.7708333333333334)))
        value = single(rnd(rnd(elapsed/Q(.02083335258066654))*number(bits(.03))))
    elif Q(.7916666865348816) < day < Q(.8333333134651184):
        ratio = rnd(rnd(day-Q(.7916666865348816))/Q(.04166662693023682))
        value = single(rnd(rnd(1-ratio)*number(bits(.03))))
    return value


def sampler(xyz, parameters, rgb, intensity, rnd):
    def mul(a, b): return single(rnd(a*b))
    def add(a, b): return single(rnd(a+b))
    def reciprocal(a): return single(rnd(1/a))
    def sqrt(a): return single(Q(math.sqrt(float(a))))
    p = list(map(number, parameters))
    point = list(map(number, xyz))
    beta = [add(mul(p[5+i], p[3]), mul(p[11+i], p[4])) for i in range(3)]
    inverse = list(map(reciprocal, beta))
    ray_coeff = [mul(p[8+i], p[3]) for i in range(3)]
    mie_coeff = [mul(p[14+i], p[4]) for i in range(3)]
    square = rnd(p[0]*p[0])
    one_minus, one_plus = single(rnd(1-square)), single(rnd(square+1))
    twice = single(rnd(p[0]*2))
    length_squared = single(rnd(rnd(rnd(point[1]*point[1])+rnd(point[0]*point[0]))+rnd(point[2]*point[2])))
    length = sqrt(length_squared)
    dot = -mul(point[1], reciprocal(length))
    ray = single(rnd(rnd(dot*dot)+1))
    denominator = single(rnd(rnd(twice*dot)+one_plus))
    inv_sqrt = reciprocal(sqrt(denominator)) if denominator else Q(0)
    cube = single(rnd(inv_sqrt*rnd(inv_sqrt*inv_sqrt)))
    phase = mul(one_minus, cube)
    inverse_log = reciprocal(single(Q(math.log(2))))
    channels = []
    for i in range(3):
        optical = mul(inverse_log, mul(-length, beta[i]))
        attenuation = single(Q(math.pow(2, float(optical))))
        scattering = add(mul(ray_coeff[i], ray), mul(mie_coeff[i], phase))
        transmitted = mul(single(rnd(1-attenuation)), scattering)
        value = mul(inverse[i], transmitted)
        value = mul(value, p[1]); value = mul(value, number(rgb[i])); value = mul(value, number(intensity))
        value = max(Q(0), min(Q(1), value))
        channels.append(int(rnd(value*255)) & MASK)
    return pack(*channels)


def verify(run, native):
    rows = [json.loads(x) for x in (run/'lighting.jsonl').read_text().splitlines()]
    texts = [x for x in rows if x['kind'] == 'text']
    require(len(texts) == 4, 'Four actual public script-loader cases')
    endpoint = lambda a,b,c:[bits(a),bits(b),c]
    expected = [
        (endpoint(0,0,0xff123456), endpoint(0,0,0), endpoint(5,5000,0xff123456), 6000, 0, True),
        (endpoint(12.5,1000.5,0xff123456), endpoint(110,6000.25,0xffba9876), endpoint(12.5,1000.5,0xff123456), 1000.5, 2, True),
        (endpoint(0,0,0), endpoint(0,0,0), endpoint(0,0,0xff000000), 6000, 0, False),
        (endpoint(4.5,400,0xff0b0d11), endpoint(2.5,200,0xff030507), endpoint(4.5,400,0xff0b0d11), 400, 0, True),
    ]
    for row, (day, dark, current, far_value, flags, enabled) in zip(texts, expected):
        require(row['day_fog'] == day and row['night_fog'] == dark and row['fog'] == current
                and row['far'] == bits(far_value) and row['flags'] == flags and row['enabled'] == enabled,
                'Exact script endpoints/case/default ownership '+str(row['id']))
        require(row['main'] == (endpoint(0,0,0) if row['id'] == 2 else current), 'Actual main-fog defaults')
    binary = [x for x in rows if x['kind'] == 'r3x']
    require(len(binary) == 5 and native['native']['R3X_cases'] == 6, 'Five valid R3X cases and rejected invalid version')
    day, dark = endpoint(0,0,0), endpoint(0,0,0)
    for i, row in enumerate(binary):
        flags = [0,4,8,0,12][i]
        if flags&4: day=endpoint(12.5+i,1000.5+i,0xff123456+i)
        if flags&8: dark=endpoint(110+i,6000.25+i,0xffba9876+i)
        require(row['input_flags'] == flags and row['day_fog'] == day and row['night_fog'] == dark
                and row['flags'] == 2, 'Real R3X load/preserved absent endpoints')
    actual = next(x for x in rows if x['kind'] == 'actual_map')
    resource = next(x for x in native['inputs'] if x['file'].lower().endswith('/map/neutralb/neutralb.r3x'))
    data = (WS/resource['file']).read_bytes()
    require(data[:4] == struct.pack('<f',1.1), 'Real neutralB R3X version')
    flags, ds, de, dc, ns, ne, nc = struct.unpack_from('<IffIffI', data, 4)
    if flags&4: day=endpoint(ds,de,dc)
    if flags&8: dark=endpoint(ns,ne,nc)
    require(actual['day_fog'] == day and actual['night_fog'] == dark, 'Actual pinned map endpoint ownership')
    mie_rows = [x for x in rows if x['kind'] == 'mie']
    require(len(mie_rows) == 27 and {(x['cw']>>8)&3 for x in mie_rows} == {0,2,3}, 'Mie boundary cases in three precisions')
    for row in mie_rows:
        require(row['value'] == bits(mie(number(row['day']), ops(row['cw']))), 'Exact selected Mie transition bits')
    frames = [x for x in rows if x['kind'] == 'frame']
    samples = [x for x in rows if x['kind'] == 'sample']
    require(len(frames) == 5 and len(samples) == 867, 'Five ordinary frames and867 real CPU samples')
    coefficient = [.8,1,1,1,0,
        .000006954956461413531,.00001176111436507199,.000024387845769524574,
        .000000415093353467455,.0000007019397685326112,.0000014555422467310564,
        .00574059784412384,.007399687077850103,.01051431242376566,
        .0013337875716388226,.001734457560814917,.002497619017958641]
    for row in frames:
        if not row['enabled']:
            require(row['fog'][2] == row['old_fog'] and row['tint'] == frames[3]['tint']
                    and row['direct'] == frames[3]['direct'] and row['position'] == frames[3]['position'],
                    'Disabled ordinary frame preserves existing lighting')
            continue
        rnd = ops(row['cw']); day_value = number(row['day'])
        require(row['night'] == bits(night(day_value,rnd)) and row['alpha'] == sun(day_value,rnd)[4], 'Actual frame clock/night/alpha')
        params = list(map(bits,coefficient));params[4]=bits(mie(day_value,rnd))
        require(row['params'] == params, 'Pinned initial coefficients and current Mie')
        require(row['exposure'] == bits(single(rnd(Q(128 if row['id']==2 else 0)/255))), 'Low-byte exposure API')
        channels = [int(rnd(number(x)*255))&MASK for x in row['sun_color'][:3]]
        old = row['old_fog']; red=((channels[0]>>2)+((old>>18)&63)+128)|0xffffff00
        green=(channels[1]&0xfffffffc)+((old>>8)&252)+512
        blue=(channels[2]>>2)+((old>>2)&63)+128
        require(row['tint'] == ((red<<16)|(green<<6)|blue)&MASK, 'Actual frame uses previous fog for tint')
        direct = [int(rnd(rnd(number(x)*number(row['alpha']))*255))&MASK for x in row['sun_color'][:3]]
        require(row['direct'] == pack(*direct), 'Actual direct-color alpha packing')
        previous_orbit = float(number(row['old_sun'][2]))
        angle = previous_orbit*-math.pi
        yy = -float(number(row['previous_far']))*math.sin(angle)
        wanted = [yy*.5,yy*math.cos(math.pi/6),float(number(row['previous_far']))*math.cos(angle)]
        require(all(abs(float(number(a))-b) <= .02+abs(b)*2e-5 for a,b in zip(row['position'],wanted)), 'Previous-orbit position/current far')
        if row['flags']&2:
            weight=number(row['night']);complement=rnd(1-weight)
            values=[bits(single(rnd(rnd(number(n)*weight)+rnd(number(d)*complement)))) for d,n in zip(row['day_fog'][:2],row['night_fog'][:2])]
            color=[int(rnd(rnd(Q((row['night_fog'][2]>>s)&255)*weight)+rnd(Q((row['day_fog'][2]>>s)&255)*complement)))&MASK for s in [16,8,0]]
            require(row['fog'] == values+[pack(*color)], 'Actual weighted day/night fog')
            continue
        selected=[x for x in samples if x['frame'] == row['id']]
        require(len(selected) == 289 and {x['index'] for x in selected} == set(range(289)), 'Complete17x17 actual sample coverage')
        sums=[0,0,0]
        for sample in selected:
            i,j=divmod(sample['index'],17); x,z=i-8,j-8
            distance=single(Q(math.sqrt(x*x+z*z)));height=single(rnd(4-min(distance,Q(4))))
            position=[bits(x*1290),bits(single(rnd(rnd(height*5160)*Q(.25)))),bits(-float(z)*1290)]
            require(sample['xyz'] == position, 'Exact selected grid geometry')
            color=sampler(position,row['params'],row['sun_color'],row['intensity'],rnd)
            require(sample['color'] == color, 'Actual software sky packed color '+str((row['id'],sample['index'])))
            for k,s in enumerate([16,8,0]):sums[k]+=(color>>s)&255
        scale=Q(.89999997615814208984375)
        factor=single(rnd(rnd(number(row['exposure'])*scale)+scale));divisor=int(rnd(Q(289)*factor))
        require(row['sample_count'] == 289 and row['divisor'] == divisor
                and row['fog'][2] == pack(*[min(255,x//divisor) for x in sums]), 'Actual289sample fog aggregation/exposure')
    draws = next(x for x in rows if x['kind'] == 'map_draw')
    mixed = [x for x in rows if x['kind'] == 'fog_frame']
    require(len(mixed) == 3, 'Three additional nontrivial ordinary fog blends')
    for row in mixed:
        rnd=ops(row['cw']);weight=night(number(row['day']),rnd);complement=rnd(1-weight)
        require(row['night'] == bits(weight) and row['mie'] == bits(mie(number(row['day']),rnd)), 'Actual mixed frame night/Mie')
        values=[bits(single(rnd(rnd(number(n)*weight)+rnd(number(d)*complement)))) for d,n in zip(row['day_fog'][:2],row['night_fog'][:2])]
        channels=[int(rnd(rnd(Q((row['night_fog'][2]>>s)&255)*weight)+rnd(Q((row['day_fog'][2]>>s)&255)*complement)))&MASK for s in [16,8,0]]
        require(row['flags'] == 2 and row['fog'] == values+[pack(*channels)], 'Exact nontrivial ordinary fog blend')
    require(draws['submissions'] > 0 and draws['first_texture_factor'] == draws['tint'], 'Ordinary map binds actual tint before BSP submissions')
    images=[(run/n).read_bytes() for n in ['lighting-midnight.bgra','lighting-noon.bgra','lighting-dusk.bgra','lighting-fog2.bgra','lighting-disabled.bgra']]
    require(all(len(x) == 640*480*4 for x in images) and len(set(images)) >= 3, 'Five real complete GPU frames with changing sky')
    return dict(status='PASS_SELECTED',text_cases=4,R3X_valid_cases=5,R3X_invalid_version=1,
                mie_cases=27,mie_precision_bits=[24,53,64],software_precision_bits=sorted({{0:24,2:53,3:64}[(x['cw']>>8)&3] for x in frames if x['id']<3}),ordinary_frames=5,additional_fog_frames=3,software_samples=867,
                selected_software_packed_bits_exact=True,software_aggregate_cases=3,
                previous_fog_tint=True,previous_orbit_position=True,disabled_preserves=True,
                actual_map_submissions=draws['submissions'],actual_texture_factor_bind=True,
                GPU_frames=5,full_lighting=False,all_CRT_FP_inputs=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args()
    file=WS/'inventory/client455-sky-lighting-native.json'
    native=json.loads(file.read_text()) if args.verify_existing else scenario('client455_sky_lighting_probe.cpp','sky-lighting','client455-sky-lighting-native','client455-sky-lighting-inputs')
    require(not native['natural_exit'] and native['native']['status']=='PASS','Completed own lighting run')
    require(native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json')
            and native['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'), 'Current normal libraries and resources')
    for key in ['source','exe','map','console','output']:
        check(native[key])
    run=(WS/native['exe']['file']).parent
    native.update(status='PASS_SELECTED',scope='Ordinary frame lighting and both fog branches with real script/R3X loaders and selected CPU/GPU consumers;full lighting remains open',
                  driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),
                  world_source=record(WS/'scripts/native/client455_world_probe.cpp'),trace=record(run/'lighting.jsonl'),verdict=verify(run,native))
    file.write_text(json.dumps(native,indent=2)+'\n');print(json.dumps(native['verdict']))


if __name__=='__main__':main()
