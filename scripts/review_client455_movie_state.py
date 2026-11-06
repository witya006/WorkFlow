"""Bind review to the six real plain/fullscreen letterbox/logo frames."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args();manifest=WS/'inventory/client455-movie-state-native.json';native=json.loads(manifest.read_text());frames=native['frames'];sheet=Image.new('RGB',(960,520),(28,28,28));draw=ImageDraw.Draw(sheet)
    if len(frames)!=6:raise ValueError('Six movie display views required')
    for index,row in enumerate(frames):
        path=WS/row['file'];preview=WS/row['preview']
        if sha(path)!=row['sha256'] or sha(preview)!=row['preview_sha256']:raise ValueError('Changed movie display view')
        view=Image.open(preview).convert('RGB');view.thumbnail((320,240));x,y=index%3*320,index//3*260;sheet.paste(view,(x,y+20));draw.text((x+4,y+3),path.stem,fill='white')
    output=WS/'artifacts/client455-movie-state/contact-sheet.png';output.parent.mkdir(parents=True,exist_ok=True);sheet.save(output);report={'manually_reviewed':args.reviewed,'native_sha256':sha(manifest),'script_sha256':sha(Path(__file__)),'frames':frames,'sheet':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'scope':'OwnGPU640x480 movie display;synthetic logo fixture,not455logo asset or fullruntime pixelparity','M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-movie-state-visual.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'reviewed':args.reviewed,'frames':len(frames),'sheet':report['sheet']}))
if __name__=='__main__':main()
