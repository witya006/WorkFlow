"""Prove real CResObject/constructor callers select the source timing object."""
import argparse,hashlib,json,re,struct
from compare_client_binaries import WS,pe
from export_character_analysis import coff_function_records
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calls(data,wanted):
    table,count=struct.unpack_from('<II',data,8);strings=table+18*count;names={};i=0
    while i<count:
        at=table+18*i;record=data[at:at+18];name=record[:8].split(b'\0',1)[0].decode('ascii',errors='replace')
        if record[:4]==bytes(4):offset=struct.unpack_from('<I',record,4)[0];name=data[strings+offset:data.index(b'\0',strings+offset)].decode('ascii')
        names[i]=name;i+=1+record[17]
    found=[];functions=coff_function_records(data)
    for section in range(1,struct.unpack_from('<H',data,2)[0]+1):
        h=20+40*(section-1);size,raw=struct.unpack_from('<II',data,h+16);reloc=struct.unpack_from('<I',data,h+24)[0];n=struct.unpack_from('<H',data,h+32)[0]
        if n==65535:raise ValueError('Unexpected overflow relocation table')
        for j in range(n):
            offset,symbol,kind=struct.unpack_from('<IIH',data,reloc+10*j)
            if names.get(symbol) not in wanted:continue
            if kind!=0x14 or not offset or offset+4>size or data[raw+offset-1]!=0xe8:raise ValueError('Timing reference not a direct CALL')
            candidates=[(name,f) for name,f in functions.items() if f['section']==section and f['section_offset']<=offset]
            if not candidates:raise ValueError('Timing call lacks containing function')
            name,f=max(candidates,key=lambda p:p[1]['section_offset']);found.append({'target':names[symbol],'caller':name,'section':section,'offset':hex(offset),'opcode':'E8 REL32'})
    return found
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args();mode='lab' if args.lab else 'normal';root=WS/'work/client-build'/('build-helper-lab' if args.lab else 'build-character-diagnostic');summary=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'));proof=json.loads((WS/'inventory/client455-animation-timing-build.json').read_text(encoding='utf-8'));cpu=json.loads((WS/'inventory/client455-animation-timing-cpu.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['build_settings'].get('RF_CLIENT_455_ANIMATION_TIMING')!='ON' or cpu['build_report_sha256']!=sha(WS/'inventory/client455-animation-timing-build.json'):raise ValueError('Verified timing build required')
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed timing source')
    ledger=json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'));patch=next(r for r in ledger if r['file']=='work/client-build/source/RF_Client/cresobject.cpp')
    if sha(WS/patch['file'])!=patch['patched_sha256'] or patch['animation_timing']['reference_report_sha256']!=sha(WS/'inventory/client455-animation-timing-reference.json'):raise ValueError('Changed timing caller patch')
    obj=root/'RF_Online.dir/Release/cresobject.obj';module=root/'R3EngineClientMT.dir/Release/client455_animation_timing.obj'
    for p in [obj,module]:
        if '/DEFAULTLIB:"LIBCMT"' not in directives(p.read_bytes()):raise ValueError('Timing caller/module not x86MT')
    advance='_RF455_AdvanceAnimationFrameValue';initialize='_RF455_InitializeAnimationControl';selected=calls(obj.read_bytes(),[advance,initialize])
    if sum(c['target']==advance and c['caller'].startswith('?CalculateCurrentAnimationFrame@CResObject@@') for c in selected)!=2 or sum(c['target']==initialize and c['caller'].startswith('??0CAnimation@@') for c in selected)!=1:raise ValueError('Actual frame/constructor callsites missing:'+str(selected))
    mapping=(root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace');linked=[]
    for symbol in [advance,initialize,'_RF455_InitializeSecondaryState']:
        lines=[line for line in mapping.splitlines() if re.search(r'\s'+re.escape(symbol)+r'\s',line)]
        if not lines:
            if symbol!= '_RF455_InitializeSecondaryState' or args.lab:raise ValueError('Missing timing symbol:'+symbol)
            continue
        if len(lines)!=1 or 'R3EngineMT:client455_animation_timing.obj' not in lines[0]:raise ValueError('Wrong timing source provider')
        address=re.search(re.escape(symbol)+r'\s+([0-9a-fA-F]{8})',lines[0]);linked.append({'symbol':symbol,'rva':hex(int(address[1],16)-0x400000),'provider':'R3EngineMT:client455_animation_timing.obj'})
    exe=root/'Release/RF_Online.bin';path=WS/'inventory/client455-animation-timing-link.json';report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {};report[mode]={'architecture':'x86','image_base':'0x400000','exe_sha256':sha(exe),'exe_bytes':exe.stat().st_size,'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'functions':linked,'actual_callsites':selected,'object_sha256':sha(obj),'module_sha256':sha(module),'scope':'Normal actualCResObject numeric andCAnimation initialization selectsource455;full455CharacterABI/normalrenderer stillopen'};path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{mode} CResObject2frame calls+CAnimationctor selectsource455')
if __name__=='__main__':main()
