"""Run only our migratedengine device/Character attachment scenario."""
import argparse,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from probe_client455_shaders import stage

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imported_slots(raw):
    header=struct.unpack_from('<I',raw,0x3c)[0];rva,size=struct.unpack_from('<II',raw,header+24+104);base=pe(raw)['image_base'];out={}
    def string(at):
        text=bytearray()
        for i in range(512):
            byte=read_va(raw,base+at+i,1)
            if byte==b'\0':return text.decode('ascii')
            text+=byte
        raise ValueError('Unterminated PE import name')
    for at in range(rva,rva+size,20):
        lookup,_,_,name,table=struct.unpack('<5I',read_va(raw,base+at,20))
        if not any([lookup,name,table]):break
        dll=string(name).lower();lookup=lookup or table;n=0
        while (item:=struct.unpack('<I',read_va(raw,base+lookup+4*n,4))[0]):
            if not item&0x80000000:out[base+table+4*n]={'dll':dll,'name':string(item+2)}
            n+=1
    return out
def exports(raw):
    header=struct.unpack_from('<I',raw,0x3c)[0];rva,size=struct.unpack_from('<II',raw,header+24+96);base=pe(raw)['image_base'];directory=read_va(raw,base+rva,40);count=struct.unpack_from('<I',directory,24)[0];names=struct.unpack_from('<I',directory,32)[0];out=set()
    for i in range(count):
        at=struct.unpack('<I',read_va(raw,base+names+4*i,4))[0];text=bytearray()
        for j in range(512):
            b=read_va(raw,base+at+j,1)
            if b==b'\0':break
            text+=b
        out.add(text.decode('ascii'))
    return out
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--level',choices=['Platform01']);args=parser.parse_args()
    build=json.loads((WS/'inventory/client455-engine9-probe-build.json').read_text(encoding='utf-8'));source=WS/build['exe'];digest=sha(source);dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');slots=imported_slots(source.read_bytes());modules=sorted(set(r['dll'] for r in slots.values()))
    if digest!=build['exe_sha256'] or 'd3d8.dll' in modules or 'd3dx8.dll' in modules or 'd3dx9_43.dll' in modules or 'd3d9.dll' not in modules or 'd3dx9_36.dll' not in modules or sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935':raise ValueError('Wrong engine runtime imports')
    available=exports(dll.read_bytes());needed=sorted(set(r['name'] for r in slots.values() if r['dll']=='d3dx9_36.dll'))
    if not set(needed)<=available:raise ValueError('SDKheader import newerthan36:'+str(set(needed)-available))
    for name,value in build['source_sha256'].items():
        if sha(WS/name)!=value:raise ValueError('Changed ownengine probe input')
    for item in build['libraries']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed engine dependency')
    parent=WS/'work/m9'/digest[:8];parent.mkdir(parents=True,exist_ok=True);root=parent/f'engine9{len(list(parent.glob("engine9*")))+1:03}';root.mkdir();exe=root/'engine9-probe.exe';shutil.copyfile(source,exe);output=root/'result.json';shader=json.loads((WS/'inventory/client455-shaders-reference.json').read_text(encoding='utf-8'));stage(root,shader)
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));resources=[]
    for name in ['Grass1.vsh','grass1.vso']:
        original=Path(paths['client_455'])/'System/shader'/name;target=root/'System/shader'/name;shutil.copyfile(original,target);resources.append({'file':'System/shader/'+name,'sha256':sha(original)})
    (root/'R3Engine.ini').write_text('[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii')
    env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);command=[str(exe)]
    if args.level:
        previous=json.loads((WS/'inventory/client455-frustum-graphics.json').read_text(encoding='utf-8'));case=next(r for r in previous['cases'] if r['case']=='level-Platform01')
        for item in case['archives']:
            original=Path(paths['client_455'])/item['path'];target=root/item['path']
            if not target.resolve().is_relative_to(root.resolve()):raise ValueError('Level input escaped own run directory')
            if sha(original)!=item['sha256']:raise ValueError('Changed level reference')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target)
        env['RF_LAB_HELPER_INPUT']='Map/Platform01/Platform01.bsp'.replace('/','\\');command.append('--level')
    run=subprocess.run(command,cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Engine9:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['stage']!='complete' or native['failures'] or native['errors'] or native['warnings'] or native['allocation_before']!=native['allocation_after'] or native['device_refs_after_release'] or native['d3d_refs_after_release']:raise ValueError('Engine9device check incomplete:'+str(native))
    report={'scope':'Real migratedR3EngineD3D9 bringup/capture/release withsource455Character owner attachedtothesamedevice;notnormalgame/455behaviorparity','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':build['entry_rva'],'native':native,'direct_imports':modules,'d3dx36_imports_verified':needed,'provider_sha256':sha(dll),'shader_inputs':resources,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-engine9-probe-build.json'),'input_exe_executed':False}
    shaders=json.loads((root/'engine-shaders.json').read_text(encoding='utf-8'))
    if shaders!={'grass_program_created':True}:raise ValueError('Engine shader path fell back')
    report['engine_shaders']=shaders;report['character_owner_attached']=True
    frame=root/'frame.bmp'
    if frame.exists():report.update(frame=frame.relative_to(WS).as_posix(),frame_sha256=sha(frame))
    if args.level:
        detail=json.loads((root/'level.json').read_text(encoding='utf-8'));report['level']=detail
        if not native.get('level_loaded',detail.get('loaded')) or detail['helpers']!=23 or detail['interiors']!=8:raise ValueError('Incomplete engine9map load')
    (WS/('inventory/client455-engine9-level.json' if args.level else 'inventory/client455-engine9-runtime.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
