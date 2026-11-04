"""Name retained SDK bodies for comparison; route other callers to own source.

No instruction bytes change. Only selected definition names, appended undefined
symbols and caller relocation indexes change in ignored working COFF copies.
"""
import struct
from export_character_analysis import coff_function_records

BINDINGS={
 '?FindParent@@YAPAUObjectMesh@@PADPAU1@H@Z':'_RFCharacterOriginal_FindByName',
 '?FindParent@@YAHPAUObjectMesh@@H0H@Z':'_RFCharacterOriginal_BindParents',
 '?RematchParent@@YAHPAUObjectMesh@@H0H@Z':'_RFCharacterOriginal_RematchParents',
 '?FindBlendParent@@YAXPAUObjectMesh@@H0HPAVObjectData@@@Z':'_RFCharacterOriginal_BindBlends',
 '?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z':'_RFCharacterOriginal_InitVertex',
 '?ConvertVtToD3D@@YAXAAVCHARACTERVERTEX@@AAUEXPTVERTEX@@@Z':'_RFCharacterOriginal_ConvertVertex',
 '?ConvertUV@@YAXAAVCHARACTERVERTEX@@UtagTEXCOORDFLOAT@@@Z':'_RFCharacterOriginal_ConvertUV',
 '?DecodeTwoBlendPhysiqueData@@YAXPAVCHARACTERVERTEX@@HPAUPHYSIQUE@@H@Z':'_RFCharacterOriginal_DecodePhysique',
}

def source_bindings(data):
    functions=coff_function_records(data)
    table,count=struct.unpack_from('<II',data,8);strings=table+18*count
    length=struct.unpack_from('<I',data,strings)[0]
    if strings+length!=len(data):raise ValueError('Expected terminal COFF string table')
    old_strings=bytearray(data[strings:]);symbols=bytearray(data[table:strings]);appended=bytearray();mapping={};changes=[]
    def add_string(name):
        offset=len(old_strings);old_strings.extend(name.encode('ascii')+b'\0');return offset
    index=0
    while index<count:
        at=table+18*index;record=data[at:at+18];section,kind,storage,aux=struct.unpack_from('<hHBB',record,12)
        if record[:4]==b'\0'*4:
            offset=struct.unpack_from('<I',record,4)[0]
            if not 4<=offset<length:raise ValueError('Bad COFF name')
            end=data.find(b'\0',strings+offset,strings+length)
            if end<0:raise ValueError('Unterminated COFF name')
            name=data[strings+offset:end].decode('ascii')
        else:name=record[:8].split(b'\0',1)[0].decode('ascii')
        if section>0 and storage==2 and name in BINDINGS:
            if name not in functions:raise ValueError('Selected symbol is not a function')
            alias=BINDINGS[name];struct.pack_into('<II',symbols,18*index,0,add_string(alias))
            undef=count+len(appended)//18
            appended.extend(struct.pack('<IIIhHBB',0,add_string(name),0,0,kind,2,0))
            mapping[index]=undef
            changes.append({'symbol':name,'retained_as':alias,'symbol_index':index,'undefined_index':undef})
        index+=1+aux
    if not changes:return data,[]
    result=bytearray(data[:table]);sections=struct.unpack_from('<H',data,2)[0]
    # Calls inside retained comparison bodies remain within the comparison group.
    retained=[(f['section'],f['section_offset'],f['section_offset']+f['size']) for n,f in functions.items() if n in BINDINGS]
    redirected=[]
    for s in range(1,sections+1):
        header=20+(s-1)*40;reloc=struct.unpack_from('<I',data,header+24)[0];n=struct.unpack_from('<H',data,header+32)[0]
        if n==65535:raise ValueError('Overflow relocation tables unsupported')
        if n and (reloc<20+40*sections or reloc+10*n>table):raise ValueError('Unbounded relocation table')
        for j in range(n):
            at=reloc+10*j;address,symbol=struct.unpack_from('<II',data,at)
            if symbol>=count:raise ValueError('Relocation symbol outside table')
            if symbol in mapping and not any(sec==s and start<=address<end for sec,start,end in retained):
                struct.pack_into('<I',result,at+4,mapping[symbol]);redirected.append({'section':s,'offset':hex(address),'from_index':symbol,'to_index':mapping[symbol]})
    struct.pack_into('<I',result,12,count+len(appended)//18)
    struct.pack_into('<I',old_strings,0,len(old_strings))
    result.extend(symbols);result.extend(appended);result.extend(old_strings)
    after=coff_function_records(bytes(result))
    for name,f in functions.items():
        if after[BINDINGS.get(name,name)]['bytes']!=f['bytes']:raise ValueError('Instruction bytes changed')
    for c in changes:c['redirected_callers']=[x for x in redirected if x['from_index']==c['symbol_index']]
    return bytes(result),changes
