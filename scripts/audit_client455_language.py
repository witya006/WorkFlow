"""Pin EDF/NDLanguage contracts,decode real language packs and make fixtures."""
import hashlib,json,shutil,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def key_bytes(encoded):
    adjusted=bytearray((v+(-(1<<((i+1)%8)) if i%2==0 else (1<<((i+1)%8))))&255 for i,v in enumerate(encoded))
    adjusted.reverse()
    return bytes(adjusted[i^1] for i in range(256))
def decode(raw):
    if len(raw)<289:raise ValueError('Short EDF envelope')
    n=struct.unpack_from('<I',raw,29)[0]
    if n>len(raw)-289:raise ValueError('Short EDF body/key')
    key=key_bytes(raw[33+n:289+n]);data=bytes((v+(-key[(i+1)%256] if i%2==0 else key[(i+1)%256]))&255 for i,v in enumerate(raw[33:33+n]))
    return data
def encode_with_envelope(raw,data):
    n=struct.unpack_from('<I',raw,29)[0]
    if len(data)!=n:raise ValueError('Roundtrip changed payload size')
    key=key_bytes(raw[33+n:289+n]);cipher=bytes((v+(key[(i+1)%256] if i%2==0 else -key[(i+1)%256]))&255 for i,v in enumerate(data))
    return raw[:33]+cipher+raw[33+n:]
def records(data):
    if len(data)<4:raise ValueError('Missing language count')
    count=struct.unpack_from('<I',data)[0];at=4;out=[]
    for _ in range(count):
        if len(data)-at<8:raise ValueError('Short language record header')
        ident,size=struct.unpack_from('<II',data,at);at+=8
        if size>len(data)-at:raise ValueError('Short language record text')
        out.append((ident,data[at:at+size]));at+=size
    return out,at
def main():
    sizes=[(0x5ee900,0xae),(0x5eec00,0x8a),(0x5eec90,0xcd),(0x5eed90,0xa8),(0x5eee80,0x73),(0x5eef00,0xdb),(0x5ef000,0x17b),(0x601e80,0x33),(0x601ec0,0x24),(0x601ef0,0x33),(0x601f30,0x19),(0x601f50,0x90),(0x601fe0,0x90),(0x6023b0,0x45),(0x603130,0x226),(0x603360,0xb1)]
    methods=[0x832970,0x82fba0,0x82c9b0,0x831dd0,0x82d300,0x82e080,0x82d9b0,0x82e730,0x82ede0,0x82f4b0,0x830920]
    tables=[0xaf94ec,0xaf82b4,0xaf6c54,0xaf918c,0xaf70e4,0xaf76d4,0xaf73dc,0xaf79cc,0xaf7cc4,0xaf7fbc,0xaf88a4];codepages=[949,1252,936,1252,1252,932,1252,1251,950,1252,874]
    pins=json.loads((WS/'config/client-target.json').read_text());references=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for at,n in sizes+[(at,0x18) for at in methods]]
        for table,at,cp in zip(tables,methods,codepages):
            if struct.unpack('<I',read_va(raw,table+76,4))[0]!=at or b'\xb8'+struct.pack('<I',cp) not in read_va(raw,at,0x18):raise ValueError('Changed virtual codepage provider')
        slots=[{'nation':i,'vtable_rva':hex(table-0x400000),'slot_offset':76,'method_rva':hex(at-0x400000),'codepage':cp} for i,(table,at,cp) in enumerate(zip(tables,methods,codepages))]
        item={'functions':bodies,'codepages':slots}
        if previous is not None and previous!=item:raise ValueError('Language contracts differ between pins')
        previous=item;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000',**item})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);root=WS/'work/client-reference/language455';root.mkdir(parents=True,exist_ok=True);countries=json.loads((WS/'inventory/client455-nation-paths-reference.json').read_text())['references'][0]['rows'];files=[];manifest=[]
    for country,cp in zip(countries,codepages):
        original=client/'DataTable'/country['folder']/'NDLanguage.edf'
        if not original.exists():continue
        raw=original.read_bytes();plain=decode(raw);rows,end=records(plain)
        if encode_with_envelope(raw,plain)!=raw:raise ValueError('EDF roundtrip failed')
        if not rows:raise ValueError('Empty real pack')
        copy=root/(country['folder']+'.edf');copy.write_bytes(raw);decoded=root/(country['folder']+'.payload');decoded.write_bytes(plain)
        row={'nation':country['id'],'folder':country['folder'],'codepage':cp,'file':str(original),'sha256':sha(raw),'copy':copy.relative_to(WS).as_posix(),'decoded':decoded.relative_to(WS).as_posix(),'decoded_sha256':sha(plain),'records':len(rows),'consumed':end,'payload_bytes':len(plain),'envelope_tail_bytes':len(raw)-289-len(plain),'zero_length':sum(not t for _,t in rows),'unterminated':sum(bool(t) and t[-1]!=0 for _,t in rows),'ids_equal_indices':all(i==ident for i,(ident,_) in enumerate(rows))}
        files.append(row);manifest.append(f'{cp}\t{copy}\t{decoded}\t{len(rows)}')
    fixture=root/'files.tsv';fixture.write_text('\n'.join(manifest)+'\n',encoding='ascii')
    report={'scope':'EDF decoding,NDLanguage byte records/index lookup and country codepage kernels;not fullETCAction factory/font/UI acceptance','references':references,'files':files,'fixture':fixture.relative_to(WS).as_posix(),'fixture_sha256':sha(fixture.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'facts':['EDF:29header/DWORDsize/payload/256key;header is read but not validated','Decoded key uses alternating +/- digit,reverse256 and swap adjacent bytes;payload alternating -/+ key[(i+1)%256]','NDLanguage:DWORDcount then count{DWORDid,DWORDbytes,bytes text};id is ignored by positional lookup6023B0','601EF0 stores codepage only after successful load603130','601F50/601FE0 scan actual IsDBCSLeadByteEx using stored codepage','603360 frees records and clears pointer;count/codepage retained'],'gaps':['Malformed/negative-size/overflow/OOM/reload quirks are not all accepted;bounded source failures must remain explicit','Full ETCAction providers/factories/launcher/network startup policies','Font selection/application and complete text/UI/gameplay acceptance'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-language-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files':len(files),'records':sum(f['records'] for f in files),'zero_length':sum(f['zero_length'] for f in files),'unterminated':sum(f['unterminated'] for f in files),'trailing_payload':[f['folder'] for f in files if f['consumed']!=f['payload_bytes']]}))
if __name__=='__main__':main()
