"""Prepare actual money-label GPU crops for inspection."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args();path=WS/'inventory/client455-money-native.json';native=json.loads(path.read_text())
    sheet=Image.new('RGB',(960,420),(28,28,28));draw=ImageDraw.Draw(sheet);frames=[]
    for y,run in enumerate(native['runs']):
        if run['exit'] or run['native']['status']!='PASS' or len(run['frames'])!=3:raise ValueError('Native money run failed')
        for x,row in enumerate(run['frames']):
            if sha(WS/row['file'])!=row['sha256'] or sha(WS/row['preview'])!=row['preview_sha256']:raise ValueError('Changed frame')
            image=Image.open(WS/row['preview']).convert('RGB');crop=image.crop((240,75,625,165));crop.thumbnail((320,170));sheet.paste(crop,(x*320,y*210+35));draw.text((x*320+5,y*210+8),run['nation']+'/'+['2^32+1','INT64_MAX','INT64_MIN'][x],fill='white');frames.append(dict(nation=run['nation'],**row))
    output=WS/'artifacts/client455-money/contact-sheet.png';output.parent.mkdir(parents=True,exist_ok=True);sheet.save(output)
    report=dict(manually_reviewed=args.reviewed,frames=frames,sheet=dict(file=output.relative_to(WS).as_posix(),sha256=sha(output)),script_sha256=sha(Path(__file__)),native_sha256=sha(path),scope='Real money label crops only;not full inventory or reference-runtime pixel equivalence',M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-money-visual.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(frames=len(frames),reviewed=args.reviewed,sheet=report['sheet'])))
if __name__=='__main__':main()
