"""Prepare and record human/agent viewing of actual message-output GPU captures."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    run=load('client455-message-dispatch-native');require(run['natural_exit']==0 and run['native']['status']=='PASS' and len(run['frames'])==5,'Accepted native output')
    sheet=Image.new('RGB',(1280,1515),'#202020');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(run['frames']):
        check(row);check(row['preview']);x=(i%2)*640;y=(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(Image.open(WS/row['preview']['file']).convert('RGB'),(x,y+25))
    path=(WS/run['exe']['file']).parent/'message-output-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-message-dispatch-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=run['frames'],reviewed=True,reviewed_frames=5,
            observations=['Actual Login member draws centered near the bottom in its target ordinary font/color',
            'Actual main message routes to chat panes0/3 and center; forced style26 appears in all four actual panes',
            'After live typed-item hover cancels actual BSP/effect/Miles aiming,C1A is visible in both chat and center',
            'Cleared output has no remaining pixels; chat uses a controlled four-pane grid,not full window-layout acceptance',
            'Tutorial was only a routing-kernel case; full Login/auth,actual Tutorial,CE7 game-action registration and fullclient remain open'],
            reference_executable_capture=False,full_Login_auth_flow=False,full_Tutorial=False,CE7_game_action_registration=False,full_client=False)
        (WS/'inventory/client455-message-dispatch-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
