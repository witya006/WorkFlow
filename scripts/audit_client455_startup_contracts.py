"""Pin target455startup contracts and distinguish them from legacy assumptions."""
import hashlib,json
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];last=None
    ranges=[('reference_winmain',0x7d04e0,0x7ec),('force_renderbits32',0x8ed5a0,11),('device_wrapper',0x8edab0,0xf7),('setup_language',0x7d2880,0xda),('configuration_filename',0xab04f8,15)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        rows=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in ranges]
        if last is not None and rows!=last:raise ValueError('Startup contracts differ between pins')
        last=rows;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':rows})
        if read_va(raw,0x8ed5a0,11)!=bytes.fromhex('c705a87c150120000000c3') or read_va(raw,0xab04f8,15)!=b'.\\R3Engine.ini\0':raise ValueError('Changed color/config contract')
    report={'scope':'Confirmed startup color/write and Create result contracts;not full455bootstrap/locale/network implementation','references':refs,'facts':['8ED5A0 writes render depth DWORD1157CA8=32, not fullscreen DWORD1157CB0','8EDAB0 calls virtualCreate;any nonzero result exits(0), then flag/input handling and return0','WinMain sets nation/language/launcher/config/network before engine and loads BGMList after WaveList;legacy bootstrap is not equivalent','Setup/Language read from .\\R3Engine.ini;locale manager/paths require further reconstruction'],'gaps':['Console camera branch adds index18 reset in455, old console only17entries;do not write beyond old table','Nation/launcher/locale/language dispatch and whole startup/Create/GUI/network remain open','Reference EXEs are static evidence only, never executed'],'script_sha256':sha((WS/'scripts/audit_client455_startup_contracts.py').read_bytes())}
    (WS/'inventory/client455-startup-contracts-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:455startup color32/Create policy/config pinned bothbins;locale/order gaps explicit')
if __name__=='__main__':main()
