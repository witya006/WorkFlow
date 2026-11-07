"""Compose timer frames and retain independent pre098 visual baselines."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-gui-timer-native');require(native['natural_exit']==0 and len(native['frames'])==6,'Timer successful run');sheet=Image.new('RGB',(1008,645),'#202020');draw=ImageDraw.Draw(sheet)
    names=['timer-idle.bgra','timer-45seconds.bgra','timer-9seconds.bgra','timer-minute.bgra','timer-partial-clip.bgra','timer-reset.bgra'];frames={Path(r['file']).name:r for r in native['frames']}
    for i,name in enumerate(names):
        row=frames[name];check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((64,64,340,166));image=image.resize((1008,372),Image.Resampling.NEAREST);image.thumbnail((504,186));x,y=(i%2)*504,(i//2)*215;sheet.paste(image,(x,y+25));draw.text((x+5,y+5),name,fill='white')
    path=(WS/native['exe']['file']).parent/'timer-contact.png';sheet.save(path);print(path)
    regressions=[]
    for name,baseline in [('client455-linker-window-native','linker-window097-before098.json'),('client455-linker-owners-native','linker-owners097-before098.json'),('client455-item-icon-metadata-native','item-metadata097-before098.json'),('client455-item-icon-native','item-icon092-before098.json')]:
        current=load(name);old_file=WS/'artifacts/client455-progress'/baseline;old=json.loads(old_file.read_text());previous={Path(r['file']).name:r for r in old['frames']};deltas=[]
        require(len(current['frames'])==len(previous),'Frame count drift')
        for row in current['frames']:
            before=previous[Path(row['file']).name];check(row);check(before);a=Image.open(WS/row['preview']['file']).convert('RGB');b=Image.open(WS/before['preview']['file']).convert('RGB');diff=ImageChops.difference(a,b);pixels=sum(p!=(0,0,0) for p in diff.get_flattened_data());deltas.append(dict(name=Path(row['file']).name,before=before['sha256'],after=row['sha256'],changed_pixels=pixels,bounds=diff.getbbox()))
        regressions.append(dict(current=name,baseline=record(old_file),frames=deltas))
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-gui-timer-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=native['frames'],reviewed=True,reviewed_frames=6,regressions=regressions,
            observations=['Real EDF inventory original and two owned Linker copies display the separate timer states','At45000ms the target rounds the displayed seconds up to46;the9000ms fixture has8000ms remaining and displays red9;white1m is visible','Partially clipped icon renders while the whole timer is rejected;label has its separate16-square clip test;reset returns exactly to idle pixels','Unclipped grade-frame order corrected to image then frame per61B6B0;clipped order remains frame then image'],reference_executable_capture=False,full_client=False)
        (WS/'inventory/client455-gui-timer-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(regressions))
if __name__=='__main__':main()
