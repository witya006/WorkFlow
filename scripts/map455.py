"""Bounded inspection of BSP39/EBP20/R3E113 containers, not a game loader."""
from dataclasses import dataclass
import struct


BSP_NAMES = (['CPlanes','CFaceId','Node','Leaf','MatListInLeaf','Object','Track','EventObjectID']
             + [f'ReadSpare{i}' for i in range(35)]
             + ['BVertex','WVertex','FVertex','VertexColor','UV','LgtUV','Face','FaceId','VertexId','ReadMatGroup']
             + [f'FreeSpare{i}' for i in range(32)])
EBP_NAMES = (['CFVertex','CFLine','CFLineId','CFLeaf','EntityList','EntityID','LeafEntityList','SoundEntityID','LeafSoundEntityList']
             + [f'ReadSpare{i}' for i in range(18)]
             + ['MapEntitiesList','SoundEntityList','SoundEntitiesList']
             + [f'FreeSpare{i}' for i in range(18)])
ENTITY_NAMES = ['CompHeader','Vertex','VColor','UV','Face','FaceId','VertexId','MatGroup','Object','Track']
STRIDES = {'CPlanes':12, 'CFaceId':4, 'Node':24, 'Leaf':25, 'MatListInLeaf':2,
           'Object':88, 'EventObjectID':2, 'BVertex':3, 'WVertex':6, 'FVertex':12,
           'VertexColor':4, 'UV':4, 'LgtUV':4, 'Face':6, 'FaceId':4, 'VertexId':4,
           'ReadMatGroup':42, 'CFVertex':12, 'CFLine':16, 'CFLineId':2,
           'CFLeaf':6, 'EntityList':84, 'EntityID':2, 'LeafEntityList':6,
           'SoundEntityID':2, 'LeafSoundEntityList':4, 'MapEntitiesList':38,
           'SoundEntityList':64, 'SoundEntitiesList':56}


@dataclass(frozen=True)
class Lump:
    name: str
    offset: int
    size: int


class MapFile:
    def __init__(self, data: bytes, kind: str):
        if kind not in ('bsp','ebp','r3e'):
            raise ValueError('Unknown map container kind')
        self.kind = kind
        self.prefix = 8 if kind=='r3e' else 4
        names = {'bsp':BSP_NAMES, 'ebp':EBP_NAMES, 'r3e':ENTITY_NAMES}[kind]
        header_size = self.prefix+8*len(names)
        if len(data) < header_size:
            raise ValueError('Truncated map header')
        if struct.unpack_from('<I',data)[0] != {'bsp':39,'ebp':20,'r3e':113}[kind]:
            raise ValueError('Unsupported map version')
        if kind=='r3e' and struct.unpack_from('<I',data,4)[0]:
            raise ValueError('Particle identity R3E is not a geometry container')
        self.version_bytes = data[:self.prefix]
        self.tail = data[header_size:]
        self.lumps = tuple(Lump(name,*struct.unpack_from('<II',data,self.prefix+i*8)) for i,name in enumerate(names))
        for lump in self.lumps:
            if lump.size and (lump.offset<header_size or lump.offset+lump.size>len(data)):
                raise ValueError(f'{lump.name}: map lump outside file')
            stride = STRIDES.get(lump.name) if kind!='r3e' else {'CompHeader':38,'VColor':4,'UV':4,'Face':6,'FaceId':2,'VertexId':2,'MatGroup':22,'Object':88}.get(lump.name)
            if stride and lump.size%stride:
                raise ValueError(f'{lump.name}: partial record (stride{stride})')
        ranges = sorted((x.offset,x.offset+x.size,x.name) for x in self.lumps if x.size)
        self.declared_overlaps = [(a[2],b[2]) for a,b in zip(ranges,ranges[1:]) if a[1]>b[0]]
        # The real BSP loader reads sequentially, ignoring stored offsets.
        # A supplied Dungeon00 header contains stale overlapping offsets;
        # expose this evidence without silently rewriting the input metadata.

    def read(self, name):
        lump = next(x for x in self.lumps if x.name==name)
        header_size = self.prefix+8*len(self.lumps)
        at = lump.offset-header_size
        return self.tail[at:at+lump.size] if lump.size else b''

    def to_bytes(self):
        return self.version_bytes+b''.join(struct.pack('<II',x.offset,x.size) for x in self.lumps)+self.tail

    def summary(self):
        return [{'name':x.name,'offset':x.offset,'size':x.size,
                 **({'records':x.size//STRIDES[x.name]} if x.name in STRIDES and self.kind!='r3e' else {})}
                for x in self.lumps if x.size]

    def sequential_offset_mismatches(self):
        """Game uses sequential fread for known records, skipping BSP ReadSpare."""
        at = self.prefix+8*len(self.lumps)
        differences = []
        for lump in self.lumps:
            if lump.name.startswith('FreeSpare'):
                break
            if self.kind=='ebp' and lump.name.startswith('ReadSpare'):
                continue
            if lump.size and lump.offset!=at:
                differences.append({'name':lump.name,'declared':lump.offset,'sequential':at})
            at += lump.size
        return differences

    def sequential_end(self):
        at=self.prefix+8*len(self.lumps)
        for lump in self.lumps:
            if lump.name.startswith('FreeSpare'):break
            if self.kind=='ebp' and lump.name.startswith('ReadSpare'):continue
            at+=lump.size
        return at


def inspect_r3t(data, header_mask=None):
    if len(data)<8:
        raise ValueError('Truncated R3T header')
    version,count=struct.unpack_from('<II',data)
    if version not in (0x3f8ccccd,0x3f99999a):
        raise ValueError('Unsupported R3T version')
    at=8+128*count
    if at>len(data):
        raise ValueError('Truncated R3T names')
    images=[]
    for i in range(count):
        if at+4>len(data):raise ValueError('Truncated R3T texture length')
        size=struct.unpack_from('<I',data,at)[0];at+=4
        if size<128 or at+size>len(data):raise ValueError('Invalid R3T DDS range')
        dds=data[at:at+size]
        masked=dds[:4]!=b'DDS '
        if masked:
            if header_mask is None or len(header_mask)!=128:raise ValueError('R3T DDS header mask required')
            dds=bytes(a^b for a,b in zip(dds[:128],header_mask))+dds[128:]
        if dds[:4]!=b'DDS ' or struct.unpack_from('<I',dds,4)[0]!=124:
            raise ValueError('R3T image is not DDS124')
        height,width=struct.unpack_from('<II',dds,12)
        levels=struct.unpack_from('<I',dds,28)[0]
        fourcc=dds[84:88]
        if not width or not height or max(width,height)>16384 or levels>15:
            raise ValueError('Invalid DDS dimensions/levels')
        block={b'DXT1':8,b'DXT3':16,b'DXT5':16}.get(fourcc)
        if block is None:raise ValueError('Unsupported DDS compression')
        expected=128+sum(max(1,((width>>level)+3)//4)*max(1,((height>>level)+3)//4)*block
                         for level in range(max(1,levels)))
        if size!=expected:raise ValueError('DDS mip payload size differs')
        images.append({'size':size,'width':width,'height':height,'masked_header':masked,
                       'mipmap_count':levels,'mipmap_payload_size_verified':True,
                       'fourcc':fourcc.decode('ascii')})
        at+=size
    if at!=len(data):raise ValueError('R3T trailing bytes')
    return {'version':struct.unpack('<f',struct.pack('<I',version))[0],'textures':images}
