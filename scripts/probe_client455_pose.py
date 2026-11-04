"""Run only new source pose checks; no input EXE or existing bulk suites."""
import hashlib,json,shutil,subprocess
from compare_client_binaries import WS
from probe_client455_animation import inputs as animation_inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
    *_,texture_root,dll,provider=animation_inputs()
    build=json.loads((WS/'inventory/client455-pose-build.json').read_text(encoding='utf-8'));source=json.loads((WS/'inventory/client455-pose-inputs.json').read_text(encoding='utf-8'))
    if build['compile_only']:raise ValueError('Pose test required')
    if sha(WS/build['library'])!=build['library_sha256'] or sha(WS/build['object'])!=build['object_sha256']:raise ValueError('Changed owned pose archive/object')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed pose source:'+name)
    for record in build['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed pose dependency')
    for name,key in [('client455-animation-reference','ani_report_sha256'),('character-mesh08-bone-pairs','pair_report_sha256'),('client455-pose-reference','pose_reference_sha256')]:
        if sha(WS/f'inventory/{name}.json')!=source[key]:raise ValueError('Changed pose input report')
    golden=WS/source['golden']
    if sha(golden)!=source['golden_sha256'] or sha(WS/'scripts/prepare_client455_pose_inputs.py')!=source['script_sha256']:raise ValueError('Changed pose oracle')
    return build,source,golden,texture_root,dll,provider

def main():
    build,source,golden,texture_root,dll,provider=inputs();original=WS/build['exe'];digest=sha(original)
    if digest!=build['exe_sha256']:raise ValueError('Changed own pose test')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'pose{len(list(base.glob("pose*")))+1:03}';root.mkdir();shutil.copytree(texture_root/'tex',root/'tex');exe=root/'pose-probe.exe';shutil.copyfile(original,exe);output=root/'result.json'
    run=subprocess.run([str(exe),str(WS),str(golden),str(dll),str(output)],cwd=root,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError(f'Own pose check:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['key_cases']!=source['key_cases'] or native['real_pairs']!=11 or native['pose_updates']!=132 or native['skin_matrices']==0:raise ValueError('Incomplete pose check')
    report={'scope':'Three source ANI evaluators and connected FrameMove pose phases,not secondary motion/normal consumers/animateddraw/M9','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'architecture':'x86','entry_rva':build['entry_rva'],'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-pose-build.json'),'input_report_sha256':sha(WS/'inventory/client455-pose-inputs.json'),'reference_report_sha256':sha(WS/'inventory/client455-pose-reference.json'),'provider_sha256':provider,'owned_heap_balance':0,'reference_exe_executed':False,'rendered':False}
    (WS/'inventory/client455-pose-cpu.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
