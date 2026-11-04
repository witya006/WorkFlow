"""Verify actual compiled draw references and selectable-source patch integrity."""
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
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
    selected = []
    cache = (build/'CMakeCache.txt').read_text(encoding='utf-8')
    for name,option,expected,obsolete in [
            ('effectutil','RF_CLIENT_455_EFFECT_LOG',b'?RF455_EffectLog@@YAXPBD@Z',b'?SendLog@@YA_NXZ'),
            ('cgp_login','RF_CLIENT_455_LOBBY_TRANSITION',None,b'?CheckFiles@@YAPADXZ')]:
        if f'{option}:BOOL=ON' not in cache:
            raise ValueError(f'{option} is disabled')
        obj = build/f'RF_Online.dir/Release/{name}.obj'
        symbols = subprocess.check_output([str(dumpbin),'/symbols',str(obj)])
        undefined = b'\n'.join(line for line in symbols.splitlines() if b'UNDEF' in line)
        if obsolete in undefined or expected is not None and expected not in undefined:
            raise ValueError(f'{name}: wrong reference branch compiled')
        selected.append({'object':obj.relative_to(WS).as_posix(),'sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
            'option':option,'obsolete_reference_absent':obsolete.decode('ascii')})
    project = (build/'RF_Online.vcxproj').read_text(encoding='utf-8-sig')
    xml = ET.fromstring(project)
    ns = {'m':'http://schemas.microsoft.com/developer/msbuild/2003'}
    definitions = ';'.join(node.text or '' for node in xml.findall('.//m:ClCompile/m:PreprocessorDefinitions',ns))
    link_options = ' '.join(node.text or '' for node in xml.findall('.//m:Link/m:AdditionalOptions',ns))
    if '_DEVELOPER_' in definitions.split(';') or re.search(r'(?:^|\s)/FORCE(?=[:\s]|$)',link_options,re.I):
        raise ValueError('Unexpected developer bypass or forced unresolved link')
    report = {'configuration':'Win32 Release diagnostic; RF_CLIENT_455_DRAW_ARGUMENTS=ON',
        'objects':records,'other_reference_selections':selected,'developer_mode':False,'forced_link':False,
        'patch_manifest_sha256':hashlib.sha256((WS/'inventory/client-behavior-patches.json').read_bytes()).hexdigest(),
        'limit':'Compiled reference selection and static 455 argument evidence; no GPU runtime or full render equivalence claimed.'}
    (WS/'inventory/client-draw-call-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: both real client objects reference the full SDK draw API; missing shortened reference is absent.')


if __name__=='__main__':
    main()
