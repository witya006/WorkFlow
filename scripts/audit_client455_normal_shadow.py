"""Pin shadow target transitions, literals and actual455BOOL callers."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];previous=None;constants=None
    functions=[('begin_shadow',0x91d330,0x286),('end_shadow',0x91d5c0,0x69),('create_texture',0x9335f0,0x74),('avatar_caller',0x51dbe0,0x69),('character_caller',0x51de60,0xd1)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455reference')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in functions]
        data=[read_va(raw,at,4) for at in [0xb397c4,0xaa9720,0xb36b60,0xb373f4]]
        if previous is not None and (previous!=bodies or data!=constants):raise ValueError('Shadow reference differences')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies});previous=bodies;constants=data
    negative,positive,low,high=[struct.unpack('<I',v)[0] for v in constants]
    if struct.unpack('<f',constants[0])[0]!=-30 or struct.unpack('<f',constants[1])[0]!=30:raise ValueError('Changed shadow dimensions')
    quad=[negative,0,positive,0xffffffff,low,low,negative,0,negative,0xffffffff,low,high,positive,0,positive,0xffffffff,high,low,positive,0,negative,0xffffffff,high,high]
    header='#pragma once\n// 91D330 literal four POSITION/DIFFUSE/TEX1 vertices,24bytes each.\nstatic const unsigned RF455_SHADOW_QUAD_BITS[24]={'+','.join(hex(v)+'u' for v in quad)+'};\n'
    destination=WS/'scripts/native/client455_normal_shadow_constants.h';destination.write_text(header)
    report={'scope':'455shadow target begin/end,texture helper and two actual callers;not ground projection or full client acceptance','references':refs,
        'constants':[{'rva':hex(at-0x400000),'bytes':4,'sha256':sha(v)} for at,v in zip([0xb397c4,0xaa9720,0xb36b60,0xb373f4],constants)],
        'quad_bits':quad,'constants_header_sha256':sha(destination.read_bytes()),
        'facts':['Limit20 lazy512x512singlelevel textures,format/usage/pool copied from currentRT;helper accepts HRESULT==0 only','Shared96byte managedVB,usage8/FVF322;lock0/96/0,quad copy then ignoredUnlockHRESULT','GetDepth->GetSurfaceLevel->GetRenderTarget->SetRenderTarget->SetDepthNULL->ReleaseLevel->ClearTarget0->BeginScene->ZFALSE',
        'Begin returns SetDepthStencilSurfaceNULL HRESULT,even though later calls mayfail;S_OK0 isfalse in both455callers','End ZTRUE->EndScene->restoreRT->restoreDS->releaseRT->releaseDS;releasedsavedslots retained at8920/8924'],
        'gaps':['Full failure/uncheckedinvalid-state/unwind/reset behavior not accepted','Original callers skip End when successful begin returns0;retain observed behavior,do not silently change return to1','Ground shadow projection91D630 and full normal actor lifecycle remain open'],
        'script_sha256':sha((WS/'scripts/audit_client455_normal_shadow.py').read_bytes())}
    (WS/'inventory/client455-normal-shadow-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('Pinned shadow begin/end/helper/two callers and quad literals in both455references')
if __name__=='__main__':main()
