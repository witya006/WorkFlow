"""Verify complete options455 bodies and country policy against both pinned PEs."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,require

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def main():
    root=WS/'artifacts/client455-progress/option164-reference'
    proofs=[dict(raw=record(root/name),**verify_regions(root/name)) for name in ['option.json','dependencies.json']]
    require([p['full_functions'] for p in proofs]==[25,28] and sum(p['full_instructions'] for p in proofs)==5879,'Complete options and dependencies')
    country_files=[('inventory/client455-option-web-discovery.json',8,0x833590,0x82bb70),('inventory/client455-charinfo-country-discovery.json',96,0x832a50,0x82c930)]
    dispatch=[]
    for pin in proofs[0]['references']:
        binary=(WS/pin['file']).read_bytes()
        require(sha(WS/pin['file'])==pin['sha256'],'Pinned target')
        for filename,slot,korea,other in country_files:
            countries=json.loads((WS/filename).read_text())['classes'];require(len(countries)==11,'Eleven country tables')
            for country in countries:
                table=country['vtables'][0];expected=int(table['functions'][slot],16)
                actual=struct.unpack('<I',read_va(binary,0x400000+int(table['vtable_rva'],16)+slot*4,4))[0]
                require(actual==expected and actual==(korea if country['name'].startswith('CKor') else other),'Country options policy dispatch')
                dispatch.append(dict(reference_sha256=pin['sha256'],country=country['name'],vtable_rva=table['vtable_rva'],slot=slot,callee_rva=hex(actual-0x400000)))
    sources=['scripts/native/client455_option_window.h','scripts/native/client455_option_window.inc','scripts/client455_option_port.py','scripts/prepare_client455_normal.py','scripts/native/client455_board_hover.cpp','scripts/native/client455_player_status_probe.cpp']
    report=dict(status='STATIC_CONFIRMED_PARTIAL',**proofs[0],additional_references=proofs[1:],total_full_functions=53,total_full_instructions=5879,country_dispatch=dispatch,country_navigation=[record(WS/f[0]) for f in country_files],country_factory_body_scope=['Korea','Taiwan','China'],all_eleven_factory_paths_proved=False,script=record(Path(__file__)),helpers=[record(WS/'scripts/client455_reference_regions.py')],sources=[record(WS/name) for name in sources],
        facts=['Actual system.spr window,common header/buttons,natural geometry and language IDs','Three sound controls160units/arrow8 and six graphics controls10,3,3,6,2,3;Gamma setter subtracts0.8 butgetter returns raw units','Korea has81children/eight switches/rating action;other policy76children/six switches','Actual option GUI events route values through ordinary HWND messages;camera/EAX/special radio rules and target-filter XOR quirk retained','Legacy internal detail-texture and keyboard-exit producer/consumer macros moved to private WM_APP IDs to avoid collisions with actual455Party/BGM messages;these private IDs are not455contracts','No-pending hover cancellation short-circuits before requiring unknown player status;pending aiming still requires status and message providers'],
        gaps=['Full settings load/save/application backends including EAX/special/new graphics and targeting are not accepted','Ordinary rating-dialog callback,startup-board dismissal and logout-restriction producer remain unconnected;native action callbacks are controlled','Guild/detail-texture remain explicit unrepresented legacy adapters;effects slider backend semantics remain partial','Native other-country policy reuses Korean assets/language and is not Taiwan localization acceptance','Country policy slots checked for all eleven tables;factory constructor/selector paths captured for Korea/Taiwan/China only','Four target bounded pointer-getters are not claimed equivalent to own fixture accessors','Player status first producer/full sideeffects and nuclear/world lifecycle remain separate open contracts;unknown status is not initialized to invented zero','Complete UI/world/gameplay and extreme FP/overflow/OOM/lifecycle domains remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-option-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],functions=53,instructions=5879,country_slots=len(dispatch))))

if __name__=='__main__':main()
