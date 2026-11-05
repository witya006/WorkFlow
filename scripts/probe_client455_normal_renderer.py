"""Validate changed renderer math and real normal CUnity/model/pose/draw path."""
import argparse,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_draw import stage_inputs
from probe_client455_engine9 import imported_slots,exports
from client455_d3d9_port import ENGINE_DEFINITIONS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['math','gpu','all'],default='all');options=parser.parse_args()
    root=WS/'work/client455-port/normal';art=WS/'artifacts/normal-renderer455';art.mkdir(parents=True,exist_ok=True)
    build=json.loads((WS/'inventory/client455-normal-build.json').read_text());normal=json.loads((WS/'inventory/client455-normal-consumers.json').read_text());ref=json.loads((WS/'inventory/client455-normal-renderer-reference.json').read_text());sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text())
    if build['build_exit'] or build['objects']!=182 or normal['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json'):raise ValueError('Current normal build/consumer evidence required')
    libraries=[WS/r['file'] for r in normal['libraries']]
    for item in normal['libraries']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed normal library')
    engine=WS/'work/client455-port/source/R3Engine';includes=[root/'include',root/'source',engine,engine/'1stclass',engine/'2ndclass',engine/'common',engine/'extension',engine/'d3d/include',WS/sdk['include']];dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';definitions=sorted(set(ENGINE_DEFINITIONS+['_NEW_UI_','_WINDOWS','RF_CLIENT_455_FRUSTUM','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION']));flags='/Zc:forScope- '+' '.join('/D'+name for name in definitions)+' '+' '.join('/I"'+str(p)+'"' for p in includes);objects=[WS/r['file'] for r in normal['objects']]
    reports=[]
    for mode,name in [('math','test_client455_normal_renderer_math.cpp'),('gpu','client455_normal_renderer_probe.cpp')]:
        if options.mode not in [mode,'all']:continue
        source=WS/'scripts/native'/name;entry=root/'generated'/name;entry.write_bytes(source.read_bytes());exe=root/'build'/('normal-renderer-'+mode+'.exe');batch=root/'generated'/('build-renderer-'+mode+'.cmd');log=art/('build-'+mode+'.txt')
        extra_sources=[]
        if mode=='gpu':
            extra_source=WS/'scripts/native/test_client455_normal_shadow.cpp';extra_entry=root/'generated'/extra_source.name;extra_entry.write_bytes(extra_source.read_bytes());extra_sources=[extra_source]
        inputs=objects+libraries if mode=='gpu' else [libraries[0]]
        forced='/FI"'+str(WS/'work/client455-port/port_std.hpp')+'"' if mode=='gpu' else ''
        batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env-renderer.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W3 {flags} {forced} "{entry}" '+' '.join('"'+str(p)+'"' for p in ([root/'generated'/p.name for p in extra_sources]+inputs))+f' d3d9.lib dinput8.lib dxguid.lib winmm.lib ws2_32.lib vfw32.lib advapi32.lib gdi32.lib user32.lib imm32.lib comdlg32.lib delayimp.lib /Fe"{exe}" /link /SUBSYSTEM:CONSOLE /OPT:REF /DELAYLOAD:mss32.dll /MAP:"{exe.with_suffix(".map")}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
        result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=entry.parent,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise ValueError('Normal renderer '+mode+' build:'+str(log))
        raw=exe.read_bytes();slots=imported_slots(raw);dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
        if sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935' or any(x['dll'] in ['d3d8.dll','d3dx8.dll','d3dx9_43.dll'] for x in slots.values()):raise ValueError('Wrong normal renderer runtime')
        if not {x['name'] for x in slots.values() if x['dll']=='d3dx9_36.dll'}<=exports(dll.read_bytes()):raise ValueError('Missing36export')
        base=WS/'work/m9'/sha(exe)[:8];base.mkdir(parents=True,exist_ok=True);index=1
        while (base/f'normal-{mode}{index:03d}').exists():index+=1
        run=base/f'normal-{mode}{index:03d}';run.mkdir();shutil.copyfile(exe,run/exe.name);output=run/'result.json'
        if mode=='math':fixture=WS/ref['golden']
        else:_,fixture=stage_inputs(run)
        result=subprocess.run([str(run/exe.name),str(fixture),str(output)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError('Normal renderer '+mode+' runtime:'+str(run/'console.txt'))
        native=json.loads(output.read_text());frames=[]
        if mode=='gpu':
            for i in range(2):
                pixels=run/f'normal-frame-{i}.bgra';data=pixels.read_bytes()
                if len(data)!=256*256*4:raise ValueError('Short normal frame')
                preview=pixels.with_suffix('.bmp');preview.write_bytes(b'BM'+struct.pack('<IHHI',54+len(data),0,0,54)+struct.pack('<IiiHHIIiiII',40,256,-256,1,32,0,len(data),2835,2835,0,0)+data);frames.append({'file':pixels.relative_to(WS).as_posix(),'sha256':sha(pixels),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview)})
        report={'scope':'Actual normal facade renderer '+mode+' scenario;not full normal WinMain/455acceptance','architecture':'x86','exe':(run/exe.name).relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(raw)['entry_rva']),'native':native,'frames':frames,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'libraries':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in inputs],'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'normal_build_sha256':sha(WS/'inventory/client455-normal-build.json'),'reference_sha256':sha(WS/'inventory/client455-normal-renderer-reference.json'),'legacy_character_linked':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
        report['definitions']=definitions
        report['extra_sources']=[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in extra_sources]
        if mode=='gpu':
            shadow=run/'normal-shadow.bgra';data=shadow.read_bytes()
            if len(data)!=512*512*4:raise ValueError('Short shadow frame')
            preview=shadow.with_suffix('.bmp');preview.write_bytes(b'BM'+struct.pack('<IHHI',54+len(data),0,0,54)+struct.pack('<IiiHHIIiiII',40,512,-512,1,32,0,len(data),2835,2835,0,0)+data)
            report['shadow_frame']={'file':shadow.relative_to(WS).as_posix(),'sha256':sha(shadow),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview)}
            report['shadow_reference_sha256']=sha(WS/'inventory/client455-normal-shadow-reference.json')
        if mode=='gpu':
            previous=WS/'inventory/client455-normal-renderer-precanonical.json';before=json.loads(previous.read_text())
            if any(native.get(k)!=v for k,v in before['native'].items()) or [r['sha256'] for r in frames]!=[r['sha256'] for r in before['frames']]:raise ValueError('Normal renderer changed previous behavior/frames')
            report['precanonical_frames_equal']=True;report['precanonical_report_sha256']=sha(previous)
        (WS/f'inventory/client455-normal-renderer-{mode}.json').write_text(json.dumps(report,indent=2)+'\n');print(mode,json.dumps(native))
if __name__=='__main__':main()
