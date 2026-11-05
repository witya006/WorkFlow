"""Audit normal compiled Character consumers before the coupled typed port."""
import collections,ctypes,hashlib,json,re,struct,xml.etree.ElementTree as ET
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from coff_references import parse

CLASSES={'ChInterface','CRender','CHARACTEROBJECT','ObjectMesh','ChAnimation','AnimationManager','CObjectManager','CMeshManager','TextureManager','ChTexture','AlphaMeshManager','EffectObjectManager','EffectObject','EffectFileList','ItemEffectList','EffectPatternList','EffectList','CEffectMap'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def owner(symbol):
    constructor=re.match(r'^\?\?(?:[01]|_[GE])([A-Za-z]\w*)@@',symbol)
    method=re.match(r'^\?[^@]+@([A-Za-z]\w*)@@',symbol)
    return (constructor or method)[1] if constructor or method else None
def map_records(text):
    result=collections.defaultdict(list)
    for line in text.splitlines():
        match=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s+(?:(?:f|i)\s+)*(.+?)\s*$',line)
        if match:result[match[1]].append({'address':int(match[2],16),'provider':match[3]})
    return result
def code_only(raw):
    pattern=rb'//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern,lambda m:re.sub(rb'[^\r\n]',b' ',m[0]),raw)
def main():
    root=WS/'work/client-build/build-character-diagnostic';binary=root/'Release/RF_Online.bin';raw=binary.read_bytes();image=pe(raw);summary=json.loads((WS/'inventory/client-character-diagnostic.json').read_text(encoding='utf-8'))
    if summary['build_exit'] or summary['generated_objects']!=180:raise ValueError('Current complete normal build required')
    mappings=map_records((root/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace'));contracts=json.loads((WS/'inventory/character-public-contracts.json').read_text(encoding='utf-8'));declarations={r['mangled']:r['declaration'] for r in contracts['contracts']};known=set(declarations);uses=[];object_records=[];source_records=[]
    undecorate=ctypes.WinDLL('Dbghelp.dll').UnDecorateSymbolName;undecorate.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32];undecorate.restype=ctypes.c_uint32
    target_counts={}
    for target in ['RF_Online','R3EngineClientMT']:
        tree=ET.parse(root/(target+'.vcxproj'));sources=[Path(n.attrib['Include']) for n in tree.iter() if n.tag.rsplit('}',1)[-1]=='ClCompile' and 'Include' in n.attrib]
        expected=len(sources);target_counts[target]=expected
        if target=='RF_Online' and expected!=180 or target=='R3EngineClientMT' and expected<65:raise ValueError('Incomplete compiled source list:'+target)
        source_by_stem=collections.defaultdict(list)
        for source in sources:
            if not source.is_file():raise ValueError('Missing compiled source:'+str(source))
            source_by_stem[source.stem.lower()].append(source);source_records.append({'file':source.relative_to(WS).as_posix(),'sha256':sha(source),'target':target})
        objects=sorted((root/f'{target}.dir/Release').glob('*.obj'))
        if len(objects)!=expected:raise ValueError('Object count changed:'+target)
        for obj in objects:
            source=source_by_stem[obj.stem.lower()]
            if len(source)!=1:raise ValueError('Ambiguous object/source mapping:'+obj.name)
            object_records.append({'file':obj.relative_to(WS).as_posix(),'sha256':sha(obj),'source':source[0].relative_to(WS).as_posix(),'target':target})
            parsed=parse(obj.read_bytes())
            for ref in parsed['references']:
                symbol=ref['symbol'];klass=owner(symbol)
                if symbol not in known and klass not in CLASSES:continue
                if symbol in known and klass not in CLASSES and klass is not None:continue # D3DX/std helpers are separate.
                if symbol not in declarations:
                    name=ctypes.create_string_buffer(8192)
                    if not undecorate(symbol.encode('ascii'),name,len(name),0):raise ValueError('Could not demangle:'+symbol)
                    declarations[symbol]=name.value.decode('ascii')
                caller=ref['caller'];matches=[] if not caller else mappings.get(caller['name'],[]);caller_map=next((m for m in matches if m['provider'].lower().endswith(':'+obj.name.lower()) or m['provider'].lower()==obj.name.lower()),None)
                status='object_reference_only';site=None;destination=None;provider=None
                if ref['form'] in ['call','tailcall'] and caller_map:
                    site=caller_map['address']+ref['offset']-caller['offset']-1;instruction=read_va(raw,site,5)
                    if instruction[0] not in [0xe8,0xe9]:raise ValueError('Mapped call opcode differs:'+symbol)
                    destination=site+5+struct.unpack_from('<i',instruction,1)[0];target_map=next((m for m in mappings.get(symbol,[]) if m['address']==destination),None)
                    if target_map:status='linked_direct_'+ref['form'];provider=target_map['provider']
                    else:status='linked_location_target_unproven'
                elif ref['relocation']==6 and caller_map:
                    site=caller_map['address']+ref['offset']-caller['offset'];destination=struct.unpack('<I',read_va(raw,site,4))[0];target_map=next((m for m in mappings.get(symbol,[]) if (m['address']+ref['addend'])&0xffffffff==destination),None)
                    if target_map:status='linked_named_address';provider=target_map['provider']
                    else:status='linked_location_target_unproven'
                record={'symbol':symbol,'declaration':declarations.get(symbol),'owner':klass or 'global','source':source[0].relative_to(WS).as_posix(),'object':obj.relative_to(WS).as_posix(),'target':target,'caller':caller['name'] if caller else None,'section':ref['section'],'offset':hex(ref['offset']),'form':ref['form'],'status':status,'call_rva':hex(site-image['image_base']) if site is not None else None,'destination_rva':hex(destination-image['image_base']) if destination is not None else None,'provider':provider};uses.append(record)
    grouped=[]
    for symbol in sorted(set(r['symbol'] for r in uses)):
        selected=[r for r in uses if r['symbol']==symbol];linked=[r for r in selected if r['status'].startswith('linked_direct_')];addresses=[r for r in selected if r['status']=='linked_named_address'];providers=sorted(set(r['provider'] for r in linked+addresses));grouped.append({'symbol':symbol,'owner':selected[0]['owner'],'declaration':declarations.get(symbol),'object_references':len(selected),'linked_calls':len(linked),'linked_address_references':len(addresses),'caller_sources':sorted(set(r['source'] for r in selected)),'providers':providers})
    # Text evidence is explicitly candidate-only. It must never override the
    # COFF/PE call proof or imply a type from a common member name alone.
    members=['m_MaxObj','m_pMesh','m_Frame','m_OMaxFrame','m_Transition','m_TransFrame','m_TransTime','m_pMatBlend','m_BlendNum','m_MatResult','m_BefMatResult','m_BefMatLocal','m_Ident','m_pExtra','m_ParticleID','m_Entity']
    pattern=re.compile(rb'(?:->|\.)\s*('+b'|'.join(m.encode('ascii') for m in members)+rb')\b');fields=[]
    for record in source_records:
        data=(WS/record['file']).read_bytes();code=code_only(data)
        for match in pattern.finditer(code):
            line=code.count(b'\n',0,match.start())+1;start=code.rfind(b'\n',0,match.start())+1;end=code.find(b'\n',match.end());text=data[start:end if end>=0 else len(data)].strip().decode('ascii',errors='replace');fields.append({'file':record['file'],'line':line,'member':match[1].decode('ascii'),'text':text,'evidence':'lexical_candidate_not_typed_or_preprocessor_verified'})
    artifact=WS/'artifacts/client-character-interface/normal-references.json';artifact.parent.mkdir(parents=True,exist_ok=True);artifact.write_text(json.dumps({'objects':object_records,'sources':source_records,'references':uses,'field_candidates':fields},indent=2)+'\n',encoding='utf-8')
    linked=[r for r in uses if r['status'].startswith('linked_direct_')];status=collections.Counter(r['status'] for r in uses);top=collections.Counter(r['owner'] for r in linked)
    report={'scope':'Normal compiled client/R3Engine named Character consumers;field tokens are candidates,not full AST/indirect-call completeness','architecture':'x86','image_base':hex(image['image_base']),'exe':binary.relative_to(WS).as_posix(),'exe_sha256':sha(binary),'entry_rva':hex(image['entry_rva']),'objects':len(object_records),'client_objects':target_counts['RF_Online'],'engine_objects':target_counts['R3EngineClientMT'],'total_named_references':len(uses),'reference_status':dict(status),'linked_direct_calls':len(linked),'linked_distinct_symbols':len(set(r['symbol'] for r in linked)),'linked_owners':dict(top),'field_candidate_count':len(fields),'functions':grouped,'artifact':artifact.relative_to(WS).as_posix(),'artifact_sha256':sha(artifact),'contracts_sha256':sha(WS/'inventory/character-public-contracts.json'),'header_sha256':sha(WS/'work/recovered/character-legacy/include/Character.h'),'script_sha256':sha(Path(__file__)),'parser_sha256':sha(WS/'scripts/coff_references.py'),'limits':['Only named relocations in current normal objects;SDK internalcallee closure/indirectcalls not claimed complete','No455 mapping inferred from a legacy method name','Lexical member references can belong to another type;typed source review required','Linked locations with target_unproven remain unproven,never counted asverifiedcalls','No source orbinary inputs mutated;no runtime suites orinputEXEs executed']}
    (WS/'inventory/client455-normal-character-api.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['objects','total_named_references','reference_status','linked_direct_calls','linked_distinct_symbols','linked_owners','field_candidate_count']}))
if __name__=='__main__':main()
