"""Port actual normal client consumers into a separate455-only source tree.

No CharacterMR link or fake method bodies. Open methods remain unresolved at link.
Engine033 and the diagnostic baseline are preserved byte-for-byte.
"""
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from compare_client_binaries import WS
from client455_d3d9_port import ENGINE_DEFINITIONS
from audit_client455_normal_character_api import code_only

def sha(data):return hashlib.sha256(data).hexdigest()
def write_owned(path,raw,previous):
    if path.exists() and path.read_bytes()!=raw and sha(path.read_bytes())!=previous.get(path.relative_to(WS).as_posix()):
        raise ValueError('Preserving differing normal port file:'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or path.read_bytes()!=raw:path.write_bytes(raw)

def section(raw,first,last):
    masked=code_only(raw);start=masked.index(first);at=masked.index(b'{',masked.index(last,start));depth=1;end=at+1
    while depth:
        if end>=len(raw):raise ValueError('Unterminated source function')
        depth+=(masked[end]==ord('{'))-(masked[end]==ord('}'));end+=1
    return start,end

def main():
    port=WS/'work/client455-port';root=port/'normal';native=WS/'scripts/native';art=WS/'artifacts/client455-normal';art.mkdir(parents=True,exist_ok=True)
    manifest=art/'sources.json';previous={r['file']:r['sha256'] for r in json.loads(manifest.read_text())} if manifest.exists() else {};records=[]
    def save(path,raw,source=None,changes=None):
        write_owned(path,raw,previous);row={'file':path.relative_to(WS).as_posix(),'sha256':sha(raw)}
        if source:row.update(input=source.relative_to(WS).as_posix(),input_sha256=sha(source.read_bytes()))
        if changes:row['changes']=changes
        records.append(row)
    # Keep the kernel type names/allocations unchanged. Add named confirmed
    # fields only to the normal port headers, leaving all existing evidence valid.
    replacements={
        'client455_mesh_bindings.h':(rb'struct RF455MeshStorage \{ unsigned char bytes\[5803\]; \};','client455_normal_mesh.inc'),
        'client455_character_manager.h':(rb'struct RF455CharacterStorage \{RF455KnownModelPrefix prefix;unsigned char tail\[388\];\};','client455_normal_model.inc'),
        'client455_animation.h':(rb'struct RF455AnimationStorage \{unsigned char bytes\[284\];\};','client455_normal_animation.inc')}
    for source in sorted(native.glob('*.h')):
        raw=source.read_bytes();changes=[]
        if source.name in replacements:
            pattern,filename=replacements[source.name];replacement=(native/filename).read_bytes()
            if source.name=='client455_animation.h':replacement=b'struct RF455AnimationData;\n'+replacement
            raw,count=re.subn(pattern,lambda _:replacement,raw)
            if count!=1:raise ValueError('Record definition changed:'+source.name)
            raw=b'#include <d3dx9.h>\n'+raw;changes=[filename]
        save(root/'include'/source.name,raw,source,changes)
    save(root/'include/Character.h',(native/'Character455.h').read_bytes(),native/'Character455.h')
    split_units=[]
    for source in sorted((port/'source/RF_Client').rglob('*')):
        if not source.is_file():continue
        if source.suffix.lower() in ['.lib','.dsp','.dsw']:continue
        raw=source.read_bytes();changes=[]
        if source.suffix.lower() in ['.cpp','.h']:
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='addcodebyyun/particlelist.cpp':
                old=b'pd3dDevice->CopyRects(backbuf,&r,1,psurface[count],&pt)'
                if raw.count(old)!=1:raise ValueError('Screenshot readback call changed')
                raw=raw.replace(old,b'pd3dDevice->GetRenderTargetData(backbuf,psurface[count])')
                old=b'Desc.Format, D3DPOOL_SCRATCH, &psurface[i], NULL'
                if raw.count(old)!=1:raise ValueError('Screenshot readback surface changed')
                raw=raw.replace(old,b'Desc.Format, D3DPOOL_SYSTEMMEM, &psurface[i], NULL')
                changes.append('D3D9 full-render-target readback into SYSTEMMEM')
            raw,n=re.subn(rb'\b(?:class|struct)\s+(CHARACTEROBJECT|ChAnimation|ObjectMesh)\s*;',b'',raw)
            if n:changes.append('replace legacy forward declarations with455type aliases')
            raw,n=re.subn(rb'\b(?:class|struct)\s+(CHARACTEROBJECT|ChAnimation|ObjectMesh)\b',rb'\1',raw)
            if n:changes.append('remove elaborated legacy type names')
            raw,n=re.subn(rb'\.m_ParticleID\b',b'.particleSlots()',raw)
            if n:changes.append('open455particle slot contract')
            raw,n=re.subn(rb'(\bpMesh\[[^\]\r\n]+\])\.m_Entity\b',rb'\1.entitySlot()',raw)
            if n:changes.append('open455entity slot contract')
            # Production modularization, not a test-only copy: the identical
            # methods are removed from their original TU and compiled once here.
            if source.name.lower() in ['global.cpp','cresobject.cpp']:
                unity=source.name.lower()=='global.cpp'
                first=b'CUnityBoneMgr::CUnityBoneMgr()' if unity else b'CAnimation::CAnimation()'
                last=b'_DestroyAnimationMgr( void )' if unity else b'CAnimation::GetRemainEffectFrameNum( void )'
                start,end=section(raw,first,last);body=raw[start:end]
                generated=b'#include "cresobject.h"\n#include "global.h"\n'
                if not unity:generated+=b'#include "client455_animation_timing.h"\n'
                if unity:
                    match=re.search(rb'ChInterface \*\s*g_ifCharIF\s*= NULL;',raw)
                    if not match:raise ValueError('Normal renderer global definition changed')
                    generated+=match[0]+b'\n'
                    # Remove after taking the section, to retain the offsets.
                generated+=body+b'\n';name='unity_managers.cpp' if unity else 'animation_control.cpp'
                destination=root/'generated'/name;save(destination,generated,source,['unchanged production function bodies extracted to separate TU']);split_units.append(destination)
                raw=raw[:start]+b'// Implementations moved to generated/'+name.encode()+b'.\n'+raw[end:]
                if unity:raw=raw[:match.start()]+b'// g_ifCharIF is defined in unity_managers.cpp'+raw[match.end():]
                changes.append('production TU split; extracted method bytes unchanged')
        save(root/'source'/source.relative_to(port/'source/RF_Client'),raw,source,changes)
    tree=ET.parse(WS/'work/client-build/build-character-diagnostic/RF_Online.vcxproj');units=[]
    for node in tree.iter():
        if node.tag.rsplit('}',1)[-1]=='ClCompile' and 'Include' in node.attrib:
            source=Path(node.attrib['Include']);base=WS/'work/client-build/source/RF_Client'
            if source.is_relative_to(base):units.append(root/'source'/source.relative_to(base))
            else:
                target=root/'generated'/source.name;save(target,source.read_bytes(),source);units.append(target)
    if len(units)!=180:raise ValueError('Normal source set changed')
    units+=split_units
    sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());engine=port/'source/R3Engine'
    directories=[root/'include',root/'source',engine,engine/'extension',engine/'1stclass',engine/'2ndclass',engine/'common',engine/'d3d/include',WS/sdk['include'],native]
    flags=sorted(set(ENGINE_DEFINITIONS+['WIN32','_WINDOWS','_NEW_UI_','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION','RF_CLIENT_455_FRUSTUM']))
    cmake='cmake_minimum_required(VERSION 3.24)\nproject(RFNormal455 LANGUAGES CXX)\nif(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)\nmessage(FATAL_ERROR "MSVC x86 required")\nendif()\nadd_library(RFClient455Consumers OBJECT\n'+''.join(' "'+p.as_posix()+'"\n' for p in units)+')\n'
    cmake+='target_include_directories(RFClient455Consumers PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\n'
    cmake+='target_compile_definitions(RFClient455Consumers PRIVATE '+' '.join(flags)+')\ntarget_compile_options(RFClient455Consumers PRIVATE /W3 /O2 /Gy /EHsc /Zc:forScope- /MP4 "/FI'+(port/'port_std.hpp').as_posix()+'")\nset_target_properties(RFClient455Consumers PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    source=native/'client455_normal_facade.cpp';facade=root/'generated'/source.name;save(facade,source.read_bytes(),source)
    cmake+='add_library(RFClient455Facade STATIC "'+facade.as_posix()+'")\ntarget_include_directories(RFClient455Facade PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\ntarget_compile_options(RFClient455Facade PRIVATE /W3 /O2 /Gy /EHsc)\nset_target_properties(RFClient455Facade PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    save(root/'CMakeLists.txt',cmake.encode());manifest.write_text(json.dumps(records,indent=2)+'\n')
    report={'scope':'Actual180original client sources plus2production TU splits against455records/D3D9;open methods remain undefined','original_sources':180,'sources':len(units),'manifest':manifest.relative_to(WS).as_posix(),'manifest_sha256':sha(manifest.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'record_inputs':{name:sha((native/name).read_bytes()) for name in ['Character455.h','client455_normal_model.inc','client455_normal_mesh.inc','client455_normal_animation.inc','client455_normal_facade.cpp']},'legacy_character_linked':False,'baseline_modified':False,'engine033_modified':False}
    (WS/'inventory/client455-normal-preparation.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared180originalsources+2production splits;no legacy Character library')
if __name__=='__main__':main()
