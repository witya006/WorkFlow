"""Bind manually inspected real world frames;never claim reference455pixel parity."""
import argparse,hashlib,json
from pathlib import Path
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args();frames=[]
    for race in ['bellato','cora','accretia']:
        path=WS/f'inventory/client455-world-{race}-native.json';native=json.loads(path.read_text())
        for row in native['frames']:
            if sha(WS/row['file'])!=row['sha256'] or sha(WS/row['preview'])!=row['preview_sha256']:raise ValueError('Changed world frame')
            frames.append({'race':race,'native_sha256':sha(path),**row})
    result={'scope':'Ownsource frames,camera0,sky/opaque;not original455comparison','script_sha256':sha(Path(__file__)),'manually_reviewed':args.reviewed,'frames':frames}
    (WS/'inventory/client455-world-visual.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'frames':len(frames),'manually_reviewed':args.reviewed}))
if __name__=='__main__':main()
