"""Build contact sheets and bind manual review to the actual intro GPU frames."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args();frames=[];sheets=[]
    for race in ['bellato','cora','accretia']:
        path=WS/f'inventory/client455-tutorial-intro-{race}-native.json';native=json.loads(path.read_text());rows=native['frames'];sheet=Image.new('RGB',(960,260*((len(rows)+2)//3)),(28,28,28));draw=ImageDraw.Draw(sheet)
        for index,row in enumerate(rows):
            raw=WS/row['file'];preview=WS/row['preview']
            if sha(raw)!=row['sha256'] or sha(preview)!=row['preview_sha256']:raise ValueError('Changed GPU frame')
            x,y=index%3*320,index//3*260;view=Image.open(preview).convert('RGB');view.thumbnail((320,240));sheet.paste(view,(x,y+20));draw.text((x+4,y+3),race+'/'+raw.stem,fill='white');frames.append({'race':race,**row,'native_sha256':sha(path)})
        output=WS/f'artifacts/client455-tutorial-intro/{race}-sheet.png';sheet.save(output);sheets.append({'file':output.relative_to(WS).as_posix(),'sha256':sha(output)})
    report={'manually_reviewed':args.reviewed,'script_sha256':sha(Path(__file__)),'frames':frames,'sheets':sheets,'scope':'Own GPU camera cuts/first fade frames;not reference-runtime pixel parity or fullTutorial','M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-intro-visual.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'reviewed':args.reviewed,'frames':len(frames),'sheets':sheets}))
if __name__=='__main__':main()
