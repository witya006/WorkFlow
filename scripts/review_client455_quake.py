"""Prepare five actual effect frames for explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-quake-effects-native');require(native['status']=='PASS' and len(native['frames'])==5,'Current native frames')
    sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);frame=Image.open(WS/row['preview']['file']);require(frame.size==(640,480),'Viewport');x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(frame,(x,y+25))
    out=(WS/native['exe']['file']).parent/'quake-contact.png';sheet.save(out);print(out)
    if args.record_reviewed:
        report=dict(reviewed=True,reviewed_frames=5,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-quake-effects-native.json'),sheet=record(out),frames=native['frames'],observations=['Flight/impact and late explosion effect frames contain visible geometry/particles','Actual countdown message text is visible over remaining effects','Post-drain and post-destructor captures are empty','These frames do not establish full world compositing or comparison with running455'],reference_executable_capture=False,full_world_effects=False,full_client=False)
        (WS/'inventory/client455-quake-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
