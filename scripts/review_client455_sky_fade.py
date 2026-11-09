"""Prepare five actual sky-fade frames; record only after viewing."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from compare_client_binaries import WS


def main():
    p=argparse.ArgumentParser();p.add_argument('--record-reviewed',action='store_true');a=p.parse_args();n=load('client455-sky-fade-native');require(n['status']=='PASS_SELECTED' and len(n['frames'])==5,'Five actual frames');sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(n['frames']):
        check(row);check(row['preview']);im=Image.open(WS/row['preview']['file']);require(im.size==(640,480),'Actual viewport');x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(im,(x,y+25))
    dest=(WS/n['exe']['file']).parent/'fade-contact.png';sheet.save(dest);print(dest)
    if a.record_reviewed:
        out=dict(reviewed=True,reviewed_frames=5,native_sha256=sha(WS/'inventory/client455-sky-fade-native.json'),script_sha256=sha(Path(__file__)),sheet=record(dest),frames=n['frames'],observations=['Actual Bellato sky visible in base and completed-fade frames','Middle and return frames visibly blend toward requested color','Full fade uniformly covers sky with requested RGB;finished sky bytes equal base','These are own engine GPU frames;no running reference455 frame equivalence is claimed'],reference_executable_capture=False,full_renderer=False);(WS/'inventory/client455-sky-fade-visual-review.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
