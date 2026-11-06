"""Pin455sprite path/texture contracts and verify realSPR structure losslessly."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()

def sprite(raw):
    version,actions=struct.unpack_from('<II',raw);pos=8;counts=[];formats={};rebuilt=bytearray(raw[:8])
    if version!=0x3f8ccccd or actions>=16:raise ValueError('Unexpected selectedSPR version/actions')
    for action in range(actions):
        n=struct.unpack_from('<I',raw,pos)[0];pos+=4;counts.append(n);rebuilt+=struct.pack('<I',n)
        if n>65535:raise ValueError('Native WORD frame domain exceeded')
        for frame in range(n):
            fields=struct.unpack_from('<6I',raw,pos);pos+=24;fmt,ox,oy,x,y,size=fields
            if not x or not y or max(ox,oy,x,y)>65535 or pos+size>len(raw):raise ValueError('Invalid selectedSPR frame')
            expected={21:4*x*y,23:2*x*y,25:2*x*y,0x31545844:x*y//2,0x35545844:x*y}.get(fmt)
            if size!=expected:raise ValueError('SelectedSPR payload does not match455format size')
            rebuilt+=struct.pack('<6I',*fields)+raw[pos:pos+size];pos+=size;formats[str(fmt)]=formats.get(str(fmt),0)+1
    if pos!=len(raw) or bytes(rebuilt)!=raw:raise ValueError('SelectedSPR failed exact roundtrip')
    return {'actions':actions,'frames':counts,'total_frames':sum(counts),'formats':formats,'roundtrip_equal':True}

def main():
    ranges=[(0x7b0110,0x8b),(0x7b01a0,0x10a),(0x7afcb0,0xff),(0x7afdb0,0xc7),(0x8cfb10,0x17),(0x8cfb90,0x2d2),(0x8d1600,0x44),(0x8f2e70,0x2f8),(0x5e5b90,0x1b),(0x5e5bb0,0x1b),(0xbdb6a0,55*128),(0x5e1920,0x93),(0x5fa190,0xee),(0x5fa370,0x52)]
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        rows=[{'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for at,n in ranges]
        if previous is not None and rows!=previous:raise ValueError('455sprite bodies/table differ')
        previous=rows;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':rows})
    table=read_va(raw,0xbdb6a0,55*128);names=[table[i*128:(i+1)*128].split(b'\0')[0].decode('ascii') for i in range(55)]
    if len(set(names))!=55:raise ValueError('Unexpected455sprite filename table')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for folder,name in [('Common','mouse.spr'),('Common','common.spr'),('ko-kr','common.spr'),('ru-ru','common.spr')]:
        p=client/'SpriteImage'/folder/name;data=p.read_bytes();inputs.append({'file':str(p),'sha256':sha(data),'bytes':len(data),**sprite(data)})
    report={'scope':'55target sprite filenames/localized fallback and source texture upload;selected normal startup sprites,not fullUI migration','references':refs,'filenames':names,'selected_inputs':inputs,'script_sha256':sha(Path(__file__).read_bytes()),'facts':['7B0110 rejectsID>=55,tries./SpriteImage/<folder>/<filename>,_access thenCommon fallback evenifmissing','Target IDs differ from legacy:loading2/login3/item8/unitparts19;only mouse0/common1 directly integrated now','8CFB90 SPRfloat1.1,actions<16,WORD frame count loaded fromDWORD,24byte frame headers and native20byte records','8F2E70 supportsDXT1/DXT5/ARGB32/R5G6B5/A1R5G5B5;managed texture,contiguous payload copy;noncompressed usessecond managedtexture +surface TRIANGLE roundtrip','5E1920/5FA190/5FA370 onlyallocate/initialize CharacterDataMgr;actualtableIO occurslater,notthisCreate boundary'],'gaps':['Other legacy UI groups/IDs/layout/resource bindings and full455UI','Target sprite Unit path replacement/cache semantics andall reload/error cases','Source bounds malformed input/checks failedHRESULT andfrees failures;unsafe/error/allocation domains notidentical','SPR reader/general animation/draw methods still legacy andnot fullycertified455','Complete Create/launcher/normal world tables/network/shutdown andM9'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-sprites-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pinned_ranges':len(ranges),'names':len(names),'selected':[{k:r[k] for k in ['file','actions','total_frames','formats','roundtrip_equal']} for r in inputs]}))
if __name__=='__main__':main()
