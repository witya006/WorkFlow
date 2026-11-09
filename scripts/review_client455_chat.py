"""Review actual chat-pane GPU output; layout is a controlled four-pane grid."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();run=load('client455-chat-native');require(not run['natural_exit'] and len(run['frames'])==5,'Successful chat native')
    sheet=Image.new('RGB',(1280,1515),'#202020');draw=ImageDraw.Draw(sheet);frames={Path(row['file']).stem:row for row in run['frames']}
    for i,name in enumerate(['chat-system','chat-party','chat-forced','chat-wrapped','chat-cleared']):
        row=frames[name];check(row);check(row['preview']);x,y=(i%2)*640,(i//2)*505;sheet.paste(Image.open(WS/row['preview']['file']),(x,y+25));draw.text((x+8,y+6),name,fill='white')
    path=(WS/run['exe']['file']).parent/'chat-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-chat-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=run['frames'],reviewed=True,reviewed_frames=5,
                    observations=['Real C1A with SYSTEM font routes to actual panes0/3;other panes stay empty',
                                  'Real localized party marker and separate body route to panes0/1',
                                  'Style26 bypasses all pane filters and renders the yellow friend message in all four panes',
                                  'Long mixed Korean/ASCII text wraps and all panes clear in the final frame',
                                  'The four boards use a synthetic grid for simultaneous inspection; full chat-window layout/input/filter controls and common C1A dispatch remain open'],reference_executable_capture=False,full_chat_UI=False,full_C1A_dispatch=False,full_client=False)
        (WS/'inventory/client455-chat-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
