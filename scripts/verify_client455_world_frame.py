"""Recheck real frame traces,matched controls and selected light/clock oracles."""
import json
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS
from probe_client455_world_frame import verify

def main():
    native=load('client455-world-frame-native');require(native['status']=='PASS' and not native['natural_exit'] and native['native']['status']=='PASS' and native['native']['warnings']==6,'Own world scenario')
    require(native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_world_frame.py') and native['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py'),'Exact world scenario producers')
    for row in [native['exe'],native['map'],native['source'],native['included_source'],native['driver_script'],native['oracle'],native['console'],native['output'],native['world_manifest']]+native['trace']+native['inputs']:check(row)
    run=(WS/native['exe']['file']).parent;verdict=verify(run);require(verdict==native['verdict'],'Reproduced world/queue/clock oracle')
    diff=verdict['changed_bytes_from_matched_clear'];require(diff['frame-base.bgra']==diff['frame-cleared.bgra']==0,'Base and cleared controls byte-identical')
    console=(WS/native['console']['file']).read_text(errors='replace');require(console.count('light-state bind=00000000 validate=00000000 passes=1 cull=3 zfunc=4')==3,'All three actual light passes validate')
    diagnostic=run/'light-diagnostic.json';geometry=json.loads(diagnostic.read_text());require(geometry['leaves']>0 and geometry['faces']>=geometry['upward']>0 and geometry['texture_width']==geometry['texture_height']==512,'Actual candidate geometry and texture')
    texture=run/'lamp-texture.dds';image=Image.open(texture).convert('RGBA');require(image.getextrema()[3]==(255,255),'Observed opaque actual light texture');preview=run/'lamp-texture.png';image.save(preview)
    for row in native['frames']:check(row);check(row['preview'])
    result=dict(status='PASS_SELECTED',script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-world-frame-native.json'),reference_sha256=sha(WS/'inventory/client455-world-frame-reference.json'),verdict=verdict,diagnostic=record(diagnostic),geometry=geometry,texture=record(texture),texture_preview=record(preview),matched_clear_control_exact=True,old_render_equivalence=False,full_world_equivalence=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-world-frame-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS_SELECTED:76queue operations/16live clock±1/visible real-world magic+regular+FX light/exact cleared control;full renderer equivalence OPEN')

if __name__=='__main__':main()
