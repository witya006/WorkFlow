"""Stage a separate real D3D9 migration tree;never modify reference orbaseline."""
import hashlib,json,shutil,xml.etree.ElementTree as ET
from pathlib import Path
from compare_client_binaries import WS
from client455_d3d9_port import migrate,ENGINE_DEFINITIONS
from client455_d3d9_edits import manual_edits

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    root=WS/'work/client455-port';baseline=WS/'work/client-build/source';records=[];changed=[];manifest=WS/'artifacts/client455-d3d9-port/source-migration.json';previous={r['file']:r for r in json.loads(manifest.read_text(encoding='utf-8'))} if manifest.exists() else {}
    for source in sorted(baseline.rglob('*')):
        if not source.is_file():continue
        relative=source.relative_to(baseline);destination=root/'source'/relative;before=source.read_bytes();after,edits=migrate(before) if source.suffix.lower() in ['.h','.cpp','.c','.inl'] else (before,[])
        after,manual=manual_edits(relative.as_posix(),after);edits+=manual;destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists() and destination.read_bytes()!=after and sha(destination.read_bytes())!=previous.get(relative.as_posix(),{}).get('port_sha256'):raise ValueError('Preserving differing port source:'+str(destination))
        if not destination.exists() or destination.read_bytes()!=after:destination.write_bytes(after)
        row={'file':relative.as_posix(),'baseline_sha256':sha(before),'port_sha256':sha(after),'edits':edits};records.append(row)
        if before!=after:changed.append(row)
    tree=ET.parse(WS/'work/client-build/build-character-diagnostic/R3EngineClientMT.vcxproj');units=[]
    for node in tree.iter():
        if node.tag.rsplit('}',1)[-1]=='ClCompile' and 'Include' in node.attrib:
            path=Path(node.attrib['Include']);path=root/'source'/path.relative_to(baseline) if path.is_relative_to(baseline) else path;units.append(path)
    if len(units)!=67:raise ValueError('Current engine source set changed')
    sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text(encoding='utf-8'));include=WS/sdk['include'];std=root/'port_std.hpp'
    std.write_text('#include <winsock2.h>\n#include <windows.h>\n#include <tchar.h>\n#include "dxutil.h"\n#include <list>\n#include <queue>\n#include <map>\n#include <vector>\n#include <string>\n#include "client455_d3d9_port.h"\nusing namespace std;\n',encoding='ascii')
    engine=root/'source/R3Engine';native=WS/'scripts/native';directories=[engine,engine/'extension',engine/'1stclass',engine/'2ndclass',engine/'common',engine/'d3d/include',include,native,WS/'work/recovered/client455/x87-math']
    flags=' '.join(ENGINE_DEFINITIONS)
    cmake='cmake_minimum_required(VERSION 3.24)\nproject(RFClient455Port LANGUAGES CXX)\nif(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)\n message(FATAL_ERROR "VS2026 x86 required")\nendif()\nadd_library(R3Engine455 STATIC\n'+''.join(' "'+str(p).replace('\\','/')+'"\n' for p in units)+')\ntarget_include_directories(R3Engine455 PRIVATE\n'+''.join(' "'+str(p).replace('\\','/')+'"\n' for p in directories)+')\ntarget_compile_definitions(R3Engine455 PRIVATE '+flags+')\ntarget_compile_options(R3Engine455 PRIVATE /W3 /EHsc /Zc:forScope- /Od /MP4)\nset_target_properties(R3Engine455 PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES MSVC_RUNTIME_LIBRARY MultiThreaded)\n'
    for path in units:
        if path.is_relative_to(root/'source'):cmake+='set_property(SOURCE "'+str(path).replace('\\','/')+'" APPEND PROPERTY COMPILE_OPTIONS "/FI'+str(std).replace('\\','/')+'")\n'
    (root/'CMakeLists.txt').write_text(cmake,encoding='utf-8');art=WS/'artifacts/client455-d3d9-port';art.mkdir(parents=True,exist_ok=True);manifest=art/'source-migration.json';manifest.write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    inputs=[WS/'scripts/client455_d3d9_port.py',WS/'scripts/client455_d3d9_edits.py',WS/'scripts/native/client455_d3d9_port.h',WS/'scripts/native/client455_r3_shader_load.inc',WS/'scripts/native/client455_r3_shader_assemble.inc']
    report={'scope':'Separate D3D9 source migration tree,not client455acceptance;no legacy Character ABI aliased','root':root.relative_to(WS).as_posix(),'baseline':'work/client-build/source','staged_files':len(records),'changed_files':len(changed),'engine_sources':len(units),'sdk_report_sha256':sha((WS/'inventory/d3dx9-headers.json').read_bytes()),'manifest':manifest.relative_to(WS).as_posix(),'manifest_sha256':sha(manifest.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'rewriter_sha256':sha((WS/'scripts/client455_d3d9_port.py').read_bytes()),'migration_inputs_sha256':{p.relative_to(WS).as_posix():sha(p.read_bytes()) for p in inputs},'baseline_mutated':False,'source_validation':'Compiler errors remain authoritative;API rewrites do notprove455behavior;nonzero indices bases/overlapping rewrites fail explicitly'}
    (WS/'inventory/client455-d3d9-port-preparation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['staged_files','changed_files','engine_sources']}))
if __name__=='__main__':main()
