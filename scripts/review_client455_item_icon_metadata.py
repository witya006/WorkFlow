"""Compose actual inventory metadata frames and record explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-item-icon-metadata-native');require(native['natural_exit']==0 and len(native['frames'])==3,'Successful inventory run required');sheet=Image.new('RGB',(1120,410),'#202020');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((0,0,560,180));x,y=i%2*560,i//2*205;sheet.paste(image,(x,y+25));draw.text((x+5,y+5),Path(row['file']).name,fill='white')
    path=(WS/native['exe']['file']).parent/'metadata-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-item-icon-metadata-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=native['frames'],reviewed=True,reviewed_frames=3,
            observations=['Actual EDF-backed payloads populate16 realCGUIInventoryBoard icons through production source metadata;image fields are not manually supplied',
                'Updating copied in-memory quantity and grade changes one icon;normal removal clears all visible icons'],reference_executable_capture=False,full_inventory=False,full_client=False)
        (WS/'inventory/client455-item-icon-metadata-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
