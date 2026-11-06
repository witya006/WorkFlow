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

def kernel_sources(native):
    owner=json.loads((WS/'inventory/client455-renderer-owner-build.json').read_text())
    animation=json.loads((WS/'inventory/client455-animation-manager-build.json').read_text())
    wanted={owner['library']:owner['library_sha256'],animation['library']:animation['library_sha256']}
    wanted.update({r['file']:r['sha256'] for r in owner['dependencies']})
    found=set();sources={};evidence=[]
    for path in sorted((WS/'inventory').glob('client455*.json')):
        report=json.loads(path.read_text(encoding='utf-8'));library=report.get('library')
        if library not in wanted or report.get('library_sha256')!=wanted[library] or not report.get('source_sha256'):continue
        found.add(library);evidence.append({'report':path.relative_to(WS).as_posix(),'sha256':sha(path.read_bytes())})
        for name,digest in report['source_sha256'].items():
            if not name.startswith('client455_') or not name.endswith('.cpp'):continue
            source=native/name
            if sha(source.read_bytes())!=digest:raise ValueError('Changed kernel algorithm:'+name)
            sources[name]=source
    if found!=set(wanted):raise ValueError('Missing kernel production source reports:'+str(set(wanted)-found))
    return sorted(sources.values()),evidence

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
            if source.name.lower()=='cland.cpp':
                start,end=section(raw,b'CLand::UnloadLevel( void )',b'CLand::UnloadLevel( void )')
                body=raw[start:end];anchor=b'\tassert( m_pLevel != NULL );'
                if body.count(anchor)!=1:raise ValueError('Land unload entry changed')
                nl=b'\r\n' if b'\r\n' in body else b'\n'
                body=body.replace(anchor,b'\t// 455 RVA 3C8F30: an uncreated level returns FALSE before cleanup.'+nl+b'\tif( m_pLevel == NULL ) return FALSE;')
                raw=raw[:start]+body+raw[end:]
                changes.append('confirmed455 unload early return before level creation;full ILevel ownership port remains open')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='mainapp.cpp':
                anchor=b'\tInitR3Engine();'
                if raw.count(anchor)!=1:raise ValueError('Normal WinMain engine boundary changed')
                nl=b'\r\n' if b'\r\n' in raw else b'\n'
                raw=b'#include "client455_nation_paths.h"'+nl+b'#include "client455_language.h"'+nl+raw.replace(anchor,b'\tif(!RF455_InitializeNationPaths()) return 0;'+nl+b'\tif(!RF455_InitializeLanguageData()){MessageBoxA(NULL,"LangPack reading failure.","RF Online",0);return 0;}'+nl+anchor)
                changes.append('confirmed nation/path/CRT-codepage/NDLanguage before engine;full font/factories/launcher pending')
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
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='addcodebyyun/particlelist.cpp':
                masked=code_only(raw);matches=list(re.finditer(rb'for\s*\(int i=0;i<MaxObj;i\+\+\)\s*\{',masked))
                if len(matches)!=1:raise ValueError('Active particle mesh loop changed')
                at=matches[0].end();nl=b'\r\n' if b'\r\n' in raw else b'\n'
                raw=raw[:at]+nl+b'\t\tif(!pMesh[i].particleSlots())continue; // 455 null effect guard'+raw[at:]
                changes.append('455 current-effect null guard before particle/entity slots')
            if source.relative_to(port/'source/RF_Client').as_posix().lower()=='addcodebyjang/foreffect.cpp':
                anchor=b'#define GetMega(a)'
                if raw.count(b'g_ChMemoryInfo')!=8 or raw.count(anchor)!=1 or b'characterMemoryInfo' in raw:raise ValueError('Memory diagnostic consumer changed')
                nl=b'\r\n' if b'\r\n' in raw else b'\n'
                raw=raw.replace(anchor,b'const CHMEMORYINFO characterMemoryInfo=RF455_GetCharacterMemoryInfo();'+nl+anchor)
                raw=raw.replace(b'g_ChMemoryInfo',b'characterMemoryInfo')
                changes.append('read confirmed process counters via source-owned memory snapshot')
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
    facade_units=[]
    for name in ['client455_normal_facade.cpp','client455_normal_renderer_math.cpp','client455_normal_contracts.cpp','client455_normal_shadow.cpp','client455_normal_effect_tables.cpp','client455_effect_tables.cpp','client455_effects.cpp','client455_normal_effects.cpp','client455_character_clock.cpp','client455_normal_clock.cpp','client455_normal_accounting.cpp','client455_nation_paths.cpp','client455_language.cpp','client455_font_settings.cpp','client455_font.cpp']:
        source=native/name;facade=root/'generated'/name;save(facade,source.read_bytes(),source);facade_units.append(facade)
    cmake+='add_library(RFClient455Facade STATIC '+''.join(' "'+p.as_posix()+'"' for p in facade_units)+')\ntarget_include_directories(RFClient455Facade PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\ntarget_compile_options(RFClient455Facade PRIVATE /W3 /O2 /Gy /EHsc)\nset_target_properties(RFClient455Facade PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    sources,kernel_evidence=kernel_sources(native);kernel_units=[]
    for source in sources:
        target=root/'generated/kernels'/source.name;save(target,source.read_bytes(),source);kernel_units.append(target)
    cmake+='add_library(RFClient455Kernels STATIC '+''.join(' "'+p.as_posix()+'"' for p in kernel_units)+')\ntarget_include_directories(RFClient455Kernels PRIVATE\n'+''.join(' "'+p.as_posix()+'"\n' for p in directories)+')\ntarget_compile_definitions(RFClient455Kernels PRIVATE _CRT_SECURE_NO_WARNINGS)\ntarget_compile_options(RFClient455Kernels PRIVATE /W3 /O2 /Gy /EHsc /MP4)\nset_target_properties(RFClient455Kernels PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    save(root/'CMakeLists.txt',cmake.encode());manifest.write_text(json.dumps(records,indent=2)+'\n')
    report={'scope':'Actual180original client sources plus2production TU splits against455records/D3D9;open methods remain undefined','original_sources':180,'sources':len(units),'manifest':manifest.relative_to(WS).as_posix(),'manifest_sha256':sha(manifest.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'record_inputs':{name:sha((native/name).read_bytes()) for name in ['Character455.h','client455_normal_model.inc','client455_normal_mesh.inc','client455_normal_animation.inc','client455_normal_facade.cpp','client455_normal_renderer_math.cpp','client455_normal_renderer_math.h','client455_normal_renderer_constants.h']},'legacy_character_linked':False,'baseline_modified':False,'engine033_modified':False}
    report['canonical_kernel_sources']=[p.relative_to(WS).as_posix() for p in kernel_units];report['kernel_source_reports']=kernel_evidence
    report['record_inputs']['client455_normal_contracts.cpp']=sha((native/'client455_normal_contracts.cpp').read_bytes())
    for name in ['client455_normal_shadow.cpp','client455_normal_shadow.h','client455_normal_shadow_constants.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_normal_effect_tables.cpp','client455_effect_tables.cpp','client455_effect_tables.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_effects.cpp','client455_effects.h','client455_effect_constants.h','client455_normal_effects.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_character_clock.cpp','client455_character_clock.h','client455_normal_clock.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_normal_accounting.cpp','client455_normal_accounting.h','client455_normal_facade.cpp']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_nation_paths.cpp','client455_nation_paths.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_language.cpp','client455_language.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    for name in ['client455_font_settings.cpp','client455_font_settings.h','client455_font.cpp','client455_font.h']:report['record_inputs'][name]=sha((native/name).read_bytes())
    snapshot=art/'pre-canonical-renderer-gpu.json'
    if not snapshot.exists():snapshot.write_bytes((WS/'inventory/client455-normal-renderer-gpu.json').read_bytes())
    preserved=WS/'inventory/client455-normal-renderer-precanonical.json'
    if not preserved.exists():preserved.write_bytes(snapshot.read_bytes())
    report['precanonical_renderer_sha256']=sha(preserved.read_bytes())
    (WS/'inventory/client455-normal-preparation.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared180originalsources+2production splits;canonical kernel sources:'+str(len(kernel_units)))
if __name__=='__main__':main()
