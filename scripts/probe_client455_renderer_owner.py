"""Run source-owned real model rendering,not an input EXE or broad suite."""
import argparse,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client455_draw import stage_inputs
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frames(root):
    result=[]
    for phase in range(2):
        path=root/f'owner-frame-{phase}.bgra';raw=path.read_bytes()
        if len(raw)!=256*256*4:raise ValueError('Incomplete owner readback')
        preview=path.with_suffix('.bmp');preview.write_bytes(b'BM'+struct.pack('<IHHI',54+len(raw),0,0,54)+struct.pack('<IiiHHIIiiII',40,256,-256,1,32,0,len(raw),2835,2835,0,0)+raw);result.append({'file':path.relative_to(WS).as_posix(),'sha256':sha(path),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview)})
    if result[0]['sha256']==result[1]['sha256']:raise ValueError('Animation didnot changeframe')
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--client',action='store_true');args=parser.parse_args()
    build=json.loads((WS/'inventory/client455-renderer-owner-build.json').read_text(encoding='utf-8'));ref=json.loads((WS/'inventory/client455-renderer-owner-reference.json').read_text(encoding='utf-8'));original=WS/build['exe'];golden=WS/ref['golden'];dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if args.client:
        summary=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
        if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_RENDERER_OWNER')!='ON':raise ValueError('Owner-enabled full client required')
        for group in ['lab_input_sha256','renderer_owner_input_sha256']:
            for name,value in summary[group].items():
                if sha(WS/name)!=value:raise ValueError('Changed fullclient input')
        original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin'
        if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Unexpected game DLL imports')
    digest=sha(original)
    for name,value in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=value:raise ValueError('Changed renderer source:'+name)
    for item in build['dependencies']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed owner dependency')
    if not args.client and digest!=build['exe_sha256'] or sha(golden)!=ref['golden_sha256'] or sha(dll)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935' or sha(WS/'scripts/audit_client455_renderer_owner.py')!=ref['script_sha256']:raise ValueError('Changed owner inputs')
    mode='client' if args.client else 'gpu';base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'{mode}{len(list(base.glob(mode+"*")))+1:03}';root.mkdir();_,fixture=stage_inputs(root);exe=root/('RF_Online.bin' if args.client else 'renderer-owner-probe.exe');shutil.copyfile(original,exe);output=root/'result.json'
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_OWNER_GOLDEN=str(golden),RF_SHADER_DLL=str(dll),RF_DRAW_FIXTURE=str(fixture),RF_LAB_HELPER_OUTPUT=str(output));command=[str(exe),'--rf-renderer-owner-scenario'] if args.client else [str(exe),str(golden),str(dll),str(fixture),str(output)]
    run=subprocess.run(command,cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Renderer owner:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['real_model_draws']!=92 or native['real_frames']!=2 or native['heap_com_balance']:raise ValueError('Incomplete owner path')
    rendered=frames(root);report={'scope':'Source renderer owner constructor/device-gate/destructor/typed contexts withreal BN-MSH-ANI-pose-mainD3D9draw;normal integration remainsopen','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'frames':rendered,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'build_report_sha256':sha(WS/'inventory/client455-renderer-owner-build.json'),'reference_report_sha256':sha(WS/'inventory/client455-renderer-owner-reference.json'),'input_exe_executed':False,'provider_sha256':sha(dll),'original_trig_parity':False}
    if args.client:
        previous=json.loads((WS/'inventory/client455-renderer-owner-gpu.json').read_text(encoding='utf-8'));link=json.loads((WS/'inventory/client455-renderer-owner-link.json').read_text(encoding='utf-8'))
        if digest!=link['lab']['exe_sha256'] or native!=previous['native'] or [r['sha256'] for r in rendered]!=[r['sha256'] for r in previous['frames']]:raise ValueError('Fullclient owner differs from component')
        report.update(component_report_sha256=sha(WS/'inventory/client455-renderer-owner-gpu.json'),link_report_sha256=sha(WS/'inventory/client455-renderer-owner-link.json'),dmalloc_balance=0,game_dlls_loaded=False,normal_game_entry_executed=False)
    (WS/f'inventory/client455-renderer-owner-{mode}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
