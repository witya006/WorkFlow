"""Audit source renderer-owner providers andactual caller relocations."""
import argparse,hashlib,json,struct
from compare_client_binaries import WS,pe
from coff_references import parse
from audit_client455_normal_character_api import map_records
from build_client455_x87_math import read_va

APIS=['_RF455_ConstructCharacterRenderer','_RF455_SetCharacterRendererDevice','_RF455_DestroyCharacterRenderer','_RF455_RendererModelContext','_RF455_BindRendererDrawContext']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');build=json.loads((WS/'inventory/client455-renderer-owner-build.json').read_text(encoding='utf-8'));summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_RENDERER_OWNER')!='ON' or sha(WS/build['library'])!=build['library_sha256']:raise ValueError('Renderer owner-enabled successful build required')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed owner source')
    exe=root/'Release/RF_Online.bin';raw=exe.read_bytes();image=pe(raw);mapping=map_records((root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace'));functions=[];calls=[]
    for symbol in APIS:
        records=[r for r in mapping.get(symbol,[]) if r['provider']=='RFClient455RendererOwner:owner.obj']
        if len(records)!=int(args.lab):raise ValueError('Unexpected owner provider selection:'+symbol)
        if records:functions.append({'symbol':symbol,'rva':hex(records[0]['address']-image['image_base']),'provider':records[0]['provider']})
    if args.lab:
        obj=root/'RF_Online.dir/Release/test_client455_renderer_owner.obj';references=parse(obj.read_bytes())['references'];selected=[r for r in references if r['symbol'] in APIS and r['form']=='call'];seen=set()
        for ref in selected:
            if not ref['caller']:raise ValueError('Missing owner caller')
            origin=next(r for r in mapping[ref['caller']['name']] if r['provider'].endswith('test_client455_renderer_owner.obj'));at=origin['address']+ref['offset']-ref['caller']['offset']-1;instruction=read_va(raw,at,5)
            if instruction[0]!=0xe8:raise ValueError('Missing final E8')
            destination=at+5+struct.unpack_from('<i',instruction,1)[0];wanted=next(r['address'] for r in mapping[ref['symbol']] if r['provider']=='RFClient455RendererOwner:owner.obj');thunks=[]
            for _ in range(8):
                if destination==wanted:break
                branch=read_va(raw,destination,5)
                if branch[0]!=0xe9:raise ValueError('Wrong source owner target')
                thunks.append({'rva':hex(destination-image['image_base']),'bytes':branch.hex()});destination+=5+struct.unpack_from('<i',branch,1)[0]
            if destination!=wanted:raise ValueError('Unresolved owner thunk')
            calls.append({'caller':ref['caller']['name'],'target':ref['symbol'],'call_rva':hex(at-image['image_base']),'destination_rva':hex(destination-image['image_base']),'linker_thunks':thunks});seen.add(ref['symbol'])
        if seen!=set(APIS):raise ValueError('Incomplete owner callsites')
    path=WS/'inventory/client455-renderer-owner-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','exe_sha256':sha(exe),'exe_bytes':len(raw),'entry_rva':hex(image['entry_rva']),'library_sha256':build['library_sha256'],'functions':functions,'actual_calls':calls,'scope':'Source renderer owner;normal typedCharacter/D3D9engine stillopen'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} rendererowner/{len(functions)}sourceAPIs linked')
if __name__=='__main__':main()
