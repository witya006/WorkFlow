"""Pin Character455shared GPU allocation/binding bodies;no runtime parity claim."""
import hashlib,json
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def digest(data):return hashlib.sha256(data).hexdigest()
def main():
    functions=[('find_vertex36',0x93de00,0x78),('upload_vertex36',0x93de80,0x94),('bind_vertex36',0x93df20,0x5d),('find_vertex64',0x93df80,0x78),('upload_vertex64',0x93e000,0x94),('bind_vertex64',0x93e0a0,0x5d),('find_indices',0x93e100,0x75),('upload_indices',0x93e180,0x94),('bind_indices',0x93e220,0x50)]
    fragments=[('mesh08_upload_rebase',0x923590,0x7a)]
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));reports=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if digest(raw)!=pins[key]['sha256']:raise ValueError('Pinned455changed')
        ranges=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':digest(read_va(raw,va,size))} for name,va,size in functions+fragments]
        if baseline is not None and ranges!=baseline:raise ValueError('Shared GPU bodies differ betweenpins')
        baseline=ranges;reports.append({'sha256':digest(raw),'architecture':'x86','image_base':'0x400000','ranges':ranges})
    report={'scope':'Static shared GPU contract research only;source implementation/native GPU test still pending','references':reports,
      'confirmed':{'manager_fields':{'buffers':0,'used_bytes':4096,'entries':1024,'opaque_dword':8192,'borrowed_device':8196},
      'vertex_block_bytes':2300000,'index_block_bytes':1000000,'allocation_failure_sentinel':1025,
      'vertex36_create':{'bytes':2300000,'usage':8,'fvf':278,'pool':1},'vertex64_create':{'bytes':2300000,'usage':8,'fvf':282,'pool':1},'index_create':{'bytes':1000000,'usage':8,'format':101,'pool':1},
      'algorithm':['First of1024slots with uint32(used+requested)<=capacity;create lazily if slot pointer0','Create success increments two global DWORD counters before Lock;Lock(used,size,out,0)','Lock failure returns0 without changing output/used;created buffer and creation counters remain','Copy bytes then Unlock ignoring HRESULT;absoluteOffset=capacity*slot+used;used+=size;return1','Bind uses quotient slot of absolute offset;stream0/buffer/offset0/stride36or64;indices useSetIndices with chosen buffer','Bind skips device0/offsetFFFFFFFF/outside1024;remainder guard mathematically redundant;do not claim meaningful HRESULT for skipped void calls','Mesh08 uploads only when index count nonzero;vertex bytes64*count,then WORDindices +=((vertexAbsolute%2300000)>>6),then index bytes2*count','Mesh08 caller ignores upload return values;constructor field4494/4502 startsFFFFFFFF;failure propagation/partial publication needs full loader audit'],
      'global_accounting_rvas':{'bytes':'0xd89600','buffers':'0xd89604'}},
      'unknowns':['Buffer owner constructor/clear/destructor/reset andopaque DWORD meaning','Exact complete64byte vertex declaration/shader use;FVF282alone does not prove it','Full normal loader publication/failure cleanup/animation/skin/draw domains','Overflow/OOM/zero-size/invalid-state failure equivalence;unsigned wrap confirmed but physical safe domain not yet selected'],
      'evidence':'artifacts/character-gpu455 cacheddecompiles/allocator-insns/gpu-loader-insns/gpu-xrefs;session10003798closed/save;no inputEXE run'}
    (WS/'inventory/client455-shared-buffers-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:9shared buffer bodies+mesh08 upload fragment equalboth455pins;source/GPU validation pending')
if __name__=='__main__':main()
