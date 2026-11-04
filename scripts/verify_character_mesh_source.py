"""Check own source selection and linked SDK InitVertex calls in the full client."""
import argparse,hashlib,json,re,struct
from compare_client_binaries import WS
from coff_source_bindings import BINDINGS
from build_client455_x87_math import read_va

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal'
    build=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic')
    summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    proof=json.loads((WS/'inventory/character-mesh-source.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CHARACTER_MESH_SOURCE')!='ON':raise ValueError('Source mesh build required')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed mesh source')
    for key in ['library','adapted_archive']:
        if sha(WS/proof[key])!=proof[key+'_sha256']:raise ValueError('Changed mesh library')
    mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
    symbols={m[1]:(int(m[2],16),line) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))}
    selected=[]
    for symbol in BINDINGS:
        va,line=symbols[symbol]
        if 'CharacterMeshSource:bindings.obj' not in line:raise ValueError('Mesh function not selected from own source:'+symbol)
        selected.append({'symbol':symbol,'va':hex(va),'rva':hex(va-0x400000),'source':'character_mesh_bindings.cpp'})
    va,line=symbols['?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z']
    if 'CharacterMR-mesh-source:character_07.obj' not in line:raise ValueError('Unadapted InitVertex selected')
    data=(build/'Release/RF_Online.bin').read_bytes();calls=[]
    for offset,symbol in [(0x726,'?FindParent@@YAHPAUObjectMesh@@H0H@Z'),(0x74f,'?FindParent@@YAHPAUObjectMesh@@H0H@Z'),(0x7c8,'?FindBlendParent@@YAXPAUObjectMesh@@H0HPAVObjectData@@@Z')]:
        site=va+offset;code=read_va(data,site,5)
        if code[0]!=0xe8:raise ValueError('InitVertex call instruction changed')
        dest=site+5+struct.unpack_from('<i',code,1)[0];target=symbols[symbol][0];forward=[]
        for _ in range(4):
            if dest==target:break
            jump=read_va(data,dest,5)
            if jump[0]!=0xe9:raise ValueError('InitVertex call does not reach own source')
            forward.append(hex(dest));dest+=5+struct.unpack_from('<i',jump,1)[0]
        if dest!=target:raise ValueError('Unresolved source call thunk')
        calls.append({'va':hex(site),'rva':hex(site-0x400000),'bytes':code.hex(),'destination_symbol':symbol,'destination_va':hex(dest),'thunks':forward})
    path=WS/'inventory/character-mesh-source-link.json';out=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    out[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':sha(build/'Release/RF_Online.bin'),'architecture':'x86','image_base':'0x400000','source_functions':selected,'actual_init_vertex_calls':calls,'component_report_sha256':sha(WS/'inventory/character-mesh-source.json'),'scope':'Four own legacy CPU bindings and three actual InitVertex call destinations verified;455packed mesh/render parity remains open.'}
    path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode}4source mesh functions/3actual InitVertex destinations;legacy ABI,not455renderer parity.')

if __name__=='__main__':main()
