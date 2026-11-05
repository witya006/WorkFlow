"""Run only our connected draw probe,using pinned input copies and D3DX."""
import hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_shaders import stage
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stage_inputs(root):
    ref=json.loads((WS/'inventory/client455-draw-reference.json').read_text(encoding='utf-8'))
    if sha(WS/'scripts/audit_client455_draw.py')!=ref['script_sha256']:raise ValueError('Changed draw input oracle')
    for item in ref['files']:
        if sha(WS/item['path'])!=item['sha256']:raise ValueError('Changed model/ANI input')
    for item in ref['textures']:
        original=WS/item['copy']
        if sha(original)!=item['sha256']:raise ValueError('Changed real model texture')
        target=root/'tex'/original.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(original,target)
    fixture=WS/ref['fixture']
    if sha(fixture)!=ref['fixture_sha256']:raise ValueError('Changed draw fixture')
    shader=json.loads((WS/'inventory/client455-shaders-reference.json').read_text(encoding='utf-8'))
    for item in shader['programs']:
        if sha(WS/item['copy'])!=item['sha256']:raise ValueError('Changed shader input')
    stage(root,shader);return ref,fixture
def frames(root):
    records=[]
    for phase in range(2):
        path=root/f'character-frame-{phase}.bgra';raw=path.read_bytes()
        if len(raw)!=256*256*4:raise ValueError('Incomplete actual GPU readback')
        bmp=root/f'character-frame-{phase}.bmp';bmp.write_bytes(b'BM'+struct.pack('<IHHI',54+len(raw),0,0,54)+struct.pack('<IiiHHIIiiII',40,256,-256,1,32,0,len(raw),2835,2835,0,0)+raw)
        records.append({'frame':path.relative_to(WS).as_posix(),'sha256':sha(path),'preview':bmp.relative_to(WS).as_posix(),'preview_sha256':sha(bmp)})
    if records[0]['sha256']==records[1]['sha256']:raise ValueError('No visible animation change')
    return records
def main():
    build=json.loads((WS/'inventory/client455-draw-build.json').read_text(encoding='utf-8'))
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed draw source:'+name)
    for item in build['dependencies']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed production dependency')
    original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Changed own executable')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935':raise ValueError('Pinned D3DX required')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'gpu{len(list(base.glob("gpu*")))+1:03}';root.mkdir();ref,fixture=stage_inputs(root);exe=root/'draw-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),str(dll),str(fixture),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Own draw probe:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['real_drawn_parts']<1 or native['animated_parts']<1 or native['owned_heap_balance'] or native['device_and_api_release_counts']:raise ValueError('Incomplete connected draw')
    report={'scope':'Source draw primitives on real animated/texture model and four analytic shared-buffer draws;full92E5F0/normal draw still open','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'frames':frames(root),'provider_sha256':sha(dll),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-draw-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-draw-reference.json'),'reference_exe_executed':False}
    (WS/'inventory/client455-draw-gpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
