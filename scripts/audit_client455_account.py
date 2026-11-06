"""Pin455 account functions/wire contracts;never execute either reference PE."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());evidence=WS/'artifacts/client455-account/reference-final.json';raw_evidence=json.loads(evidence.read_text());ranges=raw_evidence['ranges']['result'];references=[];previous=None
    countries=json.loads((WS/'inventory/client455-launcher-reference.json').read_text())['countries'];profiles=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'rva':hex(int(r['fn']['addr'],16)-0x400000),'bytes':int(r['fn']['size'],16),'sha256':sha(read_va(raw,int(r['fn']['addr'],16),int(r['fn']['size'],16)))} for r in ranges]
        bodies.append({'rva':hex(0x5f0f93-0x400000),'bytes':45,'sha256':sha(read_va(raw,0x5f0f93,45))})
        for row in countries:
            method=struct.unpack('<I',read_va(raw,int(row['vtable'],16)+256,4))[0]
            body=read_va(raw,method,40);expected=row['nation']==8
            # Country selector bodies share the verified constant-return prologue.
            true=bytes.fromhex('b8 01 00 00 00') in body
            false=bytes.fromhex('33 c0') in body
            if true==false or true!=expected:raise ValueError('Unverified ticket country selector:'+hex(method))
            bodies.append({'rva':hex(method-0x400000),'bytes':40,'sha256':sha(body)})
            if folder=='current':profiles.append({'nation':row['nation'],'slot256_rva':hex(method-0x400000),'ticket_profile':true})
        if previous is not None and bodies!=previous:raise ValueError('Account ranges differ between455pins')
        previous=bodies;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':bodies})
    report={'scope':'Gate seed,account request/reply layouts and bounded consumer fields;not fullauthentication/loginUI','references':references,'ticket_profiles':profiles,'script_sha256':sha(Path(__file__).read_bytes()),'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence.read_bytes())},
        'facts':['Group21/op12 empty request on endpoint0 accept;op13 stores BYTE+1 and LE16+3 with wrap','Seed fields are additive/xor login transforms,not AES keys','Join84=ID51/PW33;pushclose88=ID51/PW33/zero4;success clears PW33','Login342=ID51/PW33/type1/ticket257;transform allbytes then overwrite byte84','Only nation8 slot256 uses ticket at85;nullticket targetreturn undefined','Login reply50 uses result0/account1;clearPW33 unless result5','World result header3 and declareddata;sign-extended count;record72/value4/name64/status1/padding3;capacity300','Select requestLE16 and storedselected index;reply24=result/IP/port/16keys/unusedbyte','5F0F93 reads MASTER_SERVER/SERVER_TYPE default0 into setter5F0FE0;initialization callsite notyetported','Request status pending/tick,ND305/dialogF100/style5;zone-specific secondary predicates stillopen'],
        'gaps':['Actual online authentication,fullcountry bootstrap and ticket acquisition/UI','MASTER_SERVER/SERVER_TYPE ini provider invocation;source property retainsknownfield/default0','Global mode2 provider and outgoing replay routing;packer bypass branch is available,but normal provider remainsopen','World UI value/status interpretation and fulltarget UI semantics','Servernotify11 uses bounded2byte legacy shutdown/UI;targetlocalized33A-C/quit sideeffects notyetported','35gamehandlers and otherwire messages,world/gameplay/IME/lifecycle/M6F/M9','Own bounded rejection intentionallydoesnotreproduce original nullticket undefinedreturn,count128+/name0/name65+/truncation memoryerrors','Direct legacyvoid reply entrypoints retain pointer-only signatures;real framed dispatcher is lengthchecked'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['facts'][-1]='Pending/tick;activeprocess0!=2 OR mode436232==4 opens ND305/dialogF100/style5;responsecloses whenactive0!=2 OR mode!=-1'
    report['gaps'].append('Zone requestmode436232 writers/provider remainopen;known send/receive predicates are ported')
    (WS/'inventory/client455-account-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:26account/state functions and11country selectors pinned;342byte login/seed/world contracts')
if __name__=='__main__':main()
