"""Compare the current own executable with accepted074 before selecting regressions."""
import hashlib,json,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_normal_link_evidence import validate_normal_link

def sha(raw):return hashlib.sha256(raw).hexdigest()

def layout(raw):
    nt,=struct.unpack_from('<I',raw,60);count,=struct.unpack_from('<H',raw,nt+6);optional,=struct.unpack_from('<H',raw,nt+20);sections=[]
    for index in range(count):
        at=nt+24+optional+index*40;virtual,rva,size,offset=struct.unpack_from('<4I',raw,at+8);sections.append({'name':raw[at:at+8].split(b'\0')[0].decode(),'virtual':virtual,'rva':rva,'bytes':size,'offset':offset})
    debug_rva,debug_bytes=struct.unpack_from('<II',raw,nt+24+96+6*8);stamps=[nt+8]
    for section in sections:
        if section['rva']<=debug_rva<section['rva']+section['bytes']:
            debug_at=section['offset']+debug_rva-section['rva'];stamps += [debug_at+i*28+4 for i in range(debug_bytes//28)]
    return {'sections':sections,'timestamp_offsets':stamps}

def normalized(raw):
    copy=bytearray(raw)
    for at in layout(raw)['timestamp_offsets']:copy[at:at+4]=b'\0'*4
    return bytes(copy)

def main():
    baseline='c72e3d7'
    def prior(name):return json.loads(subprocess.check_output(['git','-c','safe.directory='+str(WS),'show',baseline+':inventory/'+name+'.json'],cwd=WS))
    old_link=prior('client455-normal-link');old_start=prior('client455-ui-startup-native');old_path=WS/old_start['staged_executable'];old=old_path.read_bytes();current=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(current);new=(WS/current['executable']['file']).read_bytes()
    if sha(old)!=old_link['executable']['sha256'] or not old_start['completed_existing_client_create']:raise ValueError('Changed accepted074baseline')
    old_layout,new_layout=layout(old),layout(new);equal=old_layout==new_layout and normalized(old)==normalized(new);different=[i for i in range(min(len(old),len(new))) if old[i]!=new[i]]
    report={'scope':'Own PE runtime identity against074;not455equivalence or production Tutorial integration','baseline_commit':baseline,'baseline':{'file':old_path.relative_to(WS).as_posix(),'sha256':sha(old)},'current':current['executable'],'same_size':len(old)==len(new),'same_layout':old_layout==new_layout,'same_runtime_bytes_ignoring_link_timestamps':equal,'normalized_runtime_sha256':{'old':sha(normalized(old)),'new':sha(normalized(new))},'metadata_timestamp_offsets':new_layout['timestamp_offsets'],'actual_changed_byte_offsets':different,'normal_link_sha256':sha((WS/'inventory/client455-normal-link.json').read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-intro-production.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'runtime_equal':equal,'same_size':report['same_size'],'changed_offsets':different}))
if __name__=='__main__':main()
