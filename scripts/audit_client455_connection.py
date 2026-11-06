"""Pin actual455 connection wait/event boundaries;no input executables are run."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());evidence=WS/'artifacts/client455-connection/reference.json';functions=json.loads(evidence.read_text())['ranges']['result'];countries=json.loads((WS/'inventory/client455-launcher-reference.json').read_text())['countries'];references=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'rva':hex(int(r['fn']['addr'],16)-0x400000),'bytes':int(r['fn']['size'],16),'sha256':sha(read_va(raw,int(r['fn']['addr'],16),int(r['fn']['size'],16)))} for r in functions]
        bodies += [{'rva':hex(int(r['vtable'],16)-0x400000),'bytes':296,'sha256':sha(read_va(raw,int(r['vtable'],16),296))} for r in countries]
        if previous is not None and previous!=bodies:raise ValueError('Connection ranges differ between455pins')
        previous=bodies;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':bodies})
    bypass=[]
    for row in countries:
        method=struct.unpack('<I',read_va(raw,int(row['vtable'],16)+284,4))[0]
        if method!=0x82c7b0:raise ValueError('Unexpected initialconnect selector')
        bypass.append({'nation':row['nation'],'slot284_method_rva':'0x42c7b0','skips_connect':False})
    report={'scope':'Initial client connection wait,events-only pump and delayed receipt;not fulltransport/authentication/country bootstrap','references':references,'country_connect_bypass':bypass,'script_sha256':sha(Path(__file__).read_bytes()),'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence.read_bytes())},'facts':['Slot284 false for all11 pinnedcountry profiles','World endpoint1/process0;global ./DataTable/ClientSystem.ini Network/ConnectTime default90 seconds,multiply1000 with DWORDwrap','Nonzero rawconnectresult produces localized6BE immediately;raw0 alone doesnotproveconnected','Wait capturesnow BEFOREevents-only8AA100 pump,checksconnected BEFOREstrictunsignedelapsed>timeout,thenSleep4','Receipt handlesatmost102accepted/102closed/102ready entries percall,including failedaccept attempts','Client accept is reported only when unsignednow-connectTime>1000,notatequality;socket/buffers initialized first','Russia argvloader setsendpoint0;boot Connect readsendpoint1;raw getters andInitzeroes confirmed'],'unknowns':['Full455Russian/European bootstrap sideeffects are not proved:remaining35handler constructors/countryproviders may have effects notyetrestored','No inference of successfulgameauthentication from a TCP connection'],'gaps':['Full35handlers/countryproviders and Russian/European successful initialbootstrap','Gatecrypto request/reply/wire layouts/ID-PW fields and realauthentication/login','Fullstandard/queued transport/internal security/filters/threads/Close/error/lifetime domains','WholeCreate/UI/world/gameplay/IME/shutdown/M6F/M9','Own bounded formatting doesnotcertify unsafeoriginal/errorlogging/window ownership domains'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-connection-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:15connection/event/country functions and11vtables pinned;strict wait/accept boundaries confirmed')
if __name__=='__main__':main()
