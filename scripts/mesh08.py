"""455 MESH08 lossless framing. Runtime material/GPU/bone resolution is separate.

The original loader has no input length. This tooling checks boundaries and reports
errors instead of reproducing access violations; that is not malformed-input parity.
"""
from dataclasses import dataclass
import struct

MAGIC=b'MESH08'
HEADER_BYTES=693
VERTEX_BYTES=64
BONE_BYTES=404
INDEX_LIMIT=64000

class Mesh08Error(ValueError):pass

@dataclass(frozen=True)
class Mesh08Part:
    offset:int
    header:bytes
    vertices:bytes
    indices:bytes
    bones:bytes
    vertex_count:int
    index_count:int
    bone_count:int
    @property
    def name(self):return self.header[:100].split(b'\0',1)[0]
    @property
    def parent_name(self):return self.header[100:200].split(b'\0',1)[0]
    @property
    def primary_texture(self):return self.header[398:498].split(b'\0',1)[0]
    @property
    def secondary_texture(self):return self.header[498:598].split(b'\0',1)[0]
    @property
    def vertex_offset(self):return self.offset+HEADER_BYTES+2
    @property
    def index_offset(self):return self.vertex_offset+len(self.vertices)+2
    @property
    def bone_offset(self):return self.index_offset+len(self.indices)+2
    def encode(self):
        if len(self.header)!=HEADER_BYTES or len(self.vertices)!=self.vertex_count*VERTEX_BYTES or len(self.indices)!=self.index_count*2 or len(self.bones)!=self.bone_count*BONE_BYTES:raise Mesh08Error('Inconsistent MESH08 part storage')
        return b''.join((self.header,struct.pack('<H',self.vertex_count),self.vertices,struct.pack('<H',self.index_count),self.indices,struct.pack('<H',self.bone_count),self.bones))

@dataclass(frozen=True)
class Mesh08:
    parts:tuple[Mesh08Part,...]
    consumed:int
    trailing:bytes
    def encode(self):return MAGIC+struct.pack('<H',len(self.parts))+b''.join(p.encode() for p in self.parts)+self.trailing

def decode(data:bytes,*,enforce_index_limit:bool=True)->Mesh08:
    data=bytes(data)
    if len(data)<8:raise Mesh08Error('Short MESH08 header')
    if data[:6]!=MAGIC:raise Mesh08Error('MESH08 magic mismatch')
    count=struct.unpack_from('<H',data,6)[0];at=8;parts=[]
    if count>(len(data)-8)//(HEADER_BYTES+6):raise Mesh08Error('Short MESH08 record table')
    def take(size):
        nonlocal at
        if size>len(data)-at:raise Mesh08Error(f'Short MESH08 payload at{at},wanted{size}')
        value=data[at:at+size];at+=size;return value
    def word():return struct.unpack('<H',take(2))[0]
    for _ in range(count):
        offset=at;header=take(HEADER_BYTES);vertices_count=word();vertices=take(vertices_count*VERTEX_BYTES)
        index_count=word()
        if enforce_index_limit and index_count>INDEX_LIMIT:raise Mesh08Error('MESH08 index count exceeds455limit64000')
        indices=take(2*index_count);bone_count=word();bones=take(BONE_BYTES*bone_count)
        parts.append(Mesh08Part(offset,header,vertices,indices,bones,vertices_count,index_count,bone_count))
    return Mesh08(tuple(parts),at,data[at:])

def describe(model:Mesh08):
    parts=[]
    for part in model.parts:
        indexes=struct.unpack('<'+'H'*part.index_count,part.indices) if part.indices else ()
        influences=[struct.unpack_from('<I',part.bones,BONE_BYTES*n)[0] for n in range(part.bone_count)]
        parts.append({'offset':part.offset,'name_hex':part.name.hex(),'vertex_offset':part.vertex_offset,'index_offset':part.index_offset,'bone_offset':part.bone_offset,
            'vertex_count':part.vertex_count,'index_count':part.index_count,'bone_record_count':part.bone_count,
            'max_index':max(indexes,default=None),'out_of_range_indices':sum(n>=part.vertex_count for n in indexes),
            'index_remainder3':part.index_count%3,'max_record_influences':max(influences,default=0),'influence_count_over4':sum(n>4 for n in influences)})
    return {'meshes':len(model.parts),'consumed':model.consumed,'trailing_bytes':len(model.trailing),'vertices':sum(p.vertex_count for p in model.parts),
        'indices':sum(p.index_count for p in model.parts),'bone_records':sum(p.bone_count for p in model.parts),'parts':parts}
