"""Discover actual country launcher slots from pinned455vtables,neverexecute inputs."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    pins=json.loads((WS/'config/client-target.json').read_text());lang=json.loads((WS/'inventory/client455-language-reference.json').read_text())
    ranges=[(0x7d04e0,0x7ec),(0x8392e0,0x2b4),(0x836cb0,0xca),(0x83b4f0,0xf5),(0x5e5920,0x67),(0x8395a0,0x21),(0x8395d0,0x2d),(0x839600,0x22),(0x839630,0x21),(0x562240,0x4d),(0x562290,0x2d),(0x56ad70,0x26),(0x56ada0,0x26),(0x56aad0,0x21),(0x5977e0,0x21),(0x83b5f0,0x2f),(0x83b620,0x2d),(0x83b650,0x18),(0x83b670,0x6c)]
    refs=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for at,size in ranges]
        tables=[{'rva':r['vtable_rva'],'bytes':296,'sha256':sha(read_va(raw,0x400000+int(r['vtable_rva'],16),296))} for r in lang['references'][0]['codepages']]
        if previous is not None and previous!=[bodies,tables]:raise ValueError('Launcher functions/vtables differ between455pins')
        previous=[bodies,tables];refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':bodies+tables})
    slots=[72,196,240,244,252,256,276,284,292];rows=[]
    for country in lang['references'][0]['codepages']:
        table=0x400000+int(country['vtable_rva'],16)
        rows.append({'nation':country['nation'],'vtable':hex(table),'methods':{str(n):hex(struct.unpack('<I',read_va(raw,table+n,4))[0]) for n in slots}})
    path=WS/'artifacts/client455-launcher';path.mkdir(parents=True,exist_ok=True);(path/'slots.json').write_text(json.dumps(rows,indent=2)+'\n')
    for row in rows:
        method=row['methods']['196'];expected='0x836cb0' if row['nation']==7 else '0x83b4f0' if row['nation']==3 else '0x8392e0'
        if method!=expected:raise ValueError('Country launcher selector changed')
    report={'scope':'Country launcher decoding/argument profiles and normal source-owned state;not authentication/network-order or fullETCAction acceptance','references':refs,'countries':rows,'ccr_bytes':93,'field_offsets':{'address':0,'port':4,'identifier':6,'account':57,'keys':61,'world_index':77,'personal_reference':79,'ignored_premium':83,'mode_value':87,'nation':91},'script_sha256':sha(Path(__file__).read_bytes()),'facts':['ETCAction slot196 selectsCCR93bytes for9nations;Russia/Europe argc==5 theninet_addr/atol/id/password','CCR zeroes93bytes,reads93withCreateFile share0,doesnotcheckReadFile result;extra bytesignored','CCRxor masks andfields confirmedinstructions;premium83..86 forced0,nationWORD checkedaftersettercalls','Identifiers bounded50bytes into51,password32into33 by5E5920;no encoding conversion','Argumentprofiles useendpoint0,CCR endpoint1;argumentprofiles do notsetaccount/masterkeys/premium/mode','Source WinMain nowreadslauncher beforelanguage;target FG_CB/network/instance/connect/BGM ordering remainsopen'],'gaps':['FullETCAction factory/providers and remaining bootstrap/instance/network/error policies','Target setter sideeffects beforeCCRnation-rejection notfully reproduced;own bridge commitsacceptedprofiles only','Worldindex/personal/premium/mode held in455state;target UI/network consumers notyetported','Legacy network wirepackets/ID limits andfullclient connect/auth/protocol/gameplay','OldCRT atoi overflow/nonASCII argument domains,unsafe stringreads/OOM/error logging fidelity','FullnormalCreate/title/video/UI/gameplay/shutdown/M9 acceptance'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-launcher-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:19launcher functions +11country vtables pinned;CCR93/argument routes confirmed')
if __name__=='__main__':main()
