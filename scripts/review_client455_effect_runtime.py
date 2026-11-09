"""Create and record visual review of three actual aiming frames and cleanup."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    run=load('client455-effect-runtime-native');require(not run['natural_exit'] and len(run['frames'])==4,'Successful runtime')
    sheet=Image.new('RGB',(1280,1010),'#202020');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(run['frames']):
        check(row);check(row['preview']);x,y=(i%2)*640,(i//2)*505
        sheet.paste(Image.open(WS/row['preview']['file']),(x,y+25));draw.text((x+8,y+6),Path(row['file']).stem,fill='white')
    path=(WS/run['exe']['file']).parent/'effect-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-effect-runtime-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=run['frames'],reviewed=True,reviewed_frames=4,
                    observations=['Three controlled-camera frames show the actual nuclear aiming particle resources rendered through ordinary scheduler and restored effect passes',
                                  'The fourth frame is clear after cancellation and draining the actual children/master',
                                  'Dynamic-light insertion is measured, but its world-surface compositing is outside this isolated scene'],reference_executable_capture=False,full_world_pass_order=False,full_nuclear_owner=False,full_client=False)
        (WS/'inventory/client455-effect-runtime-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
