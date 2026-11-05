"""Run our full Character routing test;never run input executables."""
import json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_draw import sha,stage_inputs
def frames(root):
    result=[]
    for phase in range(2):
        path=root/f'route-frame-{phase}.bgra';raw=path.read_bytes()
        if len(raw)!=256*256*4:raise ValueError('Incomplete route readback')
        bmp=root/f'route-frame-{phase}.bmp';bmp.write_bytes(b'BM'+struct.pack('<IHHI',54+len(raw),0,0,54)+struct.pack('<IiiHHIIiiII',40,256,-256,1,32,0,len(raw),2835,2835,0,0)+raw);result.append({'frame':path.relative_to(WS).as_posix(),'sha256':sha(path),'preview':bmp.relative_to(WS).as_posix(),'preview_sha256':sha(bmp)})
    if result[0]['sha256']==result[1]['sha256']:raise ValueError('No visible source route animation')
    return result
def inputs():
    build=json.loads((WS/'inventory/client455-character-draw-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-character-draw-reference.json').read_text(encoding='utf-8'))
    if build['compile_only'] or sha(WS/'scripts/audit_client455_character_draw.py')!=ref['script_sha256'] or sha(WS/'inventory/client455-draw-reference.json')!=ref['draw_fixture_report_sha256']:raise ValueError('Character draw inputs stale')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed route source:'+name)
    for item in build['dependencies']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed route dependency')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935':raise ValueError('Pinned D3DX required')
    return build,ref,dll
def main():
    build,ref,dll=inputs();original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Changed own route probe')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'gpu{len(list(base.glob("gpu*")))+1:03}';root.mkdir();_,fixture=stage_inputs(root);exe=root/'character-draw-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),str(dll),str(fixture),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Own Character route:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['route_cases']!=16 or native['real_draws']!=92 or native['frames']!=[160,2160] or native['heap_and_com_balance']:raise ValueError('Incomplete Character route test')
    report={'scope':'Source main/effect/transparent/batch/dynamic/shadow routing;normal migration andfull reference runtime parity open','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'frames':frames(root),'provider_sha256':sha(dll),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-character-draw-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-character-draw-reference.json'),'original_exe_executed':False,'transcendental_provider':'Modern MTsin/cos(double)->float supplied explicitly;original staticCRT bitparity notproven'}
    (WS/'inventory/client455-character-draw-gpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
