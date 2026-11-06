"""Review current ordinary RVP scene/end-fade frames from three455 maps."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageDraw
from compare_client_binaries import WS


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args()
    sheet=Image.new('RGB',(960,520),(28,28,28));draw=ImageDraw.Draw(sheet);frames=[]
    for x,race in enumerate(['bellato','cora','accretia']):
        native=WS/f'inventory/client455-rvp-runtime-{race}-native.json';body=json.loads(native.read_text())
        if body['natural_exit'] or body['native']['status']!='PASS' or len(body['frames'])!=2:raise ValueError('Current RVP run failed')
        for row in body['frames']:
            path,preview=WS/row['file'],WS/row['preview']
            if sha(path)!=row['sha256'] or sha(preview)!=row['preview_sha256']:raise ValueError('Changed RVP view')
            y=0 if path.stem=='rvp-scene' else 260
            view=Image.open(preview).convert('RGB');view.thumbnail((320,240));sheet.paste(view,(x*320,y+20))
            draw.text((x*320+4,y+3),race+'/'+path.stem,fill='white')
            frames.append(dict(race=race,native_sha256=sha(native),**row))
    path=WS/'artifacts/client455-rvp-runtime/contact-sheet.png';path.parent.mkdir(parents=True,exist_ok=True);sheet.save(path)
    report=dict(manually_reviewed=args.reviewed,frames=frames,sheet=dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)),
        script_sha256=sha(Path(__file__)),scope='Own GPU scene/end-fade checks,not reference-runtime pixel equivalence or full RVP actors',M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-runtime-visual.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(reviewed=args.reviewed,frames=6,sheet=report['sheet'])))


if __name__=='__main__':main()
