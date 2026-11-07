"""Compose the actual ready-animation frames;compare unchanged dependency pixels."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();run=load('client455-ready-cooldown-native');require(not run['natural_exit'] and len(run['frames'])==6,'Successful ready run');sheet=Image.new('RGB',(1160,1065),'#202020');draw=ImageDraw.Draw(sheet);frames={Path(r['file']).name:r for r in run['frames']}
    for i,name in enumerate(['ready-idle.bgra','ready-frame0.bgra','ready-frame8.bgra','ready-frame39.bgra','ready-detached.bgra','ready-removed.bgra']):
        row=frames[name];check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((32,90,612,420));x,y=(i%2)*580,(i//2)*355;sheet.paste(image,(x,y+25));draw.text((x+5,y+5),name,fill='white')
    path=(WS/run['exe']['file']).parent/'ready-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-ready-cooldown-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=run['frames'],reviewed=True,reviewed_frames=6,
            observations=['Actual ordinary FrameMove attaches the configured128px ready child to the banked window','Original item andtwo clones are real EDF-backed owners;original lookup uses the actual global board pack staged by the lab','The sheet advances to frame8 andholds finalframe39 untilthe next FrameMove removes the child','Ready mode3 usesSRCALPHA/ONE with target postconditions;hiddenbank expiration createsno cue;Remove clearsclone/cache ownership','SFgroup source fanout uses actualglobalForce board pack;its two CPU iconfixtures are synthetic,notfull SFUI acceptance'],reference_executable_capture=False,full_gameplay_handlers=False,full_client=False)
        (WS/'inventory/client455-ready-cooldown-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
