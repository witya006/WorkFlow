"""Synthetic offline launcher inputs;contains no real accounts or authentication data."""
import hashlib,struct

def encoded_ccr(nation,port=1):
    data=bytearray(93);struct.pack_into('<I',data,0,0x0100007f^0xcb9c4b3a);struct.pack_into('<H',data,4,port^0x4fb6);data[6:6+13]=b'fixture-user\0'
    struct.pack_into('<I',data,57,17^0x6e65e0af)
    for i,mask in enumerate([0xcfcf22e6,0x5bbcde6f,0xacdf5eda,0xbccd1b37]):struct.pack_into('<I',data,61+4*i,(0x10203040+i)^mask)
    struct.pack_into('<H',data,77,3^0x4b3a);struct.pack_into('<I',data,79,17^0xc89c183a);struct.pack_into('<I',data,83,42);struct.pack_into('<I',data,87,1^0xd29c283b);struct.pack_into('<H',data,91,nation^0x32d7)
    if len(data)!=93:raise ValueError('Synthetic launcher size')
    return bytes(data)

def stage_launcher(run,nation,workspace,port=1):
    if nation in [3,7]:
        path=run/'launcher-commandline.txt';path.write_text(f'127.0.0.1 {port} fixture-user fixture-value',encoding='utf-8')
    else:
        path=run/'System/DefaultSet.tmp';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded_ccr(nation,port))
    return {'file':path.relative_to(workspace).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'kind':'synthetic offline launcher fixture;not authentication'}
