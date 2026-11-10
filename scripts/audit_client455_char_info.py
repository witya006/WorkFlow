"""Pin CharInfo455 bodies, country layout policies and source integration evidence."""
import json, struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions
from checkpoint_client455_rvp_effects import sha, require

def record(path):
    return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def reference():
    raw=WS/'artifacts/client455-progress/charinfo161-reference/charinfo.json'
    proof=verify_regions(raw)
    additional=[verify_regions(WS/'artifacts/client455-progress/charinfo161-reference'/name) for name in ['values.json','uv.json']]
    tables=[0xaf94ec,0xaf82b4,0xaf6c54,0xaf918c,0xaf70e4,0xaf76d4,0xaf73dc,0xaf79cc,0xaf7cc4,0xaf7fbc,0xaf88a4]
    layouts=[]
    for pin in proof['references']:
        binary=(WS/pin['file']).read_bytes();rows=[]
        for nation,table in enumerate(tables):
            narrow=struct.unpack('<I',read_va(binary,table+244,4))[0]
            left=struct.unpack('<I',read_va(binary,table+332,4))[0]
            require(narrow==(0x82e0c0 if nation==5 else 0x82c670),'Actual country narrow-layout slot')
            require(left=={6:0x82d9d0,9:0x82f4d0,10:0x830940}.get(nation,0x82c850),'Actual country alignment slot')
            # Positive providers explicitly load EAX=1; negative providers XOR EAX,EAX.
            for address,value in [(narrow,nation==5),(left,nation in (6,9,10))]:
                body=read_va(binary,address,0x15 if not value else 0x18)
                require((b'\xb8\x01\x00\x00\x00' if value else b'\x33\xc0') in body,'Policy return instructions')
            rows.append(dict(nation=nation,vtable_rva=hex(table-0x400000),narrow_rva=hex(narrow-0x400000),left_rva=hex(left-0x400000),narrow=nation==5,left=nation in (6,9,10)))
        require(read_va(binary,0xaec350,12)==struct.pack('<III',0x4c5,0x4c6,0x4c7),'Actual race mastery NDLanguage indices')
        layouts.append(rows)
    require(layouts[0]==layouts[1],'Both pins have identical policies')
    result=dict(status='STATIC_CONFIRMED_PARTIAL',raw=record(raw),**proof,additional_references=[dict(raw=record(WS/'artifacts/client455-progress/charinfo161-reference'/name),**item) for name,item in zip(['values.json','uv.json'],additional)],total_full_functions=proof['full_functions']+sum(x['full_functions'] for x in additional),total_full_instructions=proof['full_instructions']+sum(x['full_instructions'] for x in additional),country_layouts=layouts[0],country_mapping_source=record(WS/'inventory/client455-language-reference.json'),input_exe_executed=False,server_modified=False,M9='OPEN')
    result['script']=record(__import__('pathlib').Path(__file__))
    result['sources']=[record(WS/name) for name in ['scripts/native/client455_char_info.h','scripts/native/client455_char_info.inc','scripts/client455_char_info_port.py','scripts/prepare_client455_normal.py']]
    result['facts']=['Outer228x395 window,three pages5/2/4sections,23actual borrowed value owners','Actual47CharInfo/common skins,natural full-height header and1x4animated highlight,close/help/resize/wheel/page input','Three race layouts including omitted force row forAccretia;11country padding/alignment policies','Different battle/make GM conditions,WORD current/maximum and clamped cropped bars/image percentages','Signed resistance range-aware setter plus legacy text-only adapter;no invented limits','Zero-max FP/SP and six-decimal experience formatting']
    result['gaps']=['Action/equipment page content providers,interactions and tab hover/help-text producer not fully ported','Legacy mastery callers lack455maximum;legacy resistance callers lack signed bounds','Full metric/stat producers and semantic names17/18 remain unaccepted;real labels are average defense range/rate,not proof of accuracy/dodge','FullUI lifecycle/repeated cross-race refresh/nonfinite,overflow,zero-range andallocation failure domains not accepted','Remaining oldMainGame windows,world/control/gameplay andallM9requirements open']
    (WS/'inventory/client455-char-info-reference.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(functions=result['total_full_functions'],instructions=result['total_full_instructions'],country_layouts=len(layouts[0]))))
    return result

if __name__=='__main__':
    reference()
    import sys
    if '--labels' in sys.argv:
        from audit_client455_language import records,decode
        from pathlib import Path
        client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
        path=client/'DataTable/en-gb/NDLanguage.edf'
        if not path.is_file():path=client/'DataTable/en-us/NDLanguage.edf'
        rows,_=records(decode(path.read_bytes()))
        ids=[0x443,0x444,0x445,0x446,0x447,0x448,0x109c,0x44a,0x44b,0x44c,0x44d,0x44e,0x7e9,0x44f,0x450,0x451,0x452,0x81c,0x81d,0x81e,0x453,0x454,0x455]
        print(json.dumps([dict(slot=i,language_id=hex(n),text=rows[n][1].rstrip(b'\0').decode('cp1252')) for i,n in enumerate(ids)],ensure_ascii=True))
