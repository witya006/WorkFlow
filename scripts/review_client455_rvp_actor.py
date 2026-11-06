"""Create a review sheet for own real455 RVP model renders,including pixel crops."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args()
    source=WS/'inventory/client455-rvp-actor-native.json';native=json.loads(source.read_text())
    if native['natural_exit'] or native['native']['status']!='PASS':raise ValueError('Actor execution failed')
    sheet=Image.new('RGB',(960,1040),(28,28,28));draw=ImageDraw.Draw(sheet);frames=[]
    for index,row in enumerate(native['frames']):
        path,preview=WS/row['file'],WS/row['preview']
        if sha(path)!=row['sha256'] or sha(preview)!=row['preview_sha256']:raise ValueError('Changed GPU output')
        view=Image.open(preview).convert('RGB');x=(index%3)*320;y=(index//3)*260
        full=view.copy();full.thumbnail((320,240));sheet.paste(full,(x,y+20));draw.text((x+4,y+3),path.stem,fill='white')
        if 'only' in path.stem or 'reset' in path.stem:
            box=ImageChops.difference(view,Image.new('RGB',view.size,(0x10,0x20,0x30))).getbbox()
            if box:
                a,b,c,d=box;box=(max(0,a-8),max(0,b-8),min(view.width,c+8),min(view.height,d+8));crop=view.crop(box);crop.thumbnail((320,240),Image.Resampling.NEAREST)
                #Upscale tiny real geometry for inspection without claiming its
                #size or detail at640x480 is larger than the original output.
                factor=min(320/crop.width,240/crop.height);crop=crop.resize((int(crop.width*factor),int(crop.height*factor)),Image.Resampling.NEAREST)
                sheet.paste(crop,(x,y+540));draw.text((x+4,y+523),path.stem+' pixel crop',fill='white')
        frames.append(row)
    path=WS/'artifacts/client455-rvp-actor/contact-sheet.png';path.parent.mkdir(parents=True,exist_ok=True);sheet.save(path)
    report=dict(manually_reviewed=args.reviewed,frames=frames,sheet=dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)),
        native_sha256=sha(source),script_sha256=sha(Path(__file__)),scope='Own actor-only/world/controlled real animation GPU frames;stock ships are small at this camera distance;not reference-runtime pixel equivalence or fullFX',M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-actor-visual.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(reviewed=args.reviewed,frames=len(frames),sheet=report['sheet'])))
if __name__=='__main__':main()
