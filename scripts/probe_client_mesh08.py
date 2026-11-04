"""Run real MESH08framing/round-trip/guarded-boundary checks in own full-client entry."""
import hashlib,json,os,shutil,subprocess
from compare_client_binaries import WS
from probe_client_helpers import import_names

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_MESH08')!='ON':raise ValueError('Successful MESH08lab required')
    for group in ['lab_input_sha256','mesh08_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale MESH08lab source:'+name)
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    linked=json.loads((WS/'inventory/client455-mesh08-link.json').read_text(encoding='utf-8'))['lab']
    if linked['exe_sha256']!=digest or len(linked['functions'])!=2:raise ValueError('MESH08linked lab proof required')
    proof=json.loads((WS/'inventory/client455-mesh08.json').read_text(encoding='utf-8'));corpus=json.loads((WS/'inventory/character-mesh08-corpus.json').read_text(encoding='utf-8'))
    if proof['corpus_report_sha256']!=sha(WS/'inventory/character-mesh08-corpus.json') or sha(WS/corpus['native_golden'])!=corpus['native_golden_sha256']:raise ValueError('MESH08corpus changed')
    for sample in corpus['samples']:
        if sha(WS/sample['copy'])!=sample['sha256']:raise ValueError('MESH08input changed')
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    root=WS/'work/client-mesh08-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True);exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected MESH08snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local game DLL')
    output=root/f'result-{len(list(root.glob("result-*.json")))+1:03}.json';env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output);env['RF_MESH08_GOLDEN']=str(WS/corpus['native_golden'])
    run=subprocess.run([str(exe),'--rf-mesh08-scenario'],cwd=root,env=env,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:raise ValueError(f'Full-client MESH08scenario failed:{run.returncode:#x}:{run.stderr!r}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native!=proof['native_test']:raise ValueError('Full-client MESH08checks differ fromcomponent')
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'native_test':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'game_dlls_loaded':False,'link_report_sha256':sha(WS/'inventory/client455-mesh08-link.json'),'scope':'Own full-client entry,source reader/writer,12pinned real samples/393parts and1309guarded truncations;Dmalloc balance0. No physicalGPU/network/gameDLL/reference EXE/normal WinMain execution. Normal fullmodel-loader integration remains open.'}
    (WS/'inventory/client455-mesh08-runtime.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{native["checks"]}actual full-client MESH08checks/{native["real_files"]}real files/{native["parts"]}parts;no GPU/network/game DLLs.')

if __name__=='__main__':main()
