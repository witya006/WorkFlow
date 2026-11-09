"""Prepare current receiver and related captures; record after actual viewing."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record-reviewed',action='store_true');args=parser.parse_args();groups=[]
    for name,count in [('nuclear-receiver',4),('nuclear-registry',5),('nuclear-minimap',6),('message-dispatch',5)]:
        native=load('client455-'+name+'-native');require(not native['natural_exit'] and native['native']['status']=='PASS' and len(native['frames'])==count,'Current native '+name);require(native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current own link')
        sheet=Image.new('RGB',(1280,1515),'#202020');draw=ImageDraw.Draw(sheet)
        for i,row in enumerate(native['frames']):
            check(row);check(row['preview']);x,y=(i%2)*640,(i//2)*505;draw.text((x+8,y+6),Path(row['file']).stem,fill='white');sheet.paste(Image.open(WS/row['preview']['file']).convert('RGB'),(x,y+25))
        file=(WS/native['exe']['file']).parent/(name+'-116-contact.png');sheet.save(file);print(file);groups.append(dict(name=name,native=record(WS/'inventory'/('client455-'+name+'-native.json')),frames=native['frames'],sheet=record(file),reviewed_frames=count))
    if args.record_reviewed:
        report=dict(script_sha256=sha(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),reviewed=True,reviewed_frames=20,groups=groups,observations=['Actual ordinary receiver creates the MiniMap marker from registry lookup','Actual inventory type33 completion emits empty-cursor C1A before showing marker;C1A readable in real chat','Receiver lab draws a batch of center messages at their initial positions without normal frame layout updates;overlap is visible and full frame/layout acceptance is not claimed','Real archived launch/impact/radar draw through current global effect system;final effect/UI frame cleared','Registry5,marker6,message5 frames separately viewed;static marker/message frames compared to115','Nearby explosion can cover the viewport;no original455 executable captures/full trajectory/quake/compositing acceptance','Both nuclear labs retain20 R3T teardown warnings;complete texture ownership/memory balance remain unproven'],reference_executable_capture=False,full_socket_auth=False,full_inventory_use=False,full_stage_lifecycle=False,full_world_effects=False,full_client=False)
        (WS/'inventory/client455-nuclear-receiver-visual-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
