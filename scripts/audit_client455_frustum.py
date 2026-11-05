"""Pin the scene frustum and generate instruction-derived finite FP cases."""
import hashlib,json,math,struct
from fractions import Fraction as F
from audit_client455_animation_timing import binary_round
from audit_client455_mesh_runtime import import_slots
from build_client455_x87_math import read_va
from compare_client_binaries import WS

def sha(data):return hashlib.sha256(data).hexdigest()
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def number(value):return F(struct.unpack('<f',struct.pack('<I',value))[0])
def stored(value,p,mode,negative_zero=False):
    value=binary_round(binary_round(value,p,mode),24,mode)
    return bits(float(value)) if value else 0x80000000 if negative_zero else 0
def sqrt_nearest(value,p):
    if not value:return F(0)
    exponent=value.numerator.bit_length()-value.denominator.bit_length()
    if value<F(2)**exponent:exponent-=1
    scale=F(2)**(exponent//2-p+1);scaled=value/(scale*scale)
    q=math.isqrt(scaled.numerator//scaled.denominator)
    midpoint=F(2*q+1,2)**2
    q+=int(scaled>midpoint or scaled==midpoint and q%2)
    return q*scale
def planes(clip,p,mode):
    out=[];r=lambda v:binary_round(v,p,mode)
    for i,column in enumerate([0,0,1,1,2,2]):
        coefficients=[]
        for row in range(4):
            a,b=clip[4*row+3],clip[4*row+column];addition=i in [0,3,4]
            v=number(a)+(number(b) if addition else -number(b))
            # x87 exact cancellation is -0 only with RC-down. Equal-sign
            # zero addition retains its sign, then the instruction FCHS flips it.
            sign_a=a>>31;sign_b=(b>>31)^int(not addition)
            zero_sign=sign_a if number(a)==number(b)==0 and sign_a==sign_b else int(mode==1)
            coefficients.append(stored(-r(v),p,mode,not zero_sign))
        x,y,z=map(number,coefficients[:3]);square=stored(r(r(y*y)+r(x*x))+r(z*z),p,mode)
        root=stored(sqrt_nearest(number(square),p),p,mode)
        reciprocal=stored(1/number(root),p,mode)
        out += [stored(number(v)*number(reciprocal),p,mode,bool(v>>31)) for v in coefficients]
    return out
def visible(minimum,maximum,values,p,mode):
    r=lambda v:binary_round(v,p,mode)
    for i in range(6):
        a=values[4*i:4*i+4]
        if any(v&0x7f800000==0x7f800000 for v in a):continue # qNaN plane: unordered dot does not reject.
        vertex=[minimum[j] if number(a[j])>0 else maximum[j] for j in range(3)]
        products=[r(number(a[j])*number(vertex[j])) for j in range(3)]
        if r(r(r(products[0]+products[1])+products[2])+number(a[3]))>0:return 0
    return 1
def matrix_product(view,projection,mode):
    out=[]
    for i in range(4):
        for j in range(4):
            terms=[F(view[4*i+k])*F(projection[4*k+j]) for k in range(4)];value=sum(terms)
            if value:out.append(bits(value));continue
            signs=[(bits(view[4*i+k])^bits(projection[4*k+j]))>>31 for k in range(4)]
            # These binary-exact products need no numerical rounding. Four
            # equal-sign zeros retain their sign; mixed zeros/cancellation use RC.
            negative=signs[0] if not any(terms) and len(set(signs))==1 else int(mode==1)
            out.append(0x80000000 if negative else 0)
    return out
def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));refs=[];previous=None
    ranges=[('scene_publish',0x8c2a90,0x1fc),('aabb',0x8c2c90,0xab),('copy_planes',0x8c2dc0,0x15),('sqrt_entry',0x874500,0x14),('sqrt_core',0x87451d,0x9d),('sqrt_load_cw',0x888dd5,0x17),('sqrt_classify_exit',0x888e48,0x4d)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455 pin')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in ranges]
        if previous is not None and previous!=bodies:raise ValueError('Frustum ranges differ')
        previous=bodies;thunk=read_va(raw,0x85412a,6)
        if thunk[:2]!=b'\xff\x25' or import_slots(raw)[struct.unpack_from('<I',thunk,2)[0]]!={'dll':'d3dx9_36.dll','name':'D3DXMatrixMultiply'}:raise ValueError('Wrong matrix provider')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies})
    identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    translated=identity.copy();translated[12:15]=[2,-3,4]
    perspective=[1.25,0,0,0,0,1.5,0,0,0,0,1.5,1,0,0,-1.25,0]
    rotated=[.75,0,.5,0,0,1,0,0,-.5,0,.75,0,3,.25,-1,1]
    ortho=[.25,0,0,0,0,.5,0,0,0,0,.125,0,0,0,0,1]
    shear=[1,.25,.5,.125,.5,1,.25,.25,.25,.5,1,.5,1,2,3,4]
    scenarios=[(identity,identity),(translated,identity),(identity,perspective),(rotated,perspective),(identity,ortho),(shear,shear)]
    matrix_rows=[];bbox_rows=[]
    for p in [24,53,64]:
        for mode in range(4):
            for view,projection in scenarios:
                clip=matrix_product(view,projection,mode)
                matrix_rows.append((p,mode,*map(bits,view),*map(bits,projection),*clip,*planes(clip,p,mode)))
            unit=planes(list(map(bits,identity)),p,mode)
            boxes=[([-.25]*3,[.25]*3),([-2]*3,[2]*3),([0]*3,[0]*3)]
            for axis in range(3):
                for direction in [-1,1]:
                    lo=[-.25]*3;hi=[.25]*3;lo[axis]=hi[axis]=direction;boxes.append((lo.copy(),hi.copy()))
                    lo[axis]=hi[axis]=direction*1.00000011920928955078125;boxes.append((lo,hi))
            for lo,hi in boxes:
                minimum=list(map(bits,lo));maximum=list(map(bits,hi));bbox_rows.append((p,mode,*minimum,*maximum,*unit,visible(minimum,maximum,unit,p,mode)))
            # Ordered sign selection and unordered-dot behavior at the source boundary.
            nanplanes=[0]*24;nanplanes[0]=0x7fc00001
            bbox_rows.append((p,mode,*([0]*6),*nanplanes,1))
            cancellation=[0]*24;cancellation[:4]=list(map(bits,[1,1,1,-16777216]))
            lo=list(map(bits,[16777216,1,0]));bbox_rows.append((p,mode,*lo,*lo,*cancellation,visible(lo,lo,cancellation,p,mode)))
    root=WS/'work/client-reference/frustum455';root.mkdir(parents=True,exist_ok=True);golden=b'FC45'+struct.pack('<3I',1,len(matrix_rows),len(bbox_rows))
    for row in matrix_rows:golden+=struct.pack('<74I',*row)
    for row in bbox_rows:golden+=struct.pack('<33I',*row)
    path=root/'frustum.bin';path.write_bytes(golden)
    report={'scope':'455 scene frustum and AABB math;normal actor lifecycle and full game visibility remain open','references':refs,'matrix_cases':len(matrix_rows),'bbox_cases':len(bbox_rows),'fp_modes':12,'golden':path.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'script_sha256':sha((WS/'scripts/audit_client455_frustum.py').read_bytes()),'oracle':'Exact Fraction x87 operations,integer-square-root nearest at inherited PC,explicit m32 spills,12PC/RC modes;binary-exact input matrix products independent of D3DX rounding. qNaN rejection branch separately modeled.','provider_sha256':'c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935','limits':['Sqrt proof covers finite nonnegative inputs with masked exceptions;CRT errno/matherr,NaN payloads,unmasked exceptions not accepted','Real camera matrix acquisition/full game visibility not accepted','No input455EXE execution;no percentage inferred from check count']}
    (WS/'inventory/client455-frustum-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{len(matrix_rows)}matrix/{len(bbox_rows)}AABB cases;7ranges equal bothpins')
if __name__=='__main__':main()
