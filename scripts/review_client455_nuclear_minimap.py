"""Prepare actual GPU frames for viewing,record only after they are viewed."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();run=load('client455-nuclear-minimap-native');require(not run['natural_exit'] and run['native']['status']=='PASS' and len(run['frames'])==6,'Successful actual UI run')
    sheet=Image.new('RGB',(1280,1515),'#202020');draw=ImageDraw.Draw(sheet)
    names=['first','warm','mature','cleared','clear-again','three-owners'];frames={Path(x['file']).stem:x for x in run['frames']}
    for i,name in enumerate(names):
        row=frames['nuclear-map-'+name];check(row);check(row['preview']);x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),name,fill='white');sheet.paste(Image.open(WS/row['preview']['file']),(x,y+25))
    file=(WS/run['exe']['file']).parent/'nuclear-map-contact.png';sheet.save(file);print(file)
    opacity=load('client455-minimap-opacity-native');opacity_frames=[row for item in opacity['runs'] for row in item['frames']];require(len(opacity_frames)==6,'Two-nation opacity captures')
    comparison=Image.new('RGB',(1280,1515),'#202020');paint=ImageDraw.Draw(comparison)
    for i,row in enumerate(opacity_frames):
        check(row);require(sha(WS/row['preview'])==row['preview_sha256'],'Opacity preview');x,y=(i//3)*640,(i%3)*505;paint.text((x+8,y+6),opacity['runs'][i//3]['nation']+' '+Path(row['file']).stem,fill='white');comparison.paste(Image.open(WS/row['preview']),(x,y+25))
    opacity_sheet=file.with_name('opacity-regression-contact.png');comparison.save(opacity_sheet);print(opacity_sheet)
    if args.record_reviewed:
        report=dict(native_sha256=sha(WS/'inventory/client455-nuclear-minimap-native.json'),script_sha256=sha(Path(__file__)),sheet=record(file),frames=run['frames'],reviewed=True,reviewed_frames=6,observations=['Actual three marker roots belong to the existing MiniMap map container','First position precedes icon/font configuration;initial background width remains zero','Repeated display uses retained icon size/font metrics and preserves draw-count pulse','Ordinary draw pulses icon alpha after drawing;empty shown markers continue pulsing','Removing children clears the map and retains their internal UI state','Coordinates/geometry are typed lab inputs;registry/race/world producer/ordinary receiver/fullminimap not accepted'],reference_executable_capture=False,full_minimap=False,normal_receiver=False,full_client=False)
        report.update(opacity_native_sha256=sha(WS/'inventory/client455-minimap-opacity-native.json'),opacity_sheet=record(opacity_sheet),opacity_frames=opacity_frames,opacity_reviewed_frames=6)
        (WS/'inventory/client455-nuclear-minimap-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
