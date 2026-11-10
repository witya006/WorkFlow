"""Verify actual455 Recall code and typed source integration;not fullAnimus acceptance."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from checkpoint_client455_rvp_effects import sha,require

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    files=[WS/'artifacts/client455-progress/recall162-reference'/name for name in ['recall.json','callers.json']]
    proofs=[dict(raw=record(path),**verify_regions(path)) for path in files]
    require(proofs[0]['full_functions']==31 and proofs[0]['full_instructions']==2791,'Full Recall window/row evidence')
    require(proofs[1]['full_functions']==8 and proofs[1]['full_instructions']==248,'Full setters/reference-item evidence')
    report=dict(status='STATIC_CONFIRMED_PARTIAL',**proofs[0],additional_references=proofs[1:],total_full_functions=sum(p['full_functions'] for p in proofs),total_full_instructions=sum(p['full_instructions'] for p in proofs),script=record(Path(__file__)),sources=[record(WS/name) for name in ['scripts/native/client455_recall_window.h','scripts/native/client455_recall_window.inc','scripts/client455_recall_port.py','scripts/prepare_client455_normal.py']],
        facts=['228x395 outer window,common header natural height,no invented animation sheet;8children andclip/content/scroll owners','Real13summon0/0..3,row204x56/icon38,13children and7x9common image numbers','Internal record name,index,itemID,spriteID,BYTElevel,DWORDHP/FP,floatEXP;source40byte layout','HP/FP fullunsigned32bit ratio,zero max0,upper clamp1 andsigned padded displayed text','EXP bar ratio is uncapped;only text upper caps99.99,background follows right-aligned glyphs','Delete compacts rows but retains content height;UpdateScrollbar preserves the target stale-height behavior','Enabled/linked clear cover;disabled red tint;None black;nonlinked clears borrowed reference item'],
        gaps=['Full455Animus item/board/table/network producers and real summon gameplay remainopen','Existing TakeOutLink source adapter andcomplete cursor/link ownership not fully accepted','Custom455save/restore settings andfullUI lifecycle remainopen','Target initial unit state/index are uninitialized;own sentinel is a bounded source choice,not target equivalence','Nonfinite/overflow/OOM andunadmitted coordinate/sprite failure domains remainopen','Five previously unindexed setter heads identified fromprologues;noIDAxref observed isnot proof of deadcode;decompiler haspositive-SP warnings,source decisions use fullASM not that pseudocode'],
        manual_IDA_metadata_only_changes=json.loads(files[1].read_text())['manual_function_heads'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-recall-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=report['total_full_functions'],instructions=report['total_full_instructions'],status=report['status'])))
if __name__=='__main__':main()
