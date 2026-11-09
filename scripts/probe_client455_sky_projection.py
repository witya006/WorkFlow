"""Observe actual CLevel/D3D projection changes and check closed-form matrices."""
import json,math,shutil,struct,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders
from compare_client_binaries import WS


def decode(bits):return list(struct.unpack('<'+'f'*len(bits),struct.pack('<'+'I'*len(bits),*bits)))
def perspective(fov,aspect,near,far):
    p=[0.]*16;y=1/math.tan(fov/2);p[0]=y/aspect;p[5]=y;p[10]=far/(far-near);p[11]=1;p[14]=-near*far/(far-near);return p
def close(a,b):return all(abs(x-y)<=2e-6+abs(y)*2e-6 for x,y in zip(a,b))


def verify(run):
    rows=[json.loads(x) for x in (run/'projection.jsonl').read_text().splitlines()];require(len(rows)==12,'All projection cases')
    for i,row in enumerate(rows):
        fov,aspect,near,far,w,h,scale=row['parameters'];sky=decode(row['sky']);world=decode(row['world']);planes=decode(row['planes']);require(row['id']==i and close(sky,perspective(fov,aspect,2,far)),'Actual temporary near2 projection')
        if not row['mode']:require(close(world,perspective(fov,aspect,near,far)) and planes==[float(100+j) for j in range(24)],'Perspective restored without frustum refresh')
        else:
            expected=[0.]*16;expected[0]=2/(w/scale);expected[5]=2/(h/scale);expected[10]=1/10000;expected[14]=.5;expected[15]=1;require(close(world,expected),'Actual orthographic restore')
            view=decode(row['view']);clip=[sum(view[r*4+k]*world[k*4+c] for k in range(4)) for r in range(4) for c in range(4)];wanted=[]
            for column,sign in [(0,1),(0,-1),(1,-1),(1,1),(2,1),(2,-1)]:
                plane=[-(clip[r*4+3]+sign*clip[r*4+column]) for r in range(4)];length=math.sqrt(sum(x*x for x in plane[:3]));wanted.extend(x/length for x in plane)
            require(all(abs(a-b)<=.002+abs(b)*2e-6 for a,b in zip(planes,wanted)),'Actual orthographic frustum refresh')
    return dict(cases=12,projection_binds=24,temporary_sky_near=2,initial_flag=0,initial_scale=5,perspective_frustum_unchanged=True,orthographic_frustum_refreshed=True,actual_device_state_exact=True,matrix_tolerance='2e-6 absolute+2e-6 relative',plane_tolerance='.002 absolute+2e-6 relative',full_renderer=False)


def main():
    source=WS/'scripts/native/client455_sky_projection_probe.cpp';exe=build_full_object_probe('sky-projection',source);holder=WS/'work/m9'/sha(exe)[:8];i=1
    while(holder/f'sky-projection-{i:03d}').exists():i+=1
    run=holder/f'sky-projection-{i:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'));inputs=copy_character_shaders(run);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);dst=run/'System/console.jpg';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(client/'System/console.jpg',dst);inputs.append(record(dst));ini=run/'R3Engine.ini';ini.write_text('[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(ini));r=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(r.stdout+r.stderr);require(not r.returncode,'Actual projection probe exit='+str(r.returncode)+' '+r.stderr.decode(errors='replace')[-700:]);verdict=verify(run)
    out=dict(status='PASS_SELECTED',scope='Actual CLevel unloaded-sky near2/world projection and orthographic frustum on own D3D device;fullsky/fade/renderer open',script_sha256=sha(Path(__file__)),source=record(source),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),exe=record(target),map=record(target.with_suffix('.map')),inputs=inputs,trace=record(run/'projection.jsonl'),console=record(run/'console.txt'),output=record(run/'result.json'),native=json.loads((run/'result.json').read_text()),verdict=verdict,natural_exit=r.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN');(WS/'inventory/client455-sky-projection-native.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(run=str(run),verdict=verdict)))


if __name__=='__main__':main()
