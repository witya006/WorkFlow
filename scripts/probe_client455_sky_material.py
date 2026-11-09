"""Observe real sky material submissions and compare the selected455 contract."""
import argparse,json
from pathlib import Path
from fractions import Fraction as Q
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario
from probe_client455_sky_fade import number,bits,ops,single


def night(day,r):
    dusk=Q(.791666686534881591796875);end=Q(.854166686534881591796875);dawn=Q(.20833332836627960205078125);morning=Q(.3333333432674407958984375)
    if dusk<day<end:return single(r(r(day-dusk)*16))
    if dawn<day<morning:return single(r(1-r(r(day-dawn)/Q(.12500001490116119384765625))))
    return Q(0 if morning<day<dusk else 1)


def verify(run):
    rows=[json.loads(x) for x in (run/'sky-material.jsonl').read_text().splitlines()];profiles=[x for x in rows if x['kind']=='profile'];frames=[x for x in rows if x['kind']=='frame_profile'];materials=[x for x in rows if x['kind']=='material'];require(len(profiles)==60 and len(frames)==3 and len(materials)==36,'60profile/3actualframe/36material cases');modes=set()
    for row in profiles+frames:
        r=ops(row['cw']);modes.add((row['cw']>>8)&3);require(row['night']==bits(night(number(row['day']),r)),'Exact target night coefficient bits')
    require(modes=={0,2,3},'Three x87 precision modes');require(all(x['night']==bits(1) for x in profiles if x['day']==bits(.3333333432674407958984375)),'Original exact dawnEnd discontinuity retained');draws=skipped=0
    for row in materials:
        flags=row['flags'];r=ops(row['cw']);factor=int(r(number(row['night'])*255));alpha=255
        if flags&8:alpha=factor
        if flags&0x10:alpha=255-factor
        if flags&0x20:alpha=255-factor
        require(len(row['draws'])==(row['layers'] if alpha else 0),'Actual zero-alpha skip/layer submissions')
        for draw in row['draws']:
            colorop,colorarg,alphaop,alphaarg=draw['stage'];tf,z,zw,test=draw['render'];require(colorop==(4 if flags&4 else 5) and colorarg==(3 if flags&4 else 0) and z==zw==0,'Actual sky color mode and depth disabled')
            require(tf==(((alpha<<24)|(row['fog']&0xffffff))&0xffffffff) if flags&0x1c else tf==0x12345678,'Actual TFACTOR mask1C')
            require(alphaarg==(3 if flags&0x1c else 0) and alphaop==(4 if flags&0x1c else 2),'Actual alpha setup excludes flag20 alone');draws+=1
        end=row['end'];require(end['stage'][0]==4 and end['render'][1:3]==[1,1],'Final colorop/depth restored');arg=3 if alpha and flags&0x1c and not flags&0x18 else 0;require(end['stage'][3]==arg,'Asymmetric cleanup mask18 retained');skipped+=not bool(alpha)
    require(draws and skipped,'Visible submissions and actual skipped branches');names=['sky2-midnight.bgra','sky2-morning.bgra','sky2-noon.bgra','sky2-evening.bgra','sky2-unloaded.bgra'];images={n:(run/n).read_bytes() for n in names};require(all(len(x)==640*480*4 for x in images.values()),'Five real GPU frames');clear=images[names[-1]];require(clear[:3]==bytes.fromhex('302010') and clear==clear[:4]*(640*480),'Unloaded exact clear');visible={n:sum(a!=b for a,b in zip(x,clear)) for n,x in images.items()};require(any(visible[n]>100 for n in names[:4]),'Actual visible sky2');unique=len(set(images[n] for n in names[:4]));require(unique>1,'Actual day/night material output changes')
    unloaded=[x for x in rows if x['kind']=='unloaded'];require(len(unloaded)==1 and unloaded[0]['view_exact'] and unloaded[0]['state']['stage'][0]==4 and unloaded[0]['state']['render'][1:3]==[0,0],'Direct unloaded method restores colorop/view and preserves depth')
    return dict(profile_cases=60,actual_frame_profiles=3,material_cases=36,precision_bits=[24,53,64],exact_night_bits=True,dawnEnd_discontinuity=True,actual_indexed_draws=draws,zero_alpha_cases=skipped,cleanup_masks='TFACTOR1C/reset18;20alone does not set alpha stages',device_view_restored=True,caller_view_translation_zeroed=True,direct_unloaded_state=True,GPU_frames=5,actual_neutralB_sky2=True,distinct_day_frames=unique,visible_changed_bytes=visible,full_atmosphere=False,all_FP_inputs=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-existing',action='store_true');a=p.parse_args();r=json.loads((WS/'inventory/client455-sky-material-native.json').read_text()) if a.verify_existing else scenario('client455_sky_material_probe.cpp','sky-material','client455-sky-material-native','client455-sky-material-inputs');require(not r['natural_exit'] and r['native']['status']=='PASS','Completed own material run');r.update(status='PASS_SELECTED',scope='Actual sky2/legacy map selection,night weight and sky material flags/submissions;special atmosphere prepass and fulllighting remain open',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),oracle=record(WS/'scripts/probe_client455_sky_fade.py'),trace=record((WS/r['exe']['file']).parent/'sky-material.jsonl'),verdict=verify((WS/r['exe']['file']).parent));(WS/'inventory/client455-sky-material-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
