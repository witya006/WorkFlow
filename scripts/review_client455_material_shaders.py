"""Render fresh native frames for human/agent inspection;record only after viewing."""
import argparse,json
from PIL import Image,ImageChops,ImageDraw
from compare_client_binaries import WS
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,check,require,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--record-review',action='store_true');a=p.parse_args();native=load('client455-material-shaders-native');require(native['status']=='PASS_SELECTED' and len(native['frames'])==4,'Four completed actual GPU frames')
    sheet=Image.new('RGB',(1280,850),(25,25,25));draw=ImageDraw.Draw(sheet);boxes=[]
    for i,row in enumerate(native['frames']):
        check(row);check(row['preview']);im=Image.open(WS/row['preview']['file']).convert('RGB');bg=Image.new('RGB',im.size,(16,32,48));box=ImageChops.difference(im,bg).getbbox();require(box is not None,'Actual visible shader geometry');boxes.append(list(box))
        x,y=(i%2)*640,(i//2)*425;draw.text((x+5,y+5),row['file'].split('/')[-1],fill='white');sheet.paste(im.resize((512,384)),(x+5,y+25));crop=im.crop(box);crop.thumbnail((120,300));sheet.paste(crop,(x+520,y+50))
    path=(WS/native['exe']['file']).parent/'material-shaders-contact.png';sheet.save(path)
    out=dict(reviewed=a.record_review,reviewed_frames=4 if a.record_review else 0,script=record(WS/'scripts/review_client455_material_shaders.py'),native_sha256=sha(WS/'inventory/client455-material-shaders-native.json'),sheet=record(path),frames=native['frames'],visible_bounds=boxes,new_visual_inspection=a.record_review,scope='Four controlled actual BSP material frames;does not prove full455appearance')
    (WS/'inventory/client455-material-shaders-visual-review.json').write_text(json.dumps(out,indent=2)+'\n');print(str(path))
if __name__=='__main__':main()
