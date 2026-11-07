"""Build a contact sheet and record only an explicitly completed visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-item-atlas-native');require(native['natural_exit']==0 and len(native['frames'])==4,'Successful atlas run required')
    sheet=Image.new('RGB',(1100,650),'#202020');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((0,0,550,300));x,y=i%2*550,i//2*325;sheet.paste(image,(x,y+25));draw.text((x+5,y+5),Path(row['file']).name,fill='white')
    path=(WS/native['exe']['file']).parent/'atlas-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-item-atlas-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=native['frames'],reviewed=True,reviewed_frames=4,
            observations=['Automatic selection draws16 item/skill/force/class/Animus/gesture/macro/unit examples at32/64 sizes without explicitSPRITE_INFO',
                'Default fallback cell is visible after unsupported classification;unitparts uses a separate real atlas;empty itemID clears mainimage'],reference_executable_capture=False,full_GUIItem=False,full_client=False)
        (WS/'inventory/client455-item-atlas-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
