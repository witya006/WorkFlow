"""Independent reader for the selected 455 map/NDMap streams; no game execution."""
import struct


class Cursor:
    def __init__(self,data):self.data=data;self.at=0
    def take(self,n):
        if n<0 or n>len(self.data)-self.at:raise ValueError('Truncated map data')
        result=self.data[self.at:self.at+n];self.at+=n;return result
    def u32(self):return struct.unpack('<I',self.take(4))[0]


def parse(main,localized):
    src,nd=Cursor(main),Cursor(localized)
    count,ncount=src.u32(),nd.u32()
    if count!=110:raise ValueError(f'Target map count must be 110, got {count}')
    if ncount!=count:raise ValueError(f'Target NDMap count mismatch: {count}/{ncount}')
    rows=[]
    for _ in range(count):
        start=src.at;record=bytearray(588)
        def read(offset,n,cursor=src):record[offset:offset+n]=cursor.take(n)
        read(0,36);read(36,64,nd);read(100,128)
        sprite=src.take(128).split(b'\0')[0]
        path=b'./SpriteImage/Common/Map/'+sprite
        if len(path)>=128:raise ValueError('Unbounded target minimap path domain')
        record[228:228+len(path)]=path
        read(356,130);read(488,4)
        portals=[bytearray(src.take(288)) for _ in range(struct.unpack_from('<I',record,488)[0])]
        links=[]
        for portal in portals:
            portal[173:237]=nd.take(64)
            links.append(src.take(portal[237]*8))
        read(496,4);mines=src.take(struct.unpack_from('<I',record,496)[0]*96)
        read(504,4);areas=[bytearray(src.take(84)) for _ in range(struct.unpack_from('<I',record,504)[0])]
        for area in areas:area[20:84]=nd.take(64)
        read(512,76)
        rows.append(dict(record=bytes(record),portals=list(map(bytes,portals)),links=links,mines=mines,areas=list(map(bytes,areas)),main_start=start,main_end=src.at))
    layers=[]
    for _ in range(2):
        n,nn=src.u32(),nd.u32();items=[]
        # Target reads, but does not compare, the localized section count.
        for _ in range(n):
            height,width,size=src.u32(),src.u32(),src.u32()
            name=src.take(size)
            if size>32:raise ValueError('Target layer name buffer domain')
            points=[]
            for _ in range(src.u32()):
                fields=bytearray(src.take(16));struct.pack_into('<I',fields,0,struct.unpack_from('<I',fields)[0]|0xff000000);fields=bytes(fields);text=nd.take(nd.u32())
                if len(text)>64:raise ValueError('Target marker text buffer domain')
                points.append(dict(fields=fields,text=text))
            image=src.take(src.u32());items.append(dict(height=height,width=width,name=name,points=points,image=image))
        layers.append(dict(localized_count=nn,items=items))
    return dict(rows=rows,layers=layers,main_consumed=src.at,localized_consumed=nd.at,main_tail=src.take(len(main)-src.at),localized_tail=nd.take(len(localized)-nd.at))
