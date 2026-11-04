"""Bounded Character455RFS framing and DDS preparation,independent fixture tooling."""
from dataclasses import dataclass
import struct

class CharacterTextureError(ValueError):pass
@dataclass(frozen=True)
class RfsEntry:
    raw_name:bytes
    offset:int
    size:int
    @property
    def name(self):return self.raw_name.split(b'\0',1)[0]
@dataclass(frozen=True)
class Rfs:
    entries:tuple[RfsEntry,...]
    payload:bytes
    def encode(self):
        if any(len(e.raw_name)!=56 or b'\0' not in e.raw_name for e in self.entries):raise CharacterTextureError('Invalid RFSname storage')
        return struct.pack('<I',len(self.entries))+b''.join(e.raw_name+struct.pack('<II',e.offset,e.size) for e in self.entries)+self.payload
    def member(self,index):
        e=self.entries[index];base=4+64*len(self.entries)
        if e.offset<base or e.offset+e.size>base+len(self.payload):raise CharacterTextureError('RFS member outside payload')
        return self.payload[e.offset-base:e.offset-base+e.size]
def parse_rfs(raw):
    if len(raw)<4:raise CharacterTextureError('Short RFScount')
    count=struct.unpack_from('<I',raw)[0]
    if count>(len(raw)-4)//64:raise CharacterTextureError('Short RFSindex')
    entries=[]
    for n in range(count):
        at=4+64*n;name=raw[at:at+56]
        if b'\0' not in name:raise CharacterTextureError('Unterminated RFSname')
        offset,size=struct.unpack_from('<II',raw,at+56);entries.append(RfsEntry(name,offset,size))
    return Rfs(tuple(entries),raw[4+64*count:])
def prepare_dds(raw,key,mip_skip=0,max_width=2048,max_height=2048):
    if len(raw)<128 or len(key)!=128:raise CharacterTextureError('Short DDS/header key')
    head=bytearray(raw[:128])
    if head[:4]!=b'DDS ':head=bytearray(a^b for a,b in zip(head,key))
    if head[:4]!=b'DDS ':raise CharacterTextureError('Not plain/masked DDS')
    values=list(struct.unpack('<32I',head));cube=bool(values[28]&0x200);skip=0
    if values[7] and max_width>=256 and max_height>=256:
        i=0
        while i<mip_skip or values[4]>max_width or values[3]>max_height:
            if i>=values[7]:break
            size=values[5];skip=(skip+size)&0xffffffff
            if values[3]<=4:break
            values[3]>>=1
            if values[4]<=4:break
            values[4]>>=1;values[5]=size//4;i+=1
        values[7]=(values[7]-i)&0xffffffff
    if skip>len(raw)-128:raise CharacterTextureError('Mip skip exceeds data')
    if values[20]==5:values[20]=4
    elif values[20]==65:
        if values[22]==16:
            if values[26]!=0x8000:values[23]=3840
        elif values[22]==32:values[23:27]=[0xff0000,65280,255,0xff000000]
    if not values[19]:values[19]=32;values[20]=4
    return {'bytes':struct.pack('<32I',*values)+raw[128+skip:],'skip':skip,'width':values[4],'height':values[3],'cube':cube}
def synthetic_dds(width=4,height=4,mips=1,cube=False,pixel=bytes([0,0,255,255])):
    fields=[0]*32;fields[0]=0x20534444;fields[1]=124;fields[2]=0x2100f;fields[3]=height;fields[4]=width;fields[5]=width*4;fields[7]=mips
    fields[19]=32;fields[20]=65;fields[22]=32;fields[23:27]=[0xff0000,65280,255,0xff000000];fields[27]=0x401008 if mips>1 else 0x1000;fields[28]=0xfe00 if cube else 0
    payload=bytearray()
    for _ in range(6 if cube else 1):
        for n in range(mips):payload+=pixel*max(1,width>>n)*max(1,height>>n)
    return struct.pack('<32I',*fields)+payload
def make_rfs(items):
    entries=[];payload=bytearray();base=4+64*len(items)
    for name,data in items:
        if len(name)>=56 or b'\0' in name:raise CharacterTextureError('Fixture RFSname too long')
        entries.append(RfsEntry(name.ljust(56,b'\0'),base+len(payload),len(data)));payload+=data
    return Rfs(tuple(entries),bytes(payload)).encode()
