"""Read/manifest selected installed assets,including their actual RFS owners."""
import hashlib,struct
from pathlib import Path

class ResourceInputs:
    def __init__(self,client):
        self.client=Path(client).resolve();self.inputs={};self.archives={};self.members=[];self.missing=set()
    def add(self,path):
        path=Path(path).resolve();assert path.is_relative_to(self.client) and path.is_file()
        relative=path.relative_to(self.client).as_posix()
        if relative not in self.inputs:
            self.inputs[relative]=dict(original=str(path),relative=relative,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    def read(self,path):
        path=Path(path).resolve();assert path.is_relative_to(self.client)
        if path.is_file():self.add(path);return path.read_bytes()
        directory=path.parent
        if directory not in self.archives:
            info=directory/'RFSINFO.DAT';names=info.read_text(encoding='ascii').split() if info.is_file() else []
            if not names:
                for index in range(1024):
                    archive=directory/f'DATA{index}.RFS'
                    if not archive.is_file():break
                    names.append(archive.name)
            table={}
            for name in names:
                archive=(directory/name).resolve();assert archive.is_relative_to(self.client)
                if not archive.is_file():continue
                with archive.open('rb') as source:
                    header=source.read(4);assert len(header)==4;count=struct.unpack('<I',header)[0]
                    assert count<=(archive.stat().st_size-4)//64
                    for _ in range(count):
                        row=source.read(64);assert len(row)==64 and b'\0' in row[:56]
                        offset,size=struct.unpack_from('<II',row,56);assert offset+size<=archive.stat().st_size
                        table.setdefault(row[:56].split(b'\0')[0].lower(),(archive,offset,size))
            self.archives[directory]=(info,table)
        info,table=self.archives[directory];member=table.get(path.name.encode('ascii').lower())
        if not member:self.missing.add(path.relative_to(self.client).as_posix());return None
        archive,offset,size=member;self.add(archive)
        if info.is_file():self.add(info)
        with archive.open('rb') as source:source.seek(offset);data=source.read(size)
        assert len(data)==size;self.members.append(dict(file=path.relative_to(self.client).as_posix(),archive=archive.relative_to(self.client).as_posix(),offset=offset,bytes=size))
        return data
