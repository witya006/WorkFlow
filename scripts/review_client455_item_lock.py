"""Compose actual lock glyph frames for visual review."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--record-reviewed',action='store_true')
    args=parser.parse_args()
    run=load('client455-item-lock-native')
    require(not run['natural_exit'] and len(run['frames'])==6,'Successful lock probe')
    frames={Path(row['file']).name:row for row in run['frames']}
    sheet=Image.new('RGB',(1720,651),'#202020')
    draw=ImageDraw.Draw(sheet)
    names=['lock-off','lock-on','lock-partial-clip','lock-outside-clip','lock-empty','lock-removed']
    for index,name in enumerate(names):
        row=frames[name+'.bgra'];check(row);check(row['preview'])
        picture=Image.open(WS/row['preview']['file']).crop((20,70,450,166)).resize((860,192),Image.Resampling.NEAREST)
        x,y=index%2*860,index//2*217
        sheet.paste(picture,(x,y+25));draw.text((x+5,y+5),name,fill='white')
    path=(WS/run['exe']['file']).parent/'lock-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-item-lock-native.json'),script_sha256=sha(Path(__file__)),
                    sheet=record(path),frames=run['frames'],reviewed=True,reviewed_frames=6,
                    observations=['Real sprite52/action0/frame0 contains an8x12 lock glyph on8x16texture',
                                  'Actual EDF inventory icon andits copies receive the small lock in the upper right corner',
                                  'Normal lock drawing survives both partial image clipping andcomplete image clip rejection',
                                  'Empty andremoved slots stop drawing while their lock childstate remains preserved'],
                    reference_executable_capture=False,full_drag_handlers=False,full_client=False)
        (WS/'inventory/client455-item-lock-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
