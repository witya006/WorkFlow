"""Current ordinary text-shader fallback checkpoint;M6/M9 remain open."""
import json,re,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_item_payloads import record
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import require,check,load,sha
from checkpoint_client455_special_shaders import call_evidence
from client455_normal_link_evidence import validate_normal_link
from probe_client455_shader_text import verify
from probe_client455_material_shaders import verify as verify_material

def fallback_call(link):
    mapping=(WS/link['map']['file']).read_text();raw=(WS/link['executable']['file']).read_bytes();base=pe(raw)['image_base']
    def symbol(name):
        m=re.search(re.escape(name)+r'\s+([0-9a-fA-F]{8})',mapping);require(m is not None,'Retained own fallback symbol');return int(m[1],16)
    binary=symbol('?RF455_LoadSpecialShaderBinary@@YAHXZ');text=symbol('?RF455_LoadSpecialShaderText@@YAHXZ');body=read_va(raw,binary,256)
    sites=[binary+i for i in range(len(body)-4) if body[i] in [0xe8,0xe9] and binary+i+5+struct.unpack_from('<i',body,i+1)[0]==text]
    require(len(sites)==1,'Actual ordinary binary loader transfers to text loader');return dict(from_rva=hex(binary-base),site_rva=hex(sites[0]-base),target_rva=hex(text-base))

def main():
    ref=load('client455-shader-text-reference');require(ref['script']['sha256']==sha(WS/'scripts/audit_client455_shader_text.py') and ref['full_assembly']==7 and ref['instructions']==872 and ref['verified_ranges']==7 and ref['CFG_complete'],'Current complete reference')
    for key in ['script','contract_verifier','raw','session','engine','snapshot']:check(ref[key])
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current full own client link');lh=sha(WS/'inventory/client455-normal-link.json');require(ref['normal_link_sha256']==lh,'Current source/runtime reference');transition=fallback_call(link);calls=call_evidence(link)
    native=load('client455-shader-text-native');require(native['status']=='PASS_SELECTED' and native['normal_link_sha256']==lh and not native['natural_exit'] and native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_shader_text.py') and native['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py'),'Exact successful fallback producer')
    for row in [native[k] for k in ['source','world_source','exe','map','console','output','driver_script']]+native['inputs']+native['outputs']:check(row)
    verdict=verify((WS/native['exe']['file']).parent,native);require(verdict==native['verdict'] and native['native']['warnings']==2,'Reproduced exact text rows/programs/selected expected failure diagnostics')
    material=load('client455-material-shaders-native');require(material['status']=='PASS_SELECTED' and material['normal_link_sha256']==lh and not material['natural_exit'] and material['native']['warnings']==0 and material['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py'),'Fresh ordinary material regression')
    for row in [material[k] for k in ['source','included_source','exe','map','console','output','driver_script','trace']]+material['inputs']+material['fixtures']:check(row)
    mv=verify_material((WS/material['exe']['file']).parent,material);require(mv==material['verdict'],'51actual BSP cases/7textures/particle light/splat retained')
    before=WS/'artifacts/client455-progress/before136';oldfile=before/'inventory/client455-material-shaders-native.json';oldreview=before/'inventory/client455-material-shaders-visual-review.json';old=json.loads(oldfile.read_text());review=json.loads(oldreview.read_text())
    require(review['reviewed'] and review['reviewed_frames']==4 and review['native_sha256']==sha(oldfile),'Previously inspected135 controlled frames');check(review['sheet']);byname={Path(x['file']).name:x for x in old['frames']};require(len(material['frames'])==len(byname)==4,'Four fresh actual GPU frames')
    for row in material['frames']:
        previous=byname[Path(row['file']).name]
        for x in [row,row['preview'],previous,previous['preview']]:check(x)
        require(row['sha256']==previous['sha256'] and row['preview']['sha256']==previous['preview']['sha256'],'Raw pixels/PNG unchanged versus reviewed135')
    review.update(native_sha256=sha(WS/'inventory/client455-material-shaders-native.json'),frames=material['frames'],reused_from_native=record(oldfile),reused_from_review=record(oldreview),reused_pixels_byte_equal=True,new_visual_inspection=False,comparison_script=record(Path(__file__)))
    (WS/'inventory/client455-material-shaders-visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
    engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'],'Current engine owner')
    require(validated_entry()['normal_link_sha256']==lh,'Exact decoded own entry');early,ui,audit,contract=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-audit'),load('client455-startup-contracts-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and not audit['unresolved_provider_modules'] and contract['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Own sound/window/device/existingCreate1/contracts/providers');check(early['events']);check(ui['events'])
    names=['shader-text-reference','shader-text-native','material-shaders-native','material-shaders-visual-review','normal-link','startup-engine-build','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),reference=record(WS/'inventory/client455-shader-text-reference.json'),engine=ref['engine'],normal_executable=link['executable'],normal_link_sha256=lh,text_fallback=verdict,ordinary_restore_calls=calls,own_fallback_call=transition,ordinary_material_regression=mv,fresh_GPU_frames=4,reused_review_pixels_byte_equal135=True,new_visual_inspection=False,shared_headers_changed=False,full_client_recompile_needed=False,previous135_gate=record(before/'inventory/client455-material-shaders-checkpoint.json'),snapshot=ref['snapshot'],fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in names},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,full_special_renderer=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-shader-text-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:text fallback/4actual programs/3objects/11params/failure recovery/currentCreate1/4freshframes byteequal135;full455/M9OPEN')
if __name__=='__main__':main()
