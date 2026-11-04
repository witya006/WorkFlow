"""Pin Character455mesh destruction,array deletion andMESH08publication contract."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    functions=[('mesh_ctor',0x9214e0,0x1c2),('mesh_dtor',0x920fd0,0xd2),('tables_dtor',0x91c3c0,0x51),('strings_dtor',0x920f20,0xa8),('deleting_dtor',0x921480,0x55),('array_dtor_iterator',0x87284c,0x63),('manager_delete_name',0x921960,0xe7),('manager_delete_id',0x921a50,0xb5),('manager_clear',0x921bc0,0x97),('mesh08_loader',0x922a00,0xe9b)]
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));reports=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(raw)!=target[key]['sha256']:raise ValueError('Pinned455changed')
        ranges=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in functions]
        if baseline is not None and ranges!=baseline:raise ValueError('Model lifetime bodies differ betweenpins')
        baseline=ranges;thunks=[]
        for va in [0x8745ba,0x871e91]:
            code=read_va(raw,va,5)
            if code[0]!=0xe9:raise ValueError('Unexpected free thunk')
            destination=va+5+struct.unpack_from('<i',code,1)[0];thunks.append({'rva':hex(va-0x400000),'target_rva':hex(destination-0x400000),'bytes':code.hex()})
        if int(thunks[0]['target_rva'],16)!=0x471e91:raise ValueError('Free families no longer share a provider')
        reports.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':ranges,'free_thunks':thunks})
    report={'scope':'Static lifetime/publication contract;source/native implementation evidence separate','references':reports,'confirmed':[
        '5803byte mesh destructor:Release4486/4490 without nulling;free+null5095/5099/4506;tables5595 thenstrings5163',
        'Tables:20interleaved pointer pairs(+4i,+80+4i),free+null each,then whole168byteszero',
        'Strings:reverse offsets132,96,68,32,4;capacity>=16 free data pointer;cap15/len0/firstbyte0 only,other bytes retained',
        'Array allocation DWORDcookie+5803count;vector dtor runs last tofirst;flags2array/flags1free;free basecookie forarray;cookie count authoritative',
        'Manager delete paths guard model ownsDWORD260 andnonnullmeshptr536;destroyarray/freecookie/clear536,thenfreemodel;count532 not reset',
        'Mesh08valid flow:construct all→materials/header/GPUperpart→copybone scratch→clearparentflag→local thenexternal binding→bone resolution→freebone scratch→publish536then532',
        'Existing array is not freed by922A00 before overwriting model fields;caller owns repeated-load policy;special model flag796 onlyset'
    ],'limits':['Raw model view knownminimum800bytes is not fullObjectData ABI','Own checked parser/errors/nullallocation cleanup differ fromunchecked AV/debugbreak/OOM/exception unwind','MemoryOps owns modern allocations;do not free unrelated binarySDK allocations with modern CRT;old heap ABI not certified','Normal model-manager/file dispatcher/BN/skeleton/animation/shaders/full renderer lifecycle still open','No input EXE execution;copied IDB50804ce1closed/save;rawartifacts/character-model455']}
    (WS/'inventory/client455-models-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:10mesh/model lifetime+loader bodies equalbothpins;free thunks share provider')
if __name__=='__main__':main()
