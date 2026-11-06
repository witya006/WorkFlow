"""Pin455 bootstrap/state/standard TCP code;never execute reference binaries."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    pins=json.loads((WS/'config/client-target.json').read_text());launcher=json.loads((WS/'inventory/client455-launcher-reference.json').read_text())
    raw_evidence=WS/'artifacts/client455-bootstrap/reference.json';evidence=json.loads(raw_evidence.read_text())
    ranges=[(int(r['fn']['addr'],16),int(r['fn']['size'],16)) for r in evidence['funcs']['result']]
    ranges += [(0x7d04e0,0x7ec),(0x7d2b90,0x13)]
    ranges += [(at,0x18 if value else 0x15) for at,value in [(0x82c9f0,1),(0x82e750,1),(0x82ee20,1),(0x831df0,1),(0x82ce90,0),(0x82c6b0,0),(0x82c6d0,0),(0x82c7f0,0)]]
    references=[];previous=None;countries=[]
    truth={0x82c9f0:True,0x82e750:True,0x82ee20:True,0x831df0:True,0x82ce90:False,0x82c6b0:False,0x82c6d0:False,0x82c7f0:False}
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for at,size in ranges]
        tables=[{'rva':hex(int(row['vtable'],16)-0x400000),'bytes':296,'sha256':sha(read_va(raw,int(row['vtable'],16),296))} for row in launcher['countries']]
        if previous is not None and previous!=bodies+tables:raise ValueError('Bootstrap ranges differ between455pins')
        previous=bodies+tables;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':bodies+tables})
    for row in launcher['countries']:
        table=int(row['vtable'],16);methods={str(slot):struct.unpack('<I',read_va(raw,table+slot,4))[0] for slot in [252,240,292,256]}
        bypass=any(truth[method] for method in methods.values())
        if bypass!=(row['nation'] in [2,3,7,8]):raise ValueError('Unexpected455instance policy')
        countries.append({'nation':row['nation'],'vtable_rva':hex(table-0x400000),'selector_rvas':{k:hex(v-0x400000) for k,v in methods.items()},'instance_bypass':bypass})
    config=WS/'work/client-reference/current/DataTable/ko-kr/FG_CB.ini'
    # The reference lab may hold only the PE;the original asset is read-only.
    if not config.exists():config=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'DataTable/ko-kr/FG_CB.ini'
    report={'scope':'FG settings,instance gate and client network state/raw standard TCP contracts;not full455transport/framing/authentication','references':references,'countries':countries,'script_sha256':sha(Path(__file__).read_bytes()),'raw_evidence':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p.read_bytes())} for p in [raw_evidence,WS/'artifacts/client455-bootstrap/tcp-assembly.json',WS/'artifacts/client455-bootstrap/network-decompilation.json']],'fg_input':{'file':str(config),'sha256':sha(config.read_bytes())},'facts':['USEFG GetPrivateProfileString nSize4 thenatol;setter7D0CD0 storesraw int,no further semanticclaim','7D2B90 betweenFG andnetwork is an empty function','Singleinstance skippedonly China/Europe/Russia/Taiwan;Japan title selector doesnotbypass','Uppercasebasename must equal13byte RF_ONLINE.BIN;Toolhelp count>1 rejected;Global mutex ERROR_ALREADY_EXISTS rejected','Null CreateMutex accepted by455;target keeps handle until process exit','Connect562350 returns rawerrorcode:0success,-1alreadyconnected;activeBYTE[6],connectedDWORD[4]','Endpoint2/logout callsvirtualAccept(0,0,0),evenrequestedprocess!=0;callbackmarksconnectedusingactive0','RawstandardTCP failure returnsWSAGetLastError AFTERclosesocket:VA8B0505 then8B050B;this canerase actualconnect failure,eventfailure -3','OnthisWindows independentWinSock andactualsource closedport bothreturn0 afterclose;beforeclose10061;connected flagstaysfalse,thisisnot successfulauthentication','455Create allocates35handlers,configures2processes;capacity6;oldsource currently12handlers/1process'], 'gaps':['455two-process transport/queuedroute236byteconfig/framing/cipher and35handlers','GateAccept crypto request569CD0;legacy wire ID/PW13bytes vs455state50/32','FullConnectToServer wait/pump beforeengine remainsunported;do notinferauthentication','FGmeaning beyondstoredvalue,fullcountryproviders/video/BGM/errorlogging','FullUI/FT/ANSI/IME/ILevel/world/shutdown/M6F/M9'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-bootstrap-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:28bootstrap/network/policy functions and11country vtables match455pins')
if __name__=='__main__':main()
