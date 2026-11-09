"""Prepare current registry/marker/message frames; record only after viewing."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();groups=[]
    for name,count in [('nuclear-registry',5),('nuclear-minimap',6),('message-dispatch',5)]:
        native=load('client455-'+name+'-native');require(not native['natural_exit'] and native['native']['status']=='PASS' and len(native['frames'])==count,'Current native '+name)
        require(native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current own link')
        sheet=Image.new('RGB',(1280,1515),'#202020');draw=ImageDraw.Draw(sheet)
        for i,row in enumerate(native['frames']):
            check(row);check(row['preview']);x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(Image.open(WS/row['preview']['file']).convert('RGB'),(x,y+25))
        file=(WS/native['exe']['file']).parent/(name+'-115-contact.png');sheet.save(file);print(file);groups.append(dict(name=name,native=record(WS/'inventory'/('client455-'+name+'-native.json')),frames=native['frames'],sheet=record(file),reviewed_frames=count))
    if args.record_reviewed:
        report=dict(script_sha256=sha(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),reviewed=True,reviewed_frames=16,groups=groups,observations=['Actual archived radar/flight/impact particles visible;nearby explosion covers the whole viewport in this lab','Actual C17 Korean countdown appears in real four-pane chat/center over the same retained explosion;no reference executable captures','Detached launch/impact eventually disappear;two final registry frames have no remaining effect pixels','Current marker6 and message5 frames visually preserved and separately hash-compared to114','This is a selected scene;full trajectory/camera quake/light compositing/world and actual group60 receiver/stage lifecycle remain open','Registry lab emits20 R3T release warnings during teardown;does not prove complete texture lifetime or memory balance'],reference_executable_capture=False,full_world_effects=False,ordinary_receiver=False,full_stage_lifecycle=False,full_client=False)
        (WS/'inventory/client455-nuclear-registry-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
