"""Compose actual GPU frames for human/model visual review,without changing them."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    report=load('client455-item-icon-native');require(report['natural_exit']==0,'Failed native run');sheet=Image.new('RGB',(1200,750),'#202020');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(report['frames']):
        check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((0,0,520,260));image.thumbnail((390,220));x,y=(i%3)*400,(i//3)*250;sheet.paste(image,(x,y+25));draw.text((x+5,y+5),row['file'].split('/')[-1],fill='white')
    path=(WS/report['exe']['file']).parent/'icons-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        review=dict(scope='Visual review of actual source GPU output;not a capture of the reference executable',native_sha256=sha(WS/'inventory/client455-item-icon-native.json'),script_sha256=sha(Path(__file__)),
            sheet=record(path),frames=report['frames'],reviewed_frames=9,reviewed=True,
            observations=['Actual455weapon cells and colored borders are visible at32/64 displayedsizes;default atlas cell is labelledDefault',
                'Mainimage remains visible when borderhidden;unusableimage is dimmed andalpha preserved;validclip crops image andborder',
                'WORD65535 quantity is visible;hiddenquantity equalsunquantifiedimage;hidden/noimage cases are empty'],
            automatic_item_atlas_factory=False,full_GUIItem=False,full_client=False)
        (WS/'inventory/client455-item-icon-visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
if __name__=='__main__':main()
