"""Selected455 light geometry oracle and small owned fixtures,not a BSP parser."""
import struct

def cases():
    identity=[float(i%5==0) for i in range(16)]
    def make(name,magic,faces=None,ids=None,leaves=1,lo=(-1,-1,-1),hi=(1,1,1),world=None,inverse=None):
        faces=faces or [(0,3,1.)];ids=ids if ids is not None else [list(range(len(faces)))]*leaves
        return dict(name=name,magic=magic,faces=faces,ids=ids,lo=lo,hi=hi,world=world or identity,inverse=inverse or identity)
    out=[]
    for magic in [False,True]:
        tag='magic' if magic else 'regular'
        out.append(make(tag+'-flags',magic,[(a,3,y) for a,y in [(0,1),(0x10,1),(0x20,1),(0x30,1),(0x40,1),(0x80,1),(0,-1),(0,0)]]))
        out.append(make(tag+'-duplicates',magic,[(0,3,1.)]*5,[[0,1,2,2,0],[2,3,4,1,4]],leaves=2))
        out.append(make(tag+'-polygon-sizes',magic,[(0,n,1.) for n in [0,1,2,3,4,5,255]]))
        for count in ([999,1000,1001,4999,5000,5001] if not magic else [666,667,668,2999,3000,3002]):
            out.append(make(tag+'-faces-'+str(count),magic,[(0,3,1.)]*count))
        out.append(make(tag+'-leaf-cap',magic,[(0,3,1.)]*270,[[i] for i in range(270)],leaves=270))
        out.append(make(tag+'-zero-box',magic,hi=(-1,-1,-1)))
        out.append(make(tag+'-width1000',magic,lo=(-500,-1,-1),hi=(500,1,1)))
        out.append(make(tag+'-width1000plus',magic,lo=(-500,-1,-1),hi=(500.25,1,1)))
        out.append(make(tag+'-tall-only',magic,lo=(-1,-2000,-1),hi=(1,2000,1)))
        out.append(make(tag+'-outside-root',magic,hi=(10001,1,1)))
        w=identity[:];w[12:15]=[7,-3,11];inv=identity[:];inv[12:15]=[-7,3,-11]
        out.append(make(tag+'-owned-transform',magic,world=w,inverse=inv))
    out.append(make('magic-tail-overwrite',True,[(0,3,1.)]*3002,[list(range(3002))+[2999,3001,0]]))
    return out

def encode(rows):
    result=bytearray(b'RFLG121\0'+struct.pack('<I',len(rows)))
    for i,row in enumerate(rows):
        faces=row['faces'];ids=row['ids'];result+=struct.pack('<4I',i,row['magic'],len(faces),len(ids));result+=struct.pack('<38f',*row['world'],*row['inverse'],*row['lo'],*row['hi'])
        for attr,n,normal in faces:result+=struct.pack('<BB2xf',attr,n,normal)
        for leaf in ids:result+=struct.pack('<I',len(leaf))+struct.pack('<'+'I'*len(leaf),*leaf)
    return bytes(result)

def expected(row):
    magic=row['magic'];lo,hi=row['lo'],row['hi'];batches=[];vertices=bytearray();pending=0;seen=[]
    if magic and (hi[0]-lo[0]>1000 or lo==hi or any(x<-10000 or x>10000 for x in (*lo,*hi))):return bytes(vertices),batches
    # Owned nodes divide X monotonically,so traversal emits front leaves in order.
    for leaf in row['ids'][:256 if magic else 128]:
        for face_id in leaf:
            attr,count,normal=row['faces'][face_id]
            if attr&(0x30 if magic else 0x10) or (magic and not normal>0):continue
            if face_id in seen:continue
            if magic and len(seen)==3000:seen.pop()
            seen.append(face_id)
            for j in range(max(0,count-2)):
                for corner in [0,j+1,j+2]:vertices+=struct.pack('<fffI',float(face_id),float(corner),float(face_id^corner),0)
                pending+=3
                if pending>=(2000 if magic else 3000):batches.append(pending);pending=0
            if not magic and len(seen)>=5000:
                if pending:batches.append(pending)
                return bytes(vertices),batches
    if pending:batches.append(pending)
    return bytes(vertices),batches
