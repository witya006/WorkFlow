"""Verify actual sky buffers/shader/prepass states and real neutralB GPU output."""
import argparse,hashlib,json,math,struct
from pathlib import Path
from fractions import Fraction as Q
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario
from probe_client455_sky_fade import number,bits,ops,single
from probe_client455_sky_projection import perspective


def floats(data):return [float(number(x)) for x in data]
def f(x):return float(single(Q(x)))
def near(a,b):return all(math.isfinite(x) and abs(x-y)<=2e-5+abs(y)*2e-6 for x,y in zip(a,b))
def matrix(a,b):return [sum(a[r*4+k]*b[k*4+c] for k in range(4)) for r in range(4) for c in range(4)]
def transpose(m):return [m[c*4+r] for r in range(4) for c in range(4)]
def sun(day,r):
    orbit=single(r(r(r(r(day-Q(.25))/Q(.5416666865348816))*Q(.949999988079071))+Q(.02500000037252903)));angle=number(bits(.025));scale=Q(1);alpha=Q(0)
    if Q(.25)<day<Q(.7916666865348816):
        angle=orbit;alpha=Q(1)
        if day<Q(.375):scale=single(r(1/single(r(r(r(day-Q(.25))*8)*Q(1.5))+1)))
        elif day>Q(.7083333134651184):scale=single(r(1/single(r(r(Q(1.5)-r(r(day-Q(.7083333134651184))/Q(.08333337306976318))*Q(1.5)))+1)))
        else:scale=number(bits(.4))
    elif orbit<=Q(.02500000037252903):alpha=single(r(r(max(number(bits(-.1)),min(Q(0),orbit))*10)+1))
    elif orbit>=Q(.9750000238418579):alpha=single(r(1-r(r(min(orbit,number(bits(1.15)))-Q(.9750000238418579))/Q(.1749999523162842))))
    theta=single(r(r(abs(r(angle-Q(.5)))*2)*Q(1.570796370506287)));phi=number(bits(4.71238899230957 if angle<Q(.5) else 1.570796370506287));return [bits(x) for x in (theta,phi,orbit,scale,alpha,Q(100))]


def verify(run):
    vertices=list(struct.iter_unpack('<5f',(run/'dome-vertices.bin').read_bytes()));require(len(vertices)==4225,'Actual4225vertex buffer');maximum=0
    for n,actual in enumerate(vertices):
        i,j=divmod(n,65);x,z=i-32,j-32;distance=f(math.sqrt(f(x*x+z*z)));height=f(32-min(distance,32));expected=[f(x*1290),f(height*5160/32),f(-z*1290),i/64,j/64];require(near(actual,expected),'Actual dome vertex/UV formula '+str(n));maximum=max(maximum,max(abs(a-b) for a,b in zip(actual,expected)))
    wanted=[]
    for i in range(64):
        for j in range(64):a=j+i*65;b=j+(i+1)*65;wanted.extend([a,b+1,b,a,a+1,b+1])
    require((run/'dome-indices.bin').read_bytes()==struct.pack('<'+'H'*len(wanted),*wanted),'Actual complete index winding/order');assets=json.loads((WS/'inventory/client455-sky-atmosphere-inputs.json').read_text());shader=next(x for x in assets['inputs'] if x['runtime_relative'].endswith('.vso'));require(hashlib.sha256((run/'actual-scatter.bin').read_bytes()).hexdigest()==shader['sha256'],'Actual device shader equals pinned Scatter.vso')
    rows=[json.loads(x) for x in (run/'atmosphere.jsonl').read_text().splitlines()];cases=[x for x in rows if x['kind']=='case'];suns=[x for x in rows if x['kind']=='sun'];require(len(cases)==16 and len(suns)==5,'All16prepass cases and5liveSunprofiles');dome_decl=bytes.fromhex('000000000200000000000c0001000500ff00000011000000');sun_decl=bytes.fromhex('000000000200000000000c00020003000000180004000a0000001c0001000500ff00000011000000');dome=sun_draws=0
    for row in cases:
        flags,available=row['flags'],bool(row['available']);expected=[]
        if available and not flags&4:expected.append(False)
        if not flags&1:expected.append(True)
        require([x['sun'] for x in row['draws']]==expected,'Actual mask1/4 draw order/availability');require(row['final_shader']==(available and flags&5==5),'Original shader clear vs both-disabled preserve')
        view=floats(row['view']);projection=floats(row['projection']);require(near(floats(row['viewproj']),matrix(view,projection)),'Restored viewproj recomputed');view[12:15]=[0,0,0];sky_projection=perspective(.6,4/3,10,60000)
        for draw in row['draws']:
            require(draw['shader']==available and draw['texture']==draw['sun'],'Actual shader carry and texture binding');require(near(floats(draw['view']),view) and near(floats(draw['projection']),sky_projection),'Actual temporary near10/far60000 and zero translation')
            if draw['sun']:
                sun_draws+=1;require(draw['vertices']==4 and draw['triangles']==2 and draw['stride']==36 and bytes.fromhex(draw['declaration'])==sun_decl,'Actual sun36 declaration');payload=bytes.fromhex(draw['vertex_data']);require(len(payload)==144,'Four actual submitted sun vertices')
                for i,(x,y,z,nx,ny,nz,color,u,v) in enumerate(struct.iter_unpack('<6fI2f',payload)):
                    require((x,y,z,u,v)==[(-1000,1000,0,0,0),(1000,1000,0,1,0),(-1000,-1000,0,0,1),(1000,-1000,0,1,1)][i],'Actual sun quad positions/UV')
            else:dome+=1;require(draw['vertices']==4225 and draw['triangles']==8192 and draw['stride']==20 and bytes.fromhex(draw['declaration'])==dome_decl,'Actual dome geometry binding')
            if available:
                constants=floats(draw['constants']);require(near(constants[:16],transpose(matrix(view,sky_projection))) and near(constants[16:32],transpose(view)),'Actual c0/c4 shader transforms');require(constants[48:52]==[0,-1,0,1] and near(constants[52:55],[.0138,.0113,.008]),'Actual direction/reflectance constants')
    scalar=[x for x in rows if x['kind']=='scalar_sun'];require(len(scalar)==72,'72scalar boundary/precision cases')
    for row in suns+scalar:require(row['values']==sun(number(row['day']),ops(row.get('cw',127))),'Exact selected live/scalar sun state bits: '+str(row))
    names=['atmosphere-midnight.bgra','atmosphere-morning.bgra','atmosphere-noon.bgra','atmosphere-evening.bgra','atmosphere-disabled.bgra'];images={n:(run/n).read_bytes() for n in names};require(all(len(x)==640*480*4 for x in images.values()),'Five complete actual sky frames');control=images[names[-1]];changes={n:sum(a!=b for a,b in zip(x,control)) for n,x in images.items()};require(changes['atmosphere-noon.bgra']>100,'Atmosphere visibly contributes');previous=json.loads((WS/'artifacts/client455-progress/client455-sky-material-native-before126.json').read_text());old=next(x for x in previous['frames'] if Path(x['file']).name=='sky2-noon.bgra');require(hashlib.sha256(control).hexdigest()==old['sha256'],'Matched disabled-atmosphere frame equals125noon')
    return dict(prepass_cases=16,shader_available_modes=2,vertices=4225,triangles=8192,index_bytes=49152,geometry_max_absolute_error=maximum,device_shader_byte_equal=True,actual_dome_draws=dome,actual_sun_draws=sun_draws,temporary_projection_near10_far60000=True,view_projection_restored_exact=True,shader_carry_and_disabled_preserve=True,sun_state_cases=5,scalar_sun_cases=72,sun_state_bits_exact_selected=True,GPU_frames=5,changed_bytes_from_disabled=changes,disabled_frame_byte_equal125=True,full_lighting=False,all_FP_inputs=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-existing',action='store_true');a=p.parse_args();r=json.loads((WS/'inventory/client455-sky-atmosphere-native.json').read_text()) if a.verify_existing else scenario('client455_sky_atmosphere_probe.cpp','sky-atmosphere','client455-sky-atmosphere-native','client455-sky-material-inputs');require(not r['natural_exit'] and r['native']['status']=='PASS','Completed atmosphere run');run=(WS/r['exe']['file']).parent;r.update(status='PASS_SELECTED',scope='Actual atmosphere resources,shader/dome/sun/prepass states and selected Sun scalar update;full lighting/fog/FP paths remain open',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),trace=record(run/'atmosphere.jsonl'),buffers=[record(run/n) for n in ['dome-vertices.bin','dome-indices.bin','actual-scatter.bin']],verdict=verify(run));(WS/'inventory/client455-sky-atmosphere-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
