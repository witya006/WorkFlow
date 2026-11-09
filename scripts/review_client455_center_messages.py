"""Review real localized center-message frames and their final cleanup."""
import argparse
import json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    run=load('client455-center-messages-native');require(run['natural_exit']==0 and len(run['frames'])==4,'Successful current runtime')
    names=['center-c1a','center-queued','center-fading','center-cleared'];frames={Path(row['file']).stem:row for row in run['frames']}
    sheet=Image.new('RGB',(1280,1010),'#202020');draw=ImageDraw.Draw(sheet)
    for i,name in enumerate(names):
        row=frames[name];check(row);check(row['preview']);x,y=(i%2)*640,(i//2)*505;sheet.paste(Image.open(WS/row['preview']['file']),(x,y+25));draw.text((x+8,y+6),name,fill='white')
    path=(WS/run['exe']['file']).parent/'center-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        result=dict(native_sha256=sha(WS/'inventory/client455-center-messages-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=run['frames'],reviewed=True,reviewed_frames=4,
                    observations=['Actual Korean C1A/CE7 records render through the restored center owner and real medium GDI font',
                                  'The queue occupies centered lines; later frame shows their fading and the last frame is clear',
                                  'The probe crops the actual640x480 device viewport, excluding the20pixel backbuffer margin',
                                  'Messages are submitted directly to the actual MainGame member; full C1A dispatch/chat/live hover cancellation is still open'],reference_executable_capture=False,full_C1A_dispatch=False,full_stage_teardown=False,full_client=False)
        (WS/'inventory/client455-center-messages-visual-review.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
