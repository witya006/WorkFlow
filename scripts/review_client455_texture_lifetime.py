"""Prepare and record a visual review of the current texture-lifetime scenario."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-texture-lifetime-native');require(not native['natural_exit'] and len(native['frames'])==5,'Complete real scenario frames')
    sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    old=load('client455-nuclear-registry-native');equal=[]
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);frame=Image.open(WS/row['preview']['file']);require(frame.size==(640,480),'Actual viewport');x,y=(i%2)*640,(i//2)*505
        draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(frame,(x,y+25))
        if any(x['sha256']==row['sha256'] for x in old['frames']):equal.append(Path(row['file']).name)
    out=(WS/native['exe']['file']).parent/'texture-lifetime-contact.png';sheet.save(out);print(out)
    if args.record_reviewed:
        report=dict(reviewed=True,reviewed_frames=5,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-texture-lifetime-native.json'),sheet=record(out),frames=native['frames'],byte_equal_historical_frames=equal,observations=['Actual flight/impact frames contain the nuclear effect geometry/particles','Countdown UI is visible with actual locale text/numeric marker','Both post-drain/post-destructor frames are empty','Nonempty particle frames are not asserted byte-identical across seeded/timed runs'],reference_executable_capture=False,full_world_effects=False,full_client=False)
        (WS/'inventory/client455-texture-lifetime-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
