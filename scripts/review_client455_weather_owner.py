"""Prepare five real ordinary weather/world frames for explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    native=load('client455-weather-owner-native');require(native['status']=='PASS_SELECTED' and len(native['frames'])==5,'Five actual weather frames')
    sheet=Image.new('RGB',(1280,1515),(28,28,28));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);frame=Image.open(WS/row['preview']['file']);require(frame.size==(640,480),'Actual viewport')
        x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(frame,(x,y+25))
    out=(WS/native['exe']['file']).parent/'weather-owner-contact.png';sheet.save(out);print(out)
    if args.record_reviewed:
        report=dict(reviewed=True,reviewed_frames=5,script_sha256=sha(Path(__file__)),native_sha256=sha(WS/'inventory/client455-weather-owner-native.json'),sheet=record(out),frames=native['frames'],
                    observations=['Actual neutralB BSP and sky are visible through ordinary level draw calls',
                                  'Five frames exercise midnight/dawn/noon/dusk/night and five per-owner exposure values',
                                  'The selected camera looks upward;thin geometry strips are visible and remain an unresolved world/camera/material fidelity issue',
                                  'This is own-client visual review;no running reference455 pixel equivalence is claimed'],reference_executable_capture=False,full_lighting=False,full_client=False)
        (WS/'inventory/client455-weather-owner-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
