"""Bounded regular x86 COFF references,including calls,tailcalls and data."""
import struct

def parse(data):
    def span(at,size):
        if at<0 or size<0 or at+size>len(data):raise ValueError('COFF range outside file')
        return data[at:at+size]
    span(0,20);machine,count,_,table,symbol_count,optional,_=struct.unpack_from('<HHIIIHH',data)
    if machine!=0x14c or optional:raise ValueError('Expected regular x86 COFF')
    span(20,40*count);span(table,18*symbol_count+4);strings=table+18*symbol_count;string_size=struct.unpack_from('<I',data,strings)[0]
    if string_size<4:raise ValueError('Short COFF string table')
    span(strings,string_size);symbols={};functions=[];i=0
    while i<symbol_count:
        at=table+18*i;name8=span(at,8);value,section,kind,storage,aux=struct.unpack_from('<IhHBB',data,at+8)
        if i+1+aux>symbol_count:raise ValueError('COFF auxiliary symbols exceed table')
        if name8[:4]==bytes(4):
            offset=struct.unpack_from('<I',name8,4)[0]
            if not 4<=offset<string_size:raise ValueError('COFF symbol name outside strings')
            end=data.find(b'\0',strings+offset,strings+string_size)
            if end<0:raise ValueError('Unterminated COFF symbol')
            name=data[strings+offset:end].decode('ascii')
        else:name=name8.split(b'\0',1)[0].decode('ascii')
        symbols[i]={'name':name,'value':value,'section':section,'kind':kind,'storage':storage}
        if section>0 and kind&0x20 and storage in [2,3]:
            if section>count:raise ValueError('COFF function section outside table')
            h=20+40*(section-1);size,raw=struct.unpack_from('<II',data,h+16)
            if value>=size:raise ValueError('COFF function outside section')
            span(raw,size);functions.append({'name':name,'section':section,'offset':value,'storage':storage})
        i+=1+aux
    sections=[];references=[]
    for section in range(1,count+1):
        at=20+40*(section-1);size,raw,reloc,_,relocs,_,flags=struct.unpack_from('<IIIIHHI',data,at+16)
        if relocs==65535:raise ValueError('COFF relocation overflow unsupported')
        if size and not (raw==0 and flags&0x80):span(raw,size)
        span(reloc,10*relocs);section_functions=sorted([f for f in functions if f['section']==section],key=lambda f:f['offset'])
        sections.append({'size':size,'raw':raw,'flags':flags})
        for j in range(relocs):
            offset,symbol,kind=struct.unpack_from('<IIH',data,reloc+10*j)
            if symbol not in symbols:raise ValueError('COFF reference uses absent/auxiliary symbol')
            if offset+4>size or raw==0:raise ValueError('COFF relocation outside raw section')
            opcode=data[raw+offset-1] if offset else None
            form='call' if kind==0x14 and opcode==0xe8 else 'tailcall' if kind==0x14 and opcode==0xe9 else 'other'
            candidates=[f for f in section_functions if f['offset']<=offset];caller=candidates[-1] if candidates else None
            references.append({'symbol':symbols[symbol]['name'],'section':section,'offset':offset,'relocation':kind,'form':form,'addend':struct.unpack_from('<I',data,raw+offset)[0],'caller':caller})
    return {'symbols':symbols,'functions':functions,'sections':sections,'references':references}
