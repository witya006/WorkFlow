"""Run source main/effect/deferred draw in the complete client own entry."""
import json,os,shutil,subprocess
from compare_client_binaries import WS,pe
from probe_client455_character_draw import inputs,frames,sha
from probe_client455_draw import stage_inputs
from probe_client_helpers import import_names
def main():
    source,ref,dll=inputs();build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'));gpu=json.loads((WS/'inventory/client455-character-draw-gpu.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_CHARACTER_DRAW')!='ON':raise ValueError('Main draw-enabled full client required')
    for group in ['lab_input_sha256','character_draw_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Changed source main draw caller')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must remain delayed')
    base=WS/'work/m9'/digest[:8];base.mkdir(parents=True,exist_ok=True);root=base/f'client{len(list(base.glob("client*")))+1:03}';root.mkdir();_,fixture=stage_inputs(root);exe=root/'RF_Online.bin';shutil.copyfile(original,exe);output=root/'result.json'
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    env=os.environ.copy();env.update(RF_SHADER_DLL=str(dll),RF_DRAW_FIXTURE=str(fixture),RF_LAB_HELPER_OUTPUT=str(output));run=subprocess.run([str(exe),'--rf-character-draw-scenario'],cwd=root,env=env,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(root/'stdout.txt').write_bytes(run.stdout);(root/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Fullclient main draw:{run.returncode:#x}:{run.stderr!r};{root}')
    native=json.loads(output.read_text(encoding='utf-8'));rendered=frames(root)
    if native!=gpu['native'] or [f['sha256'] for f in rendered]!=[f['sha256'] for f in gpu['frames']]:raise ValueError('Fullclient main draw differs from component')
    report={'scope':'Source main/effect/transparent/batch/dynamic/shadow routes inside fullclient ownentry;not normal game/455 parity','architecture':'x86','exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'frames':rendered,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'component_report_sha256':sha(WS/'inventory/client455-character-draw-gpu.json'),'dmalloc_balance':0,'game_dlls_loaded':False,'normal_game_entry_executed':False};(WS/'inventory/client455-character-draw-client.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native));print(root)
if __name__=='__main__':main()
