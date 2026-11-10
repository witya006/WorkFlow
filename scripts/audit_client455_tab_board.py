"""Verify the455 TabBoard dependency without accepting its unported CharInfo caller."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions
from client455_normal_link_evidence import validate_normal_link
from checkpoint_client455_rvp_effects import sha,check,require
def record(path):
    path=Path(path);return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    raw=WS/'artifacts/client455-progress/charinfo160-reference/tab-board.json';proof=verify_regions(raw)
    require(proof['full_functions']==17 and proof['full_instructions']==1318,'Complete TabBoard reference')
    source=WS/'scripts/native/client455_gui_tab_board.cpp';header=source.with_suffix('.h')
    reference=dict(status='STATIC_CONFIRMED_PARTIAL',raw=record(raw),**proof,script=record(__file__),sources=[record(source),record(header),record(WS/'scripts/prepare_client455_normal.py')],
        prior_runtime=record(WS/'artifacts/client455-progress/before160/manifest.json'),
        facts=['Expandable sections use container membership as state;header mouse stroke toggles',
               'Initial header/content geometry,retained children,centered label,stacked reflow and real scrollbar observer',
               'SetAmount uses contentHeight-viewportHeight and current clamp,then shifts entire body',
               'Source-owned RAII groups replace private1268/492-byte records;not a shared binary ABI',
               '7B4E30(style0) resets thumb6x18;639590(total0) keeps prior extent,so full-frame reload equality is not the original rule'],
        gaps=['Ordinary CharInfo455 outer window/3pages/23value owners/mastery/race producers not yet connected',
              'Current normal executable does not retain TabBoard455;the component probe is the real caller',
              'Unsafe target clear/reinit stale-list/empty-reflow/allocation failure andcoordinate-overflow domains not accepted',
              'Full remaining MainGame UI/world/control/gameplay/client455 acceptance open'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-tab-board-reference.json').write_text(json.dumps(reference,indent=2)+'\n')
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());require(validate_normal_link(link)=='PASS','Current link')
    native=json.loads((WS/'inventory/client455-tab-board-native.json').read_text())
    require(native['status']=='PASS' and native['natural_exit']==0 and native['native']['status']=='PASS' and len(native['frames'])==4 and all(native['frame_relations'].values()),'Actual component/GPU')
    require(native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Same source build context')
    for item in native['sources']+native['inputs']:check(item)
    check(native['script'])
    for item in native['frames']:check(item);check(item['preview'])
    obj=WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release/client455_gui_tab_board.obj';require(obj.is_file(),'Actual normal component object')
    require('CGUITabBoard455' not in (WS/link['map']['file']).read_text(),'Do not claim current ordinary retention')
    before=WS/'artifacts/client455-progress/before160/work/client455-port/normal/build/RF_Online.bin';old=before.read_bytes();current=(WS/link['executable']['file']).read_bytes()
    debug=[]
    for image in [old,current]:
        nt=struct.unpack_from('<I',image,0x3c)[0];directory=struct.unpack_from('<II',image,nt+24+96+6*8)
        require(directory[1]==28,'One exact IMAGE_DEBUG_DIRECTORY')
        require(read_va(image,0x400000+directory[0]+4,4)==image[nt+8:nt+12],'Debug timestamp equals COFF linker timestamp')
        debug.append(directory)
    require(debug[0]==debug[1],'Same debug-directory location')
    old_image,new_image=pe(old),pe(current)
    require(old_image['architecture']==new_image['architecture']=='x86' and old_image['image_base']==new_image['image_base']==0x400000 and old_image['entry_rva']==new_image['entry_rva'],'Same image architecture/base/entry')
    require(len(old_image['sections'])==len(new_image['sections']),'Same complete section count')
    sections=[]
    for a,b in zip(old_image['sections'],new_image['sections']):
        require(a['name']==b['name'] and a['rva']==b['rva'] and a['raw_size']==b['raw_size'],'Compare exact complete runtime section identity')
        equal=old[a['raw_offset']:a['raw_offset']+a['raw_size']]==current[b['raw_offset']:b['raw_offset']+b['raw_size']]
        differences=[i for i,(x,y) in enumerate(zip(old[a['raw_offset']:a['raw_offset']+a['raw_size']],current[b['raw_offset']:b['raw_offset']+b['raw_size']])) if x!=y]
        except_timestamp=all(debug[0][0]+4<=a['rva']+i<debug[0][0]+8 for i in differences)
        sections.append(dict(name=a['name'],raw_equal=equal,equal_except_verified_debug_timestamp=except_timestamp,differing_bytes=len(differences),first_differing_rvas=[hex(a['rva']+i) for i in differences[:8]]))
    require(all(x['equal_except_verified_debug_timestamp'] for x in sections),'Unused dependency changed runtime bytes beyond verified linker timestamp')
    bindings=[]
    for address,name in [(0x620230,'CGUITabBoard455'),(0x620360,'~CGUITabBoard455'),(0x620410,'Init455'),(0x620a60,'Clear455'),(0x620ad0,'SetSize'),(0x620b60,'SetHeaderSprites455'),(0x620c00,'SetTitle455'),(0x620d40,'IsOpened455'),(0x620db0,'SetOpened455'),(0x620fe0,'Reflow455'),(0x6211e0,'RepositionScroll455'),(0x621300,'Content455'),(0x6213f0,'ScrollEvent'),(0x621440,'MouseEvent')]:
        bindings.append(dict(rva=hex(address-0x400000),symbol='CGUITabBoard455::'+name,source=record(header if address==0x620230 else source),scope='Semantic dependency/component only;RAII/privateABI and unsafe domain gaps',retained_in_ordinary_executable=False,complete_equivalence=False))
    binding_report=dict(schema_version=1,reference_sha256=proof['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=bindings)
    (WS/'inventory/client455-tab-board-bindings.json').write_text(json.dumps(binding_report,indent=2)+'\n')
    names=['tab-board-reference','tab-board-bindings','tab-board-native','normal-build','normal-consumers','normal-link','normal-preparation']
    gate=dict(status='PARTIAL_COMPONENT_ONLY',scope='Recovered actual455TabBoard dependency;ordinary CharInfo still unported',script=record(__file__),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],normal_component_object=record(obj),
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=reference['prior_runtime'],
        normal_sections_compared_before160=sections,verified_linker_debug_timestamp_rva=hex(debug[0][0]+4),last_ordinary_runtime_checkpoint=record(WS/'artifacts/client455-progress/before160/inventory/client455-hud-checkpoint.json'),
        component_source_verified=True,component_GPU_frames=4,ordinary_CharInfo_connected=False,retained_in_ordinary_executable=False,explicit_function_bindings=len(bindings),
        gaps=reference['gaps'],world_entered=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-tab-board-checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
    file=WS/'inventory/client-features.json';registry=json.loads(file.read_text());feature=dict(id='CLIENT455-TABBOARD-160',status='partial_component',description=gate['scope'],
        implementation=['scripts/native/client455_gui_tab_board.h','scripts/native/client455_gui_tab_board.cpp'],evidence=['inventory/client455-tab-board-checkpoint.json','inventory/client455-tab-board-reference.json'],
        ordinary_CharInfo_connected=False,retained_in_ordinary_executable=False,full_client=False,M6='OPEN',M9='OPEN')
    matches=[i for i,x in enumerate(registry['features']) if x['id']==feature['id']]
    if matches:registry['features'][matches[0]]=feature
    else:registry['features'].append(feature)
    file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    print('PARTIAL_COMPONENT_ONLY:17functions/1318instructions,bothpins;expandable sections/GPU;ordinary CharInfo not connected;runtime sections equal except verified linker timestamp')
if __name__=='__main__':main()
