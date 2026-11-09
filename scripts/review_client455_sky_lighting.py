"""Prepare actual ordinary lighting GPU readbacks for explicit review."""
import argparse
import json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    native=load('client455-sky-lighting-native')
    require(native['status']=='PASS_SELECTED' and len(native['frames'])==5,'Five real ordinary lighting frames')
    sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);frame=Image.open(WS/row['preview']['file']);require(frame.size==(640,480),'Actual viewport')
        x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(frame,(x,y+25))
    out=(WS/native['exe']['file']).parent/'lighting-contact.png';sheet.save(out);print(out)
    if args.record_reviewed:
        result=dict(reviewed=True,reviewed_frames=5,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-sky-lighting-native.json'),sheet=record(out),frames=native['frames'],
                    observations=['Actual neutralB sky2 is rendered through the ordinary lighting frame at midnight,noon and Mie-transition dusk',
                                  'Endpoint-fog and disabled-lighting frames use the same real sky resources',
                                  'World tint binding is checked on actual BSP submissions separately;these are sky readbacks',
                                  'Full lighting/fog/world/CRT parity with running455 remains open'],reference_executable_capture=False,full_lighting=False)
        (WS/'inventory/client455-sky-lighting-visual-review.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
