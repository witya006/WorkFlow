"""Review the actual screen/hover/returned Linker frames."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args()
    run=load('client455-board-hover-native');require(not run['natural_exit'] and len(run['frames'])==6,'Successful hover probe')
    sheet=Image.new('RGB',(1260,1155),'#202020');draw=ImageDraw.Draw(sheet)
    frames={Path(row['file']).name:row for row in run['frames']}
    for index,name in enumerate(['hover-idle','hover-picked','hover-updated','hover-replaced','hover-cleared','hover-returned']):
        row=frames[name+'.bgra'];check(row);check(row['preview']);picture=Image.open(WS/row['preview']['file']).crop((0,70,630,430))
        x,y=index%2*630,index//2*385;sheet.paste(picture,(x,y+25));draw.text((x+5,y+5),name,fill='white')
    path=(WS/run['exe']['file']).parent/'hover-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-board-hover-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),
                    frames=run['frames'],reviewed=True,reviewed_frames=6,
                    observations=['Actual screen Draw shows the real EDF inventory icon andthe cloned item onthe cursor',
                                  'The item iscentered before its64px resize,matching the target order;rawflag21 lock remainsvisible',
                                  'Ordinary manager FrameMove updates the catched timer once;replacement copies the original state',
                                  'Clear removes the catched item andrestores the real mouse sprite;ReturnHover creates real registered Linker copies',
                                  'The probe checks the null-avatar fast path then uses an actual ordinary avatar with status0 andoffline network initialization;nonphysical size/lifetime cases use synthetic CPU icons',
                                  'Nuclear aiming cancellation/fulloperationqueue/three-layer tooltips/gameplay remain unaccepted'],
                    reference_executable_capture=False,full_gameplay_handlers=False,full_client=False)
        (WS/'inventory/client455-board-hover-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
