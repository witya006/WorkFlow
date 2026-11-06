"""Pin real455 progress/tutorial contracts and reject unsupported startup assumptions."""
import hashlib,json,re,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_name(raw,address):
    value=bytearray()
    for i in range(128):
        byte=read_va(raw,address+i,1)[0]
        if not byte:return value.decode('ascii')
        value.append(byte)
    raise ValueError('Unterminated RTTI type')
def static_references(raw,address):
    candidates=[];image=pe(raw)
    for section in image['sections']:
        if section['name']!='.text':continue
        data=raw[section['raw_offset']:section['raw_offset']+section['raw_size']]
        for opcode in [b'\xe8',b'\xe9']:
            at=data.find(opcode)
            while at!=-1:
                if at+5<=len(data):
                    target=(image['image_base']+section['rva']+at+5+struct.unpack_from('<i',data,at+1)[0])&0xffffffff
                    if target==address:candidates.append({'rva':hex(section['rva']+at),'opcode':opcode.hex()})
                at=data.find(opcode,at+1)
    absolute=[];needle=struct.pack('<I',address);at=raw.find(needle)
    while at!=-1:
        absolute.append(hex(at));at=raw.find(needle,at+1)
    return {'relative_E8_E9_candidates':candidates,'absolute_pointer_file_offsets':absolute,'computed_indirect_calls_excluded':False}
def main():
    evidence=WS/'artifacts/client455-progress/reference.json';source=json.loads(evidence.read_text());pins=json.loads((WS/'config/client-target.json').read_text());rows=source['ranges']['result'];previous=None;references=[];classes=[]
    expected=[(0,'CGP_Title',0x557b60,0xab0e14),(1,'CGP_LogIn',0x53b860,0xab0014),(2,'CGP_Tutorial',0x5584d0,0xab0f9c),(3,'CGP_MainGame',0x5454e0,0xab0324)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        ranges=[{'rva':hex(int(row['fn']['addr'],16)-0x400000),'bytes':int(row['fn']['size'],16),'sha256':sha(read_va(raw,int(row['fn']['addr'],16),int(row['fn']['size'],16)))} for row in rows]
        for stage,name,constructor,vtable in expected:
            locator=struct.unpack('<I',read_va(raw,vtable-4,4))[0];type_address=struct.unpack('<I',read_va(raw,locator+12,4))[0];type_name=read_name(raw,type_address+8)
            if type_name!='.?AV'+name+'@@':raise ValueError('Unexpected stage RTTI:'+type_name)
            slots=struct.unpack('<13I',read_va(raw,vtable,52))
            if folder=='current':classes.append({'stage':stage,'name':name,'constructor_rva':hex(constructor-0x400000),'vtable_rva':hex(vtable-0x400000),'RTTI':type_name,'slots_rva':[hex(value-0x400000) for value in slots]})
            for address,size in [(vtable-4,56),(locator,20),(type_address,8+len(type_name)+1)]:ranges.append({'rva':hex(address-0x400000),'bytes':size,'sha256':sha(read_va(raw,address,size))})
        call_scan=static_references(raw,0x5f0eb0)
        if call_scan['relative_E8_E9_candidates'] or call_scan['absolute_pointer_file_offsets']:raise ValueError('INI reader needs further caller analysis')
        if previous is not None and previous!=ranges:raise ValueError('455 progress ranges differ')
        previous=ranges;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':ranges,'master_ini_reader_references':call_scan})
    normal=WS/'work/client455-port/normal/source';header=normal/'mainapp.h';factory=normal/'mainapp.cpp';header_raw=header.read_bytes();factory_raw=factory.read_bytes()
    constants={name:int(re.search(rb'#define\s+'+name.encode()+rb'\s+(0[xX][0-9a-fA-F]+|\d+)',header_raw)[1],0) for name in ['MAX_GAME_PROGRESS','GPI_TITLE','GPI_LOGIN','GPI_MAIN_GAME']}
    report={'scope':'Static reverse of455 stage/tutorial/progress contracts and current source gaps;no runtime equivalence claim','references':references,'stages':classes,'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence.read_bytes())},'script_sha256':sha(Path(__file__).read_bytes()),'current_source':{'header':header.relative_to(WS).as_posix(),'header_sha256':sha(header_raw),'factory':factory.relative_to(WS).as_posix(),'factory_sha256':sha(factory_raw),'constants':constants,'tutorial_factory_present':b'new CGP_Tutorial' in factory_raw,'modulo_transition_present':b'( m_byGameProgressID + 1 ) % MAX_GAME_PROGRESS' in factory_raw},
        'facts':['Avatar20165 is stage field:constructor0;stage mainloop sets it after successfulstage Create;stage2 is Tutorial,not replay','Avatar20168 is separatelyread by420BE0;requestedstage2 maps to3 when nonzero;otherwise constructs CGP_Tutorial derivedfrom CGP_MainGame','MainApp mainloop7D1370 uses stage object next DWORD at20 via7D1470,not modulo stageID+1','Network562BE0 routes stage2 with Avatar20168==0 into tutorial message handling564520;unknown tutorial messages return1 without networksend','Login342 transform skips in Avatarstage2 independently of Avatar20168','Stage1 CGP_LogIn uses vtable LoadData53F7A0;country slot284 guards its old reconnect path;all11 selectors were already pinnedfalse in052','ZoneRequestMode436232 has confirmed writers42DCA0;2->3 after queuednetwork connect,3->4 onrequest;7/8/9/10/11 belongworld-transition paths','MASTER_SERVER ini reader5F0EB0 has no discoveredIDA xrefs,no E8/E9 candidates andno absolutepointer bytes in eitherpin;do notinsert it into startup onthis evidence'],
        'gaps':['Full455 Title/Login/Tutorial/MainGame factory,stage next-value and lifecycles;current source remains3stages/modulo','Entire Tutorial runtime and all client-only tutorial message handlers','Avatar stage field/20168 and network routing/transform wiring require joint source migration;do notmap old GPI_MAIN_GAME2 to455Tutorial2','Unknown computedindirectcall possibility for5F0EB0;SERVER_TYPE reset/writer semantics notfullycertified','Zone transition/state writer consumers and otherseed writer56BEA0','Actual full loginUI/real authentication/countrybootstrap/35handlers/world/gameplay/IME/shutdown/M6F/M9'],
        'input_exe_executed':False,'server_modified':False,'runtime_changed':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['facts'][6]='Transition state436232 has setter42DCA0:2->3 and7->8 when process0/socket0 info flag+48 is set;3->4 invokes53B430;remaining7/9/10/11 paths involve world transitions'
    (WS/'inventory/client455-progress-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'pinned_functions':len(rows),'stages':[(r['stage'],r['name']) for r in classes],'legacy_stages':constants['MAX_GAME_PROGRESS'],'tutorial_factory_present':report['current_source']['tutorial_factory_present'],'static_ini_references':0,'runtime_changed':False,'M9':'OPEN'}))
if __name__=='__main__':main()
