"""Compose real inventory copy frames and record an explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-icon-links-native');require(native['natural_exit']==0 and len(native['frames'])==3,'Successful icon links run required')
    sheet=Image.new('RGB',(520,420),'#202020');draw=ImageDraw.Draw(sheet)
    frames={Path(row['file']).name:row for row in native['frames']}
    for i,name in enumerate(['links-before.bgra','links-propagated.bgra','links-detached.bgra']):
        row=frames[name];check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((0,15,520,130));sheet.paste(image,(0,i*140+25));draw.text((5,i*140+5),name,fill='white')
    path=(WS/native['exe']['file']).parent/'links-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-icon-links-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=native['frames'],reviewed=True,reviewed_frames=3,
            observations=['A real inventory icon and two explicitly registered CGUIItem copies draw the same real item image',
                'Quantity255 and unusable tint propagate to both registered copies',
                'After unregistering the middle copy it retains gray255 while the original and other copy become white2'],
            reference_executable_capture=False,ordinary_Linker_Macro_registration=False,full_client=False)
        (WS/'inventory/client455-icon-links-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
