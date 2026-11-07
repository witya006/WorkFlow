"""Compose actual banked window frames and record an explicit visual review."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();native=load('client455-linker-window-native');require(native['natural_exit']==0 and len(native['frames'])==8,'Successful actual window run required')
    sheet=Image.new('RGB',(1176,1170),'#202020');draw=ImageDraw.Draw(sheet);frames={Path(r['file']).name:r for r in native['frames']}
    for i,name in enumerate(['window-collapsed.bgra','window-expanded.bgra','window-selected3.bgra','window-pinned-subset.bgra','window-scaled640.bgra']):
        row=frames[name];check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((32,80,620,370));x,y=i%2*588,i//2*315;sheet.paste(image,(x,y+25));draw.text((x+5,y+5),name,fill='white')
    for i,name in enumerate(['glyph-normal.bgra','glyph-clipped.bgra','glyph-after-clip.bgra']):
        row=frames[name];check(row);check(row['preview']);image=Image.open(WS/row['preview']['file']).crop((32,22,96,50)).resize((384,168),Image.Resampling.NEAREST);sheet.paste(image,(i*392,980));draw.text((i*392+5,955),name,fill='white')
    path=(WS/native['exe']['file']).parent/'window-contact.png';sheet.save(path);print(path)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-linker-window-native.json'),script_sha256=sha(Path(__file__)),sheet=record(path),frames=native['frames'],reviewed=True,reviewed_frames=8,
            observations=['Ordinary CGUIWindow hierarchy draws the real455main/common sprites,bank glyphs and actualowned item icons',
                'Collapsed and five-bank expanded layouts,selection3,pinned subset and640-width scaling are visible',
                'Fixture uses16actualinventory originals and50admitted clones;Potion11 icons are excluded because their cooldown provider explicitlyrefuses',
                'Image-text draws mapped symbols with a gap for an unknown character;clipping changes UV state retained by the following normal draw'],
            reference_executable_capture=False,actual_gameplay_item_actions=False,full_Linker=False,full_client=False)
        (WS/'inventory/client455-linker-window-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
