"""Build a derived engine with confirmed455startup fixes;preserve engine033."""
import hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    base=WS/'work/client455-port';root=base/'startup-engine';art=WS/'artifacts/client455-startup-engine';art.mkdir(parents=True,exist_ok=True);root.mkdir(parents=True,exist_ok=True)
    template=base/'CMakeLists.txt';cmakeText=template.read_text();sources=[]
    for match in re.finditer(r'^ "([^"]+\.cpp)"$',cmakeText,re.M):
        source=Path(match[1]);sources.append({'file':source.relative_to(WS).as_posix(),'sha256':sha(source)})
    if len(sources)!=67:raise ValueError('Base engine source list changed')
    previous=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text()) if (WS/'inventory/client455-startup-engine-build.json').exists() else {};old={row['file']:row['sha256'] for row in previous.get('derived_sources',[])};derived=[]
    for filename in ['r3enginekernel.cpp','r3d3dwrapper.cpp','r3text.cpp','r3d3dtex.cpp']:
        source=base/'source/R3Engine'/('1stclass' if filename=='r3d3dtex.cpp' else '2ndclass')/filename;raw=source.read_bytes()
        if filename=='r3enginekernel.cpp':
            anchor=b'GetR3State()->mbFullScreen = TRUE;'
            if raw.count(anchor)!=1:raise ValueError('Legacy forced fullscreen changed')
            raw=raw.replace(anchor,b'GetR3State()->mRenderBits = 32; // 455:8ED5A0;preserve configured window mode')
        elif filename=='r3d3dwrapper.cpp':
            anchor=b'\tCreate(hInstance);'
            if raw.count(anchor)!=1:raise ValueError('Legacy Create wrapper changed')
            raw=raw.replace(anchor,b'\tif(Create(hInstance)!=S_OK) exit(0); // 455:8EDB72..7A;any nonzero result')
        elif filename=='r3text.cpp':
            anchor=b'static CR3Font stCR3Font;'
            if raw.count(anchor)!=1:raise ValueError('Legacy active text boundary changed')
            header=(WS/'scripts/native/client455_font.h').as_posix()
            raw=(f'#include "{header}"\n'.encode()+raw[:raw.index(anchor)]+(WS/'scripts/native/client455_text_bridge.inc').read_bytes())
        else:
            from prepare_client455_normal import section
            start,end=section(raw,b'void *GetDDSTexFromBuffer(',b'void *GetDDSTexFromBuffer(')
            raw=raw[:start]+(WS/'scripts/native/client455_sprite_texture.inc').read_bytes()+raw[end:]
        target=root/'source'/filename;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw and sha(target)!=old.get(target.relative_to(WS).as_posix()):raise ValueError('Preserving changed derived source')
        if not target.exists() or target.read_bytes()!=raw:target.write_bytes(raw)
        derived.append({'file':target.relative_to(WS).as_posix(),'sha256':sha(target),'original':source.relative_to(WS).as_posix(),'original_sha256':sha(source)})
        cmakeText=cmakeText.replace(source.as_posix(),target.as_posix())
    cmakeText=cmakeText.replace('R3Engine455','R3Engine455Startup');(root/'CMakeLists.txt').write_text(cmakeText)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());cmake=Path(info['installation_path'])/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe';build=root/'build';oldLibrary=base/'build-vs2026/Release/R3Engine455.lib';oldHash=sha(oldLibrary)
    config=subprocess.run([str(cmake),'-S',str(root),'-B',str(build),'-G','Visual Studio 18 2026','-A','Win32','-T','v145','-DCMAKE_SYSTEM_VERSION=10.0.26100.0'],capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(art/'configure.txt').write_bytes(config.stdout+config.stderr)
    if config.returncode:raise ValueError('Derived engine configure failed')
    result=subprocess.run([str(cmake),'--build',str(build),'--config','Release','--target','R3Engine455Startup','--parallel','4'],capture_output=True,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW);log=art/'build.txt';log.write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Derived engine build:'+str(log))
    library=build/'Release/R3Engine455Startup.lib';objects=list((build/'R3Engine455Startup.dir/Release').glob('*.obj'))
    if len(objects)!=67 or sha(oldLibrary)!=oldHash or any(sha(WS/row['file'])!=row['sha256'] for row in sources):raise ValueError('Engine source/object/baseline drift')
    report={'scope':'Derived source engine with455color32 call and strict Create exit policy;remaining wrapper/camera/console/whole startup semantics open','architecture':'x86','build_exit':0,'objects':67,'library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'base_cmake':{'file':template.relative_to(WS).as_posix(),'sha256':sha(template)},'base_sources':sources,'derived_sources':derived,'baseline_library':{'file':oldLibrary.relative_to(WS).as_posix(),'sha256':oldHash},'cmake':{'file':(root/'CMakeLists.txt').relative_to(WS).as_posix(),'sha256':sha(root/'CMakeLists.txt')},'log':{'file':log.relative_to(WS).as_posix(),'sha256':sha(log)},'script_sha256':sha(WS/'scripts/build_client455_engine_startup.py'),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['text_bridge']={name:sha(WS/'scripts/native'/name) for name in ['client455_text_bridge.inc','client455_font.h']}
    report['sprite_texture']={'client455_sprite_texture.inc':sha(WS/'scripts/native/client455_sprite_texture.inc')}
    (WS/'inventory/client455-startup-engine-build.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:derived67engine units;033source/library preserved;455color32/Create policy built')
if __name__=='__main__':main()
