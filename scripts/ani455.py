"""Bounded lossless ANI framing from455's93C1F0/93AE20;no animation math yet."""
from dataclasses import dataclass
import struct

STRIDES=(20,16,16,8)
class AniError(ValueError):pass
@dataclass(frozen=True)
class AniTrack:
    offset:int
    header:bytes
    counts:tuple
    key_offsets:tuple
    keys:tuple
    @property
    def name(self):return self.header[:100].split(b'\0',1)[0]
    @property
    def enabled(self):return struct.unpack_from('<H',self.header,100)[0]
    @property
    def maximum(self):return struct.unpack_from('<H',self.header,102)[0]
    def encode(self):return self.header+b''.join(struct.pack('<H',n)+key for n,key in zip(self.counts,self.keys))
@dataclass(frozen=True)
class Ani:
    prefix:bytes
    tracks:tuple
    consumed:int
    trailing:bytes
    @property
    def maximum(self):return max((t.maximum for t in self.tracks),default=0)
    def encode(self):return self.prefix+b''.join(t.encode() for t in self.tracks)+self.trailing

def decode(raw):
    raw=bytes(raw)
    if not raw:raise AniError('Missing count byte')
    count=raw[0];at=2;tracks=[]
    def take(n):
        nonlocal at
        if at>len(raw) or n>len(raw)-at:raise AniError(f'Short ANI at{at},wanted{n}')
        b=raw[at:at+n];at+=n;return b
    for _ in range(count):
        start=at;header=take(140);counts=[];offsets=[];keys=[]
        for stride in STRIDES:
            n=struct.unpack('<H',take(2))[0];counts.append(n);offsets.append(at);keys.append(take(n*stride))
        tracks.append(AniTrack(start,header,tuple(counts),tuple(offsets),tuple(keys)))
    return Ani(raw[:2],tuple(tracks),at,raw[at:])
