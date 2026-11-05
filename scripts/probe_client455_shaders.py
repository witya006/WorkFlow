"""Exercise our shaders on HAL using only the pinned D3DX compiler/runtime."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
    ref=json.loads((WS/'inventory/client455-shaders-reference.json').read_text(encoding='utf-8'));build=json.loads((WS/'inventory/client455-shaders-build.json').read_text(encoding='utf-8'))
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed shader source')
    if sha(WS/'scripts/audit_client455_shaders.py')!=ref['script_sha256']:raise ValueError('Changed shader oracle')
    for p in ref['programs']:
        if sha(WS/p['copy'])!=p['sha256'] or sha(WS/p['decoded'])!=p['decoded_sha256']:raise ValueError('Changed shader fixture')
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935':raise ValueError('Pinned D3DX9_36 required')
    return ref,build,dll
def stage(root,ref):
    target=root/'System/shader';target.mkdir(parents=True)
    for item in ref['programs']:shutil.copyfile(WS/item['copy'],target/(item['name']+'.sho'))
    plain=b'[vertex shader]\r\nfloat4 main(float4 p:POSITION):POSITION{return p;}'
    (root/'fallback.shr').write_bytes(plain);(root/'priority.shr').write_bytes(plain)
    # Independent fixture uses the already pinned key bytes to prove that an
    # existing SHO is preferred even when its decoded text has no shader block.
    import re
    key=bytes(int(x,16) for x in re.findall(r'0x([0-9a-f]{2})',(WS/'scripts/native/client455_shader_key.h').read_text(encoding='ascii')))
    raw=b'no shader blocks';(root/'priority.sho').write_bytes(bytes(value^key[i%137] for i,value in enumerate(raw)))
def source_proof(root,ref):
    wanted=[]
    for program in ref['programs']:
        for stageName in ['vertex','pixel']:
            if program[stageName+'_sha256']:wanted.append({'program':program['name'],'stage':stageName,'sha256':program[stageName+'_sha256']})
    for i,item in enumerate(wanted):
        actual=root/f'compiled-source-{i:02}.hlsl'
        if sha(actual)!=item['sha256']:raise ValueError('Compiler received different shader input')
    return wanted
def main():
    ref,build,dll=inputs();original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Changed own shader executable')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'gpu{len(list(base.glob("gpu*")))+1:03}';root.mkdir();stage(root,ref);exe=root/'shaders-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Shader GPU:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['programs']!=12 or native['vertex_shaders']!=12 or native['pixel_shaders']!=3 or native['device_refs_after_release'] or native['api_refs_after_release']:raise ValueError('Shader GPU checks incomplete')
    sources=source_proof(root,ref)
    report={'scope':'Actual shader resource bootstrap/12SHO/15stages/2declarations/one harness triangle;not fullCharacter draw/normal integration','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'frame':(root/'shader-frame.bgra').relative_to(WS).as_posix(),'frame_sha256':sha(root/'shader-frame.bgra'),'actual_compiler_sources':sources,'provider_sha256':sha(dll),'build_report_sha256':sha(WS/'inventory/client455-shaders-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-shaders-reference.json')};(WS/'inventory/client455-shaders-gpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
