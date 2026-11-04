"""Verify actual compiled draw references and selectable-source patch integrity."""
import hashlib
import json
import subprocess
from pathlib import Path
from compare_client_binaries import WS


def main():
    build = WS/'work/client-build/build-character-diagnostic'
    if 'RF_CLIENT_455_DRAW_ARGUMENTS:BOOL=ON' not in (build/'CMakeCache.txt').read_text(encoding='utf-8'):
        raise ValueError('455 draw branch is not enabled')
    patches = json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'))
    for patch in patches:
        if hashlib.sha256((WS/patch['file']).read_bytes()).hexdigest() != patch['patched_sha256']:
            raise ValueError('Behavior patch changed')
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dumpbin = Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    full = b'?DrawCharacter@CRender@@QAEXPAVCHARACTEROBJECT@@QAMMMM@Z'
    short = b'?DrawCharacter@CRender@@QAEXPAVCHARACTEROBJECT@@PAMM@Z'
    records = []
    for name in ('cresobject','cnpc'):
        obj = build/f'RF_Online.dir/Release/{name}.obj'
        symbols = subprocess.check_output([str(dumpbin),'/symbols',str(obj)])
        undefined = b'\n'.join(line for line in symbols.splitlines() if b'UNDEF' in line)
        if full not in undefined or short in undefined:
            raise ValueError(f'{name}: wrong draw reference selected')
        records.append({'object':obj.relative_to(WS).as_posix(),
            'sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
            'full_reference':full.decode('ascii'),'missing_short_reference_absent':True})
    report = {'configuration':'Win32 Release diagnostic; RF_CLIENT_455_DRAW_ARGUMENTS=ON',
        'objects':records,'patch_manifest_sha256':hashlib.sha256((WS/'inventory/client-behavior-patches.json').read_bytes()).hexdigest(),
        'limit':'Compiled reference selection and static 455 argument evidence; no GPU runtime or full render equivalence claimed.'}
    (WS/'inventory/client-draw-call-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: both real client objects reference the full SDK draw API; missing shortened reference is absent.')


if __name__=='__main__':
    main()
