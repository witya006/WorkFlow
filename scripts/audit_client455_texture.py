"""Pin recovered Character texture/RFS bodies, XOR key and actual D3DX imports."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from audit_client455_mesh_runtime import import_slots
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    # Boundaries from functions-final.json plus manually disassembled DeleteID.
    # Keep them here so static pin verification does not require an IDA cache.
    functions=[(0x5dfc40,0x69),(0x933540,0x1f),(0x933560,0x18),(0x933580,0x18),
        (0x933670,0x44),(0x9336c0,0x73),(0x933740,0x63),(0x9337b0,0x4c),
        (0x933800,0x188),(0x933de0,0xb2),(0x934120,0x144),(0x934270,0x124),
        (0x9343a0,0x31),(0x9344d0,0xe1),(0x9346d0,0x60),(0x934760,0x5f),
        (0x9347c0,0x1b5),(0x934a20,0x33d),(0x935090,0x106),(0x936950,0x124),
        (0x9379e0,0x8cb),(0x937840,0x138),(0x9382b0,0xed),(0x9345c0,0x67)]
    targets=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];baseline=None
    importsWanted={0xa08026:'D3DXCreateTextureFromFileInMemoryEx',0xa0802c:'D3DXCreateCubeTextureFromFileInMemoryEx',0x854124:'D3DXCreateTextureFromFileA'}
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        if sha(data)!=targets[key]['sha256']:raise ValueError('Pinned455changed')
        image=pe(data);base=image['image_base'];bodies=[read_va(data,va,size) for va,size in functions]
        if baseline is not None and baseline!=bodies:raise ValueError('Texture/RFS bodies differ betweenpins')
        baseline=bodies;slots=import_slots(data);imports=[]
        for va,name in importsWanted.items():
            thunk=read_va(data,va,6)
            if thunk[:2]!=b'\xff\x25':raise ValueError('Texture thunk changed')
            slot=struct.unpack_from('<I',thunk,2)[0]
            if slots[slot]!={'dll':'d3dx9_36.dll','name':name}:raise ValueError('Texture runtime provider mismatch')
            imports.append({'rva':hex(va-base),'iat_rva':hex(slot-base),**slots[slot]})
        xor=read_va(data,0xbf83f0,128)
        if xor!=read_va(data,0xbf7f00,128) or sha(xor)!='ab9397fdafc4f574dc5ae5ced0a8676232e13a118d41dd2837542316ab6246e4':raise ValueError('Character DDS XOR key changed')
        references.append({'sha256':sha(data),'architecture':'x86','image_base':hex(base),'functions':[{'rva':hex(va-base),'size':size,'sha256':sha(body),'bounds':'manual disassembly [9345C0,934627);IDA decompile failed' if va==0x9345c0 else 'cached IDA lookup_funcs'} for (va,size),body in zip(functions,bodies)],'imports':imports,'xor':{'rva':'0x7f83f0','same_as_engine_rva':'0x7f7f00','size':128,'sha256':sha(xor)}})
    dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll');data=dll.read_bytes()
    if sha(data)!='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935':raise ValueError('D3DX provider changed')
    image=pe(data);base=image['image_base'];nt=struct.unpack_from('<I',data,0x3c)[0];rva,size=struct.unpack_from('<II',data,nt+24+96);directory=struct.unpack('<IIHH7I',read_va(data,base+rva,40));exports=[]
    for n in range(directory[7]):
        nameRva=struct.unpack('<I',read_va(data,base+directory[9]+4*n,4))[0];name=read_va(data,base+nameRva,96).split(b'\0',1)[0].decode('ascii')
        if name not in importsWanted.values():continue
        ordinal=struct.unpack('<H',read_va(data,base+directory[10]+2*n,2))[0]
        if ordinal>=directory[6]:raise ValueError('Export ordinal outofbounds')
        entry=struct.unpack('<I',read_va(data,base+directory[8]+4*ordinal,4))[0]
        if rva<=entry<rva+size:raise ValueError('Forwarded texture export')
        exports.append({'name':name,'rva':hex(entry)})
    if len(exports)!=3:raise ValueError('Missing texture exports')
    report={'scope':'Static body/import equality onboth455pins;source matching demonstrated only on the recorded valid domains','references':references,'provider':{'path':str(dll),'sha256':sha(data),'architecture':'x86','preferred_image_base':hex(base),'exports':exports},'confirmed':[
        '288byte manager known fields/272byte entry; borrowed device and getter texture pointers; allocator opaque4/full private STL ABI not certified',
        'Init resets known scalar fields but retains vector; Clear retains capacity,nextID,estimatedBytes; accounting cumulative; dtor does not clear global last-manager pointer',
        'Uppercase ASCII lookup:first vector entry matching exact or alternate.RFT;Add tests full source name before basename; delete uses exact name and deletes all matches',
        'RFS count +64byte index(56name/offset/size),first duplicate wins;directory is negative-cached before opening;RFSINFO whitespace list suppresses DATA0..1023 fallback even if empty;stop first missing DATA',
        '935090 drops first component for relative slash-containing paths;absolute colon+slash copied;uppercases;no full path canonicalization',
        'DDS128 XOR,raw pitch/linear-size mip skipping and width/height<=4 break quirks;maxwidth/height<256 disable skipping;pixel format repair',
        'Custom2D/RFC(oneMip+white color key)/RFT,FileA(original),customRFT again,FileA(RFC),FileA(RFT);flags8 only from first custom load',
        'Cube upload uses separate local and returns still-zero2D local:actual cube orphan+null result preserved;test wrapper releases real orphan after observation',
        'Source provider keeps FILE open through GPU call,close after;missing/zero-length leaves caller cube flag unchanged'
    ],'limits':['No normal full model-loader/shared Character GPU/skeleton/animation integration','Malformed/truncated/OOM/percent strings/nonASCII locale/unsafe format-string and unchecked failure behavior not equivalent;owned bounds errors documented','Original logger/allocator details/global cache teardown/device-reset lifecycle and full private class ABI remain open','Physical tests compare owned preparation with independently generated golden and actual pinnedD3DX exports,not original RF_Online execution'],
    'analysis_sessions':'6117161d expired,subsequent call Session not found;final bounds from a2f02f23 closed/save;9345C0 manually disassembled,decompilation failed;no inputEXE execution','cached_evidence':[{ 'file':p.relative_to(WS).as_posix(),'sha256':sha(p.read_bytes())} for p in sorted((WS/'artifacts/character-texture455').glob('*.json'))]}
    (WS/'inventory/client455-texture-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{len(functions)}matching455body ranges,XOR key,3D3DX9imports/exports')
if __name__=='__main__':main()
