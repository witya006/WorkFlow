"""Pin EFF conversion/application/particle contracts and real format samples."""
import hashlib,json,struct
from pathlib import Path
from fractions import Fraction as F
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_client455_animation_timing import binary_round

def sha(raw):return hashlib.sha256(raw).hexdigest()
def decoded(raw):
    records=[];at=0
    while at<len(raw):
        if len(raw)-at<2:raise ValueError('short size')
        size=struct.unpack_from('<H',raw,at)[0]
        if not 2<=size<=176 or size>len(raw)-at:raise ValueError('invalid record length')
        padded=bytearray(176);struct.pack_into('<HB',padded,0,176,2);padded[:size]=raw[at:at+size]
        if any(0 not in padded[start:] for start in [3,23,43,152]):raise ValueError('name escapes176byte record')
        records.append(bytes(padded));at+=size
    return records
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];previous=None;constants=None
    functions=[('read_eff',0x92b380,0x31f),('convert176',0x929070,0x161),('construct292',0x920e40,0xde),('apply_record',0x927040,0x1bd),('apply_file',0x9293d0,0x84),('apply_filter',0x9281a0,0x198),('reset_mesh',0x91c760,0x2c),('reset_model',0x91f2b0,0x4d),('has_mesh_particles',0x91c6d0,0x34),('has_model_particles',0x91fc00,0x3c),('mon_list_add',0x92cb70,0xb5),('item_list_add',0x92cc30,0xc0),('mon_list_read',0x92cd60,0x133),('item_list_read',0x92cea0,0x117),('animus_caller',0x4572d0,0x4f)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455reference')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in functions]
        # Only selected particle indirection fragments,not its full emitter math.
        fragments=[{'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for at,n in [(0x7bc9b0,0x81),(0x7bcef8,0x91),(0x7bd099,0x7c)]]
        data=[read_va(raw,at,8) for at in [0xb292f8,0xb3a8c0,0xb3a8b8,0xb3a8b0]]
        if previous is not None and (previous!=bodies or data!=constants or fragments!=refs[0]['particle_fragments']):raise ValueError('EFF ranges/literals differ')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'particle_fragments':fragments});previous=bodies;constants=data
    names=['UNIT','RATE','EPSILON','MAX'];header='#pragma once\n// Exact double operands used by927040 x87 factor conversion.\n'+''.join('static const unsigned long long RF455_EFFECT_'+name+'_BITS='+hex(struct.unpack('<Q',data)[0])+'ull;\n' for name,data in zip(names,constants));destination=WS/'scripts/native/client455_effect_constants.h';destination.write_text(header)
    unit,rate,epsilon,maximum=[F(struct.unpack('<d',v)[0]) for v in constants];golden=bytearray(b'EFM1');cases=[]
    for precision in [24,53,64]:
        for mode in range(4):
            rounded=lambda v:binary_round(v,precision,mode)
            for grade,intensity in [(0,0),(1,0),(8,0),(9,0),(35,0),(-1,0),(2147483647,0),(36,0),(36,.25),(36,1),(36,-.5)]:
                intensity=struct.unpack('<f',struct.pack('<f',intensity))[0]
                value=rounded(rounded(F(intensity)-epsilon)*maximum) if grade==36 else rounded(rounded(F(grade)*unit)*rate)
                cases.append((precision,mode,grade,intensity,int(value)&0xffffffff))
    golden+=struct.pack('<I',len(cases))+b''.join(struct.pack('<IIifI',*row) for row in cases)
    stage=WS/'work/client-reference/eff455';stage.mkdir(parents=True,exist_ok=True);(stage/'factors.bin').write_bytes(golden)
    root=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'CHEF';files=[];invalid=[];sizes={};recordCount=0;candidates=[];seen=set()
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower()!='.eff':continue
        raw=path.read_bytes()
        try:records=decoded(raw)
        except ValueError as error:invalid.append({'file':str(path),'sha256':sha(raw),'reason':str(error)});continue
        recordCount+=len(records)
        for r in records:
            size=struct.unpack_from('<H',r)[0];sizes[str(size)]=sizes.get(str(size),0)+1
        digest=sha(raw)
        if records and digest not in seen:
            seen.add(digest);candidates.append((path,raw,records))
    chosen=candidates[:10]
    chosen+=[row for row in candidates if any(struct.unpack_from('<H',r)[0]==172 for r in row[2])][:2]
    for path,raw,records in chosen:
        copy=stage/f'real_{len(files):02d}.eff';copy.write_bytes(raw);files.append({'original':str(path),'copy':copy.relative_to(WS).as_posix(),'sha256':sha(raw),'records':len(records)})
    manifest=stage/'inputs.txt';manifest.write_text(''.join(str(WS/row['copy'])+'\n' for row in files))
    report={'scope':'Pinned EFF176->numeric292 conversion,registry/application/reset and selected particle indirections;not complete emitter/frame/game acceptance','references':refs,
        'constants':[{'rva':hex(at-0x400000),'bytes':8,'sha256':sha(v)} for at,v in zip([0xb292f8,0xb3a8c0,0xb3a8b8,0xb3a8b0],constants)],'constants_header_sha256':sha(destination.read_bytes()),
        'factor_golden':(stage/'factors.bin').relative_to(WS).as_posix(),'factor_golden_sha256':sha(golden),'factor_cases':len(cases),'fp_modes':12,
        'valid_real_files_records':recordCount,'record_sizes':sizes,'unparsed_files':invalid,'files':files,'fixture':manifest.relative_to(WS).as_posix(),'fixture_sha256':sha(manifest.read_bytes()),
        'facts':['Loose EFF concatenates WORD-sized records,padded to176/type2;byte2 not checked. String starts:tex1+3,tex2+23,directory+43,meshfilter+152;strlen can cross20byte field boundaries',
        'Runtime292 numeric156..204,particle208/224/240,entity256,frequency288;mesh current effect5455 supplies slot views. File/filter names are own modern source storage',
        'Lookup exact filename then ordered uppercase meshfilter;empty filter applies all,matching filter canoverride it. Duplicate file/filter record replaced;reload retains other filters',
        'Apply caches texture pointers120/124/attempt56/60;cached branch doesnotwrite mesh texture IDs. Grade36 uses intensity-epsilon times UINTMAX;other signedgrade uses 2^32*rate,then truncate signed64/lowDWORD',
        'Init resets hidden5567/alpha5131/secondary textures/IDs then applies inline5163. HasEffect tests3particle IDs andentity,not render-material predicate91C710','Animus4572D0 passes36 to ApplyFile;MAX_PATTERN_SIZE normal facade updated accordingly'],
        'gaps':['Bounded malformed/short/overlong-name/OOM policies differ from original unchecked copies/UI/loops','Numeric draw view doesnot reproduce private classic STL bytes;known strings live in source-owned std::strings. Untouched opaque bytes seeded0,notoriginal undefined stack parity','Full particle/entity consumers include more math/flags than proven slot mapping;normal gameplay/effect lifecycle and full acceptance open','Original pattern tail grades9..35 remains explicitly unknown;no false zero fallback'],
        'script_sha256':sha(Path(__file__).read_bytes())}
    (WS/'inventory/client455-effects-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'sample_files':len(files),'records':recordCount,'sizes':sizes,'unparsed':len(invalid),'factor_cases':len(cases)}))
if __name__=='__main__':main()
