"""Selected ordinary binary shader owner checkpoint;M6/M9 remain open."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_item_payloads import record
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import require,check,sha,load
from client455_normal_link_evidence import validate_normal_link
from audit_client455_special_shaders import contracts
from probe_client455_special_shaders import verify
from probe_client455_world_frame import verify as world_verify


def call_evidence(link):
    raw=(WS/link['executable']['file']).read_bytes();mapping=(WS/link['map']['file']).read_text();base=pe(raw)['image_base']
    import re
    def symbol(name):
        m=re.search(re.escape(name)+r'\s+([0-9a-fA-F]{8})',mapping);require(m is not None,'Retained own symbol '+name);return int(m[1],16)
    restore=symbol('?D3D_R3RestoreDevice@@YAJXZ');load=symbol('?RF455_LoadSpecialShaderBinary@@YAHXZ');release=symbol('?RF455_ReleaseSpecialShaders@@YAXXZ');data=read_va(raw,restore,256);calls=[]
    for i in range(len(data)-4):
        if data[i]==0xe8:
            target=restore+i+5+struct.unpack_from('<i',data,i+1)[0]
            if target in [load,release]:calls.append(dict(call_rva=hex(restore+i-base),target_rva=hex(target-base),operation='load' if target==load else 'release'))
    require([x['operation'] for x in calls]==['release','load'],'Exact ordinary restore CALLs release then load')
    return calls


def main():
    reference=load('client455-special-shaders-reference');require(reference['script']['sha256']==sha(WS/'scripts/audit_client455_special_shaders.py') and reference['full_assembly']==15 and reference['instructions']==1592 and reference['verified_ranges']==20 and reference['CFG_complete'],'Current full selected reference')
    for key in ['raw','session','inputs','engine','snapshot']:check(reference[key])
    raw=json.loads((WS/reference['raw']['file']).read_text());require(contracts(raw)[1]==1592,'Reproduced full assembly/CFG coverage')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current complete own client link');lh=sha(WS/'inventory/client455-normal-link.json');require(reference['normal_link_sha256']==lh,'Reference describes exact current PE');calls=call_evidence(link)
    engine=load('client455-startup-engine-build');require(engine['library_sha256']==reference['engine']['sha256'],'Actual shader-owner library');native=load('client455-special-shaders-native')
    require(native['status']=='PASS_SELECTED' and not native['natural_exit'] and native['normal_link_sha256']==lh and native['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py') and native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_special_shaders.py'),'Current successful ordinary owner probe')
    for row in [native[k] for k in ['exe','map','source','world_source','driver_script','trace','console','output']]+native['inputs']+native['outputs']:check(row)
    verdict=verify((WS/native['exe']['file']).parent,native);require(verdict==native['verdict'],'Reproduced shader program/owner/overlap verification')
    tests=load('client455-special-shaders-parser-tests');require(tests['status']=='PASS' and tests['tests']==4,'Small bounded parser checks');check(tests['script']);check(tests['parser'])
    world=load('client455-world-frame-native');require(world['status']=='PASS' and world['normal_link_sha256']==lh and not world['natural_exit'],'Fresh real world-frame run');wv=world_verify((WS/world['exe']['file']).parent);require(wv==world['verdict'],'Actual world light/clock checks')
    verification=load('client455-world-frame-verification');require(verification['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and verification['verdict']==wv,'Fresh independent world verification')
    before=WS/'artifacts/client455-progress/before134';oldfile=before/'inventory/client455-world-frame-native.json';reviewfile=before/'inventory/client455-world-frame-visual-review.json';old=json.loads(oldfile.read_text());review=json.loads(reviewfile.read_text())
    require(review['reviewed'] and review['reviewed_frames']==5 and review['native_sha256']==sha(oldfile),'Verified133 visual review');check(review['sheet']);oldframes={Path(x['file']).name:x for x in old['frames']};require(len(world['frames'])==len(oldframes)==5,'Five fresh actual GPU frames')
    for row in world['frames']:
        previous=oldframes[Path(row['file']).name]
        for value in [row,row['preview'],previous,previous['preview']]:check(value)
        require(row['sha256']==previous['sha256'] and row['preview']['sha256']==previous['preview']['sha256'],'Byte-exact current pixels/PNG versus reviewed133')
    review.update(native_sha256=sha(WS/'inventory/client455-world-frame-native.json'),frames=world['frames'],script_sha256=sha(Path(__file__)),reused_from_review=record(reviewfile),reused_from_native=record(oldfile),reused_pixels_byte_equal=True,new_visual_inspection=False)
    (WS/'inventory/client455-world-frame-visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
    require(validated_entry()['normal_link_sha256']==lh,'Current decoded own entry');early,ui,audit,contract=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-audit'),load('client455-startup-contracts-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and not audit['unresolved_provider_modules'] and contract['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current ordinary sound/window/device/existingCreate1/contracts/providers')
    check(early['events']);check(ui['events'])
    previous=before/'inventory/client455-material-layout-checkpoint.json';prior=json.loads(previous.read_text());gaps=[x.replace('its full special shader owner/draw pipeline is not yet ported','its binary shader owner is restored134;ordinary special draw/constants remain open') for x in prior['gaps']]+reference['gaps']
    names=['special-shaders-reference','special-shaders-inputs','special-shaders-native','special-shaders-parser-tests','startup-engine-build','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','world-frame-native','world-frame-verification','world-frame-visual-review']
    out=dict(status='PARTIAL',scope=reference['scope'],script=record(Path(__file__)),reference=record(WS/'inventory/client455-special-shaders-reference.json'),engine=reference['engine'],normal_executable=link['executable'],normal_link_sha256=lh,ordinary_restore_calls=calls,shader_owner=verdict,world_regression=wv,fresh_GPU_frames=5,reused_review_pixels_byte_equal133=True,new_visual_inspection=False,shared_headers_changed=False,full_client_recompile_needed=False,previous133_gate=record(previous),snapshot=reference['snapshot'],fresh_evidence={n:record(WS/f'inventory/client455-{n}.json') for n in names},gaps=gaps,unchanged_bulk_suites_rerun=False,full_special_draw=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-special-shaders-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:4real shaders/3ordinary restore cycles/overlap semantics/fullPE Create1/5fresh frames byteequal133;special draw/M6/M9 OPEN')


if __name__=='__main__':main()
