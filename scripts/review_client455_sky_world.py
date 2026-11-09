"""Prepare actual sky frames and record review only after they have been viewed."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    p=argparse.ArgumentParser();p.add_argument('--record-reviewed',action='store_true');args=p.parse_args();native=load('client455-sky-world-native');require(native['status']=='PASS_SELECTED' and len(native['frames'])==5,'Actual five sky frames');sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);im=Image.open(WS/row['preview']['file']);require(im.size==(640,480),'Sky viewport');x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(im,(x,y+25))
    dest=(WS/native['exe']['file']).parent/'sky-contact.png';sheet.save(dest);print(dest)
    if args.record_reviewed:
        out=dict(reviewed=True,reviewed_frames=5,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-sky-world-native.json'),sheet=record(dest),frames=native['frames'],observations=['Actual loaded Bellato sky is visible against the exact unloaded clear control','Translation/world-near3000/orthographic-restore controls are byte-identical to the base sky frame','No pixel comparison against running455 or fullsky/fade/renderer parity is claimed'],reference_executable_capture=False,full_renderer=False);(WS/'inventory/client455-sky-world-visual-review.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
