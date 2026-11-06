"""Check real Avatar/inventory money setters against independent signed64 cases."""
import ctypes,hashlib,json,math,shutil,subprocess
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def expected(value,mode):
    if value>=0:return f'{value:,}'
    rounded=float(value)
    if mode==1 and rounded>value:rounded=math.nextafter(rounded,-math.inf)
    if mode in [2,3] and rounded<value:rounded=math.nextafter(rounded,math.inf)
    magnitude=int(abs(rounded));signed=magnitude if magnitude<1<<63 else -(1<<63)
    return '-'+f'{signed:,}'
def main():
    source=WS/'scripts/native/client455_money_probe.cpp';exe=build_full_object_probe('money',source);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);runs=[]
    values=[0,1,-1,999,1000,1001,-1000,2147483647,2147483648,4294967295,4294967296,4294967297,-4294967297,(1<<53)-1,(1<<53)+1,-((1<<53)+1),-((1<<53)+3),-(1<<62)-1,(1<<63)-1,-(1<<63),-((1<<63)-1),1234567890123456,-1234567890123456]
    fixture=''.join(f'{mode} {value} {expected(value,mode)}\n' for mode in range(4) for value in values)
    for nation,folder in [('Korea','ko-kr'),('Russia','ru-ru')]:
        index=1
        while(parent/f'money-{folder}-{index:03d}').exists():index+=1
        run=parent/f'money-{folder}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'));inputs=[]
        for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF',f'DataTable/{folder}/NDLanguage.edf','SpriteImage/Common/mouse.spr',f'SpriteImage/{folder}/common.spr']:
            path=run/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(client/name,path);inputs.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),original=str(client/name)))
        config=run/'R3Engine.ini';config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');cases=run/'money-cases.txt';cases.write_text(fixture,encoding='ascii')
        for path in [config,cases]:inputs.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
        try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        finally:
            remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes,remove.restype=[ctypes.c_wchar_p],ctypes.c_int;remove(str(run/'System/010.TTF'))
        console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
        for path in sorted(run.glob('*.bgra')):
            preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),preview=preview.relative_to(WS).as_posix(),preview_sha256=sha(preview)))
        def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)) if path.exists() else None
        native=json.loads(output.read_text()) if output.exists() else None
        runs.append(dict(nation=nation,exe=record(target),map=record(target.with_suffix('.map')),output=record(output),console=record(console),trace=record(run/'money-trace.txt'),inputs=inputs,frames=frames,native=native,exit=result.returncode))
        if result.returncode:break
        if any(sha(WS/r['file'])!=r['sha256'] or ('original' in r and sha(Path(r['original']))!=r['sha256']) for r in inputs):raise ValueError('Mutated money input')
    report=dict(scope='Actual source Avatar/inventory signed64 setter chain, selected x87 rounding and GPU label geometry;not full currency economy/protocol or Tutorial acceptance',source=dict(file=source.relative_to(WS).as_posix(),sha256=sha(source)),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),runs=runs,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-money-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([dict(nation=r['nation'],exit=r['exit'],native=r['native'],console=(WS/r['console']['file']).read_text(errors='replace')[-1200:]) for r in runs]))
    if len(runs)!=2 or any(r['exit'] for r in runs):raise SystemExit(1)
if __name__=='__main__':main()
