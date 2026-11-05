"""Prove both real normal callers reach source frustum functions in the final PE."""
import argparse,hashlib,json,struct
from compare_client_binaries import WS,pe
from coff_references import parse
from audit_client455_normal_character_api import map_records
from build_client455_x87_math import read_va
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-frustum-build.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_FRUSTUM')!='ON' or proof['native']['status']!='PASS':raise ValueError('Successful selected frustum build required')
    if proof['reference_report_sha256']!=sha(WS/'inventory/client455-frustum-reference.json'):raise ValueError('Changed frustum reference')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed frustum source')
    ledger=json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'));exe=root/'Release/RF_Online.bin';raw=exe.read_bytes();image=pe(raw);mapping=map_records((root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace'));calls=[]
    specifications=[('global','?SetCharacterClipping@@','_RF455_PublishSystemCharacterFrustum','client455_frustum_system'),('cresobject','?ProcessClipping@CResObject@@','_RF455_IsBBoxInFrustum','client455_frustum')]
    for stem,caller_prefix,target,module in specifications:
        source=WS/f'work/client-build/source/RF_Client/{stem}.cpp';entry=next(p for p in ledger if p['file']==source.relative_to(WS).as_posix())
        if sha(source)!=entry['patched_sha256'] or entry['frustum']['reference_report_sha256']!=proof['reference_report_sha256']:raise ValueError('Changed frustum caller')
        obj=root/f'RF_Online.dir/Release/{stem}.obj';body=root/f'R3EngineClientMT.dir/Release/{module}.obj'
        for path in [obj,body]:
            if '/DEFAULTLIB:"LIBCMT"' not in directives(path.read_bytes()):raise ValueError('Expected modern x86MT caller/module')
        parsed=parse(obj.read_bytes());selected=[r for r in parsed['references'] if r['form']=='call' and r['symbol']==target and r['caller'] and r['caller']['name'].startswith(caller_prefix)]
        if len(selected)!=1:raise ValueError('Missing actual frustum caller:'+stem)
        if any(r['symbol'].startswith(('?SetFustumNormalPlane@@','?IsBBoxInFrustum@@')) for r in parsed['references']):raise ValueError('Legacy clipping reference survived')
        ref=selected[0];caller=next(m for m in mapping[ref['caller']['name']] if m['provider'].lower().endswith(stem+'.obj'));site=caller['address']+ref['offset']-ref['caller']['offset']-1;instruction=read_va(raw,site,5)
        if instruction[0]!=0xe8:raise ValueError('Not a final direct call')
        destination=site+5+struct.unpack_from('<i',instruction,1)[0];thunks=[];provider=None
        for _ in range(8):
            provider=next((m for m in mapping[target] if m['address']==destination and m['provider'].lower().endswith(':'+module+'.obj')),None)
            if provider:break
            branch=read_va(raw,destination,5)
            if branch[0]!=0xe9:raise ValueError(f'Wrong final source destination:{stem}:{destination:x}')
            thunks.append({'rva':hex(destination-image['image_base']),'bytes':branch.hex()});destination+=5+struct.unpack_from('<i',branch,1)[0]
        if not provider:raise ValueError('Unresolved/cyclic linker thunk')
        calls.append({'caller':ref['caller']['name'],'call_rva':hex(site-image['image_base']),'target':target,'destination_rva':hex(destination-image['image_base']),'linker_thunks':thunks,'provider':provider['provider'],'object_sha256':sha(obj),'module_sha256':sha(body),'source_sha256':sha(source)})
    path=WS/'inventory/client455-frustum-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':hex(image['image_base']),'exe_sha256':sha(exe),'exe_bytes':len(raw),'entry_rva':hex(image['entry_rva']),'actual_calls':calls,'build_report_sha256':sha(WS/'inventory/client455-frustum-build.json'),'scope':'Selected producer/AABB calls in actual normal source;full actor/Character layout/camera behavior remains open'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} twoactualfrustum calls resolve tosource;oldSDKclippingreferences absent')
if __name__=='__main__':main()
