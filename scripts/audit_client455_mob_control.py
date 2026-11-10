"""Verify MobControl/shared movement bodies,skin routes and country name dispatch."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,require

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    root=WS/'artifacts/client455-progress/mob-control163-reference'
    proofs=[dict(raw=record(root/name),**verify_regions(root/name)) for name in ['mob-control.json','dependencies.json','support.json']]
    require([p['full_functions'] for p in proofs]==[21,8,5] and sum(p['full_instructions'] for p in proofs)==3119,'Complete MobControl/shared movement bodies')
    countries=WS/'inventory/client455-charinfo-country-discovery.json';dispatch=[]
    for pin in proofs[0]['references']:
        binary=(WS/pin['file']).read_bytes();require(sha(WS/pin['file'])==pin['sha256'],'Pinned target')
        require(read_va(binary,0xbdd2a8,4)==bytes.fromhex('db0fc93f'),'Exact movement half-pi float constant')
        require(struct.unpack('<3I',read_va(binary,0xbd70b0,12))==(0x3ce,0x3cf,0x39d),'Actual command language IDs')
        for country in json.loads(countries.read_text())['classes']:
            table=country['vtables'][0];expected=int(table['functions'][53],16);actual=struct.unpack('<I',read_va(binary,0x400000+int(table['vtable_rva'],16)+53*4,4))[0]
            require(actual==expected and expected==(0x832ed0 if country['name']=='CKorETCAction' else 0x82c5e0),'Actual country MobName virtual53')
            dispatch.append(dict(reference_sha256=pin['sha256'],country=country['name'],vtable_rva=table['vtable_rva'],slot=53,callee_rva=hex(actual-0x400000)))
    report=dict(status='STATIC_CONFIRMED_PARTIAL',**proofs[0],additional_references=proofs[1:],total_full_functions=34,total_full_instructions=3119,country_dispatch=dispatch,country_navigation=record(countries),script=record(Path(__file__)),sources=[record(WS/name) for name in ['scripts/native/client455_mob_control.h','scripts/native/client455_mob_control.inc','scripts/native/client455_gui_move.inc','scripts/client455_mob_control_port.py','scripts/prepare_client455_normal.py']],
        facts=['Real13summon root/board/EXP/resource/commands andmain4HP/FP skins;16children/threecommands','Signed HP/FP values clamp negatives0,zero max0,130x11 upper-clamped bars and%6d / %d text','Korea trims seven name bytes only when strlen>7;other10country methods preserve input;name centered in42pixels','EXP fraction clamps0..1,whole9pixelsteps andseparate90pixel remainder line;display capped99.99','Extra resource uses equipped records12/13,IMUL32wrap before signed division andseparate whole-step gauge','Hover/click/leave,actual0x530 windowmessage and200/150ms command animation','Shared movement records reset onregistration,zero startinactive,sine result roundedfloat,exact endpoint andacceleration/wave branches'],
        gaps=['Full455Animus item/board/network gameplay producers andactualsummon scenario remainopen','Extra resource producer4711F0 identified butnot yet integrated into ordinary inventory/equipment provider','Tooltip uses actual localized IDs through legacy SetTooltip adapter;full455 tooltip owner/style/scheduling policy not accepted','Legacy SetMobState declaration hasno observed caller orstandalone body;do not invent a behavior binding','Uninitialized initial values andfullUI lifecycle/resource reload/error domains remainopen','Nonfinite/coordinate overflow/OOM andextreme timing/velocity domains not accepted;own rejects some outside admitted domains','Country name branch verified againstall11vtables;fullfont/country UI equivalence not accepted'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-mob-control-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],functions=34,instructions=3119,country_slots=len(dispatch))))
if __name__=='__main__':main()
