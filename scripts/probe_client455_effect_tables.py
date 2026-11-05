"""Run source455effect tables through the actual normal facade;no input EXE."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ref=json.loads((WS/'inventory/client455-effect-tables-reference.json').read_text());build=json.loads((WS/'inventory/client455-normal-build.json').read_text())
    if build['build_exit'] or build['objects']!=182:raise ValueError('Current normal source build required')
    root=WS/'work/client455-port/normal';art=WS/'artifacts/normal-effects455';art.mkdir(parents=True,exist_ok=True);sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text());dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    source=WS/'scripts/native/test_client455_effect_tables.cpp';entry=root/'generated'/source.name;entry.write_bytes(source.read_bytes());library=root/'build/Release/RFClient455Facade.lib';exe=root/'build/effect-tables-probe.exe';log=art/'build.txt';batch=root/'generated/build-effect-tables.cmd'
    includes=' '.join('/I"'+str(p)+'"' for p in [root/'include',WS/sdk['include']])
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env-effect-tables.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W3 /D_CRT_SECURE_NO_WARNINGS {includes} "{entry}" "{library}" /Fe"{exe}" /link /SUBSYSTEM:CONSOLE /OPT:REF /MAP:"{exe.with_suffix(".map")}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=entry.parent,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError('Effect tables build:'+str(log))
    base=WS/'work/m9'/sha(exe)[:8];base.mkdir(parents=True,exist_ok=True);i=1
    while (base/f'effects{i:03d}').exists():i+=1
    run=base/f'effects{i:03d}';run.mkdir();shutil.copyfile(exe,run/exe.name);output=run/'result.json';fixture=run/'reference';fixture.mkdir()
    for row in ref['files']:
        path=WS/row['copy']
        if sha(path)!=row['sha256']:raise ValueError('Changed real effect input')
        shutil.copyfile(path,fixture/path.name)
    golden=WS/ref['golden']
    if sha(golden)!=ref['golden_sha256']:raise ValueError('Changed independent selections')
    shutil.copyfile(golden,fixture/golden.name)
    result=subprocess.run([str(run/exe.name),str(fixture),str(output)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Effect tables run:'+str(run/'console.txt'))
    native=json.loads(output.read_text());report={'scope':'Actual normal source pattern/item loaders and selected defined/explicitly unknown queries;not full455effects or client acceptance','architecture':'x86','exe':(run/exe.name).relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,
        'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),
        'reference_sha256':sha(WS/'inventory/client455-effect-tables-reference.json'),'normal_build_sha256':sha(WS/'inventory/client455-normal-build.json'),'fixtures':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in sorted(fixture.iterdir())],
        'legacy_character_linked':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-effect-tables-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(native))
if __name__=='__main__':main()
