"""Prepare actual sky2 day/night readbacks for explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from compare_client_binaries import WS


def main():
    p=argparse.ArgumentParser();p.add_argument('--record-reviewed',action='store_true');a=p.parse_args();n=load('client455-sky-material-native');require(n['status']=='PASS_SELECTED' and len(n['frames'])==5,'Five actual sky2 frames');sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(n['frames']):
        check(row);check(row['preview']);im=Image.open(WS/row['preview']['file']);require(im.size==(640,480),'Actual viewport');x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(im,(x,y+25))
    dest=(WS/n['exe']['file']).parent/'sky-material-contact.png';sheet.save(dest);print(dest)
    if a.record_reviewed:
        out=dict(reviewed=True,reviewed_frames=5,native_sha256=sha(WS/'inventory/client455-sky-material-native.json'),script_sha256=sha(Path(__file__)),sheet=record(dest),frames=n['frames'],observations=['Real neutralB sky2 geometry/textures are visible and day/night material states alter output','Four fixed-clock times produce different actual GPU frames;released sky leaves exact clear control','Atmosphere/sun prepass remains missing;this is not complete reference455 visual equivalence'],reference_executable_capture=False,full_atmosphere=False);(WS/'inventory/client455-sky-material-visual-review.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
