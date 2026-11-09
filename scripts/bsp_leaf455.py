"""Finite affine/leaf oracle from4558C0980/8FAE20/8FAF00;no BSP file parser."""
import struct


def cases():
    identity=[float(i%5==0) for i in range(16)];matrices=[('identity',identity)]
    for name in ['translation','quarter-turn','scale','reflection','shear','unused-homogeneous']:
        m=identity[:]
        if name=='translation':m[12:15]=[-6,1,2]
        elif name=='quarter-turn':m[0]=m[5]=0;m[1]=-1;m[4]=1
        elif name=='scale':m[0]=.5;m[5]=2;m[10]=-1
        elif name=='reflection':m[0]=-1
        elif name=='shear':m[4]=.5
        else:m[3]=5;m[7]=-2;m[11]=3;m[15]=7
        matrices.append((name,m))
    return [dict(name=f'{name}/topology{topology}/{i}',inverse=m,point=p,topology=topology) for name,m in matrices for topology in range(4) for i,p in enumerate([[-3,-2,7],[-3,0,7],[-3,2,7],[0,0,0],[3,-2,7]])]


def expected(row):
    m,p=row['inverse'],row['point'];point=[sum(p[j]*m[j*4+i] for j in range(3))+m[12+i] for i in range(3)];kind=row['topology']
    if kind==3:leaf=-1
    elif kind==2:leaf=0
    elif kind==1:leaf=2 if point[1]>=0 else 3 # Root leaf0 is not a successful early stop.
    else:leaf=1 if point[0]>=0 else (2 if point[1]>=0 else 3)
    return point,leaf


def encode(rows):
    return struct.pack('<I',len(rows))+b''.join(struct.pack('<I19f',r['topology'],*r['point'],*r['inverse']) for r in rows)
