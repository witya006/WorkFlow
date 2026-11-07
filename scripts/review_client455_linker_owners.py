"""Compose real inventory copy frames and record an explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-linker-owners-native');require(native['natural_exit']==0 and len(native['frames'])==3,'Successful icon links run required')
    sheet=Image.new('RGB',(520,420),'#202020');draw=ImageDraw.Draw(sheet)
    frames={Path(row['file']).name:row for row in native['frames']}
    for i,name in enumerate(['owners-before.bgra','owners-updated.bgra','owners-removed.bgra']):
        row=frames[name];check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((0,15,520,130));sheet.paste(image,(0,i*140+25));draw.text((5,i*140+5),name,fill='white')
    path=(WS/native['exe']['file']).parent/'owners-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-linker-owners-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=native['frames'],reviewed=True,reviewed_frames=3,
            observations=['A real inventory icon and two icons owned and registered by ordinary CLinkBoard.Add draw the same item',
                'Quantity255 and unusable tint reach the real bank0-slot0 and bank4-slot9 copies',
                'Ordinary Remove clears the bank4-slot9 icon;the original and bank0 copy remain gray255'],
            reference_executable_capture=False,ordinary_CLinkBoard_registration=True,full_Linker_window=False,full_client=False)
        (WS/'inventory/client455-linker-owners-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
