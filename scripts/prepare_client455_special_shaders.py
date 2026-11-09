"""Pin the actual binary shader list and its four single-stage source files."""
import json,struct,re,shutil
from pathlib import Path
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import require,sha
from audit_client455_item_payloads import record
from shader455 import key,xor


def parse_init(data):
    at=0
    def take(n):
        nonlocal at
        if n<0 or at+n>len(data):raise ValueError('Truncated binary shader list')
        value=data[at:at+n];at+=n;return value
    def count(limit):
        n=struct.unpack('<i',take(4))[0]
        if not 0<=n<=limit:raise ValueError('Shader list outside table capacity')
        return n
    def string(n):
        raw=take(n)
        if b'\0' not in raw:raise ValueError('Unterminated shader-list string')
        return raw.split(b'\0',1)[0].decode('ascii')
    path=string(256);fx=[string(256) for _ in range(count(128))];stages=[]
    for kind in ['vertex','pixel']:
        stages.extend(dict(kind=kind,name=string(256),profile=string(32)) for _ in range(count(128)))
    objects=[]
    for _ in range(count(128)):
        vertex,pixel=struct.unpack('<ii',take(8));parameters=[take(196).hex() for _ in range(count(10))]
        objects.append(dict(vertex=vertex,pixel=pixel,parameters=parameters))
    if at!=len(data):raise ValueError('Trailing binary shader-list bytes')
    return dict(path=path,effects=fx,stages=stages,objects=objects,bytes=at)


def main():
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);source=client/'System/Shader';root=WS/'work/client-reference/special-shaders455';root.mkdir(parents=True,exist_ok=True)
    mask=key();header=(WS/'scripts/native/client455_shader_key.h').read_text();encoded=bytes(int(x,16) for x in re.findall(r'0x([0-9a-f]{2})',header));require(encoded==mask,'Reuse the verified Character key')
    parsed=parse_init((source/'init.r3o').read_bytes());require(len(parsed['stages'])==4 and not parsed['effects'] and not parsed['objects'],'Actual455 init.r3o2VS/2PS/0FX/0objects')
    inputs=[];programs=[]
    for name in ['init.r3o']+[Path(x['name']).stem+'.sho' for x in parsed['stages']]:
        original=source/name;dest=root/name
        if dest.exists():require(sha(dest)==sha(original),'Immutable pinned shader copy')
        else:shutil.copyfile(original,dest)
        inputs.append(dict(**record(dest),original=str(original),runtime_relative='System/shader/'+name))
        if name.endswith('.sho'):
            plain=xor(dest.read_bytes(),mask);require(xor(plain,mask)==dest.read_bytes() and b'main' in plain,'Actual shader XOR round trip')
            decoded=root/(Path(name).stem+'.hlsl');decoded.write_bytes(plain);programs.append(dict(name=name,decoded=record(decoded),encrypted=record(dest)))
    output=dict(scope='Actual455 special-material binary shader inputs;not Character shaders',script=record(Path(__file__)),decoder=record(WS/'scripts/shader455.py'),key_header=record(WS/'scripts/native/client455_shader_key.h'),init=parsed,inputs=inputs,programs=programs)
    (WS/'inventory/client455-special-shaders-inputs.json').write_text(json.dumps(output,indent=2)+'\n');print('Pinned2VS/2PS/zero FX/zero serialized objects;',parsed['bytes'],'bytes')


if __name__=='__main__':main()
