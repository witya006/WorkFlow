"""Produce hash-bound contact sheets for manual review;no new native execution."""
import hashlib,json
from PIL import Image,ImageDraw
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    path=WS/'inventory/client455-briefing-window-native.json';native=json.loads(path.read_text());sheets=[]
    for run in native['runs']:
        sheet=Image.new('RGB',(960,4*264),(240,240,240));draw=ImageDraw.Draw(sheet)
        for index,row in enumerate(run['frames']):
            frame=WS/row['file'];preview=WS/row['preview']
            if sha(frame)!=row['sha256'] or sha(preview)!=row['preview_sha256']:raise ValueError('Changed visual evidence')
            image=Image.open(preview);image.thumbnail((320,240));x,y=(index%3)*320,(index//3)*264;sheet.paste(image,(x,y+24));draw.text((x+4,y+4),preview.stem,fill='black')
        output=(WS/run['exe']['file']).parent/'contact-sheet.png';sheet.save(output);sheets.append({'nation':run['nation'],'file':output.relative_to(WS).as_posix(),'sha256':sha(output),'frames':len(run['frames'])})
    result={'native_sha256':sha(path),'script_sha256':sha(__import__('pathlib').Path(__file__)),'sheets':sheets,'manually_reviewed':False}
    (WS/'inventory/client455-briefing-window-visual.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(sheets))
if __name__=='__main__':main()
