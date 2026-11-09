"""Prepare and record visual review of automatically lit real map objects."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-entity-owner-native');require(native['status']=='PASS_SELECTED' and len(native['frames'])==4,'Completed4 real owner frames')
    sheet=Image.new('RGB',(1280,1010),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);frame=Image.open(WS/row['preview']['file']);require(frame.size==(640,480),'Actual viewport');x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(frame,(x,y+25))
    path=(WS/native['exe']['file']).parent/'entity-owner-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(reviewed=True,reviewed_frames=4,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-entity-owner-native.json'),sheet=record(path),frames=native['frames'],observations=['Real loaded NeutralB gate/tree objects are visible','Shader-enabled tree uses pinned LitGrass;disabled route uses fixed lighting','Lighting bit originates from original EBP entries;fullworld/pixel equivalence against running455 is not claimed'],reference_executable_capture=False,full_gameplay=False)
        (WS/'inventory/client455-entity-owner-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
