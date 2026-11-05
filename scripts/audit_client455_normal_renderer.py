"""Pin actual455normal draw/state/registration wrappers and their literals."""
import hashlib,json,struct
from fractions import Fraction as F
from audit_client455_animation_timing import binary_round
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];previous=None;constants=None
    functions=[('unset_state',0x91cbb0,0x1f2),('set_light',0x91cdb0,0x30),('set_state',0x91cde0,0x33c),('draw_at_position',0x92fe80,0x29e),('draw_matrix',0x92fba0,0x33),('shadow_at_position',0x930500,0x143),('model_cull',0x934f00,0xbe),('register_mesh',0x9313f0,0x88),('is_load_animation',0x9316a0,0x1c),('match_animation',0x9316c0,0x64),('set_alpha',0x931740,0x32),('get_alpha',0x931780,0xd),('set_material',0x931790,0x20),('frame_move',0x923a40,0xcb2)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455reference')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in functions]
        data=[read_va(raw,0xbf8320,64),read_va(raw,0xaa9750,8),read_va(raw,0xab0048,8)]
        if previous is not None and (previous!=bodies or data!=constants):raise ValueError('Wrapper ranges/constants differ')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies});previous=bodies;constants=data
    matrix,degrees,radians=constants
    header='#pragma once\n// Literal455 coordinate conversion and x87 double operands.\nstatic const unsigned RF455_NORMAL_COORDINATE_BITS[16]={'+','.join(hex(v)+'u' for v in struct.unpack('<16I',matrix))+'};\nstatic const unsigned long long RF455_NORMAL_DEGREES_BITS='+hex(struct.unpack('<Q',degrees)[0])+'ull;\nstatic const unsigned long long RF455_NORMAL_RADIANS_BITS='+hex(struct.unpack('<Q',radians)[0])+'ull;\n'
    (WS/'scripts/native/client455_normal_renderer_constants.h').write_text(header)
    report={'scope':'Confirmed normal455wrapper ranges/constants;not complete high-level behavior or original process execution','references':refs,'constants':[{'rva':hex(at-0x400000),'bytes':len(data),'sha256':sha(data)} for at,data in [(0xbf8320,matrix),(0xaa9750,degrees),(0xab0048,radians)]],'coordinate_matrix':list(struct.unpack('<16f',matrix)),'degree_operand':struct.unpack('<d',degrees)[0],'radian_operand':struct.unpack('<d',radians)[0],'constants_header_sha256':sha(header.encode()),'bounds':['934F00 spills dot to m32 BEFORE adding plane.w;8C2C90 source helper is different','91CBB0 is actual UnSetState via ResObject caller7CD340;91D320 hasno xrefs andisnotaccepted asUnSetState','9316A0 loads animation synchronously=false;itdoesnotjustinspect load flag','9313F0 ignores boolean andregisters deferred model in caller-provided manager','92FE80 argument4 isscale,argument5 unused,argument6 optional unscaled-translation matrix','930500 ignores position/alpha anduses argument5 asscale;profiling/CRT/error domains remainopen'],'script_sha256':sha((WS/'scripts/audit_client455_normal_renderer.py').read_bytes())}
    report['constants_header_sha256']=sha((WS/'scripts/native/client455_normal_renderer_constants.h').read_bytes())
    golden=bytearray(b'NW45'+struct.pack('<III',1,96,60))
    angles=[0,90,180,-90,720,.125,-.25,1e10]
    boxes=[([1,.5,0],[1,.5,0],[1,2**-24,0,-1]),([-2,-3,-4],[2,3,4],[1,0,0,1]),([-2,-3,-4],[2,3,4],[-1,0,0,1]),([0,0,0],[0,0,0],[0,0,0,0]),([1,2,3],[4,5,6],[.25,-.5,1,-1])]
    for p in [24,53,64]:
        for mode in range(4):
            r=lambda v:binary_round(v,p,mode)
            for angle in angles:
                angle=struct.unpack('<f',struct.pack('<f',angle))[0];out=binary_round(r(r(F(report['degree_operand'])-F(angle))*F(report['radian_operand'])),24,mode)
                stored=-0.0 if not out and mode==1 and angle==report['degree_operand'] else float(out)
                golden+=struct.pack('<IIff',p,mode,angle,stored)
    for p in [24,53,64]:
        for mode in range(4):
            r=lambda v:binary_round(v,p,mode)
            for low,high,plane in boxes:
                vertex=[F(low[i] if plane[i]>0 else high[i]) for i in range(3)];terms=[r(F(plane[i])*vertex[i]) for i in range(3)];dot=binary_round(r(r(terms[1]+terms[0])+terms[2]),24,mode);inside=int(r(dot+F(plane[3]))<=0)
                golden+=struct.pack('<II10fI',p,mode,*low,*high,*plane,inside)
    target=WS/'work/client-reference/normal-renderer455/math.bin';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(golden);report.update(golden=target.relative_to(WS).as_posix(),golden_sha256=sha(golden),angle_cases=96,box_cases=60)
    (WS/'inventory/client455-normal-renderer-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('Pinned14normal455wrapper ranges;constants',report['coordinate_matrix'])
if __name__=='__main__':main()
