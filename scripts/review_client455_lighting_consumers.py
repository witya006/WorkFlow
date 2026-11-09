"""Prepare actual fixed/Grass lighting frames for explicit review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-lighting-consumers-native')
    require(native['status']=='PASS_SELECTED' and len(native['frames'])==5,'Five selected entity frames');sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);frame=Image.open(WS/row['preview']['file']);require(frame.size==(640,480),'Actual viewport');x,y=(i%2)*640,(i//2)*505
        draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(frame,(x,y+25))
    path=(WS/native['exe']['file']).parent/'lighting-consumers-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        out=dict(reviewed=True,reviewed_frames=5,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-lighting-consumers-native.json'),sheet=record(path),frames=native['frames'],
                 observations=['Stock grass geometry is visible through ordinary CEntity fixed and shader methods',
                               'Disabled/day map tint,lit fixed,Grass1 and LitGrass1 are exercised',
                               'Actual submitted Grass shaders match pinned bytecode;no running455 pixel equivalence or full lighting acceptance is claimed'],reference_executable_capture=False,full_lighting=False,full_client=False)
        (WS/'inventory/client455-lighting-consumers-visual-review.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
